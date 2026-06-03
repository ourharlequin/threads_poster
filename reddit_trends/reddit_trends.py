"""
reddit_trends.py — парсит Reddit RSS, извлекает темы через Cerebras,
переводит на нужные языки и сохраняет в DuckDB.

Запускать раз в день в 07:30 по Белграду до генерации постов.
Результат читают все участники через load_topics(group, lang, db_path).
"""

import html
import json
import logging
import os
import re
import time
from datetime import date

import duckdb
import feedparser
from cerebras.cloud.sdk import Cerebras
from dotenv import load_dotenv

from config import SUBREDDITS, ACCOUNTS, LANG_NAMES

load_dotenv()

DB_PATH        = os.getenv("REDDIT_DB_PATH", "data/reddit.duckdb")
MODEL          = "gpt-oss-120b"
POSTS_PER_SUB  = 10
MIN_SUMMARY_LEN = 30
REQUEST_DELAY  = 1.5

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [reddit_trends] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("reddit_trends")

RSS_TEMPLATE = "https://www.reddit.com/r/{subreddit}/top.rss?sort=top&t=day"
#RSS_TEMPLATE_POPULAR = "https://www.reddit.com/r/{subreddit}/hot.rss"
#RSS_TEMPLATE_RISING = "https://www.reddit.com/r/{subreddit}/rising.rss"
#RSS_TEMPLATE_CONTROVERSIAL = "https://www.reddit.com/r/{subreddit}/controversial.rss?sort=controversial&t=day"


# ── DB ────────────────────────────────────────────────────────────────────────

