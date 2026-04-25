import csv
import time
import random
import requests
import os
import xml.etree.ElementTree as ET
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

# Доля постов, которые будут использовать новость как триггер (формат "news")
# Остальные получат новости как фоновый контекст
NEWS_POST_SHARE = 0.01  # ~25% постов = формат news

FIELDNAMES = ["content", "format", "status", "created_at"]

if not GROQ_API_KEY:
    print("Ошибка: GROQ_API_KEY не найден в .env файле!")
    exit(1)

# ── RSS-источники новостей Петербурга ─────────────────────────────────────────
RSS_FEEDS = [
    "https://sanktpeterburg.bezformata.com/rss.xml",
]

def fetch_news(max_items: int = 30) -> list[str]:
    """Забирает заголовки из RSS-лент. Возвращает список строк."""
    headlines = []
    headers = {"User-Agent": "Mozilla/5.0 (compatible; CarouselBot/1.0)"}

    for url in RSS_FEEDS:
        try:
            r = requests.get(url, headers=headers, timeout=10)
            r.raise_for_status()
            root = ET.fromstring(r.content)
            for item in root.iter("item"):
                title = item.findtext("title")
                if title:
                    title = title.strip()
                    if len(title) > 10:
                        headlines.append(title)
        except Exception as e:
            print(f"  RSS ошибка ({url}): {e}")

    random.shuffle(headlines)
    headlines = headlines[:max_items]

    if headlines:
        print(f"  Загружено новостей: {len(headlines)} из {len(RSS_FEEDS)} источников")
    else:
        print("  Новости не загружены, продолжаем без них")

    return headlines


# ── Контекст сериала ──────────────────────────────────────────────────────────
SERIES_CONTEXT = """
Ты пишешь записи для абсурдистского петербургского дневника-сериала «Карусели».
Повествование ведётся от первого лица, герой живёт в Петербурге.

Сквозные персонажи (используй их время от времени, не обязательно в каждом посте):
- Осип — близкий друг, периодически ночует, звонит в колокола, участвует в авантюрах
- Рафаил — сосед или знакомый, обидчивый
- Кейдж — с ним плавают по рекам
- Эзоп — владелец катера, пишет басни

Персонажи из Ветхого завета (появляются как обычные петербуржцы, без пафоса):
- Иов — жалуется, но терпит; живёт где-то на Петроградской
- Иона — боится больших рыб, иногда в них оказывается
- Валаам — приходит с ослом, осёл иногда говорит невпопад
- Самсон — очень сильный, но теряет вещи
- Руфь — собирает что-то на пустырях за Обводным
- Товит — слепой, но ориентируется лучше всех

Персонажи из дикой природы (как полноправные участники событий):
- бобёр — строит что-то в неподходящих местах
- лось — заходит в парадные, стоит у лифта
- выдра — плавает рядом, наблюдает
- ворон — сидит на клавикорде, комментирует

Персонажи из религии (православие, без иронии, но абсурдно):
- батюшка с соседней церкви — даёт советы по хозяйству
- схимник — иногда появляется в метро, молчит
- звонарь — это часто Осип, но иногда кто-то другой

Recurring детали и объекты (вплетай естественно, не все сразу):
- клавикорд (стоит на лестнице или мешает передвижению)
- трусы (используются как крышка, прячут вещи под ними)
- раки и миноги (вылавливают из Мойки или готовят)
- Мойка (главная река, место действия и поисков)
- соседи сверху (постоянно что-то делают не то)
- кофе (ищет или пьёт в начале или конце дня)

Стиль и тон:
- Короткие рубленые предложения. Абсурд подаётся как обыденность — без удивления и объяснений
- Бытовые детали соседствуют с абсолютно нереальными событиями на равных
- Иногда запись начинается с газетного заголовка в кавычках, потом реакция героя одной фразой
- Никаких хэштегов, никаких эмодзи, никаких морали и выводов
- Никаких объяснений абсурда — он просто есть
- Финал записи — незавершённое действие, многоточие, или планы на следующий шаг
- Длина: 3–6 предложений, не больше 450 символов

Важно: каждая запись — уникальная ситуация. Не повторяй предыдущие сюжеты дословно.
Пиши только текст записи, ничего лишнего.
"""

