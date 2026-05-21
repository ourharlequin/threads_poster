"""
merger.py — каждый день в 07:45 по Белграду сливает данные
из четырёх участников в единый analytics.duckdb для Superset.

Источники (пропускаются если файл не существует):
  /app/data/budimir/data.duckdb
  /app/data/slava/data.duckdb
  /app/data/tanya/data.duckdb
  /app/data/chiara/data.duckdb

Результат:
  /app/data/analytics/analytics.duckdb
  Таблицы: account_insights, post_insights, posts
  (с доп. колонкой participant)
"""

import os
import logging
import time
from zoneinfo import ZoneInfo

import duckdb
import schedule

ANALYTICS_DB = "/app/data/analytics/analytics.duckdb"
MERGE_AT     = "07:45"
TIMEZONE     = ZoneInfo("Europe/Belgrade")

SOURCES = {
    "budimir": "/app/data/budimir/data.duckdb",
    "slava":   "/app/data/slava/data.duckdb",
    "tanya":   "/app/data/tanya/data.duckdb",
    "chiara":  "/app/data/chiara/data.duckdb",
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [merger] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("merger")


def merge():
    os.makedirs(os.path.dirname(ANALYTICS_DB), exist_ok=True)

    available = {
        name: path
        for name, path in SOURCES.items()
        if os.path.exists(path)
    }

    if not available:
        log.warning("Нет доступных источников — пропускаю")
        return

    log.info(f"Начинаю слияние: {list(available)}")

    with duckdb.connect(ANALYTICS_DB) as dest:
        for name, path in available.items():
            dest.execute(f"ATTACH '{path}' AS {name} (READ_ONLY)")

        # ── account_insights ──────────────────────────────────────────────
        union = " UNION ALL ".join(
            f"SELECT '{name}' AS participant, * FROM {name}.account_insights"
            for name in available
        )
        dest.execute(f"CREATE OR REPLACE TABLE account_insights AS {union}")

        # ── posts ─────────────────────────────────────────────────────────
        union = " UNION ALL ".join(
            f"SELECT '{name}' AS participant, * FROM {name}.posts"
            for name in available
        )
        dest.execute(f"CREATE OR REPLACE TABLE posts AS {union}")

        # ── post_insights (через posts чтобы получить participant) ────────
        union = " UNION ALL ".join(
            f"""
            SELECT '{name}' AS participant, pi.*
            FROM {name}.post_insights pi
            """
            for name in available
        )
        dest.execute(f"CREATE OR REPLACE TABLE post_insights AS {union}")

        for name in available:
            dest.execute(f"DETACH {name}")

    counts = {}
    with duckdb.connect(ANALYTICS_DB, read_only=True) as dest:
        for t in ("account_insights", "posts", "post_insights"):
            counts[t] = dest.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]

    log.info(
        f"Слияние завершено — "
        f"account_insights: {counts['account_insights']}, "
        f"posts: {counts['posts']}, "
        f"post_insights: {counts['post_insights']}"
    )


def main():
    log.info(f"Merger запущен. Слияние каждый день в {MERGE_AT} по Белграду")
    log.info(f"Источники: {list(SOURCES)}")

    # Запустить сразу при старте
    merge()

    schedule.every().day.at(MERGE_AT).do(merge)

    while True:
        schedule.run_pending()
        time.sleep(30)


if __name__ == "__main__":
    main()
