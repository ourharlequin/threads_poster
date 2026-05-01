# Project Notes — threads_poster

## Архитектура

```
[Groq LLM] ← generate_posts.py --account <account_id>
                ↓
           DuckDB (data/data.duckdb) — таблица posts (status: pending)
                ↓
publisher.py (6 потоков, окно 9:00–21:00 Белград, интервал 10–40 мин)
                ↓
           Threads API → опубликованные посты
                ↓
           posts.status = 'posted' + threads_post_id
                ↓
fetch_insights.py (05:00 Белград) → post_insights + account_insights
```

**Ключевые файлы:**
- `generate_posts.py` — генерирует посты через Groq API (llama-3.3-70b), паузы 3с между запросами
- `publisher.py` — 6 потоков, по одному на аккаунт, умное расписание
- `fetch_insights.py` — сбор метрик из Threads Insights API (запуск в 05:00 через scheduler)
- `scheduler.py` — планировщик: insights 05:00, генерация 08:00, refresh токенов каждые 58 дней
- `prompts.py` — конфиг промптов: system-промпт + форматы для каждого аккаунта
- `get_tokens.py` — OAuth-хелпер для получения Threads long-lived токенов (все скоупы)
- `refresh_tokens.py` — обновление токенов (каждые 58 дней через scheduler)
- `test_publish.py` — тестовая публикация одного поста без окна времени
- `Dockerfile` + `docker-compose.yml` — сервисы: publisher (always), scheduler (always), generator и refresher (по запросу)

**Переменные окружения (`Budimir/.env`):**
- `META_APP_ID` / `META_APP_SECRET` — для get_tokens.py
- `ACCOUNT_N_ID` — account_id аккаунта
- `ACCOUNT_N_USER_ID` — Threads USER_ID
- `ACCOUNT_N_THREADS_TOKEN` — long-lived токен Threads (60 дней)
- `ACCOUNT_N_GROQ_TOKEN` — Groq API токен

---

## Схема БД (DuckDB)

| Таблица | Назначение |
|---|---|
| `posts` | Все посты: pending → posted / failed |
| `post_insights` | Снапшоты метрик поста (views/likes/replies/reposts/quotes), пишутся ежедневно 7 дней после публикации |
| `account_insights` | Дневные метрики аккаунта + followers_count (UPSERT по account_id + date) |

---

## Аккаунты

| # | account_id | Threads-профиль | USER_ID | Тема | Язык | Статус |
|---|---|---|---|---|---|---|
| 1 | event_parsing | event_parsing | 26528771100143116 | AI-новости 2026 | EN | ✅ |
| 2 | budeschka | budeschka | 35121164990863983 | Сюрреалистические истории | RU | ✅ |
| 3 | cycling_superhero | cycling_superhero | 26887077647646890 | Велоспорт | EN | ✅ |
| 4 | claude_space | claude_space | 26666671099619981 | Anthropic / Claude | RU | ✅ |
| 5 | aire.porteno | aire.porteno | 26699742642998871 | Кафе и места Буэнос-Айреса | ES | ✅ |
| 6 | mind_the_tap | mind_the_tap | 36298180553102299 | Кафе и места Лондона | EN | ✅ |

---

## Meta App

- **App ID:** 1509405377206199
- **Redirect URI (зарегистрирован):** `https://localhost/callback`
- **Scopes:** все доступные — `threads_basic`, `threads_content_publish`, `threads_delete`, `threads_keyword_search`, `threads_location_tagging`, `threads_manage_insights`, `threads_manage_mentions`, `threads_manage_replies`, `threads_profile_discovery`, `threads_read_replies`, `threads_share_to_instagram`

---

## Superset (аналитика)

### Архитектура

```
Budimir/data/data.duckdb ─┐
Slava/data/data.duckdb   ─┼─ merger.py (07:45 Белград) ──→ data/analytics.duckdb ──→ Superset :8088
Tanya/data/data.duckdb   ─┘
```

- **merger** — слияние трёх БД в одну, добавляет колонку `participant` (budimir / slava / tanya)
- **Superset** — Apache Superset 4.1.1 с DuckDB-коннектором (`duckdb-engine`)
- DuckDB открывается в `read_only=True` (через `connect_args`) — 4 gunicorn-воркера читают одновременно без конфликтов
- При слиянии (≈1–2 с) Superset временно недоступен — незаметно

### Запуск

```bash
# Из корня проекта (не из Budimir/)
docker compose up -d
```

Superset: **http://localhost:8088** — логин `admin` / `admin`  
Dashboard: http://localhost:8088/superset/dashboard/1/

### Чарты на дашборде

| Чарт | Тип | Датасет |
|---|---|---|
| Просмотры по аккаунтам | Line | account_insights |
| Рост фолловеров | Line | account_insights |
| Вовлечённость по аккаунтам | Bar | account_insights |
| Постов опубликовано по дням | Bar | posts |
| Топ постов по просмотрам | Table | post_insights |
| Статус постов | Pie | posts |

### Схема analytics.duckdb

