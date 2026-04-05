# Threads Auto-Poster

Automated content generation and publishing bot for Meta Threads. Uses the Groq API (LLaMA 3.3 70B) to generate posts and the Threads API to publish them on a schedule — all running in Docker.

---

## How It Works

1. **`generate_posts.py`** calls the Groq API to generate posts in multiple formats (facts, cases, tips, myths, opinions) and saves them to `posts.csv` with `status: pending`.
2. **`publisher.py`** reads `posts.csv` every N minutes, picks the next pending post, publishes it to Threads via the Meta Graph API, and marks it as `posted`.
3. Published posts are archived to `archive.csv` on the next generator run to prevent duplicates.

---

## Project Structure

```
threads_poster/
├── generate_posts.py     # AI post generator (Groq API)
├── publisher.py          # Scheduler + Threads publisher
├── posts.csv             # Post queue (auto-created)
├── archive.csv           # Published posts archive (auto-created)
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env                  # Your secrets (never commit this)
```

---

## Prerequisites

- [Docker](https://www.docker.com/) & Docker Compose
- A [Groq](https://console.groq.com/home) account
- A Meta developer app with Threads API access

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-username/threads-poster.git
cd threads-poster
```

### 2. Create your `.env` file

Copy the example and fill in your credentials:

```bash
cp _env .env
```

Open `.env` and add your tokens:

```env
GROQ_API_KEY=
THREADS_ACCESS_TOKEN=
THREADS_USER_ID=
```

---

## Getting Your API Tokens

### GROQ_API_KEY

Generate your free API key at [console.groq.com](https://console.groq.com/home).

---

### THREADS_ACCESS_TOKEN and THREADS_USER_ID

You need a **60-day long-lived Threads token**. Follow these steps:

> **Video walkthrough:** [YouTube tutorial](https://www.youtube.com/watch?v=juGzoj_x7CU&t=1080s) (timestamps 0:03 – 0:17)
> **Official docs:** [developers.facebook.com/docs/threads/get-started](https://developers.facebook.com/docs/threads/get-started)

**Step 1 — Authorize your app and get a short-lived code**

Open this URL in your browser. Replace `YOUR_THREADS_ID` with your Meta app's client ID:

```
https://threads.net/oauth/authorize?client_id=YOUR_THREADS_ID&redirect_uri=https://www.integromat.com/oauth/cb/oauth2&scope=threads_basic,threads_content_publish,threads_keyword_search,threads_manage_insights,threads_manage_mentions,threads_manage_replies,threads_read_replies&response_type=code
```

After authorization, you'll be redirected. Copy the `code` value from the redirect URL.

**Step 2 — Exchange the code for a short-lived access token**

```
https://graph.threads.net/oauth/access_token?client_id=YOUR_THREADS_ID&client_secret=YOUR_SECRET_KEY&redirect_uri=https://www.integromat.com/oauth/cb/oauth2&grant_type=authorization_code&code=YOUR_TOKEN
```

Replace `YOUR_THREADS_ID`, `YOUR_SECRET_KEY`, and `YOUR_TOKEN` with your values. The response will contain a short-lived `access_token` and your `user_id` — save both.

**Step 3 — Exchange for a 60-day long-lived token**

```
https://graph.threads.net/access_token?grant_type=th_exchange_token&client_secret=YOUR_SECRET_KEY&access_token=YOUR_TOKEN
```

Replace `YOUR_SECRET_KEY` and `YOUR_TOKEN`. The response contains your long-lived `access_token`. Paste this into your `.env` as `THREADS_ACCESS_TOKEN`, and the `user_id` from Step 2 as `THREADS_USER_ID`.

---

## Configuration

### Customize post formats

Open `generate_posts.py` and edit the `FORMATS` list. Each format has:

- `name` — internal label
- `count` — how many posts of this type to generate per run
- `prompt` — the instruction sent to the AI

Add, remove, or modify formats to match your content strategy.

### Set the publishing interval

Open `publisher.py` and find this line:

```python
schedule.every(29).minutes.do(publish_text_thread)
```

Change `29` to however many minutes you want between posts. For example, `60` for hourly posting.

---

## Running with Docker

```bash
# 1. Build the Docker image
docker-compose build

# 2. Generate posts (fills posts.csv with ~50 AI-written posts)
docker-compose run --rm threads_generator

# 3. Start the publisher (runs continuously, posts on schedule)
docker-compose up -d threads_publisher
```

To check publisher logs:

```bash
docker logs -f threads_publisher
```

To stop:

```bash
docker-compose down
```

---

## Workflow Summary

```
docker-compose run --rm threads_generator
        ↓
  posts.csv filled with pending posts
        ↓
docker-compose up -d threads_publisher
        ↓
  posts published every N minutes to Threads
        ↓
  run generator again when queue runs low
```

---

## Notes

- The generator automatically archives `posted` entries to `archive.csv` before each new run and uses them to prevent duplicate content.
- If a post fails to publish (API error), it is marked `failed` and skipped on subsequent runs.
- The `threads_generator` service uses the `tools` Docker Compose profile, meaning it only runs when called explicitly with `docker-compose run`.
- Never commit your `.env` file — it's listed in `.gitignore` by default.

---

## License

MIT
