"""
Планировщик для автоматизации четырёх задач:
- Сбор метрик:        каждый день в 05:00 по Белграду
- Генерация постов:   каждый день в 08:00 по Белграду (последовательно по аккаунтам)
- Обновление токенов: каждые 58 дней в 08:00 по Белграду
- Ответы на реплаи:   5 раз в день (09:00, 12:00, 15:00, 18:00, 21:00)
"""

import os
import logging
import subprocess
import sys
import time
from datetime import date

import requests
import schedule
from dotenv import load_dotenv

load_dotenv()

INSIGHTS_AT = "05:00"
RUN_AT = "08:00"
REFRESH_EVERY_DAYS = 58
REPLY_HOURS = ["09:00", "12:00", "15:00", "18:00", "21:00"]
THREADS_API_BASE = os.getenv("THREADS_API_BASE", "http://host.docker.internal:7843")
POSTS_PER_ACCOUNT = int(os.getenv("SCHEDULER_POSTS_COUNT", "30"))
STATE_FILE = os.path.join(os.path.dirname(__file__), "data", "scheduler_state.txt")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [scheduler] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("scheduler")


def get_last_run_date() -> date | None:
    try:
        with open(STATE_FILE) as f:
            return date.fromisoformat(f.read().strip())
    except Exception:
        return None


def save_last_run_date():
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        f.write(date.today().isoformat())


def load_account_ids() -> list[str]:
    ids = []
    for i in range(1, 100):
        acc_id = os.getenv(f"ACCOUNT_{i}_ID")
        if not acc_id:
            break
        ids.append(acc_id)
    return ids


def generate_all():
    accounts = load_account_ids()
    if not accounts:
        log.error("Нет аккаунтов в .env — генерация отменена")
        return

    log.info(f"Начинаю генерацию для {len(accounts)} аккаунтов: {accounts}")

    for acc_id in accounts:
        log.info(f"→ Генерирую посты для {acc_id}...")
        result = subprocess.run(
            [sys.executable, "generate_posts.py", "--account", acc_id, "--count", str(POSTS_PER_ACCOUNT)],
            capture_output=False,
        )
        if result.returncode != 0:
            log.error(f"  ❌ Ошибка генерации для {acc_id} (код {result.returncode})")
        else:
            log.info(f"  ✅ {acc_id} — готово")

    save_last_run_date()
    log.info("Генерация завершена для всех аккаунтов")


def fetch_insights():
    log.info("Собираю метрики из Threads Insights API...")
    result = subprocess.run(
        [sys.executable, "fetch_insights.py"],
        capture_output=False,
    )
    if result.returncode != 0:
        log.error(f"❌ Ошибка сбора метрик (код {result.returncode})")
    else:
        log.info("✅ Метрики собраны")


def reply_all():
    accounts = load_account_ids()
    if not accounts:
        return
    log.info(f"Reply worker: обрабатываю {len(accounts)} аккаунтов")
    for acc_id in accounts:
        try:
            r = requests.get(f"{THREADS_API_BASE}/replies/fetch/{acc_id}", timeout=120)
            data = r.json().get("data", {})
            log.info(f"  {acc_id}: {data.get('new_comments', 0)} новых комментариев")
        except Exception as e:
            log.error(f"  {acc_id}: ошибка fetch_replies: {e}")
            continue
        try:
            r = requests.post(f"{THREADS_API_BASE}/replies/auto-reply/{acc_id}", timeout=300)
            data = r.json().get("data", {})
            log.info(f"  {acc_id}: ответили на {data.get('replied', 0)} комментариев")
        except Exception as e:
            log.error(f"  {acc_id}: ошибка auto_reply: {e}")


def refresh_tokens():
    log.info("Обновляю Threads-токены...")
    result = subprocess.run(
        [sys.executable, "refresh_tokens.py"],
        capture_output=False,
    )
    if result.returncode != 0:
        log.error(f"❌ Ошибка обновления токенов (код {result.returncode})")
    else:
        log.info("✅ Токены обновлены")


def main():
    accounts = load_account_ids()
    log.info(f"Планировщик запущен. Аккаунты: {accounts}")
    log.info(f"Сбор метрик    — каждый день в {INSIGHTS_AT} по Белграду")
    log.info(f"Генерация      — каждый день в {RUN_AT} по Белграду")
    log.info(f"Обновление токенов — каждые {REFRESH_EVERY_DAYS} дней")
    log.info(f"Ответы на реплаи   — {', '.join(REPLY_HOURS)} по Белграду")

    # Если сегодня генерация ещё не запускалась — запустить сразу
    if get_last_run_date() != date.today():
        log.info("Пропущенный запуск обнаружен — запускаю генерацию сейчас")
        generate_all()

    schedule.every().day.at(INSIGHTS_AT).do(fetch_insights)
    schedule.every().day.at(RUN_AT).do(generate_all)
    schedule.every(REFRESH_EVERY_DAYS).days.at(RUN_AT).do(refresh_tokens)
    for t in REPLY_HOURS:
        schedule.every().day.at(t).do(reply_all)

    while True:
        schedule.run_pending()
        time.sleep(30)


if __name__ == "__main__":
    main()