Те же три таблицы что в participant-БД + колонка `participant`:
- `account_insights` — дневные метрики аккаунтов всех участников
- `posts` — все посты (pending / posted / failed)
- `post_insights` — снапшоты метрик постов

### Ключевые файлы

```
superset/
├── Dockerfile           — образ Superset с duckdb-engine
├── Dockerfile.merger    — лёгкий Python образ для merger (uid=1000)
├── merger.py            — слияние БД, запуск в 07:45 по Белграду + при старте
├── setup_db.py          — регистрирует analytics.duckdb в Superset при первом запуске
├── create_charts.py     — создаёт 6 чартов и дашборд через REST API (запускать вручную)
├── superset_config.py   — Redis-кэш, SQLite для метаданных Superset
└── docker-init.sh       — entrypoint: init при первом старте → gunicorn
data/
└── analytics.duckdb     — объединённая БД (создаётся merger'ом)
```

### Переменные окружения (корневой .env или через docker-compose)

- `SUPERSET_SECRET_KEY` — случайный hex-ключ (в `Budimir/.env`)
- `SUPERSET_ADMIN_USER` / `SUPERSET_ADMIN_PASSWORD` / `SUPERSET_ADMIN_EMAIL` — дефолты: admin/admin

### Решённые проблемы

- `?read_only=true` в URI не работает с duckdb-engine 0.13.4 → использовать `connect_args: {read_only: true}` в `extra`
- Файл `analytics.duckdb` создавался от root → merger теперь запускается от uid=1000 (совпадает с superset-пользователем)
- Чарты создаются через API, но `slices` не линкуются автоматически → привязывать через ORM (`dash.slices = charts`)

---

## Найденные и исправленные проблемы

- [x] `groq` отсутствовал в `requirements.txt`
- [x] `duckdb` отсутствовал в `requirements.txt`
- [x] `norse` формат — убран (устаревший)
- [x] `get_groq_token` прерывался при пропуске в нумерации аккаунтов — исправлен перебор
- [x] `generate_posts.py` не инициализировал БД — добавлен `init_db()`
- [x] Параллельный запуск генераторов вызывал конфликт блокировок DuckDB — запускать последовательно
- [x] `data/` и `**/.env` добавлены в `.gitignore`
- [x] `followers_count` возвращал 0 при `period=day` — вынесен в отдельный запрос с `period=lifetime`
- [x] Токен budeschka записан с ошибкой при копировании — исправлен вручную

---

## История изменений

### 2026-04-28
- Получены токены и USER_ID для всех 6 аккаунтов через `get_tokens.py`
- Написан `prompts.py` — тематика и форматы для каждого аккаунта
- Добавлены паузы и retry в `generate_posts.py` (3с между запросами, экспоненциальный backoff при 429)
- Сгенерировано 30 постов на каждый аккаунт (183 итого в БД)
- Протестирована публикация — все 6 аккаунтов публикуют успешно
- publisher.py запущен в продакшн, настроен автозапуск
- Создан PR #3: `feature/multi-account-publisher`

### 2026-04-29
- Написан `fetch_insights.py` — сбор post-level и account-level метрик
- Добавлен запуск insights в `scheduler.py` в 05:00 по Белграду
- `get_tokens.py` расширен до полного набора OAuth-скоупов
- Перевыпущены токены для всех 6 аккаунтов с новыми скоупами
- Протестировано: 6/6 аккаунтов, данные в БД
- Создан PR #5: `feature/multi-account-publisher`

---

## Текущий статус

- [x] Токены и USER_ID для всех 6 аккаунтов (все скоупы)
- [x] `prompts.py` заполнен для всех аккаунтов
- [x] Генерация и публикация в продакшне
- [x] Автозапуск настроен
- [x] Сбор метрик работает (05:00 ежедневно)
- [x] PR #3 и PR #5 запушены
- [x] Superset поднят, дашборд с 6 чартами работает
- [x] Merger сливает данные всех участников в analytics.duckdb (07:45 Белград)

---

## Полезные команды

```bash
# Генерация постов для одного аккаунта
python generate_posts.py --account event_parsing --count 30

# Тестовая публикация (без окна времени)
python test_publish.py

# Сбор метрик вручную
python fetch_insights.py

# Запуск паблишера
python publisher.py

# Обновление токенов (раз в месяц, или через scheduler автоматически)
python refresh_tokens.py

# Docker — publisher/scheduler (из Budimir/)
cd Budimir
docker-compose up -d

# Docker — аналитика Superset (из корня проекта)
cd ..  # корень threads_poster
docker compose up -d
docker compose logs merger       # проверить слияние
docker compose logs superset     # проверить Superset

# Пересоздать чарты и дашборд
python superset/create_charts.py

# Привязать чарты к дашборду вручную (если слетели)
docker compose exec superset bash -c "python -c \"
from superset import create_app; app = create_app()
with app.app_context():
    from superset.extensions import db
    from superset.models.dashboard import Dashboard
    from superset.models.slice import Slice
    dash = db.session.query(Dashboard).filter_by(id=1).first()
    dash.slices = db.session.query(Slice).all()
    db.session.commit()
\""
```
