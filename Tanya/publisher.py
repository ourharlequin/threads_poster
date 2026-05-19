"""
Publisher для Threads — постинг в 6 аккаунтов.

Логика:
- 6 потоков, по одному на аккаунт (независимое расписание)
- Окно постинга: 9:00–21:00 по Белграду
- Интервал между постами: 10–40 минут (рандом)
- Имитация набора текста: 1–5 секунд перед публикацией
- 5% шанс пропустить публикацию
- Источник постов: DuckDB (status='pending')
- После публикации: status='posted' + threads_post_id
"""

import os
import time
import random
import logging
import threading
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import requests
import duckdb
from dotenv import load_dotenv

# ── Настройки ────────────────────────────────────────────────────────────────
load_dotenv()

DB_PATH = os.getenv("DB_PATH", "data/data.duckdb")
DB_LOCK = threading.Lock()

TIMEZONE = ZoneInfo("Europe/Belgrade")
START_HOUR = 9
END_HOUR = 21

MIN_INTERVAL_MIN = 10
MAX_INTERVAL_MIN = 40

TYPING_DELAY_MIN_SEC = 1
TYPING_DELAY_MAX_SEC = 5

SKIP_PROBABILITY = 0.05

THREADS_API_BASE = "https://graph.threads.net/v1.0"
PUBLISH_DELAY_SEC = 30  # Meta recommends 30s after container creation before publishing

# ── Логирование ──────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(threadName)s] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("publisher")


# ── Инициализация БД ─────────────────────────────────────────────────────────
def init_db():
    """Создаёт таблицу posts и sequence если их нет."""
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
    log.info(f"DB инициализирована: {DB_PATH}")


# ── Загрузка аккаунтов из .env ───────────────────────────────────────────────
def load_accounts() -> list[dict]:
    """
    Парсит .env вида:
      ACCOUNT_1_ID=karuseli_main
      ACCOUNT_1_USER_ID=12345
      ACCOUNT_1_THREADS_TOKEN=xxx
    Возвращает список словарей с данными по аккаунтам.
    """
    accounts = []
    for i in range(1, 100):
        acc_id = os.getenv(f"ACCOUNT_{i}_ID")
        if not acc_id:
            break

        user_id = os.getenv(f"ACCOUNT_{i}_USER_ID")
        threads_token = (
            os.getenv(f"ACCOUNT_{i}_THREADS_TOKEN")
            or os.getenv("THREADS_TOKEN")
        )

        if not user_id or not threads_token:
            log.warning(f"Account {acc_id}: пропущен USER_ID или THREADS_TOKEN — skip")
            continue

        daily_limit_str = os.getenv(f"ACCOUNT_{i}_DAILY_LIMIT")
        daily_limit = int(daily_limit_str) if daily_limit_str else None

        accounts.append({
            "account_id": acc_id,
            "threads_user_id": user_id,
            "threads_token": threads_token,
            "daily_limit": daily_limit,
        })

    return accounts


# ── DuckDB операции (короткие соединения) ────────────────────────────────────
def get_next_pending_post(account_id: str) -> dict | None:
    """Берёт самый старый pending пост для аккаунта."""
    with DB_LOCK, duckdb.connect(DB_PATH) as conn:
        row = conn.execute(
            """
            SELECT id, content
            FROM posts
            WHERE account_id = ? AND status = 'pending'
            ORDER BY created_at ASC
            LIMIT 1
            """,
            [account_id],
        ).fetchone()

    if not row:
        return None
    return {"id": row[0], "content": row[1]}


def count_posted_today(account_id: str) -> int:
    """Считает посты со статусом 'posted' за сегодня по Belgrade-времени."""
    today_start = datetime.now(TIMEZONE).replace(hour=0, minute=0, second=0, microsecond=0)
    with DB_LOCK, duckdb.connect(DB_PATH) as conn:
        row = conn.execute(
            "SELECT COUNT(*) FROM posts WHERE account_id = ? AND status = 'posted' AND posted_at >= ?",
            [account_id, today_start],
        ).fetchone()
    return row[0] if row else 0


def update_post_status(post_id: int, status: str, threads_post_id: str | None = None):
    """Обновляет статус поста после публикации."""
    with DB_LOCK, duckdb.connect(DB_PATH) as conn:
        if status == "posted":
            conn.execute(
                """
                UPDATE posts
                SET status = ?, posted_at = ?, threads_post_id = ?
                WHERE id = ?
                """,
                [status, datetime.now(TIMEZONE), threads_post_id, post_id],
            )
        else:
            conn.execute(
                "UPDATE posts SET status = ? WHERE id = ?",
                [status, post_id],
            )


