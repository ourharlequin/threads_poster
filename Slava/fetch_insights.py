"""
fetch_insights.py — собирает метрики из Threads Insights API.
Запускать раз в день в 05:00 по Белграду (через scheduler.py).

Что собирает:
- Post-level:    views, likes, replies, reposts, quotes
                 для постов опубликованных за последние 7 дней
- Account-level: views, likes, replies, reposts, quotes, followers_count
                 за вчерашний день по Белграду
"""

import os
import time
import logging
from datetime import datetime, timedelta, date
from zoneinfo import ZoneInfo

import requests
import duckdb
from dotenv import load_dotenv

load_dotenv()

DB_PATH          = os.getenv("DB_PATH", "data/data.duckdb")
TIMEZONE         = ZoneInfo("Europe/Belgrade")
THREADS_API_BASE = "https://graph.threads.net/v1.0"
POST_LOOKBACK_DAYS = 7
API_CALL_DELAY   = 0.5  # секунд между запросами

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [insights] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("insights")


# ── DB ────────────────────────────────────────────────────────────────────────

def init_db():
    os.makedirs(os.path.dirname(DB_PATH) or ".", exist_ok=True)
    with duckdb.connect(DB_PATH) as conn:
        conn.execute("CREATE SEQUENCE IF NOT EXISTS post_insights_id_seq START 1")
        conn.execute("CREATE SEQUENCE IF NOT EXISTS account_insights_id_seq START 1")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS post_insights (
                id         INTEGER PRIMARY KEY DEFAULT nextval('post_insights_id_seq'),
                post_id    INTEGER NOT NULL,
                fetched_at TIMESTAMPTZ DEFAULT now(),
                views      INTEGER DEFAULT 0,
                likes      INTEGER DEFAULT 0,
                replies    INTEGER DEFAULT 0,
                reposts    INTEGER DEFAULT 0,
                quotes     INTEGER DEFAULT 0
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS account_insights (
                id              INTEGER PRIMARY KEY DEFAULT nextval('account_insights_id_seq'),
                account_id      VARCHAR NOT NULL,
                date            DATE NOT NULL,
                fetched_at      TIMESTAMPTZ DEFAULT now(),
                views           INTEGER DEFAULT 0,
                likes           INTEGER DEFAULT 0,
                replies         INTEGER DEFAULT 0,
                reposts         INTEGER DEFAULT 0,
                quotes          INTEGER DEFAULT 0,
                followers_count INTEGER,
                UNIQUE (account_id, date)
            )
        """)
    log.info("Insights-таблицы инициализированы")


# ── Аккаунты ─────────────────────────────────────────────────────────────────

def load_accounts() -> list[dict]:
    accounts = []
    for i in range(1, 100):
        acc_id = os.getenv(f"ACCOUNT_{i}_ID")
        if not acc_id:
            break
        user_id = os.getenv(f"ACCOUNT_{i}_USER_ID")
        token   = os.getenv(f"ACCOUNT_{i}_THREADS_TOKEN") or os.getenv("THREADS_TOKEN")
        if user_id and token:
            accounts.append({"account_id": acc_id, "user_id": user_id, "token": token})
    return accounts


# ── Post-level insights ───────────────────────────────────────────────────────

def get_recent_posts() -> list[dict]:
    cutoff = datetime.now(TIMEZONE) - timedelta(days=POST_LOOKBACK_DAYS)
    with duckdb.connect(DB_PATH, read_only=True) as conn:
        rows = conn.execute(
            """
            SELECT id, account_id, threads_post_id
            FROM posts
            WHERE status = 'posted'
              AND posted_at >= ?
              AND threads_post_id IS NOT NULL
            ORDER BY posted_at DESC
            """,
            [cutoff],
        ).fetchall()
    return [{"id": r[0], "account_id": r[1], "threads_post_id": r[2]} for r in rows]


def fetch_post_metrics(media_id: str, token: str) -> dict | None:
    resp = requests.get(
        f"{THREADS_API_BASE}/{media_id}/insights",
        params={
            "metric": "views,likes,replies,reposts,quotes",
            "access_token": token,
        },
        timeout=30,
    )
    if resp.status_code != 200:
        log.error(f"  Post {media_id}: {resp.status_code} {resp.text[:120]}")
        return None

    metrics = {}
    for item in resp.json().get("data", []):
        values = item.get("values", [])
        metrics[item["name"]] = values[0]["value"] if values else 0
    return metrics


def save_post_insights(post_id: int, metrics: dict):
    with duckdb.connect(DB_PATH) as conn:
        conn.execute(
            """
            INSERT INTO post_insights (post_id, views, likes, replies, reposts, quotes)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            [
                post_id,
                metrics.get("views",   0),
                metrics.get("likes",   0),
                metrics.get("replies", 0),
                metrics.get("reposts", 0),
                metrics.get("quotes",  0),
            ],
        )