# ── Форматы постов ────────────────────────────────────────────────────────────
FORMATS = [
    {
        "name": "daily",
        "count": 13,
        "prompt": (
            "Напиши одну дневниковую запись для сериала «Карусели». "
            "Обычный день: герой просыпается, что-то происходит, он куда-то идёт или что-то готовит. "
            "Абсурд встроен в быт незаметно. Без заголовка. "
            "Строго до 450 символов."
        )
    },
    {
        "name": "headline",
        "count": 5,
        "prompt": (
            "Напиши одну дневниковую запись для сериала «Карусели». "
            "Начни с придуманного газетного заголовка в кавычках (петербургская тематика, абсурдная новость). "
            "Потом одна фраза реакции героя — флегматичная или тревожная. "
            "Потом 2–3 предложения о том, что он делает дальше. "
            "Строго до 450 символов."
        )
    },
    {
        "name": "osip",
        "count": 7,
        "prompt": (
            "Напиши одну дневниковую запись для сериала «Карусели» с участием Осипа. "
            "Они вместе делают что-то абсурдное — ловят что-то, куда-то плывут, готовят, "
            "попадают в странную ситуацию. Осип упоминается естественно, как старый друг. "
            "Строго до 450 символов."
        )
    },
    {
        "name": "sleep",
        "count": 5,
        "prompt": (
            "Напиши одну дневниковую запись для сериала «Карусели» про сон или пробуждение. "
            "Герой засыпает с каким-то ритуалом, или просыпается после долгого сна, "
            "или обнаруживает что-то странное рядом с кроватью. "
            "Сон и реальность не разграничены. "
            "Строго до 450 символов."
        )
    },
    {
        "name": "biblical",
        "count": 8,
        "prompt": (
            "Напиши одну дневниковую запись для сериала «Карусели» с персонажем из Ветхого завета. "
            "Выбери одного: Иов, Иона, Валаам (с ослом), Самсон, Руфь, Товит. "
            "Персонаж появляется как обычный петербуржец — заходит в гости, встречается на улице, "
            "что-то просит или теряет. Без пафоса и богословия. "
            "Строго до 450 символов."
        )
    },
    {
        "name": "wildlife",
        "count": 5,
        "prompt": (
            "Напиши одну дневниковую запись для сериала «Карусели» с диким животным как участником событий. "
            "Выбери одного: бобёр, лось, выдра, ворон. "
            "Животное делает что-то конкретное и уместное — строит, наблюдает, мешает, помогает. "
            "Никакого очеловечивания напрямую, но поведение говорящее. "
            "Строго до 450 символов."
        )
    },
    {
        "name": "church",
        "count": 5,
        "prompt": (
            "Напиши одну дневниковую запись для сериала «Карусели» с религиозным персонажем. "
            "Батюшка с соседней церкви даёт совет по хозяйству, схимник стоит в метро, "
            "звонарь звонит не вовремя. Без иронии над верой — просто абсурдный быт рядом с церковью. "
            "Строго до 450 символов."
        )
    },
]

# ── Генерация prompt для формата news ────────────────────────────────────────
def make_news_prompt(headline: str, use_character: bool = False) -> str:
    """
    Строит prompt для формата news.
    use_character — иногда просим реагировать через конкретного персонажа.
    """
    character_hint = ""
    if use_character:
        characters = [
            "Осип", "Иов", "Локи", "Один", "Иона", "Тор", "Руфь",
            "Валаам (с ослом)", "батюшка с соседней церкви", "Скальд",
        ]
        char = random.choice(characters)
        character_hint = (
            f"Реакцию на новость выражает или комментирует {char} — "
            f"вплети его естественно, одной фразой или действием. "
        )

    return (
        f"Напиши одну дневниковую запись для сериала «Карусели». "
        f"Начни с этого реального новостного заголовка в кавычках: «{headline}». "
        f"Потом — реакция героя: флегматичная, тревожная или совершенно неуместная. "
        f"{character_hint}"
        f"Потом 1–2 предложения о том, что герой делает дальше — никак не связанном с новостью. "
        f"Строго до 450 символов."
    )


