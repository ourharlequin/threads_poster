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

# Docker
docker-compose up -d publisher
docker-compose up -d scheduler
docker-compose --profile tools run --rm threads_generator --account event_parsing
docker-compose --profile tools run --rm threads_refresher
```