def init_db():
    os.makedirs(os.path.dirname(DB_PATH) or ".", exist_ok=True)
    with duckdb.connect(DB_PATH) as conn:
        conn.execute("CREATE SEQUENCE IF NOT EXISTS daily_topics_id_seq START 1")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS daily_topics (
                id            INTEGER PRIMARY KEY DEFAULT nextval('daily_topics_id_seq'),
                date          DATE    NOT NULL,
                account_group VARCHAR NOT NULL,
                lang          VARCHAR NOT NULL DEFAULT 'en',
                topics        TEXT    NOT NULL,
                created_at    TIMESTAMPTZ DEFAULT now(),
                UNIQUE (date, account_group, lang)
            )
        """)


def save_topics(group: str, lang: str, topics: list[dict]):
    today = date.today()
    topics_json = json.dumps(topics, ensure_ascii=False)
    with duckdb.connect(DB_PATH) as conn:
        existing = conn.execute(
            "SELECT id FROM daily_topics WHERE date = ? AND account_group = ? AND lang = ?",
            [today, group, lang],
        ).fetchone()
        if existing:
            conn.execute(
                "UPDATE daily_topics SET topics = ?, created_at = now() WHERE date = ? AND account_group = ? AND lang = ?",
                [topics_json, today, group, lang],
            )
        else:
            conn.execute(
                "INSERT INTO daily_topics (date, account_group, lang, topics) VALUES (?, ?, ?, ?)",
                [today, group, lang, topics_json],
            )
    log.info(f"[{group}/{lang}] Сохранено {len(topics)} тем")


def load_topics(group: str, lang: str, db_path: str = DB_PATH) -> list[dict]:
    today = date.today()
    try:
        with duckdb.connect(db_path, read_only=True) as conn:
            row = conn.execute(
                "SELECT topics FROM daily_topics WHERE date = ? AND account_group = ? AND lang = ?",
                [today, group, lang],
            ).fetchone()
    except Exception:
        return []
    if not row:
        return []
    return json.loads(row[0])


# ── Парсинг RSS ───────────────────────────────────────────────────────────────

def clean_summary(raw: str) -> str:
    text = re.sub(r'<!--.*?-->', '', raw, flags=re.DOTALL)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = html.unescape(text)
    text = re.sub(r'\s*submitted by.*$', '', text, flags=re.DOTALL)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def fetch_subreddit(subreddit: str) -> list[dict]:
    url = RSS_TEMPLATE.format(subreddit=subreddit)
    feed = feedparser.parse(url)
    posts = []
    for entry in feed.entries[:POSTS_PER_SUB]:
        summary = clean_summary(entry.get("summary", ""))
        if len(summary) < MIN_SUMMARY_LEN:
            continue
        posts.append({
            "title":   entry.get("title", "").strip(),
            "summary": summary[:500],
        })
    log.info(f"  r/{subreddit}: {len(posts)} постов")
    return posts


def fetch_group(subreddits: list[str]) -> list[dict]:
    all_posts = []
    for sub in subreddits:
        try:
            all_posts.extend(fetch_subreddit(sub))
        except Exception as e:
            log.warning(f"  r/{sub}: ошибка — {e}")
        time.sleep(REQUEST_DELAY)
    return all_posts


# ── LLM: извлечение и перевод ─────────────────────────────────────────────────

def extract_topics_en(client: Cerebras, group: str, posts: list[dict]) -> list[dict]:
    posts_text = "\n".join(
        f"- {p['title']}" + (f": {p['summary'][:200]}" if p['summary'] else "")
        for p in posts
    )

    instruction = (
        "Analyze these Reddit posts and extract 5 distinct themes worth writing about.\n"
        "For each theme return:\n"
        "- theme: short label (5 words max)\n"
        "- tension: the core conflict, contradiction, or uncomfortable truth in one sentence\n"
        "- hook: a concrete anonymous scenario from the posts that makes it tangible "
        "(1-2 sentences, no usernames, no subreddit names)\n\n"
        "Return ONLY a valid JSON array of 5 objects. Example:\n"
        '[{"theme": "The guilt of surviving", '
        '"tension": "When justice arrives without your participation, does it still count?", '
        '"hook": "A person laughed when their abuser was severely injured. She had not had nightmares since."}]'
    )

    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": instruction},
                {"role": "user",   "content": f"Reddit posts:\n{posts_text}"},
            ],
            max_completion_tokens=1500,
            temperature=0.5,
        )
        content = resp.choices[0].message.content
        if not content:
            log.warning(f"Cerebras вернул пустой ответ [{group}/en]")
            return []
        raw = content.strip()
        start, end = raw.find("["), raw.rfind("]")
        if start == -1 or end == -1:
            log.warning(f"LLM не вернул JSON [{group}/en]: {raw[:100]}")
            return []
        topics = json.loads(raw[start:end + 1])
        return [t for t in topics if isinstance(t, dict) and all(k in t for k in ("theme", "tension", "hook"))]
    except Exception as e:
        log.error(f"Cerebras error [{group}/en]: {e}")
        return []


def translate_topics(client: Cerebras, topics: list[dict], lang: str) -> list[dict]:
    lang_name = LANG_NAMES.get(lang, lang)
    topics_json = json.dumps(topics, ensure_ascii=False)

    instruction = (
        f"Translate the following JSON array of theme objects into {lang_name}.\n"
        "Translate all three fields: theme, tension, hook.\n"
        "Keep the JSON structure identical. Return ONLY valid JSON, no markdown."
    )

    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": instruction},
                {"role": "user",   "content": topics_json},
            ],
            max_completion_tokens=1500,
            temperature=0.2,
        )
        content = resp.choices[0].message.content
        if not content:
            log.warning(f"Cerebras вернул пустой ответ при переводе [{lang}]")
            return topics
        raw = content.strip()
        start, end = raw.find("["), raw.rfind("]")
        if start == -1 or end == -1:
            log.warning(f"Перевод не вернул JSON [{lang}]: {raw[:100]}")
            return topics  # fallback: оригинал на английском
        translated = json.loads(raw[start:end + 1])
        return [t for t in translated if isinstance(t, dict) and all(k in t for k in ("theme", "tension", "hook"))]
    except Exception as e:
        log.error(f"Ошибка перевода [{lang}]: {e} — используем английский")
        return topics


# ── main ─────────────────────────────────────────────────────────────────────

def main():
    init_db()

    cerebras_key = os.getenv("CEREBRAS_API_KEY")
    if not cerebras_key:
        log.error("CEREBRAS_API_KEY не найден в .env")
        return

    client = Cerebras(api_key=cerebras_key)

    # Определяем какие языки нужны для каждой группы
    group_langs: dict[str, set[str]] = {}
    for acc_cfg in ACCOUNTS.values():
        g, l = acc_cfg["group"], acc_cfg["lang"]
        group_langs.setdefault(g, set()).add(l)

    for group, subreddits in SUBREDDITS.items():
        langs_needed = group_langs.get(group, {"en"})
        log.info(f"Группа '{group}': сабреддитов={len(subreddits)}, языки={langs_needed}")

        posts = fetch_group(subreddits)
        log.info(f"[{group}] Постов с текстом: {len(posts)}")
        if not posts:
            log.warning(f"[{group}] Нет постов — пропускаю")
            continue

        # Извлекаем темы на английском
        topics_en = extract_topics_en(client, group, posts)
        if not topics_en:
            log.warning(f"[{group}] LLM не вернул темы — пропускаю")
            continue

        # Сохраняем английскую версию
        save_topics(group, "en", topics_en)

        # Переводим и сохраняем остальные языки
        for lang in langs_needed:
            if lang == "en":
                continue
            log.info(f"[{group}] Перевожу на {LANG_NAMES.get(lang, lang)}...")
            translated = translate_topics(client, topics_en, lang)
            save_topics(group, lang, translated)

    log.info("Готово")


if __name__ == "__main__":
    main()
