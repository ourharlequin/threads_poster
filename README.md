# Threads Auto-Poster

Multi-account automated content generation and publishing system for Meta Threads. Generates posts via Cerebras API (llama3.1-8b), publishes them on a schedule via Meta Graph API, and exposes a REST API + MCP server for management through Claude.

---

## Architecture

```
HuggingFace (Qwen2.5-72B) ← chat & prompt optimization
Cerebras (llama3.1-8b)    ← generate_posts.py --account <id> --count N
                                ↓
                     DuckDB (data/data.duckdb) — posts table (status: pending)
                                ↓
         publisher.py (per-account threads, window 9:00–21:00 Belgrade, 10–40 min intervals)
                                ↓
                     Threads API → published posts
                                ↓
         fetch_insights.py (05:00 Belgrade) → post_insights + account_insights
                                ↓
         merger.py (07:45 Belgrade) → data/analytics.duckdb → Superset :8088
```

**MCP layer:**
```
Claude Code (stdio)
    ↕ JSON-RPC
mcp_server/threads_mcp_server.py  (local)
    ↕ httpx — THREADS_API_BASE=http://localhost:7843
threads_api  (Docker, port 7843)
    ↕ DuckDB + subprocess + Docker socket
/app/participants/{name}/   — participant scripts
/app/data/{name}/data.duckdb
/app/data/analytics/analytics.duckdb
```

---

## Participants & Accounts

### Budimir (6 accounts) — active
### Tanya (6 accounts) — active
### Slava (6 accounts) — active

---

## Project Structure

```
threads_poster/
  Budimir/                     — participant folder
    prompts.py                 — system prompts and formats for all 6 accounts
    generate_posts.py          — post generation: --account <id> --count N, temp=0.9
    publisher.py               — per-account publishing threads
    scheduler.py               — insights 05:00, generation 08:00, token refresh every 58 days
    fetch_insights.py          — post-level and account-level metrics from Threads Insights API
    refresh_tokens.py          — token renewal (every 58 days via scheduler)
    test_publish.py            — force-publish one post without time window
    get_tokens.py              — OAuth helper for long-lived Threads tokens (all scopes)
    .env                       — credentials (never commit)
  Tanya/                       — same structure
  Slava/                       — same structure
  threads_api/
    main.py                    — FastAPI app, lifespan, router mounting
    registry.py                — auto-discovery of /app/participants/, PARTICIPANTS + REGISTRY
    db.py                      — DuckDB helpers, asyncio.Lock for writes, db_path as param
    subprocess_runner.py       — whitelisted scripts, scripts_dir + db_path as env vars
    routers/
      analytics.py             — top-posts, followers, account-stats, compare, queue-stats
      content.py               — queue, generate, add, delete, skip
      publishing.py            — force, status, fetch-insights
      system.py                — health, token-expiry, refresh-tokens, logs, accounts
      superset.py              — status, merger-run, rebuild
  mcp_server/
    threads_mcp_server.py      — 21 @mcp.tool() via FastMCP + httpx
  superset/
    Dockerfile
    Dockerfile.merger
    merger.py                  — merges all participant DBs into analytics.duckdb
    setup_db.py                — registers analytics.duckdb in Superset on first run
    create_charts.py           — creates 6 charts and dashboard via REST API (run manually)
    superset_config.py         — Redis cache, SQLite for Superset metadata
    docker-init.sh             — entrypoint: init on first start → gunicorn
  data/
    analytics.duckdb           — merged DB (created by merger)
  docker-compose.yml
```

---

## Database Schema (DuckDB)

| Table | Purpose |
|---|---|
| `posts` | All posts: pending → posted / failed |
| `post_insights` | Post metric snapshots (views/likes/replies/reposts/quotes), written daily for 7 days after publish |
| `account_insights` | Daily account metrics + followers_count (UPSERT by account_id + date) |

`analytics.duckdb` has the same three tables with an added `participant` column (budimir / tanya / slava).

---

## HTTP API (21 endpoints)

### Analytics `GET /analytics/...`

| Path | Parameters | Source |
|------|-----------|--------|
| `/analytics/top-posts` | `limit=10, days=30, participant=` | analytics.duckdb |
| `/analytics/followers` | `account_id=, days=30` | analytics.duckdb |
| `/analytics/account-stats` | `account_id` (required), `days=7` | analytics.duckdb |
| `/analytics/compare` | `days=7` | analytics.duckdb |
| `/analytics/queue-stats` | — | all data.duckdb |

### Content `/content/...`

