import os
import json
import duckdb
from collections import Counter, defaultdict
from openai import OpenAI
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

import registry

router = APIRouter()

ANALYTICS_DB = "/app/data/analytics/analytics.duckdb"


def _get_account(account_id: str) -> dict:
    if account_id not in registry.REGISTRY:
        raise HTTPException(404, f"Account '{account_id}' not found")
    return registry.REGISTRY[account_id]


def _load_prompts(scripts_dir: str) -> dict:
    path = os.path.join(scripts_dir, "prompts.py")
    ns: dict = {}
    with open(path, "r", encoding="utf-8") as f:
        exec(f.read(), ns)  # noqa: S102
    return ns["ACCOUNTS"]


def _write_prompts(scripts_dir: str, accounts: dict):
    path = os.path.join(scripts_dir, "prompts.py")
    parts = [
        '"""\n'
        'Конфигурация промптов по аккаунтам.\n'
        'Каждый аккаунт — отдельная тема, свой system-промпт и форматы постов.\n'
        '"""\n\n'
        'ACCOUNTS: dict[str, dict] = {\n'
    ]
    for acc_id, config in accounts.items():
        parts.append(f'\n    {repr(acc_id)}: {{\n')
        parts.append(f'        "system": (\n            {repr(config["system"])}\n        ),\n')
        parts.append('        "formats": {\n')
        for fmt_name, fmt_text in config["formats"].items():
            parts.append(f'            {repr(fmt_name)}: (\n                {repr(fmt_text)}\n            ),\n')
        parts.append('        },\n')
        parts.append('    },\n')
    parts.append(
        '}\n\n\n'
        'def get_account_config(account_id: str) -> dict:\n'
        '    """Возвращает конфиг промптов для аккаунта или бросает KeyError."""\n'
        '    if account_id not in ACCOUNTS:\n'
        '        raise KeyError(\n'
        '            f"Аккаунт \'{account_id}\' не найден в prompts.py. "\n'
        '            f"Доступные: {list(ACCOUNTS.keys())}"\n'
        '        )\n'
        '    return ACCOUNTS[account_id]\n'
    )
    with open(path, "w", encoding="utf-8") as f:
        f.writelines(parts)


def _fetch_posts(account_id: str, metric: str, limit: int, worst: bool) -> list[dict]:
    if metric == "rate":
        score = "CAST(pi.likes + pi.replies + pi.reposts + pi.quotes AS FLOAT) / NULLIF(pi.views, 0)"
    else:
        score = "pi.views * 0.4 + (pi.likes + pi.replies + pi.reposts + pi.quotes) * 0.6"
    order = "ASC" if worst else "DESC"
    with duckdb.connect(ANALYTICS_DB, read_only=True) as conn:
        rows = conn.execute(
            f"""
            SELECT p.content, pi.views, pi.likes, pi.replies, pi.reposts, pi.quotes,
                   ({score}) AS score, p.threads_post_id
            FROM posts p
            JOIN post_insights pi ON p.id = pi.post_id AND p.participant = pi.participant
            WHERE p.account_id = ? AND p.status = 'posted'
            ORDER BY score {order} NULLS LAST
            LIMIT ?
            """,
            [account_id, limit],
        ).fetchall()
    return [
        {"content": r[0], "views": r[1], "likes": r[2], "replies": r[3],
         "reposts": r[4], "quotes": r[5], "score": round(r[6] or 0, 4),
         "threads_post_id": r[7], "comments": {}}
        for r in rows
    ]


def _fetch_comment_signals(db_path: str, account_id: str, post_ids: list[str]) -> dict[str, dict]:
    """Returns {threads_post_id: {breakdown, notable}} from reply_log."""
    if not post_ids:
        return {}
    placeholders = ", ".join(["?"] * len(post_ids))
    try:
        with duckdb.connect(db_path, read_only=True) as conn:
            rows = conn.execute(
                f"""
                SELECT post_id, sentiment, comment_text
                FROM reply_log
                WHERE account_id = ?
                  AND post_id IN ({placeholders})
                  AND comment_text IS NOT NULL AND comment_text != ''
                """,
                [account_id] + post_ids,
            ).fetchall()
    except Exception:
        return {}

    by_post: dict[str, list] = defaultdict(list)
    for post_id, sentiment, text in rows:
        by_post[post_id].append((sentiment or "unclassified", text))

    result = {}
    for post_id, items in by_post.items():
        breakdown = dict(Counter(s for s, _ in items))
        notable = [t for s, t in items if s in ("negative", "question")][:3]
        result[post_id] = {"breakdown": breakdown, "notable": notable}
    return result


def _fmt_posts(posts: list[dict]) -> str:
    parts = []
    for i, p in enumerate(posts, 1):
        lines = [
            f"{i}. score={p['score']} | views={p['views']} likes={p['likes']} "
            f"replies={p['replies']} reposts={p['reposts']} quotes={p['quotes']}",
            f"   {p['content'][:300]}",
        ]
        c = p.get("comments", {})
        if c.get("breakdown"):
            bd = ", ".join(f"{k}={v}" for k, v in c["breakdown"].items())
            lines.append(f"   Comments: {bd}")
        for note in c.get("notable", []):
            lines.append(f"   ↳ {note[:150]}")
        parts.append("\n".join(lines))
    return "\n\n".join(parts)


