"""
Генератор постов для Threads через Cerebras API.
Использование: python generate_posts.py --account event_parsing
"""

import json
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

DB_PATH         = os.getenv("DB_PATH", "data/data.duckdb")
REDDIT_DB_PATH  = os.getenv("REDDIT_DB_PATH", "../reddit_trends/data/reddit.duckdb")
MODEL          = "llama3.1-8b"
POSTS_COUNT    = 30
REQUEST_DELAY  = 3.0   # секунды между запросами
MAX_RETRIES    = 3
RETRY_DELAY    = 15.0  # пауза после 429

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
)
log = logging.getLogger("generator")


def _load_reddit_topics(group: str, lang: str) -> list[dict]:
    """Читает темы дня из центральной Reddit DB. Возвращает [] если данных нет."""
    from datetime import date
    try:
        with duckdb.connect(REDDIT_DB_PATH, read_only=True) as conn:
            row = conn.execute(
                "SELECT topics FROM daily_topics WHERE date = ? AND account_group = ? AND lang = ?",
                [date.today(), group, lang],
            ).fetchone()
        return json.loads(row[0]) if row else []
    except Exception:
        return []


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

    from reddit_trends_config import ACCOUNTS as REDDIT_ACCOUNTS
    acc_reddit = REDDIT_ACCOUNTS.get(account_id)
    topics_context = ""
    if acc_reddit:
        topic_group = acc_reddit["group"]
        topic_lang  = acc_reddit["lang"]
        topics = _load_reddit_topics(topic_group, topic_lang)
        if topics:
            lines = ["\n\nToday's material (optional inspiration, don't mention Reddit, don't copy verbatim):"]
            for t in topics:
                lines.append(f"\n— {t.get('theme', '')}")
                lines.append(f"  Tension: {t.get('tension', '')}")
                lines.append(f"  Hook: {t.get('hook', '')}")
            topics_context = "\n".join(lines)
            log.info(f"Темы дня [{topic_group}/{topic_lang}]: {[t.get('theme') for t in topics]}")
        else:
            log.info(f"Тем дня нет [{topic_group}/{topic_lang}], генерирую без контекста")
    else:
        log.info(f"Аккаунт {account_id} не найден в reddit config — генерирую без контекста")

    client    = Cerebras(api_key=cerebras_key)
    fmt_names = list(formats.keys())
    generated = 0
    failed    = 0

    with duckdb.connect(DB_PATH) as conn:
        for i in range(count):
            fmt_name   = random.choice(fmt_names)
            fmt_prompt = formats[fmt_name]
            content    = generate_post(client, fmt_name, fmt_prompt + topics_context, system_prompt)

            if not content:
                failed += 1
            else:
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
