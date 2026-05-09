import os
import httpx
from mcp.server.fastmcp import FastMCP

mcp  = FastMCP("threads")
BASE = os.getenv("THREADS_API_BASE", "http://localhost:7843")


def _get(path: str, timeout: int = 30, **params) -> dict:
    r = httpx.get(f"{BASE}{path}", params={k: v for k, v in params.items() if v is not None}, timeout=timeout)
    r.raise_for_status()
    return r.json()


def _post(path: str, timeout: int = 30, **body) -> dict:
    r = httpx.post(f"{BASE}{path}", json={k: v for k, v in body.items() if v is not None}, timeout=timeout)
    r.raise_for_status()
    return r.json()


def _delete(path: str, **params) -> dict:
    r = httpx.delete(f"{BASE}{path}", params={k: v for k, v in params.items() if v is not None}, timeout=30)
    r.raise_for_status()
    return r.json()


def _patch(path: str, **params) -> dict:
    r = httpx.patch(f"{BASE}{path}", params={k: v for k, v in params.items() if v is not None}, timeout=30)
    r.raise_for_status()
    return r.json()


# ── Аналитика ─────────────────────────────────────────────────────────────────

@mcp.tool()
def threads_top_posts(limit: int = 10, days: int = 30, participant: str | None = None) -> dict:
    """Топ постов по просмотрам из analytics.duckdb. participant: budimir/slava/tanya или не указывать для всех."""
    return _get("/analytics/top-posts", limit=limit, days=days, participant=participant)


@mcp.tool()
def threads_follower_growth(account_id: str, days: int = 30) -> dict:
    """Динамика фолловеров аккаунта по дням."""
    return _get("/analytics/followers", account_id=account_id, days=days)


@mcp.tool()
def threads_account_stats(account_id: str, days: int = 7) -> dict:
    """Сводная статистика аккаунта: просмотры, лайки, репосты, replies, quotes за период."""
    return _get("/analytics/account-stats", account_id=account_id, days=days)


@mcp.tool()
def threads_cross_account_compare(days: int = 7) -> dict:
    """Сравнение всех аккаунтов по метрикам за период."""
    return _get("/analytics/compare", days=days)


@mcp.tool()
def threads_queue_stats() -> dict:
    """Количество постов по статусам (pending/posted/failed) для каждого аккаунта."""
    return _get("/analytics/queue-stats")


# ── Контент ───────────────────────────────────────────────────────────────────

@mcp.tool()
def threads_list_queue(account_id: str, limit: int = 20) -> dict:
    """Список pending постов в очереди для аккаунта."""
    return _get("/content/queue", account_id=account_id, limit=limit)


@mcp.tool()
def threads_generate_posts(account_id: str, count: int = 30) -> dict:
    """Запустить генерацию постов через Cerebras (асинхронно, не блокирует)."""
    return _post("/content/generate", account_id=account_id, count=count)


@mcp.tool()
def threads_add_post(account_id: str, content: str) -> dict:
    """Добавить пост вручную в очередь (status=pending)."""
    return _post("/content/add", account_id=account_id, content=content)


@mcp.tool()
def threads_delete_post(account_id: str, post_id: int) -> dict:
    """Удалить pending пост из очереди по ID."""
    return _delete(f"/content/post/{post_id}", account_id=account_id)


@mcp.tool()
def threads_skip_post(account_id: str, post_id: int) -> dict:
    """Пометить pending пост как skipped (не удаляет, publisher пропустит)."""
    return _patch(f"/content/post/{post_id}/skip", account_id=account_id)


# ── Публикация ────────────────────────────────────────────────────────────────

@mcp.tool()
def threads_force_publish(account_id: str) -> dict:
    """Форс-публикация одного поста прямо сейчас (без окна 9-21). Синхронный, таймаут 60с."""
    return _post("/publishing/force", timeout=65, account_id=account_id)


