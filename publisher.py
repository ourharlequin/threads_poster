import pandas as pd
import requests
import time
import schedule
from dotenv import load_dotenv
import os

load_dotenv()

ACCESS_TOKEN    = os.getenv("THREADS_ACCESS_TOKEN")
THREADS_USER_ID = os.getenv("THREADS_USER_ID")
CSV_FILE        = "posts.csv"

def publish_text_thread():
    # ── Проверка конфига ──────────────────────────────────────────────────────
    if not ACCESS_TOKEN or not THREADS_USER_ID:
        print("❌ Нет ACCESS_TOKEN или THREADS_USER_ID в .env")
        return

    df = pd.read_csv(CSV_FILE)
    pending_posts = df[df['status'] == 'pending']

    if pending_posts.empty:
        print("✅ Все посты опубликованы!")
        return

    index        = pending_posts.index[0]
    text_content = pending_posts.loc[index, 'content']

    # ── Шаг 1: создать контейнер ─────────────────────────────────────────────
    url    = f"https://graph.threads.net/v1.0/{THREADS_USER_ID}/threads"
    params = {
        'media_type':   'TEXT',
        'text':         text_content,
        'access_token': ACCESS_TOKEN,
    }

    try:
        response = requests.post(url, data=params)
        print(f"[Контейнер] {response.status_code}: {response.text}")  # ← ключевой лог

        data         = response.json()
        container_id = data.get('id')

        if not container_id:
            print(f"❌ Не получен container_id. Ответ: {data}")
            # Пометить пост как failed, чтобы не пытаться снова
            df.at[index, 'status'] = 'failed'
            df.to_csv(CSV_FILE, index=False)
            return

        # ── Шаг 2: подождать перед публикацией (требование Threads API) ───────
        time.sleep(5)

        # ── Шаг 3: опубликовать ───────────────────────────────────────────────
        publish_url = f"https://graph.threads.net/v1.0/{THREADS_USER_ID}/threads_publish"
        publish_res = requests.post(publish_url, data={
            'creation_id':  container_id,
            'access_token': ACCESS_TOKEN,
        })
        print(f"[Публикация] {publish_res.status_code}: {publish_res.text}")  # ← ключевой лог

        if publish_res.status_code == 200:
            df.at[index, 'status'] = 'posted'
            df.to_csv(CSV_FILE, index=False)
            print(f"✅ Опубликовано: {text_content[:50]}...")
        else:
            print(f"❌ Ошибка публикации: {publish_res.text}")
            df.at[index, 'status'] = 'failed'
            df.to_csv(CSV_FILE, index=False)

    except Exception as e:
        print(f"❌ Исключение: {e}")


schedule.every(29).minutes.do(publish_text_thread)

print("Автопостинг запущен...")
while True:
    schedule.run_pending()
    time.sleep(1)