def make_news_context_injection(headlines: list[str]) -> str:
    """
    Формирует короткую вставку с 2 новостями для фонового контекста.
    Добавляется в prompt не-news форматов.
    """
    if not headlines:
        return ""
    sample = random.sample(headlines, min(2, len(headlines)))
    items = "\n".join(f'- «{h}»' for h in sample)
    return (
        f"\n\nФоновый контекст — реальные новости Петербурга сегодня "
        f"(можешь упомянуть вскользь или проигнорировать):\n{items}"
    )


# ── Groq API ──────────────────────────────────────────────────────────────────
def generate_post(prompt: str) -> str | None:
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SERIES_CONTEXT},
            {"role": "user",   "content": prompt},
        ],
        "max_tokens": 300,
        "temperature": 0.95,
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
    truncated = text[:limit].rsplit(".", 1)
    return truncated[0].strip() + "." if len(truncated) > 1 else text[:limit].strip()


# ── CSV-хелперы ───────────────────────────────────────────────────────────────
def read_csv(path: str) -> list[dict]:
    try:
        with open(path, newline="", encoding="utf-8-sig") as f:
            return list(csv.DictReader(f))
    except FileNotFoundError:
        return []


def write_csv(path: str, rows: list[dict]):
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def append_csv(path: str, rows: list[dict]):
    file_exists = os.path.isfile(path)
    with open(path, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if not file_exists:
            writer.writeheader()
        writer.writerows(rows)


# ── Архивирование ─────────────────────────────────────────────────────────────
def archive_posted():
    rows = read_csv(CSV_FILE)
    posted        = [r for r in rows if r.get("status") == "posted"]
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

    # 2. Тянем новости
    print("\nЗагрузка новостей...")
    news_pool = fetch_news(max_items=30)
    news_pool_copy = list(news_pool)  # копия для фоновых инъекций

    # 3. Собираем тексты из архива + текущей очереди для защиты от дублей
    archive_texts = {r["content"].strip() for r in read_csv(ARCHIVE_FILE)}
    for p in pending_before:
        archive_texts.add(p["content"].strip())

    # 4. Строим список задач
    #    — сначала обычные форматы
    tasks = []
    for fmt in FORMATS:
        tasks.extend([fmt] * fmt["count"])
    random.shuffle(tasks)
    tasks = tasks[:POSTS_PER_RUN]

    #    — вставляем news-слоты: ~25% позиций заменяем на формат news
    news_count = int(POSTS_PER_RUN * NEWS_POST_SHARE)
    if news_pool:
        news_indices = random.sample(range(len(tasks)), min(news_count, len(news_pool), len(tasks)))
        available_headlines = list(news_pool)
        random.shuffle(available_headlines)
        for idx, headline in zip(news_indices, available_headlines):
            tasks[idx] = {
                "name": "news",
                "headline": headline,
                "prompt": make_news_prompt(headline, use_character=random.random() > 0.5),
            }

    # 5. Генерируем посты
    generated = []
    skipped   = 0

    print(f"\nЗапуск генерации {POSTS_PER_RUN} постов "
          f"(из них news: {sum(1 for t in tasks if t['name'] == 'news')})...")

    for i, fmt in enumerate(tasks, 1):
        print(f"  [{i}/{POSTS_PER_RUN}] Формат: {fmt['name']}", end=" ", flush=True)

        # Для не-news форматов добавляем фоновые новости в prompt
        if fmt["name"] != "news" and news_pool_copy:
            prompt = fmt["prompt"] + make_news_context_injection(news_pool_copy)
        else:
            prompt = fmt["prompt"]

        text = generate_post(prompt)

        if not text:
            print("→ ошибка API")
            skipped += 1
            continue

        if text in archive_texts:
            print("→ дубликат")
            skipped += 1
            continue

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
        time.sleep(9.0)

    # 6. Записываем итог
    final_list = pending_before + generated
    if final_list:
        write_csv(CSV_FILE, final_list)
        print(f"\nГотово! В очереди {len(final_list)} постов "
              f"(новых: {len(generated)}, пропущено: {skipped}).")
    else:
        print("\nНичего не создано.")


if __name__ == "__main__":
    main()
