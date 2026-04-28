# Project Notes — threads_poster

## Architecture

```
[Groq LLM] ← generate_posts.py (manually or docker-compose --profile tools)
                ↓
           posts.csv (status: pending)
                ↓
publisher.py (every 29 minutes)
                ↓
           Threads API → published posts
                ↓
posts.csv (status: posted) → archive.csv
```

**Key files:**
- `generate_posts.py` — generates 50 posts via Groq API (llama-3.3-70b), 8 formats
- `publisher.py` — reads posts.csv and publishes the first pending post to Threads
- `posts.csv` — post queue (`content`, `format`, `status`, `created_at`)
- `archive.csv` — archive of published posts (deduplication)
- `Dockerfile` + `docker-compose.yml` — two services: publisher (always on) and generator (on demand)

**Environment variables (`.env`):**
- `GROQ_API_KEY` — for generate_posts.py
- `THREADS_ACCESS_TOKEN` — for publisher.py
- `THREADS_USER_ID` — for publisher.py

---

## Issues Found

- [x] `groq` missing from `requirements.txt` — fixed
- [x] `norse` format — outdated, removed (new architecture without it)
- [x] `NEWS_POST_SHARE = 0.01` — removed, format logic reworked
- [x] `duckdb` missing from `requirements.txt` — fixed

---

## Changes (2026-04-28)

### What Was Done

**Architecture reworked:**
- `publisher.py` — replaced with a multi-threaded publisher (6 accounts, DuckDB, smart scheduling)
- `generate_posts.py` — rewritten from scratch: real post generator via Groq API
- `prompts.py` — new file, prompt config separated per account
- `refresh_tokens.py` — new file, Threads token refresh (run once a month)
- `requirements.txt` — removed `pandas`, `schedule`; added `duckdb`, `groq`
- `Dockerfile` — removed legacy CSV, added `tzdata` and `mkdir -p data`
- `docker-compose.yml` — added `env_file`, volume `threads_data`, service `threads_refresher`
- `.env` — migrated to `ACCOUNT_N_*` format

**Key decisions:**
- Groq tokens — separate per account (`ACCOUNT_N_GROQ_TOKEN`)
- Threads token — one shared `THREADS_TOKEN` for now (experiments); add `ACCOUNT_N_THREADS_TOKEN` when moving to production
- Prompts — in `prompts.py`, dict `account_id → {system, formats}`, each account has its own topic
- DB — DuckDB, file `data/data.duckdb`, table `posts` (id, account_id, content, status, created_at, posted_at, threads_post_id)
- Schedule — posting window 9:00–21:00 Belgrade time, interval 10–40 min (random), 5% skip chance

### Current Status

- [ ] Get `USER_ID` and `THREADS_TOKEN` for all 6 accounts ✅ Done (2026-04-28)
- [ ] Fill in `ACCOUNT_2..6_*` in `.env` ✅ Done (2026-04-28)
- [ ] Fill in topics for accounts 2–6 in `prompts.py` — in progress
- [ ] Test generation: `docker-compose --profile tools run --rm threads_generator --account event_parsing`
- [ ] Test publishing

### Accounts (testers in Threads poster app)

| # | account_id | Threads profile | USER_ID | Status |
|---|---|---|---|---|
| 1 | event_parsing | event_parsing | 26528771100143116 | ✅ token ready |
| 2 | budeschka | budeschka | 35121164990863983 | ✅ token ready |
| 3 | cycling_superhero | cycling_superhero | 26887077647646890 | ✅ token ready |
| 4 | claude_space | claude_space | 26666671099619981 | ✅ token ready |
| 5 | aire.porteno | aire.porteno | 26699742642998871 | ✅ token ready |
| 6 | mind_the_tap | mind_the_tap | 36298180553102299 | ✅ token ready |
