import csv
import time
import random
import requests
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# ── Настройки ────────────────────────────────────────────────────────────────
GROQ_API_KEY  = os.getenv("GROQ_API_KEY")
MODEL         = "llama-3.3-70b-versatile"
CSV_FILE      = "posts.csv"
ARCHIVE_FILE  = "archive.csv"
POSTS_PER_RUN = 50
MAX_LENGTH    = 500

FIELDNAMES = ["content", "format", "status", "created_at"]

if not GROQ_API_KEY:
    print("Ошибка: GROQ_API_KEY не найден в .env файле!")
    exit(1)

# ── Форматы постов ────────────────────────────────────────────────────────────
FORMATS = [
    {
        "name": "fact",
        "count": 15,
        "prompt": (
            "Write a Threads post about AI automation as a 'fact of the day'. "
            "Structure: one surprising stat or research finding → what it means in practice → takeaway. "
            "3-4 sentences. Conversational tone, no headers, no hashtags, no emoji. "
            "Keep it strictly under 450 characters. "
            "Return only the post text."
        )
    },
    {
        "name": "case",
        "count": 13,
        "prompt": (
            "Write a Threads post as a 'before/after automation mini-case'. "
            "Pick a specific job or task. Show: what used to take hours → what now takes minutes → which tool made it happen. "
            "3-4 sentences. Use concrete time figures. Conversational tone, no headers, no hashtags, no emoji. "
            "Keep it strictly under 450 characters. "
            "Return only the post text."
        )
    },
    {
        "name": "tip",
        "count": 10,
        "prompt": (
            "Write a Threads post with a practical AI tool or automation tip. "
            "Name a specific tool + why it matters + how to get started. "
            "3-4 sentences. Conversational tone, no headers, no hashtags, no emoji. "
            "Keep it strictly under 450 characters. "
            "Return only the post text."
        )
    },
    {
        "name": "myth",
        "count": 7,
        "prompt": (
            "Write a Threads post busting a common myth about AI automation. "
            "Structure: the myth → the reality → a concrete example. "
            "3-4 sentences. Conversational tone, no headers, no hashtags, no emoji. "
            "Keep it strictly under 450 characters. "
            "Return only the post text."
        )
    },
    {
        "name": "opinion",
        "count": 5,
        "prompt": (
            "Write a Threads post as a first-person opinion on AI automation. "
            "Start with a bold or controversial take → back it up → end with a question for the reader. "
            "3-4 sentences. Conversational tone, no headers, no hashtags, no emoji. "
            "Keep it strictly under 450 characters. "
            "Return only the post text."
        )
    },
]

# ── Groq API ──────────────────────────────────────────────────────────────────
def generate_post(prompt: str) -> str | None:
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an AI automation expert with a sharp, conversational writing style. "
                    "You write short posts for Threads in English. No headers, no hashtags, no emoji. "
                    "Every post must cover a unique situation or example — never repeat yourself. "
                    "Every post must be under 450 characters."
                )
            },
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 300,
        "temperature": 0.9,
    }
    try:
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30,
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"  Groq error: {e}")
        return None


def trim_to_limit(text: str, limit: int = MAX_LENGTH) -> str:
    """Обрезает текст по последней точке, не выходя за лимит."""
    if len(text) <= limit:
        return text
    truncated = text[:limit].rsplit('.', 1)
    return truncated[0].strip() + '.' if len(truncated) > 1 else text[:limit].strip()


# ── CSV-хелперы ───────────────────────────────────────────────────────────────
def read_csv(path: str) -> list[dict]:
    try:
        with open(path, newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))
    except FileNotFoundError:
        return []


def write_csv(path: str, rows: list[dict]):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def append_csv(path: str, rows: list[dict]):
    file_exists = os.path.isfile(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if not file_exists:
            writer.writeheader()
        writer.writerows(rows)


# ── Архивирование ─────────────────────────────────────────────────────────────
def archive_posted():
    rows = read_csv(CSV_FILE)
    posted       = [r for r in rows if r.get("status") == "posted"]
    still_pending = [r for r in rows if r.get("status") == "pending"]

    if not posted:
        print("Нет опубликованных постов для архивации.")
        return still_pending

    append_csv(ARCHIVE_FILE, posted)
    print(f"Перенесено в архив: {len(posted)} постов.")
    return still_pending


# ── Основной запуск ───────────────────────────────────────────────────────────
def main():
    # 1. Архивируем старое
    pending_before = archive_posted() or []

    # 2. Собираем тексты из архива + текущей очереди для защиты от дублей
    archive_texts = {r["content"].strip() for r in read_csv(ARCHIVE_FILE)}
    for p in pending_before:
        archive_texts.add(p["content"].strip())

    # 3. Строим список задач по форматам
    tasks = []
    for fmt in FORMATS:
        tasks.extend([fmt] * fmt["count"])
    random.shuffle(tasks)

    # 4. Генерируем новые посты
    generated = []
    skipped   = 0

    print(f"\nЗапуск генерации {POSTS_PER_RUN} постов...")
    for i, fmt in enumerate(tasks[:POSTS_PER_RUN], 1):
        print(f"  [{i}/{POSTS_PER_RUN}] Формат: {fmt['name']}", end=" ", flush=True)
        text = generate_post(fmt["prompt"])

        if not text:
            print("→ ошибка API")
            skipped += 1
            continue

        if text in archive_texts:
            print("→ дубликат")
            skipped += 1
            continue

        # Обрезаем если модель всё равно вышла за лимит
        if len(text) > MAX_LENGTH:
            original_len = len(text)
            text = trim_to_limit(text)
            print(f"→ обрезан ({original_len} → {len(text)} симв.)", end=" ")

        archive_texts.add(text)
        generated.append({
            "content":    text,
            "format":     fmt["name"],
            "status":     "pending",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        })
        print(f"→ OK ({len(text)} симв.)")
        time.sleep(1.5)

    # 5. Записываем итог в posts.csv
    final_list = pending_before + generated
    if final_list:
        write_csv(CSV_FILE, final_list)
        print(f"\nГотово! В очереди {len(final_list)} постов "
              f"(новых: {len(generated)}, пропущено: {skipped}).")
    else:
        print("\nНичего не создано.")


if __name__ == "__main__":
    main()