# ── Threads API ──────────────────────────────────────────────────────────────
def publish_to_threads(user_id: str, token: str, text: str) -> str | None:
    """
    Двухшаговая публикация:
    1. Создать контейнер
    2. Опубликовать его
    Возвращает threads_post_id или None при ошибке.
    """
    # Шаг 1 — контейнер
    create_url = f"{THREADS_API_BASE}/{user_id}/threads"
    create_resp = requests.post(
        create_url,
        data={"media_type": "TEXT", "text": text, "access_token": token},
        timeout=30,
    )

    if create_resp.status_code != 200:
        log.error(f"Контейнер не создан: {create_resp.status_code} {create_resp.text}")
        return None

    container_id = create_resp.json().get("id")
    if not container_id:
        log.error(f"Нет container_id в ответе: {create_resp.json()}")
        return None

    # Threads требует паузу перед публикацией
    time.sleep(PUBLISH_DELAY_SEC)

    # Шаг 2 — публикация
    publish_url = f"{THREADS_API_BASE}/{user_id}/threads_publish"
    pub_resp = requests.post(
        publish_url,
        data={"creation_id": container_id, "access_token": token},
        timeout=30,
    )

    if pub_resp.status_code != 200:
        log.error(f"Публикация не удалась: {pub_resp.status_code} {pub_resp.text}")
        return None

    threads_post_id = pub_resp.json().get("id")
    return threads_post_id


# ── Утилиты времени ──────────────────────────────────────────────────────────
def now_belgrade() -> datetime:
    return datetime.now(TIMEZONE)


def is_within_posting_window(now: datetime) -> bool:
    return START_HOUR <= now.hour < END_HOUR


def seconds_until_window_opens(now: datetime) -> float:
    """Сколько секунд до ближайшего START_HOUR."""
    target = now.replace(hour=START_HOUR, minute=0, second=0, microsecond=0)
    if now >= target:
        target += timedelta(days=1)
    return (target - now).total_seconds()


# ── Основной цикл для одного аккаунта ────────────────────────────────────────
def publisher_loop(account: dict):
    """Бесконечный цикл публикации для одного аккаунта."""
    acc_id = account["account_id"]
    user_id = account["threads_user_id"]
    token = account["threads_token"]
    daily_limit = account.get("daily_limit")

    log.info(f"[{acc_id}] Стартую publisher loop"
             + (f" (лимит {daily_limit}/день)" if daily_limit else ""))

    while True:
        try:
            # 1. Проверка окна постинга
            now = now_belgrade()
            if not is_within_posting_window(now):
                wait_sec = seconds_until_window_opens(now)
                wake_at = now + timedelta(seconds=wait_sec)
                log.info(f"[{acc_id}] Вне окна. Сплю до {wake_at:%H:%M}")
                time.sleep(wait_sec)
                continue

            # 2. Проверка дневного лимита
            if daily_limit is not None:
                posted_today = count_posted_today(acc_id)
                if posted_today >= daily_limit:
                    wait_sec = seconds_until_window_opens(now)
                    log.info(f"[{acc_id}] Дневной лимит достигнут ({posted_today}/{daily_limit}). Сплю до завтра.")
                    time.sleep(wait_sec)
                    continue

            # 3. Random skip
            if random.random() < SKIP_PROBABILITY:
                log.info(f"[{acc_id}] Random skip — пропускаю публикацию")
            else:
                # 4. Берём пост
                post = get_next_pending_post(acc_id)
                if not post:
                    log.info(f"[{acc_id}] Нет pending постов. Жду 10 мин.")
                    time.sleep(600)
                    continue

                # 4. Имитация набора
                typing_delay = random.uniform(TYPING_DELAY_MIN_SEC, TYPING_DELAY_MAX_SEC)
                time.sleep(typing_delay)

                # 5. Публикация
                threads_post_id = publish_to_threads(user_id, token, post["content"])

                if threads_post_id:
                    update_post_status(post["id"], "posted", threads_post_id)
                    log.info(
                        f"[{acc_id}] ✅ Опубликовано (id={post['id']}, "
                        f"threads_id={threads_post_id}): {post['content'][:50]}..."
                    )
                else:
                    update_post_status(post["id"], "failed")
                    log.error(f"[{acc_id}] ❌ Публикация не удалась (id={post['id']})")

            # 6. Случайный интервал до следующей попытки
            interval_min = random.uniform(MIN_INTERVAL_MIN, MAX_INTERVAL_MIN)
            log.info(f"[{acc_id}] Сплю {interval_min:.1f} мин до следующего поста")
            time.sleep(interval_min * 60)

        except Exception as e:
            log.exception(f"[{acc_id}] Ошибка в цикле: {e}")
            time.sleep(60)


# ── main ─────────────────────────────────────────────────────────────────────
def main():
    init_db()
    accounts = load_accounts()
    if not accounts:
        log.error("Не загружено ни одного аккаунта. Проверь .env")
        return

    log.info(f"Загружено {len(accounts)} аккаунтов: "
             f"{', '.join(a['account_id'] for a in accounts)}")

    threads = []
    for acc in accounts:
        t = threading.Thread(
            target=publisher_loop,
            args=(acc,),
            name=f"pub-{acc['account_id']}",
            daemon=True,
        )
        t.start()
        threads.append(t)
        # Небольшой стартовый сдвиг между потоками — чтобы не били API одновременно
        time.sleep(2)

    # Главный поток просто живёт пока живут дочерние
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        log.info("Получен сигнал остановки. Выхожу.")


if __name__ == "__main__":
    main()
