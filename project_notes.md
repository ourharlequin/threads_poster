# Project Notes — threads_poster

## Архитектура

```
[Groq LLM] ← generate_posts.py (вручную или docker-compose --profile tools)
                ↓
           posts.csv (status: pending)
                ↓
publisher.py (каждые 29 минут)
                ↓
           Threads API → опубликованные посты
                ↓
posts.csv (status: posted) → archive.csv
```

**Ключевые файлы:**
- `generate_posts.py` — генерирует 50 постов через Groq API (llama-3.3-70b), 8 форматов
- `publisher.py` — читает posts.csv и публикует первый pending-пост в Threads
- `posts.csv` — очередь постов (`content`, `format`, `status`, `created_at`)
- `archive.csv` — архив опубликованных постов (дедупликация)
- `Dockerfile` + `docker-compose.yml` — два сервиса: publisher (always) и generator (по запросу)

**Переменные окружения (`.env`):**
- `GROQ_API_KEY` — для generate_posts.py
- `THREADS_ACCESS_TOKEN` — для publisher.py
- `THREADS_USER_ID` — для publisher.py

---

## Найденные проблемы

- [x] `groq` отсутствует в `requirements.txt` — исправлено
- [x] Формат `norse` — устаревший, убран (новая архитектура без него)
- [x] `NEWS_POST_SHARE = 0.01` — убран, логика форматов переработана
- [x] `duckdb` отсутствовал в `requirements.txt` — исправлено

---

## Изменения (2026-04-28)

### Что сделано

**Архитектура переработана:**
- `publisher.py` — заменён на многопоточный паблишер (6 аккаунтов, DuckDB, умное расписание)
- `generate_posts.py` — написан заново: реальный генератор постов через Groq API
- `prompts.py` — новый файл, конфиг промптов отдельно на каждый аккаунт
- `refresh_tokens.py` — новый файл, обновление Threads-токенов (запускать раз в месяц)
- `requirements.txt` — убраны `pandas`, `schedule`; добавлены `duckdb`, `groq`
- `Dockerfile` — убраны legacy CSV, добавлены `tzdata` и `mkdir -p data`
- `docker-compose.yml` — добавлены `env_file`, volume `threads_data`, сервисы `threads_refresher`
- `.env` — мигрировал на формат `ACCOUNT_N_*`

**Ключевые решения:**
- Токены Groq — отдельные на каждый аккаунт (`ACCOUNT_N_GROQ_TOKEN`)
- Токен Threads — пока один общий `THREADS_TOKEN` для экспериментов; при переходе на продакшн добавить `ACCOUNT_N_THREADS_TOKEN`
- Промпты — в `prompts.py`, словарь `account_id → {system, formats}`, каждый аккаунт своя тема
- БД — DuckDB, файл `data/data.duckdb`, таблица `posts` (id, account_id, content, status, created_at, posted_at, threads_post_id)
- Расписание — окно 9:00–21:00 по Белграду, интервал 10–40 мин (рандом), 5% пропуск

### Текущий статус

- [ ] Получить `USER_ID` и `THREADS_TOKEN` для 6 аккаунтов (проблема на стороне Facebook — не удаётся получить маркер пользователя через Graph API Explorer)
- [ ] Заполнить `ACCOUNT_2..6_*` в `.env`
- [ ] Заполнить тематику аккаунтов 2–6 в `prompts.py`
- [ ] Протестировать генерацию: `docker-compose --profile tools run --rm threads_generator --account budimir`
- [ ] Протестировать публикацию

### Аккаунты (тестировщики в приложении Threads poster)

| # | account_id | Threads-профиль | USER_ID | Статус |
|---|---|---|---|---|
| 1 | budimir | Budimir Voroshilov | 26528771100143116 | ✅ токен есть |
| 2 | event_parsing | event_parsing | — | ⏳ нет токена |
| 3 | claude_space | claude_space | — | ⏳ нет токена |
| 4 | budeschka | budeschka | — | ⏳ нет токена |
| 5 | cycling_superhero | cycling_superhero | — | ⏳ нет токена |
| 6 | aire.porteno | aire.porteno | — | ⏳ нет токена |
