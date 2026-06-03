# THREADY v2 — SaaS Architecture Plan

> Autonomous posting infrastructure for Threads — multi-tenant SaaS

---

## Vision

Move from a folder-per-participant system to a proper multi-tenant SaaS platform.
First customers: Budimir, Slava, Tanya, Chiara.
Target: any agency or creator can register, connect their Threads accounts, and run.

---

## Tech Stack

| Layer | Technology | Notes |
|-------|-----------|-------|
| Backend | FastAPI | keep existing, extend |
| Database | PostgreSQL | replaces .env + DuckDB per participant |
| Analytics | DuckDB | keep, add tenant_id |
| Auth | authlib + JWT | email/password + Google + GitHub |
| Frontend | Jinja2 + HTMX | no SPA, server-rendered |
| Workers | Python (asyncio) | scheduler + publisher per tenant |
| Queue | PostgreSQL (pg_notify) | replaces file-based queue |
| Cache | Redis | sessions, rate limiting |
| Infra | Docker Compose | same VPS, extend existing |

---

## Architecture Overview

```
Browser
  └── thready.digital
        ├── / landing (public)
        ├── /auth/*         → Auth routes (login, register, OAuth callbacks)
        ├── /dashboard/*    → Personal cabinet (requires login)
        │     ├── accounts  → Manage Threads accounts
        │     ├── queue     → Post queue + approval
        │     ├── analytics → Per-account stats
        │     ├── prompts   → Prompt editor
        │     └── knowledge → Archived accounts + learnings
        └── /api/*          → Internal API (workers use this)

Workers (per tenant, dynamic)
  ├── scheduler   → generates posts, puts in queue
  └── publisher   → publishes approved/auto posts via Threads API
```

---

## Database Schema (PostgreSQL)

### users
```sql
id          UUID PRIMARY KEY
email       TEXT UNIQUE
name        TEXT
avatar_url  TEXT
created_at  TIMESTAMPTZ
```

### oauth_accounts (Google / GitHub login)
```sql
id              UUID PRIMARY KEY
user_id         UUID → users
provider        TEXT  -- 'google' | 'github'
provider_uid    TEXT
access_token    TEXT
created_at      TIMESTAMPTZ
UNIQUE (provider, provider_uid)
```

### sessions
```sql
id          UUID PRIMARY KEY
user_id     UUID → users
token_hash  TEXT UNIQUE
expires_at  TIMESTAMPTZ
created_at  TIMESTAMPTZ
```

### threads_accounts
```sql
id              UUID PRIMARY KEY
user_id         UUID → users
account_id      TEXT UNIQUE      -- handle, e.g. "mind_the_tap"
user_id_threads TEXT             -- Threads numeric user_id
threads_token   TEXT             -- long-lived token (encrypted)
token_expires_at TIMESTAMPTZ
status          TEXT DEFAULT 'active'  -- active | archived | deleted
language        TEXT             -- EN | RU | ES | PT
niche           TEXT
description     TEXT
created_at      TIMESTAMPTZ
archived_at     TIMESTAMPTZ
```

### account_snapshots (on archive — final stats)
```sql
id              UUID PRIMARY KEY
account_id      UUID → threads_accounts
snapshot_date   DATE
views_total     BIGINT
followers_final INT
followers_delta INT
posts_total     INT
avg_views_post  INT
top_topics      JSONB            -- ["cycling", "london", ...]
best_time_utc   INT              -- hour 0-23
engagement_rate FLOAT
notes           TEXT
```

### prompts
```sql
id          UUID PRIMARY KEY
account_id  UUID → threads_accounts
version     INT
content     TEXT
is_active   BOOL DEFAULT true
created_at  TIMESTAMPTZ
updated_at  TIMESTAMPTZ
```

### posts
```sql
id              UUID PRIMARY KEY
account_id      UUID → threads_accounts
content         TEXT
status          TEXT  -- draft | pending_approval | approved | posted | rejected | failed
threads_post_id TEXT
scheduled_at    TIMESTAMPTZ
posted_at       TIMESTAMPTZ
created_at      TIMESTAMPTZ
generation_meta JSONB   -- model, prompt_version, topics used
```

### post_insights
```sql
id          UUID PRIMARY KEY
post_id     UUID → posts
fetched_at  TIMESTAMPTZ
views       INT
likes       INT
replies     INT
reposts     INT
quotes      INT
```

### account_insights (daily rollup)
```sql
id              UUID PRIMARY KEY
account_id      UUID → threads_accounts
date            DATE
views           INT
likes           INT
replies         INT
reposts         INT
quotes          INT
followers_count INT
UNIQUE (account_id, date)
```

### knowledge_entries (learnings from archived accounts)
```sql
id              UUID PRIMARY KEY
user_id         UUID → users
source_account  UUID → threads_accounts  -- nullable (account that generated this)
language        TEXT
niche           TEXT
tags            TEXT[]
title           TEXT
body            TEXT                     -- the actual learning
confidence      FLOAT                    -- 0.0–1.0, auto-calculated
created_at      TIMESTAMPTZ
```

---

## Auth Flows

### Email / Password
```
POST /auth/register  { email, password, name }
POST /auth/login     { email, password }        → JWT token (httpOnly cookie)
POST /auth/logout
POST /auth/reset-password
```

