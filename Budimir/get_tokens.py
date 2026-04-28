"""
Получает USER_ID и long-lived THREADS_TOKEN для одного аккаунта.

Запуск:
  python get_tokens.py

Требования в .env:
  META_APP_ID=...
  META_APP_SECRET=...

В Meta App Console (Threads API → Настройки → URL обратного вызова) должен быть:
  https://localhost/callback

Процесс:
  1. Скрипт откроет браузер со ссылкой авторизации
  2. Войди в нужный аккаунт Threads и подтверди доступ
  3. Браузер перейдёт на https://localhost/callback?code=... (покажет ошибку — это нормально)
  4. Скопируй полный URL из адресной строки и вставь сюда
  5. Скрипт выдаст готовые строки для .env
"""

import os
import sys
import webbrowser
import urllib.parse

import requests
from dotenv import load_dotenv

load_dotenv()

APP_ID = os.getenv("META_APP_ID")
APP_SECRET = os.getenv("META_APP_SECRET")
REDIRECT_URI = "https://localhost/callback"
SCOPES = "threads_basic,threads_content_publish"

AUTH_URL = "https://threads.net/oauth/authorize"
TOKEN_URL = "https://graph.threads.net/oauth/access_token"
LONGTERM_URL = "https://graph.threads.net/access_token"
ME_URL = "https://graph.threads.net/me"


def check_env():
    missing = []
    if not APP_ID:
        missing.append("META_APP_ID")
    if not APP_SECRET:
        missing.append("META_APP_SECRET")
    if missing:
        print("❌ Добавь в .env:")
        for k in missing:
            print(f"   {k}=...")
        sys.exit(1)


def build_auth_url() -> str:
    params = {
        "client_id": APP_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPES,
        "response_type": "code",
    }
    return AUTH_URL + "?" + urllib.parse.urlencode(params)


def extract_code(raw_url: str) -> str | None:
    """Извлекает code из URL, вставленного пользователем."""
    raw_url = raw_url.strip()
    try:
        parsed = urllib.parse.urlparse(raw_url)
        params = dict(urllib.parse.parse_qsl(parsed.query))
        if "error" in params:
            print(f"❌ Ошибка авторизации: {params.get('error_description', params['error'])}")
            return None
        code = params.get("code")
        if not code:
            print("❌ В URL нет параметра code. Убедись что скопировал полный URL.")
            return None
        return code
    except Exception as e:
        print(f"❌ Не удалось разобрать URL: {e}")
        return None


def exchange_code(code: str) -> str | None:
    """Обменивает code на short-lived token."""
    resp = requests.post(TOKEN_URL, data={
        "client_id": APP_ID,
        "client_secret": APP_SECRET,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI,
        "code": code,
    }, timeout=15)
    if resp.status_code != 200:
        print(f"❌ Ошибка получения токена: {resp.status_code} {resp.text}")
        return None
    return resp.json().get("access_token")


def get_long_lived_token(short_token: str) -> str | None:
    """Обменивает short-lived на long-lived токен (60 дней)."""
    resp = requests.get(LONGTERM_URL, params={
        "grant_type": "th_exchange_token",
        "client_secret": APP_SECRET,
        "access_token": short_token,
    }, timeout=15)
    if resp.status_code != 200:
        print(f"❌ Ошибка получения long-lived токена: {resp.status_code} {resp.text}")
        return None
    return resp.json().get("access_token")


def get_user_info(token: str) -> dict | None:
    """Получает id и username пользователя."""
    resp = requests.get(ME_URL, params={
        "fields": "id,username",
        "access_token": token,
    }, timeout=15)
    if resp.status_code != 200:
        print(f"❌ Ошибка получения user info: {resp.status_code} {resp.text}")
        return None
    return resp.json()


def main():
    check_env()

    auth_url = build_auth_url()

    print("\n=== Threads Token Helper ===\n")
    print("📋 Шаги:")
    print("   1. Войди в браузере в нужный аккаунт Threads")
    print("   2. Открой ссылку ниже и подтверди доступ")
    print("   3. Браузер перейдёт на https://localhost/callback — покажет ошибку (это нормально)")
    print("   4. Скопируй полный URL из адресной строки и вставь сюда\n")
    print(f"🔗 Ссылка:\n   {auth_url}\n")

    webbrowser.open(auth_url)

    raw_url = input("📋 Вставь полный URL из адресной строки: ").strip()
    if not raw_url:
        print("❌ URL не введён.")
        sys.exit(1)

    code = extract_code(raw_url)
    if not code:
        sys.exit(1)

    print("\n🔄 Обмениваю code на токен...")
    short_token = exchange_code(code)
    if not short_token:
        sys.exit(1)

    print("🔄 Получаю long-lived токен...")
    long_token = get_long_lived_token(short_token)
    if not long_token:
        sys.exit(1)

    print("🔄 Получаю USER_ID...")
    user_info = get_user_info(long_token)
    if not user_info:
        sys.exit(1)

    user_id = user_info["id"]
    username = user_info.get("username", "?")

    print(f"\n✅ Готово! Аккаунт: @{username}\n")
    print("─── Добавь в .env ───────────────────────────────────")
    print(f"ACCOUNT_N_ID={username}")
    print(f"ACCOUNT_N_USER_ID={user_id}")
    print(f"ACCOUNT_N_THREADS_TOKEN={long_token}")
    print("─────────────────────────────────────────────────────")
    print("(замени N на нужный номер аккаунта)\n")


if __name__ == "__main__":
    main()