def collect_post_insights(accounts: list[dict]):
    token_map = {a["account_id"]: a["token"] for a in accounts}
    posts = get_recent_posts()
    log.info(f"Post insights: {len(posts)} постов за последние {POST_LOOKBACK_DAYS} дней")

    ok = fail = 0
    for post in posts:
        token = token_map.get(post["account_id"])
        if not token:
            continue
        metrics = fetch_post_metrics(post["threads_post_id"], token)
        if metrics:
            save_post_insights(post["id"], metrics)
            ok += 1
        else:
            fail += 1
        time.sleep(API_CALL_DELAY)

    log.info(f"Post insights: ✅ {ok}  ❌ {fail}")


# ── Account-level insights ────────────────────────────────────────────────────

def yesterday_range_unix() -> tuple[int, int]:
    """Unix timestamps начала и конца вчерашнего дня по Белграду."""
    today     = datetime.now(TIMEZONE).replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday = today - timedelta(days=1)
    return int(yesterday.timestamp()), int(today.timestamp())


def fetch_account_metrics(user_id: str, token: str, since: int, until: int) -> dict | None:
    # Запрос 1: дневные метрики за вчера
    resp = requests.get(
        f"{THREADS_API_BASE}/{user_id}/threads_insights",
        params={
            "metric": "views,likes,replies,reposts,quotes",
            "period": "day",
            "since":  since,
            "until":  until,
            "access_token": token,
        },
        timeout=30,
    )
    if resp.status_code != 200:
        log.error(f"  Account {user_id}: {resp.status_code} {resp.text[:120]}")
        return None

    metrics = {}
    for item in resp.json().get("data", []):
        values = item.get("values", [])
        metrics[item["name"]] = values[-1]["value"] if values else 0

    # Запрос 2: текущий followers_count (только lifetime)
    time.sleep(API_CALL_DELAY)
    resp2 = requests.get(
        f"{THREADS_API_BASE}/{user_id}/threads_insights",
        params={
            "metric": "followers_count",
            "period": "lifetime",
            "access_token": token,
        },
        timeout=30,
    )
    if resp2.status_code == 200:
        for item in resp2.json().get("data", []):
            values = item.get("values", [])
            metrics["followers_count"] = values[-1]["value"] if values else None
    else:
        log.warning(f"  followers_count {user_id}: {resp2.status_code} {resp2.text[:80]}")
        metrics["followers_count"] = None

    return metrics


def save_account_insights(account_id: str, target_date: date, metrics: dict):
    with duckdb.connect(DB_PATH) as conn:
        existing = conn.execute(
            "SELECT id FROM account_insights WHERE account_id = ? AND date = ?",
            [account_id, target_date],
        ).fetchone()

        if existing:
            conn.execute(
                """
                UPDATE account_insights
                SET fetched_at = now(),
                    views = ?, likes = ?, replies = ?,
                    reposts = ?, quotes = ?, followers_count = ?
                WHERE account_id = ? AND date = ?
                """,
                [
                    metrics.get("views",           0),
                    metrics.get("likes",           0),
                    metrics.get("replies",         0),
                    metrics.get("reposts",         0),
                    metrics.get("quotes",          0),
                    metrics.get("followers_count"),
                    account_id, target_date,
                ],
            )
        else:
            conn.execute(
                """
                INSERT INTO account_insights
                    (account_id, date, views, likes, replies, reposts, quotes, followers_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    account_id, target_date,
                    metrics.get("views",           0),
                    metrics.get("likes",           0),
                    metrics.get("replies",         0),
                    metrics.get("reposts",         0),
                    metrics.get("quotes",          0),
                    metrics.get("followers_count"),
                ],
            )


def collect_account_insights(accounts: list[dict]):
    since, until = yesterday_range_unix()
    target_date  = (datetime.now(TIMEZONE) - timedelta(days=1)).date()
    log.info(f"Account insights за {target_date} ({len(accounts)} аккаунтов)")

    ok = fail = 0
    for acc in accounts:
        metrics = fetch_account_metrics(acc["user_id"], acc["token"], since, until)
        if metrics:
            save_account_insights(acc["account_id"], target_date, metrics)
            log.info(
                f"  [{acc['account_id']}] "
                f"views={metrics.get('views', 0)}  "
                f"likes={metrics.get('likes', 0)}  "
                f"followers={metrics.get('followers_count', '?')}"
            )
            ok += 1
        else:
            fail += 1
        time.sleep(API_CALL_DELAY)

    log.info(f"Account insights: ✅ {ok}  ❌ {fail}")


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    init_db()
    accounts = load_accounts()
    if not accounts:
        log.error("Не загружено ни одного аккаунта. Проверь .env")
        return

    log.info(f"Загружено {len(accounts)} аккаунтов: {[a['account_id'] for a in accounts]}")
    collect_post_insights(accounts)
    collect_account_insights(accounts)
    log.info("Сбор метрик завершён")


if __name__ == "__main__":
    main()
