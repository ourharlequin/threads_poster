# MCP Server для threads_poster

## Статус: реализовано, не задеплоено

---

## Архитектура

```
Claude Code (stdio)
    ↕ JSON-RPC
threads_mcp_server.py  (Python, локально, C:\Users\ourha\threads_poster\mcp_server\)
    ↕ httpx, THREADS_API_BASE=http://localhost:7843
threads_api  (Docker, port 7843)
    ↕ DuckDB (read_only) + subprocess + Docker socket
/app/participants/{name}/   — скрипты участников
/app/data/{name}/data.duckdb — БД участников
/app/data/analytics/analytics.duckdb — объединённая аналитика
```

**VPS-режим:** `ssh -L 7843:localhost:7843 root@23.26.0.184 -N -f` — конфиг MCP не меняется.

---

## Файловая структура

```
threads_poster/
  threads_api/
    Dockerfile
    requirements.txt          # fastapi, uvicorn, duckdb, python-dotenv, docker, httpx
    main.py                   # FastAPI app, lifespan, монтирование роутеров
    registry.py               # авто-дискавери /app/participants/, PARTICIPANTS + REGISTRY
    db.py                     # duckdb-хелперы, asyncio.Lock на запись, db_path как параметр
    subprocess_runner.py      # вайтлист скриптов, scripts_dir + db_path как параметры
    routers/
      analytics.py            # top-posts, followers, account-stats, compare, queue-stats
      content.py              # queue, generate, add, delete, skip
      publishing.py           # force, status, fetch-insights
      system.py               # health, token-expiry, refresh-tokens, logs, accounts
      superset.py             # status, merger-run, rebuild
  mcp_server/
    threads_mcp_server.py     # 21 @mcp.tool(), httpx, FastMCP
    requirements.txt          # mcp>=1.27.0, httpx>=0.28.1
  migrate.sh                  # одноразовый скрипт миграции на VPS
```

---

## Авто-дискавери участников (`registry.py`)

`threads_api` сканирует `/app/participants/` при старте. Каждая подпапка с `.env` — участник.
Для добавления нового участника нужно только 2 строки в `docker-compose.yml`:

```yaml
- ./NewGuy:/app/participants/newguy:ro
- ./NewGuy/data:/app/data/newguy
```

Текущие участники:

| participant | Аккаунтов | .env | Статус |
|---|---|---|---|
| budimir | 6 | есть | активен |
| tanya | 6 | есть | активен |
| slava | — | нет | неактивен |

Именование контейнеров: `{participant}_publisher`, `{participant}_scheduler`

---

## HTTP API — 21 эндпоинт

### Analytics (`GET /analytics/...`)

| Path | Параметры | Данные |
|------|-----------|--------|
| `/analytics/top-posts` | `limit=10, days=30, participant=` | analytics.duckdb |
| `/analytics/followers` | `account_id=, days=30` | analytics.duckdb |
| `/analytics/account-stats` | `account_id` (обяз.), `days=7` | analytics.duckdb |
| `/analytics/compare` | `days=7` | analytics.duckdb |
| `/analytics/queue-stats` | — | все data.duckdb |

### Content (`/content/...`)

| Method | Path | Описание |
|--------|------|----------|
| GET | `/content/queue` | Список pending постов (`account_id`, `limit=20`) |
| POST | `/content/generate` | Запустить `generate_posts.py` async (`account_id`, `count`) |
| POST | `/content/add` | Добавить пост вручную (`account_id`, `content`) |
| DELETE | `/content/post/{post_id}` | Удалить pending пост (`account_id`) |
| PATCH | `/content/post/{post_id}/skip` | Пометить как skipped (`account_id`) |

### Publishing (`/publishing/...`)

| Method | Path | Описание |
|--------|------|----------|
| POST | `/publishing/force` | Форс-публикация через `test_publish.py` (`account_id`) |
| GET | `/publishing/status` | Статус всех publisher/scheduler контейнеров |
| POST | `/publishing/fetch-insights` | Запустить `fetch_insights.py` (`participant`) |

### System (`/system/...`)

| Method | Path | Описание |
|--------|------|----------|
| GET | `/system/health` | Пинг |
| GET | `/system/token-expiry` | Валидность токенов (live-проверка через Threads API) |
| POST | `/system/refresh-tokens` | Запустить `refresh_tokens.py` (`participant`) |
| GET | `/system/logs` | `docker logs` (`container`, `lines=50`) |
| GET | `/system/accounts` | Список всех аккаунтов всех участников |

