"""
Генератор постов для Threads через Cerebras API.
Использование: python generate_posts.py --account event_parsing
"""

import os
import sys
import argparse
import random
import logging
import time
from datetime import datetime, timezone

import duckdb
from cerebras.cloud.sdk import Cerebras
from dotenv import load_dotenv

from prompts import get_account_config

load_dotenv()

DB_PATH        = os.getenv("DB_PATH", "data/data.duckdb")
MODEL          = "gpt-oss-120b"
POSTS_COUNT    = 30
REQUEST_DELAY  = 3.0   # секунды между запросами
MAX_RETRIES    = 3
RETRY_DELAY    = 15.0  # пауза после 429

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
)
log = logging.getLogger("generator")


def init_db():
    os.makedirs(os.path.dirname(DB_PATH) or ".", exist_ok=True)
    with duckdb.connect(DB_PATH) as conn:
        conn.execute("CREATE SEQUENCE IF NOT EXISTS posts_id_seq START 1")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id              INTEGER PRIMARY KEY DEFAULT nextval('posts_id_seq'),
                account_id      VARCHAR NOT NULL,
                content         TEXT    NOT NULL,
                status          VARCHAR NOT NULL DEFAULT 'pending',
                created_at      TIMESTAMPTZ DEFAULT now(),
                posted_at       TIMESTAMPTZ,
                threads_post_id VARCHAR
            )
        """)


MAX_CHARS = 500  # Threads API limit


def truncate_to_limit(text: str, limit: int = MAX_CHARS) -> str:
    """Truncate to last complete sentence within limit, or hard-cut at word boundary."""
    if len(text) <= limit:
        return text
    chunk = text[:limit]
    for sep in (".", "!", "?"):
        pos = chunk.rfind(sep)
        if pos > 0:
            return chunk[: pos + 1].strip()
    pos = chunk.rfind(" ")
    return (chunk[:pos] if pos > 0 else chunk).strip()


def generate_post(client: Cerebras, fmt_name: str, fmt_prompt: str, system_prompt: str) -> str | None:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user",   "content": fmt_prompt},
                ],
                max_completion_tokens=200,
                temperature=0.9,
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            err = str(e)
            if "rate_limit" in err.lower() or "429" in err or "too many requests" in err.lower():
                log.warning(f"Rate limit ({fmt_name}), попытка {attempt}/{MAX_RETRIES}. Жду {RETRY_DELAY}с...")
                time.sleep(RETRY_DELAY * attempt)
            else:
                log.error(f"Cerebras error ({fmt_name}): {e}")
                return None
    log.error(f"Не удалось сгенерировать пост ({fmt_name}) после {MAX_RETRIES} попыток")
    return None


def main():
    parser = argparse.ArgumentParser(
        description="Генерирует посты через Cerebras и записывает в DuckDB"
    )
    parser.add_argument("--account", required=True,
                        help="account_id (например: event_parsing, aire.porteno)")
    parser.add_argument("--count", type=int, default=POSTS_COUNT,
                        help=f"Количество постов (по умолчанию {POSTS_COUNT})")
    args = parser.parse_args()
    account_id = args.account
    count      = args.count

    init_db()

    cerebras_key = os.getenv("CEREBRAS_API_KEY")
    if not cerebras_key:
        log.error("CEREBRAS_API_KEY не найден в .env")
        sys.exit(1)

    try:
        config = get_account_config(account_id)
    except KeyError as e:
        log.error(e)
        sys.exit(1)

    system_prompt = config["system"]
    formats       = config["formats"]

    client    = Cerebras(api_key=cerebras_key)
    fmt_names = list(formats.keys())
    generated = 0
    failed    = 0

    with duckdb.connect(DB_PATH) as conn:
        for i in range(count):
            fmt_name   = random.choice(fmt_names)
            fmt_prompt = formats[fmt_name]
            content    = generate_post(client, fmt_name, fmt_prompt, system_prompt)

            if not content:
                failed += 1
            else:
                content = truncate_to_limit(content)
                conn.execute(
                    """
                    INSERT INTO posts (account_id, content, status, created_at)
                    VALUES (?, ?, 'pending', ?)
                    """,
                    [account_id, content, datetime.now(timezone.utc)],
                )
                generated += 1
                log.info(f"[{i+1}/{count}] {fmt_name}: {content[:60]}...")

            if i < count - 1:
                time.sleep(REQUEST_DELAY)

    log.info(f"Готово. Сгенерировано: {generated}, ошибок: {failed}")


if __name__ == "__main__":
    main()
