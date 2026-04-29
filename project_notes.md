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
```

**Ключевые файлы:**
- `generate_posts.py` — генерирует посты через Groq API (llama-3.3-70b), паузы 3с между запросами
- `publisher.py` — 6 потоков, по одному на аккаунт, умное расписание
- `prompts.py` — конфиг промптов: system-промпт + форматы для каждого аккаунта
- `get_tokens.py` — OAuth-хелпер для получения Threads long-lived токенов
- `refresh_tokens.py` — обновление токенов (запускать раз в месяц)
- `test_publish.py` — тестовая публикация одного поста без окна времени
- `Dockerfile` + `docker-compose.yml` — сервисы: publisher (always), generator и refresher (по запросу)

**Переменные окружения (`Budimir/.env`):**
- `META_APP_ID` / `META_APP_SECRET` — для get_tokens.py
- `ACCOUNT_N_ID` — account_id аккаунта
- `ACCOUNT_N_USER_ID` — Threads USER_ID
- `ACCOUNT_N_THREADS_TOKEN` — long-lived токен Threads (60 дней)
- `ACCOUNT_N_GROQ_TOKEN` — Groq API токен

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
- **Scopes:** `threads_basic`, `threads_content_publish`

---

## Найденные и исправленные проблемы

- [x] `groq` отсутствовал в `requirements.txt`
- [x] `duckdb` отсутствовал в `requirements.txt`
- [x] `norse` формат — убран (устаревший)
- [x] `get_groq_token` прерывался при пропуске в нумерации аккаунтов — исправлен перебор
- [x] `generate_posts.py` не инициализировал БД — добавлен `init_db()`
- [x] Параллельный запуск генераторов вызывал конфликт блокировок DuckDB — запускать последовательно
- [x] `data/` и `**/.env` добавлены в `.gitignore`

---

## Изменения (2026-04-28)

### Что сделано

- Получены токены и USER_ID для всех 6 аккаунтов через `get_tokens.py`
- Написан `prompts.py` — тематика и форматы для каждого аккаунта
- Добавлены паузы и retry в `generate_posts.py` (3с между запросами, экспоненциальный backoff при 429)
- Сгенерировано 30 постов на каждый аккаунт (183 итого в БД)
- Протестирована публикация — все 6 аккаунтов публикуют успешно
- Создан PR #3: `feature/multi-account-publisher`

### Текущий статус

- [x] Токены и USER_ID для всех 6 аккаунтов
- [x] `prompts.py` заполнен для всех аккаунтов
- [x] Генерация протестирована (30 постов × 6 аккаунтов)
- [x] Публикация протестирована на всех 6 аккаунтах
- [x] PR #3 создан и запушен
- [x] Запустить publisher.py в продакшн (Docker или напрямую)
- [x] Настроить автозапуск (systemd / Task Scheduler / docker restart: always)
- [x] Обновить токены через `refresh_tokens.py` через ~55 дней

---

## Полезные команды

```bash
# Генерация постов для одного аккаунта
python generate_posts.py --account event_parsing --count 30

# Тестовая публикация (без окна времени)
python test_publish.py

# Запуск паблишера
python publisher.py

# Обновление токенов (раз в месяц)
python refresh_tokens.py

# Docker
docker-compose up -d publisher
docker-compose --profile tools run --rm threads_generator --account event_parsing
docker-compose --profile tools run --rm threads_refresher
```