def _call_groq(account_id: str, metric: str, accounts: dict, top: list, worst: list) -> dict:
    api_key = os.environ.get("HF_TOKEN")
    if not api_key:
        raise HTTPException(500, "HF_TOKEN not set")

    config = accounts.get(account_id, {})
    current_system = config.get("system", "")
    current_formats = config.get("formats", {})
    metric_desc = "engagement/views ratio" if metric == "rate" else "views×0.4 + engagement×0.6"
    formats_str = "\n".join(f'  "{k}":\n    {v}' for k, v in current_formats.items())

    system_prompt = (
        "You are an expert at analyzing social media performance and writing AI prompt instructions.\n"
        "Analyze top vs worst posts, identify patterns, suggest improved prompt formats.\n"
        "Use BOTH engagement metrics AND comment sentiment as signals:\n"
        "- Negative comments reveal factual errors, clickbait, or unclear claims to avoid.\n"
        "- Questions reveal vague or misleading phrasing that needs to be more specific.\n"
        "- Positive comments reveal emotional hooks and topics that resonate.\n"
        "PRIMARY focus: improve 'formats' entries. Change 'system' only if clearly needed.\n"
        "Return ONLY valid JSON (no markdown) with these keys:\n"
        '- "analysis": string (2-3 sentences on what works vs what doesn\'t, referencing comment patterns)\n'
        '- "new_formats": dict of format_name -> improved instruction string\n'
        '- "new_system": string OR null\n'
        '- "reasoning": string (why these changes)'
    )
    user_prompt = (
        f"Account: {account_id}\n"
        f"Ranking metric: {metric_desc}\n\n"
        f"=== CURRENT SYSTEM PROMPT ===\n{current_system}\n\n"
        f"=== CURRENT FORMATS ===\n{formats_str}\n\n"
        f"=== TOP {len(top)} POSTS ===\n{_fmt_posts(top)}\n\n"
        f"=== WORST {len(worst)} POSTS ===\n{_fmt_posts(worst)}\n\n"
        "Suggest improved formats (and optionally new system prompt). Return ONLY JSON."
    )

    client = OpenAI(base_url="https://router.huggingface.co/v1", api_key=api_key)
    resp = client.chat.completions.create(
        model="Qwen/Qwen2.5-72B-Instruct",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=4096,
        temperature=0.3,
    )
    text = resp.choices[0].message.content.strip()
    # Extract JSON robustly — llama may add preamble text or markdown fences
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise HTTPException(502, f"Cerebras response is not JSON: {text[:200]}")
    return json.loads(text[start:end + 1])


@router.get("/analyze/{account_id}")
def analyze_prompts(account_id: str, metric: str = "weighted"):
    """Анализ топ/худших постов и предложение улучшений промптов через Cerebras."""
    if metric not in ("weighted", "rate"):
        raise HTTPException(400, "metric must be 'weighted' or 'rate'")
    acc = _get_account(account_id)
    try:
        accounts = _load_prompts(acc["scripts_dir"])
    except FileNotFoundError:
        raise HTTPException(404, f"prompts.py not found for participant '{acc['participant']}'")
    top = _fetch_posts(account_id, metric, limit=10, worst=False)
    worst = _fetch_posts(account_id, metric, limit=10, worst=True)
    if len(top) < 3:
        raise HTTPException(422, f"Not enough data for '{account_id}' — need at least 3 posted+insights rows")
    post_ids = [p["threads_post_id"] for p in top + worst if p.get("threads_post_id")]
    signals = _fetch_comment_signals(acc["db_path"], account_id, post_ids)
    for p in top + worst:
        p["comments"] = signals.get(p.get("threads_post_id"), {})
    suggestion = _call_groq(account_id, metric, accounts, top, worst)
    return {"ok": True, "data": {"account_id": account_id, "metric": metric, "suggestion": suggestion}}


class ApplyRequest(BaseModel):
    new_system: str | None = None
    new_formats: dict[str, str] | None = None


@router.post("/apply/{account_id}")
def apply_prompts(account_id: str, body: ApplyRequest):
    """Применить предложенные изменения промптов к prompts.py участника."""
    if not body.new_system and not body.new_formats:
        raise HTTPException(400, "Provide new_system or new_formats")
    acc = _get_account(account_id)
    try:
        accounts = _load_prompts(acc["scripts_dir"])
    except FileNotFoundError:
        raise HTTPException(404, f"prompts.py not found for participant '{acc['participant']}'")
    if account_id not in accounts:
        raise HTTPException(404, f"Account '{account_id}' not found in prompts.py")
    if body.new_system:
        accounts[account_id]["system"] = body.new_system
    if body.new_formats:
        accounts[account_id]["formats"].update(body.new_formats)
    _write_prompts(acc["scripts_dir"], accounts)
    return {
        "ok": True,
        "data": {
            "account_id": account_id,
            "system_updated": bool(body.new_system),
            "formats_updated": list(body.new_formats.keys()) if body.new_formats else [],
        },
    }
