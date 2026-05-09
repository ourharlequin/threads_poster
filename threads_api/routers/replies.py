import os
import json
import time
import logging
import duckdb
import requests
from collections import Counter
from datetime import datetime, timedelta
from openai import OpenAI
from fastapi import APIRouter, HTTPException

import registry

router = APIRouter()
log = logging.getLogger("replies")

THREADS_API_BASE = "https://graph.threads.net/v1.0"
API_DELAY = 0.5
PUBLISH_DELAY_SEC = 5
BATCH_SIZE = 20


def _get_account(account_id: str) -> dict:
    if account_id not in registry.REGISTRY:
        raise HTTPException(404, f"Account '{account_id}' not found")
    return registry.REGISTRY[account_id]


def _init_reply_log(db_path: str):
    os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
    with duckdb.connect(db_path) as conn:
        conn.execute("CREATE SEQUENCE IF NOT EXISTS reply_log_id_seq START 1")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS reply_log (
                id           INTEGER PRIMARY KEY DEFAULT nextval('reply_log_id_seq'),
                account_id   VARCHAR NOT NULL,
                post_id      VARCHAR NOT NULL,
                comment_id   VARCHAR NOT NULL,
                username     VARCHAR,
                comment_text TEXT,
                reply_id     VARCHAR,
                sentiment    VARCHAR,
                fetched_at   TIMESTAMPTZ DEFAULT now(),
                replied_at   TIMESTAMPTZ
            )
        """)


def _get_posts_with_replies(db_path: str, account_id: str) -> list[dict]:
    """Возвращает только посты у которых есть хотя бы 1 reply по данным insights."""
    with duckdb.connect(db_path, read_only=True) as conn:
        rows = conn.execute("""
            SELECT p.threads_post_id, p.content
            FROM posts p
            JOIN post_insights pi ON pi.post_id = p.id
            WHERE p.account_id = ?
              AND p.threads_post_id IS NOT NULL
              AND pi.replies > 0
            GROUP BY p.threads_post_id, p.content
            ORDER BY MAX(pi.replies) DESC
        """, [account_id]).fetchall()
    return [{"post_id": r[0], "content": r[1]} for r in rows]


def _fetch_thread_replies(post_id: str, token: str) -> list[dict]:
    """Скачивает все комментарии через /conversation с поддержкой пагинации."""
    results = []
    params = {"fields": "id,text,username,timestamp", "access_token": token}
    url = f"{THREADS_API_BASE}/{post_id}/conversation"
    while url:
        resp = requests.get(url, params=params, timeout=15)
        if resp.status_code != 200:
            log.warning("conversation API error for %s: %s", post_id, resp.text[:200])
            break
        body = resp.json()
        results.extend(body.get("data", []))
        url = body.get("paging", {}).get("next")
        params = {}  # next URL уже содержит все параметры
    return results


def _existing_comment_ids(db_path: str, account_id: str) -> set[str]:
    with duckdb.connect(db_path, read_only=True) as conn:
        rows = conn.execute(
            "SELECT comment_id FROM reply_log WHERE account_id = ?", [account_id]
        ).fetchall()
    return {r[0] for r in rows}


def _insert_comments(db_path: str, account_id: str, post_id: str,
                     comments: list[dict], skip_ids: set[str]) -> int:
    new = [c for c in comments if c.get("id") and c["id"] not in skip_ids]
    if not new:
        return 0
    with duckdb.connect(db_path) as conn:
        for c in new:
            conn.execute("""
                INSERT INTO reply_log (account_id, post_id, comment_id, username, comment_text)
                VALUES (?, ?, ?, ?, ?)
            """, [account_id, post_id, c["id"], c.get("username", ""), c.get("text", "")])
    return len(new)


def _get_unanswered(db_path: str, account_id: str) -> list[dict]:
    with duckdb.connect(db_path, read_only=True) as conn:
        rows = conn.execute("""
            SELECT rl.id, rl.comment_id, rl.comment_text, rl.username, rl.post_id,
                   p.content AS post_content
            FROM reply_log rl
            LEFT JOIN posts p ON p.threads_post_id = rl.post_id AND p.account_id = rl.account_id
            WHERE rl.account_id = ?
              AND rl.reply_id IS NULL
              AND rl.comment_text IS NOT NULL
              AND rl.comment_text != ''
            ORDER BY rl.fetched_at DESC
            LIMIT 50
        """, [account_id]).fetchall()
    return [
        {
            "row_id": r[0], "comment_id": r[1], "comment_text": r[2],
            "username": r[3], "post_id": r[4], "post_content": r[5] or "",
        }
        for r in rows
    ]


def _llm_client() -> OpenAI:
    api_key = os.environ.get("HF_TOKEN")
    if not api_key:
        raise HTTPException(500, "HF_TOKEN not set")
    return OpenAI(base_url="https://router.huggingface.co/v1", api_key=api_key)


def _generate_replies(comments: list[dict]) -> dict[str, str]:
    client = _llm_client()
    items = [
        {
            "comment_id": c["comment_id"],
            "post": c["post_content"][:300],
            "username": c["username"],
            "comment": c["comment_text"],
        }
        for c in comments
    ]
    user_msg = (
        "For each comment write a short natural reply (1-2 sentences). "
        "Match the language of the comment. Be warm but brief.\n\n"
        "Return ONLY valid JSON: [{\"comment_id\": \"...\", \"reply\": \"...\"}, ...]\n\n"
        + json.dumps(items, ensure_ascii=False)
    )
    resp = _llm_client().chat.completions.create(
        model="Qwen/Qwen2.5-72B-Instruct",
        messages=[
            {"role": "system", "content": (
                "You write short natural replies to social media comments on behalf of the post author. "
                "Match the language of the comment. 1-2 sentences max."
            )},
            {"role": "user", "content": user_msg},
        ],
        max_tokens=2048,
        temperature=0.7,
    )
    text = resp.choices[0].message.content.strip()
    start, end = text.find("["), text.rfind("]")
    if start == -1 or end == -1:
        raise HTTPException(502, f"LLM response is not JSON array: {text[:200]}")
    parsed = json.loads(text[start:end + 1])
    return {item["comment_id"]: item["reply"] for item in parsed
            if "comment_id" in item and "reply" in item}


def _analyze_sentiment(comments: list[dict]) -> list[dict]:
    client = _llm_client()
    items = [{"comment_id": c["comment_id"], "text": c["comment_text"]} for c in comments]
    user_msg = (
        "Classify the sentiment of each comment as one of: positive, negative, question, neutral.\n"
        "Return ONLY valid JSON: [{\"comment_id\": \"...\", \"sentiment\": \"...\"}, ...]\n\n"
        + json.dumps(items, ensure_ascii=False)
    )
    resp = client.chat.completions.create(
        model="Qwen/Qwen2.5-72B-Instruct",
        messages=[
            {"role": "system", "content": "Classify social media comment sentiment. Return JSON only."},
            {"role": "user", "content": user_msg},
        ],
        max_tokens=1024,
        temperature=0.1,
    )
    text = resp.choices[0].message.content.strip()
    start, end = text.find("["), text.rfind("]")
    if start == -1 or end == -1:
        return []
    return json.loads(text[start:end + 1])


def _publish_reply(comment_id: str, reply_text: str, token: str, user_id: str) -> str | None:
    resp = requests.post(
        f"{THREADS_API_BASE}/{user_id}/threads",
        params={"access_token": token},
        json={"media_type": "TEXT", "text": reply_text, "reply_to_id": comment_id},
        timeout=15,
    )
    if resp.status_code != 200:
        log.warning("create reply container failed for %s: %s", comment_id, resp.text[:200])
        return None
    container_id = resp.json().get("id")
    if not container_id:
        return None

    time.sleep(PUBLISH_DELAY_SEC)

    resp2 = requests.post(
        f"{THREADS_API_BASE}/{user_id}/threads_publish",
        params={"access_token": token},
        json={"creation_id": container_id},
        timeout=15,
    )
    if resp2.status_code != 200:
        log.warning("publish reply failed for container %s: %s", container_id, resp2.text[:200])
        return None
    return resp2.json().get("id")


def _mark_replied(db_path: str, row_id: int, reply_id: str):
    with duckdb.connect(db_path) as conn:
        conn.execute(
            "UPDATE reply_log SET reply_id = ?, replied_at = now() WHERE id = ?",
            [reply_id, row_id],
        )


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/debug/{account_id}")
def debug_replies(account_id: str):
    """Сравнение /replies и /conversation для поста с наибольшим числом реплаев."""
    acc = _get_account(account_id)
    with duckdb.connect(acc["db_path"], read_only=True) as conn:
        row = conn.execute("""
            SELECT p.threads_post_id, p.content, pi.replies
            FROM posts p
            JOIN post_insights pi ON pi.post_id = p.id
            WHERE p.account_id = ? AND p.threads_post_id IS NOT NULL
            ORDER BY pi.replies DESC
            LIMIT 1
        """, [account_id]).fetchone()
    if not row:
        return {"ok": False, "error": "no posts with insights found"}
    post = {"post_id": row[0], "content": row[1][:100], "replies_count": row[2]}
    fields = "id,text,username,timestamp"

    r1 = requests.get(
        f"{THREADS_API_BASE}/{post['post_id']}/replies",
        params={"fields": fields, "access_token": acc["token"]},
        timeout=15,
    )
    r2 = requests.get(
        f"{THREADS_API_BASE}/{post['post_id']}/conversation",
        params={"fields": fields, "access_token": acc["token"]},
        timeout=15,
    )
    return {
        "ok": True,
        "data": {
            "post_id": post["post_id"],
            "content": post["content"],
            "replies_in_db": post["replies_count"],
            "replies":      {"status": r1.status_code, "raw": r1.json()},
            "conversation": {"status": r2.status_code, "raw": r2.json()},
        },
    }


@router.get("/fetch/{account_id}")
def fetch_replies(account_id: str):
    """Скачать новые комментарии из Threads API и сохранить в reply_log."""
    acc = _get_account(account_id)
    _init_reply_log(acc["db_path"])
    posts = _get_posts_with_replies(acc["db_path"], account_id)
    if not posts:
        return {"ok": True, "data": {"new_comments": 0, "posts_checked": 0}}

    existing = _existing_comment_ids(acc["db_path"], account_id)
    total_new = 0
    for post in posts:
        replies = _fetch_thread_replies(post["post_id"], acc["token"])
        total_new += _insert_comments(acc["db_path"], account_id, post["post_id"], replies, existing)
        existing.update(r["id"] for r in replies if r.get("id"))
        time.sleep(API_DELAY)

    return {"ok": True, "data": {"new_comments": total_new, "posts_checked": len(posts)}}


@router.get("/sentiment/{account_id}")
def replies_sentiment(account_id: str, days: int = 30):
    """Анализ тональности комментариев за период через Cerebras."""
    acc = _get_account(account_id)
    _init_reply_log(acc["db_path"])
    cutoff = datetime.utcnow() - timedelta(days=days)
    with duckdb.connect(acc["db_path"], read_only=True) as conn:
        rows = conn.execute("""
            SELECT comment_id, comment_text, username, sentiment
            FROM reply_log
            WHERE account_id = ? AND fetched_at >= ?
              AND comment_text IS NOT NULL AND comment_text != ''
            ORDER BY fetched_at DESC
            LIMIT 200
        """, [account_id, cutoff]).fetchall()

    if not rows:
        return {"ok": True, "data": {"total": 0, "breakdown": {}, "notable": []}}

    comments = [
        {"comment_id": r[0], "comment_text": r[1], "username": r[2], "sentiment": r[3]}
        for r in rows
    ]

    to_classify = [c for c in comments if not c["sentiment"]]
    classified: dict[str, str] = {}
    for i in range(0, len(to_classify), BATCH_SIZE):
        results = _analyze_sentiment(to_classify[i:i + BATCH_SIZE])
        for item in results:
            classified[item["comment_id"]] = item["sentiment"]

    if classified:
        with duckdb.connect(acc["db_path"]) as conn:
            for cid, sentiment in classified.items():
                conn.execute(
                    "UPDATE reply_log SET sentiment = ? WHERE comment_id = ?",
                    [sentiment, cid],
                )

    for c in comments:
        if c["comment_id"] in classified:
            c["sentiment"] = classified[c["comment_id"]]

    breakdown = dict(Counter(c["sentiment"] or "unclassified" for c in comments))
    notable = [
        {"username": c["username"], "text": c["comment_text"], "sentiment": c["sentiment"]}
        for c in comments
        if c["sentiment"] in ("negative", "question")
    ][:20]

    return {"ok": True, "data": {"total": len(comments), "breakdown": breakdown, "notable": notable}}


@router.post("/auto-reply/{account_id}")
def auto_reply(account_id: str):
    """Сгенерировать и опубликовать ответы на все неотвеченные комментарии через Cerebras."""
    acc = _get_account(account_id)
    _init_reply_log(acc["db_path"])
    unanswered = _get_unanswered(acc["db_path"], account_id)
    if not unanswered:
        return {"ok": True, "data": {"replied": 0, "message": "No unanswered comments"}}

    published = 0
    failed = 0
    for i in range(0, len(unanswered), BATCH_SIZE):
        batch = unanswered[i:i + BATCH_SIZE]
        try:
            replies_map = _generate_replies(batch)
        except Exception as e:
            log.error("LLM error for batch: %s", e)
            failed += len(batch)
            continue

        for comment in batch:
            reply_text = replies_map.get(comment["comment_id"])
            if not reply_text:
                failed += 1
                continue
            reply_id = _publish_reply(
                comment["comment_id"], reply_text, acc["token"], acc["user_id"]
            )
            if reply_id:
                _mark_replied(acc["db_path"], comment["row_id"], reply_id)
                published += 1
            else:
                failed += 1
            time.sleep(API_DELAY)

    return {"ok": True, "data": {"replied": published, "failed": failed, "total": len(unanswered)}}