| Method | Path | Description |
|--------|------|-------------|
| GET | `/content/queue` | List pending posts (`account_id`, `limit=20`) |
| POST | `/content/generate` | Run `generate_posts.py` async (`account_id`, `count`) |
| POST | `/content/add` | Add post manually (`account_id`, `content`) |
| DELETE | `/content/post/{post_id}` | Delete pending post (`account_id`) |
| PATCH | `/content/post/{post_id}/skip` | Mark as skipped (`account_id`) |

### Publishing `/publishing/...`

| Method | Path | Description |
|--------|------|-------------|
| POST | `/publishing/force` | Force-publish via `test_publish.py` (`account_id`) |
| GET | `/publishing/status` | Status of all publisher/scheduler containers |
| POST | `/publishing/fetch-insights` | Run `fetch_insights.py` (`participant`) |

### System `/system/...`

| Method | Path | Description |
|--------|------|-------------|
| GET | `/system/health` | Ping |
| GET | `/system/token-expiry` | Token validity (live check via Threads API) |
| POST | `/system/refresh-tokens` | Run `refresh_tokens.py` (`participant`) |
| GET | `/system/logs` | `docker logs` (`container`, `lines=50`) |
| GET | `/system/accounts` | All accounts across all participants |

### Superset `/superset/...`

| Method | Path | Description |
|--------|------|-------------|
| GET | `/superset/status` | superset/merger/redis container status |
| POST | `/superset/merger-run` | Force merger run via docker exec |
| POST | `/superset/rebuild` | Recreate charts and dashboard via Superset REST API |

---

## MCP Tools (21)

```python
# Analytics
threads_top_posts(limit, days, participant)
threads_follower_growth(account_id, days)
threads_account_stats(account_id, days)
threads_cross_account_compare(days)
threads_queue_stats()

# Content
threads_list_queue(account_id, limit)
threads_generate_posts(account_id, count)
threads_add_post(account_id, content)
threads_delete_post(account_id, post_id)
threads_skip_post(account_id, post_id)

# Publishing
threads_force_publish(account_id)
threads_publisher_status()
threads_fetch_insights(participant)

# System
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

## Analytics Dashboard (Superset)

Apache Superset 4.1.1 at **http://localhost:8088** — login `admin` / `admin`

| Chart | Type | Dataset |
|---|---|---|
| Views by account | Line | account_insights |
| Follower growth | Line | account_insights |
| Engagement by account | Bar | account_insights |
| Posts published per day | Bar | posts |
| Top posts by views | Table | post_insights |
| Post status distribution | Pie | posts |

---

## Infrastructure

**VPS:** `root@23.26.0.184`
**Deployment:** GitHub Actions auto-deploys `threads_api` on every push to `main`.

**Add a new participant** — add 2 lines to `docker-compose.yml`:
```yaml
- ./NewGuy:/app/participants/newguy:ro
- ./NewGuy/data:/app/data/newguy
```
`registry.py` auto-discovers any subfolder with a `.env` at startup.

Container naming: `{participant}_publisher`, `{participant}_scheduler`

---

## Environment Variables

**Per-participant `.env`:**
```env
META_APP_ID=
META_APP_SECRET=
ACCOUNT_N_ID=
ACCOUNT_N_USER_ID=
ACCOUNT_N_THREADS_TOKEN=     # 60-day long-lived token
CEREBRAS_API_KEY=
HF_TOKEN=                    # HuggingFace token for chat/optimize
SUPERSET_SECRET_KEY=
```

---

## Key Commands

```bash
# Generate posts for one account
cd Budimir && python generate_posts.py --account event_parsing --count 30

# Force-publish one post (no time window)
python test_publish.py

# Collect insights manually
python fetch_insights.py

# Refresh tokens
python refresh_tokens.py

# Start all services (from project root)
docker compose up -d

# SSH tunnel for local MCP access
ssh -L 7843:localhost:7843 root@23.26.0.184 -N -f

# Verify API
curl http://localhost:7843/system/health

# Deploy threads_api manually on VPS
cd /root/threads_poster && docker compose up -d --build threads_api

# Recreate Superset charts and dashboard
python superset/create_charts.py

# Re-link charts to dashboard via ORM (if detached)
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

---

## Meta App

- **App ID:** 1509405377206199
- **Redirect URI:** `https://localhost/callback`
- **Scopes:** `threads_basic`, `threads_content_publish`, `threads_delete`, `threads_keyword_search`, `threads_location_tagging`, `threads_manage_insights`, `threads_manage_mentions`, `threads_manage_replies`, `threads_profile_discovery`, `threads_read_replies`, `threads_share_to_instagram`

---

## License

MIT
