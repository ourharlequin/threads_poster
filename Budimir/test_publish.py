"""
Тестовая публикация одного поста для каждого аккаунта.
Запуск: python test_publish.py
"""

import os
import time
import logging
import requests
import duckdb
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv("DB_PATH", "data/data.duckdb")
THREADS_API_BASE = "https://graph.threads.net/v1.0"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
log = logging.getLogger("test_publish")


def load_accounts() -> list[dict]:
    accounts = []
    for i in range(1, 100):
        acc_id = os.getenv(f"ACCOUNT_{i}_ID")
        if not acc_id:
            continue
        user_id = os.getenv(f"ACCOUNT_{i}_USER_ID")
        token = os.getenv(f"ACCOUNT_{i}_THREADS_TOKEN")
        if user_id and token:
            accounts.append({"account_id": acc_id, "user_id": user_id, "token": token})
    return accounts


def get_next_pending(account_id: str) -> dict | None:
    with duckdb.connect(DB_PATH) as conn:
        row = conn.execute(
            "SELECT id, content FROM posts WHERE account_id = ? AND status = 'pending' ORDER BY created_at ASC LIMIT 1",
            [account_id],
        ).fetchone()
    return {"id": row[0], "content": row[1]} if row else None


def publish(user_id: str, token: str, text: str) -> str | None:
    resp = requests.post(
        f"{THREADS_API_BASE}/{user_id}/threads",
        data={"media_type": "TEXT", "text": text, "access_token": token},
        timeout=30,
    )
    if resp.status_code != 200:
        log.error(f"Контейнер: {resp.status_code} {resp.text}")
        return None
    container_id = resp.json().get("id")
    time.sleep(5)
    resp2 = requests.post(
        f"{THREADS_API_BASE}/{user_id}/threads_publish",
        data={"creation_id": container_id, "access_token": token},
        timeout=30,
    )
    if resp2.status_code != 200:
        log.error(f"Публикация: {resp2.status_code} {resp2.text}")
        return None
    return resp2.json().get("id")


def mark_posted(post_id: int, threads_post_id: str):
    from datetime import datetime, timezone
    with duckdb.connect(DB_PATH) as conn:
        conn.execute(
            "UPDATE posts SET status='posted', posted_at=?, threads_post_id=? WHERE id=?",
            [datetime.now(timezone.utc), threads_post_id, post_id],
        )


accounts = load_accounts()
log.info(f"Аккаунтов: {len(accounts)}")

for acc in accounts:
    acc_id = acc["account_id"]
    post = get_next_pending(acc_id)
    if not post:
        log.warning(f"[{acc_id}] Нет pending постов")
        continue

    log.info(f"[{acc_id}] Публикую: {post['content'][:80]}...")
    threads_id = publish(acc["user_id"], acc["token"], post["content"])

    if threads_id:
        mark_posted(post["id"], threads_id)
        log.info(f"[{acc_id}] ✅ Опубликовано (threads_id={threads_id})")
    else:
        log.error(f"[{acc_id}] ❌ Ошибка публикации")
