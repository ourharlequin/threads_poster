# Workers

Dynamic per-tenant background tasks (replace Docker containers per participant).

- scheduler.py   — generates posts on configured schedule, reads from PostgreSQL
- publisher.py   — picks approved posts, publishes via Threads API, writes insights
- refresher.py   — refreshes Threads tokens every 55 days