### Google OAuth
```
GET  /auth/google           → redirect to Google
GET  /auth/google/callback  → exchange code → create/find user → session
```

### GitHub OAuth
```
GET  /auth/github           → redirect to GitHub
GET  /auth/github/callback  → exchange code → create/find user → session
```

---

## Threads Account OAuth (Meta API)

Replaces the manual `get_tokens.py` script.

```
Dashboard → "Add Threads Account"
  ↓
GET /accounts/threads/connect
  ↓ redirect to:
https://threads.net/oauth/authorize
  ?client_id={META_APP_ID}
  &redirect_uri=https://thready.digital/accounts/threads/callback
  &scope=threads_basic,threads_content_publish,...
  &response_type=code
  &state={signed_csrf_token}
  ↓
User authorizes in Threads
  ↓
GET /accounts/threads/callback?code=...&state=...
  → verify state (CSRF)
  → exchange code → short-lived token → long-lived token (60 days)
  → GET /me → account_id + user_id
  → save to threads_accounts table
  ↓
Redirect to dashboard/accounts ✓
```

**Meta App Console:** add `https://thready.digital/accounts/threads/callback`
to allowed redirect URIs alongside existing `https://localhost/callback`.

Token refresh: background job runs every 55 days,
calls `POST /auth/refresh-tokens` for all active accounts.

---

## Account Lifecycle

```
connect → active → archived → (deleted after 90 days)
```

### On Archive
1. Stop scheduler + publisher for this account
2. Fetch final stats from Threads API
3. Write `account_snapshots` record
4. Run LLM analysis on top 20 posts → extract:
   - best performing topics
   - optimal posting time
   - tone/style patterns
5. Write `knowledge_entries` linked to this account's niche + language
6. Set `status = 'archived'`

### In Analytics
- Archived accounts shown in separate "Archive" section
- All historical data preserved (never deleted)
- Contribute to knowledge base queries

### In landing-stats endpoint
- `accounts_count` = only `status = 'active'` accounts
- Filter: `WHERE status = 'active'` instead of REGISTRY hack

---

## Knowledge Base

When a new account is created with niche X + language Y:
- System queries `knowledge_entries` for matching niche/language
- Relevant learnings shown in dashboard: "For EN cycling accounts, morning posts (7-9 UTC) average 2.3× more views"
- LLM prompt for new account is pre-seeded with relevant knowledge

Knowledge entries are also editable by the user — they can add manual notes,
flag entries as outdated, etc.

---

## Migration Plan (v1 → v2)

### Phase 0: Parallel run
- v2 runs on same VPS, different port
- v1 keeps running uninterrupted
- Budimir/Slava/Tanya/Chiara register in v2 first

### Phase 1: Foundation (2 weeks)
- [ ] PostgreSQL setup + schema
- [ ] Auth: email/password + Google + GitHub
- [ ] Basic dashboard skeleton (Jinja2 + HTMX)
- [ ] Session management

### Phase 2: Threads OAuth (1 week)
- [ ] Meta OAuth callback endpoint
- [ ] Token storage (encrypted) in PostgreSQL
- [ ] Token refresh job
- [ ] Account management UI

### Phase 3: Migrate existing accounts (1 week)
- [ ] Script: import Budimir/Slava/Tanya/Chiara accounts from .env → PostgreSQL
- [ ] Migrate prompts
- [ ] Migrate post history from DuckDB → PostgreSQL

### Phase 4: Workers (2 weeks)
- [ ] Scheduler reads config from PostgreSQL (not .env)
- [ ] Publisher reads tokens from PostgreSQL
- [ ] Post queue UI with approval flow
- [ ] Per-tenant scheduler config (times, cadence)

### Phase 5: Analytics & Knowledge (1 week)
- [ ] Analytics dashboard per tenant (port existing queries)
- [ ] Account archive flow + snapshot
- [ ] LLM analysis on archive → knowledge entries
- [ ] Knowledge base UI

### Phase 6: SaaS features (ongoing)
- [ ] Invite system
- [ ] Pricing tiers
- [ ] Billing (Stripe)
- [ ] White-label reports

---

## Key Files from v1 to Reference

| v1 file | Purpose | v2 equivalent |
|---------|---------|---------------|
| `Budimir/get_tokens.py` | Threads OAuth flow | `/accounts/threads/callback` endpoint |
| `threads_api/routers/analytics.py` | Analytics queries | port to PostgreSQL schema |
| `threads_api/routers/landing.py` | Landing page | keep as-is, update stats endpoint |
| `threads_api/registry.py` | Account registry | `threads_accounts` table |
| `Budimir/prompts.py` | Prompt templates | `prompts` table + editor UI |
| `Budimir/generate_posts.py` | Post generation | `services/post_generator.py` |
| `Budimir/publish_post.py` | Threads API publish | `workers/publisher.py` |
| `superset/` | Analytics dashboards | internal analytics UI |

---

## Open Questions

- [ ] Encryption for stored Threads tokens (KMS vs app-level AES)
- [ ] Multi-account per user: one user can have multiple Threads accounts ✓
- [ ] Team accounts: multiple users sharing one set of accounts (agency use-case)?
- [ ] Self-hosted vs managed PostgreSQL (current VPS vs Supabase/RDS)
- [ ] Pricing model: per account? per view? flat fee?