### Superset (`/superset/...`)

| Method | Path | Описание |
|--------|------|----------|
| GET | `/superset/status` | Статус контейнеров superset/merger/redis |
| POST | `/superset/merger-run` | Форс-запуск merger через docker exec |
| POST | `/superset/rebuild` | Пересоздать чарты и дашборд через Superset REST API |

---

## 21 MCP инструмент

```
# Аналитика
threads_top_posts(limit, days, participant)
threads_follower_growth(account_id, days)
threads_account_stats(account_id, days)
threads_cross_account_compare(days)
threads_queue_stats()

# Контент
threads_list_queue(account_id, limit)
threads_generate_posts(account_id, count)
threads_add_post(account_id, content)
threads_delete_post(account_id, post_id)
threads_skip_post(account_id, post_id)

# Публикация
threads_force_publish(account_id)
threads_publisher_status()
threads_fetch_insights(participant)

# Система
threads_health()
threads_token_expiry()
threads_refresh_tokens(participant)
threads_logs(container, lines)
threads_list_accounts()

# Superset
threads_superset_status()
threads_merger_run()
threads_superset_rebuild()
```

---

## Subprocess-стратегия

| Скрипт | Режим | Таймаут |
|--------|-------|---------|
| `generate_posts.py` | async (не блокирует) | — |
| `test_publish.py` | sync | 60 с |
| `fetch_insights.py` | sync | 120 с |
| `refresh_tokens.py` | sync | 30 с |

`cwd` = `scripts_dir` участника, `DB_PATH` передаётся явно как env var.
Только 4 вайтлистированных скрипта.

---

## DuckDB конкурентность

- **Чтение**: `read_only=True`, кратковременные соединения
- **Запись** (add/delete/skip): `asyncio.Lock()` + retry 3×200мс

---

## docker-compose.yml (root) — сервис threads_api

```yaml
threads_api:
  build:
    context: ./threads_api
  container_name: threads_api
  restart: always
  ports:
    - "7843:7843"
  environment:
    - TZ=Europe/Belgrade
    - SUPERSET_URL=http://threads_superset:8088
    - SUPERSET_ADMIN_USER=${SUPERSET_ADMIN_USER:-admin}
    - SUPERSET_ADMIN_PASSWORD=${SUPERSET_ADMIN_PASSWORD:-admin}
  volumes:
    - ./Budimir:/app/participants/budimir:ro
    - ./Budimir/data:/app/data/budimir
    - ./Tanya:/app/participants/tanya:ro
    - ./Tanya/data:/app/data/tanya
    - ./Slava:/app/participants/slava:ro
    - ./Slava/data:/app/data/slava
    - ./data:/app/data/analytics:ro
    - /var/run/docker.sock:/var/run/docker.sock:ro
  depends_on:
    - merger
```

---

## .mcp.json

Файл: `C:\Users\ourha\Fusion360 MCP\.mcp.json` — уже добавлено:

```json
"threads": {
  "command": "python",
  "args": ["C:\\Users\\ourha\\threads_poster\\mcp_server\\threads_mcp_server.py"],
  "env": { "THREADS_API_BASE": "http://localhost:7843" }
}
```

---

## Миграция на VPS (одноразово)

```bash
bash /root/threads_poster/migrate.sh
```

Скрипт делает:
1. Останавливает контейнеры Budimir/Tanya/Slava
2. Копирует данные из named volumes → bind mount директории
3. Удаляет старые контейнеры `threads_publisher` / `threads_scheduler` (Budimir)
4. `git pull`
5. Перезапускает всех участников с новыми bind mounts
6. Поднимает `threads_api`
7. Проверяет `/system/health` и `/system/accounts`

---

## Деплой (после миграции)

GitHub Actions автоматически деплоит `threads_api` при каждом пуше в main.

Ручной деплой:
```bash
cd /root/threads_poster
docker compose up -d --build threads_api
```

---

## Верификация

```bash
# SSH-туннель
ssh -L 7843:localhost:7843 root@23.26.0.184 -N -f

# Проверить API
curl http://localhost:7843/system/health
# → {"ok": true, "data": {"status": "ok"}}

# В Claude Code
/mcp  # → threads сервер с 21 инструментом

# Тест инструментов
threads_health()
threads_list_accounts()    # → все аккаунты budimir + tanya
threads_queue_stats()      # → pending/posted/failed по всем участникам
threads_top_posts(days=7)  # → топ постов за неделю
```
