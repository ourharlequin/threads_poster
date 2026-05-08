"""
Обновляет Threads-токены в .env на новые (каждый токен живёт 60 дней).
Запускать раз в месяц:
  docker-compose --profile tools run --rm threads_refresher
"""

import os
import re
import sys
import logging
import requests
from dotenv import load_dotenv

load_dotenv()

ENV_FILE = os.path.join(os.path.dirname(__file__), ".env")
REFRESH_URL = "https://graph.threads.net/refresh_access_token"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
)
log = logging.getLogger("refresher")


def refresh_token(token: str) -> str | None:
    """Обменивает токен на новый через Threads API."""
    try:
        resp = requests.get(
            REFRESH_URL,
            params={"grant_type": "th_refresh_token", "access_token": token},
            timeout=15,
        )
        if resp.status_code == 200:
            return resp.json().get("access_token")
        log.error(f"Ошибка обновления: {resp.status_code} {resp.text}")
        return None
    except Exception as e:
        log.error(f"Исключение при обновлении токена: {e}")
        return None


def update_env_file(replacements: dict[str, str]):
    """Заменяет значения переменных в .env файле."""
    with open(ENV_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    for var_name, new_value in replacements.items():
        content = re.sub(
            rf"^({re.escape(var_name)}=).*$",
            rf"\g<1>{new_value}",
            content,
            flags=re.MULTILINE,
        )

    with open(ENV_FILE, "w", encoding="utf-8") as f:
        f.write(content)


def main():
    # Собираем все токены: глобальный + по аккаунтам
    tokens_to_refresh: dict[str, str] = {}

    global_token = os.getenv("THREADS_TOKEN")
    if global_token:
        tokens_to_refresh["THREADS_TOKEN"] = global_token

    for i in range(1, 100):
        acc_id = os.getenv(f"ACCOUNT_{i}_ID")
        if not acc_id:
            break
        token = os.getenv(f"ACCOUNT_{i}_THREADS_TOKEN")
        if token:
            tokens_to_refresh[f"ACCOUNT_{i}_THREADS_TOKEN"] = token

    if not tokens_to_refresh:
        log.error("Нет токенов для обновления. Проверь .env")
        sys.exit(1)

    log.info(f"Найдено токенов: {len(tokens_to_refresh)} → {list(tokens_to_refresh.keys())}")

    replacements = {}
    for var_name, old_token in tokens_to_refresh.items():
        log.info(f"Обновляю {var_name}...")
        new_token = refresh_token(old_token)
        if new_token:
            replacements[var_name] = new_token
            log.info(f"✅ {var_name} обновлён")
        else:
            log.error(f"❌ {var_name} — не удалось обновить, оставляю старый")

    if replacements:
        update_env_file(replacements)
        log.info(f"Записано в .env: {len(replacements)} токен(ов)")
    else:
        log.error("Ни один токен не обновлён")
        sys.exit(1)


if __name__ == "__main__":
    main()