@mcp.tool()
def threads_publisher_status() -> dict:
    """Статус контейнеров threads_publisher и threads_scheduler."""
    return _get("/publishing/status")


@mcp.tool()
def threads_fetch_insights(participant: str = "budimir") -> dict:
    """Запустить сбор метрик из Threads Insights API прямо сейчас. Синхронный, таймаут 120с."""
    return _post("/publishing/fetch-insights", timeout=125, participant=participant)


# ── Система ───────────────────────────────────────────────────────────────────

@mcp.tool()
def threads_health() -> dict:
    """Пинг API. Проверить что threads_api доступен."""
    return _get("/system/health")


@mcp.tool()
def threads_token_expiry() -> dict:
    """Проверить валидность Threads-токенов для всех аккаунтов (токены живут 60 дней)."""
    return _get("/system/token-expiry")


@mcp.tool()
def threads_refresh_tokens(participant: str = "budimir") -> dict:
    """Обновить Threads-токены через API и записать новые в .env. Синхронный, таймаут 30с."""
    return _post("/system/refresh-tokens", timeout=35, participant=participant)


@mcp.tool()
def threads_logs(container: str, lines: int = 50) -> dict:
    """Docker logs контейнера. container: threads_publisher|threads_scheduler|threads_api|threads_superset|threads_merger."""
    return _get("/system/logs", container=container, lines=lines)


@mcp.tool()
def threads_list_accounts() -> dict:
    """Список всех аккаунтов с account_id, participant и user_id."""
    return _get("/system/accounts")


# ── Оптимизация промптов ──────────────────────────────────────────────────────

@mcp.tool()
def threads_analyze_prompts(account_id: str, metric: str = "weighted") -> dict:
    """Анализ топ/худших постов и предложение улучшений промптов через Claude. metric: 'weighted' (views×0.4 + engagement×0.6) или 'rate' (engagement/views)."""
    return _get("/optimize/analyze/" + account_id, metric=metric)


@mcp.tool()
def threads_apply_prompts(account_id: str, new_formats: dict | None = None, new_system: str | None = None) -> dict:
    """Применить предложенные изменения промптов к prompts.py. new_formats — dict format_name→text, new_system — строка или None."""
    return _post("/optimize/apply/" + account_id, new_formats=new_formats, new_system=new_system)


# ── Superset ──────────────────────────────────────────────────────────────────

@mcp.tool()
def threads_superset_status() -> dict:
    """Статус контейнеров Superset-стека: superset, merger, redis."""
    return _get("/superset/status")


@mcp.tool()
def threads_merger_run() -> dict:
    """Форс-запуск merger.py прямо сейчас (в норме запускается в 07:45). Обновляет analytics.duckdb."""
    return _post("/superset/merger-run", timeout=60)


@mcp.tool()
def threads_superset_rebuild() -> dict:
    """Пересоздать все чарты и дашборд в Superset через REST API."""
    return _post("/superset/rebuild", timeout=60)


# ── Комментарии ───────────────────────────────────────────────────────────────

@mcp.tool()
def threads_fetch_replies(account_id: str, days: int = 7) -> dict:
    """Скачать новые комментарии к постам аккаунта из Threads API и сохранить в reply_log."""
    return _get(f"/replies/fetch/{account_id}", timeout=120, days=days)


@mcp.tool()
def threads_replies_sentiment(account_id: str, days: int = 30) -> dict:
    """Анализ тональности комментариев аккаунта за период (positive/negative/question/neutral) через Cerebras."""
    return _get(f"/replies/sentiment/{account_id}", timeout=120, days=days)


@mcp.tool()
def threads_auto_reply(account_id: str) -> dict:
    """Сгенерировать и опубликовать ответы на все неотвеченные комментарии через Cerebras. Полный автопилот."""
    return _post(f"/replies/auto-reply/{account_id}", timeout=300)


if __name__ == "__main__":
    mcp.run()
