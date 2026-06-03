import os
from fastapi import APIRouter, Query, HTTPException
from db import query_data, query_analytics
from registry import PARTICIPANTS, REGISTRY, build_registry

router = APIRouter()


@router.get("/top-posts")
def top_posts(
    limit: int = Query(10, ge=1, le=100),
    days: int = Query(30, ge=1),
    participant: str | None = None,
):
    where = f"p.status = 'posted' AND p.posted_at >= (CURRENT_TIMESTAMP - INTERVAL '{days}' DAY)"
    params: list = []
    if participant:
        where += " AND p.participant = ?"
        params.append(participant)

    rows = query_analytics(
        f"""
        SELECT p.account_id, p.participant, LEFT(p.content, 300) AS content,
               MAX(pi.views)   AS views,
               MAX(pi.likes)   AS likes,
               MAX(pi.replies) AS replies,
               MAX(pi.reposts) AS reposts,
               MAX(pi.quotes)  AS quotes
        FROM posts p
        JOIN post_insights pi ON pi.post_id = p.id AND pi.participant = p.participant
        WHERE {where}
        GROUP BY p.id, p.account_id, p.participant, p.content
        ORDER BY views DESC
        LIMIT {limit}
        """,
        params or None,
    )
    keys = ("account_id", "participant", "content", "views", "likes", "replies", "reposts", "quotes")
    return {"ok": True, "data": [dict(zip(keys, r)) for r in rows]}


@router.get("/followers")
def followers(
    account_id: str = Query(...),
    days: int = Query(30, ge=1),
):
    rows = query_analytics(
        f"""
        SELECT date, followers_count
        FROM account_insights
        WHERE account_id = ?
          AND date >= (CURRENT_DATE - INTERVAL '{days}' DAY)
        ORDER BY date ASC
        """,
        [account_id],
    )
    return {"ok": True, "data": [{"date": str(r[0]), "followers_count": r[1]} for r in rows]}


@router.get("/account-stats")
def account_stats(
    account_id: str = Query(...),
    days: int = Query(7, ge=1),
):
    rows = query_analytics(
        f"""
        WITH account AS (
            SELECT COALESCE(SUM(views), 0) AS views,
                   MAX(followers_count)    AS followers_count,
                   COUNT(*)                AS days_with_data
            FROM account_insights
            WHERE account_id = ?
              AND date >= (CURRENT_DATE - INTERVAL '{days}' DAY)
        ),
        post_engagement AS (
            SELECT COALESCE(SUM(best.likes),   0) AS likes,
                   COALESCE(SUM(best.replies), 0) AS replies,
                   COALESCE(SUM(best.reposts), 0) AS reposts,
                   COALESCE(SUM(best.quotes),  0) AS quotes
            FROM (
                SELECT MAX(pi.likes)   AS likes,
                       MAX(pi.replies) AS replies,
                       MAX(pi.reposts) AS reposts,
                       MAX(pi.quotes)  AS quotes
                FROM posts p
                JOIN post_insights pi ON pi.post_id = p.id AND pi.participant = p.participant
                WHERE p.account_id = ?
                  AND p.posted_at >= (CURRENT_TIMESTAMP - INTERVAL '{days}' DAY)
                GROUP BY p.id
            ) best
        )
        SELECT a.views, pe.likes, pe.replies, pe.reposts, pe.quotes,
               a.followers_count, a.days_with_data
        FROM account a, post_engagement pe
        """,
        [account_id, account_id],
    )
    if not rows or rows[0][6] == 0:
        raise HTTPException(404, f"No data for account '{account_id}'")
    r = rows[0]
    keys = ("views", "likes", "replies", "reposts", "quotes", "followers_count", "days_with_data")
    return {"ok": True, "data": {"account_id": account_id, **dict(zip(keys, r))}}


@router.get("/compare")
def compare(days: int = Query(7, ge=1)):
    rows = query_analytics(
        f"""
        SELECT account_id, participant,
               SUM(views), SUM(likes), SUM(replies), SUM(reposts), SUM(quotes),
               MAX(followers_count)
        FROM account_insights
        WHERE date >= (CURRENT_DATE - INTERVAL '{days}' DAY)
        GROUP BY account_id, participant
        ORDER BY SUM(views) DESC
        """,
    )
    keys = ("account_id", "participant", "views", "likes", "replies", "reposts", "quotes", "followers_count")
    return {"ok": True, "data": [dict(zip(keys, r)) for r in rows]}


@router.get("/landing-stats")
def landing_stats():
    active_ids = list(REGISTRY.keys()) or list(build_registry().keys())
    id_filter = (
        f"AND account_id IN ({','.join(repr(x) for x in active_ids)})"
        if active_ids else ""
    )
    acc_rows = query_analytics(f"""
        SELECT
            account_id,
            participant,
            COALESCE(SUM(views),   0)                   AS views_30d,
            COALESCE(SUM(replies), 0)                   AS replies_30d,
            MAX(followers_count) - MIN(followers_count) AS followers_delta,
            MAX(followers_count)                        AS followers_current
        FROM account_insights
        WHERE date >= CURRENT_DATE - INTERVAL '30' DAY
          {id_filter}
        GROUP BY account_id, participant
        ORDER BY SUM(views) DESC
    """)
    posts_row = query_analytics("""
        SELECT COUNT(*) FROM posts
        WHERE status = 'posted'
          AND posted_at >= CURRENT_TIMESTAMP - INTERVAL '30' DAY
    """)

    total_views = 0
    total_replies = 0
    total_followers_delta = 0
    operators: set[str] = set()
    participant_views: dict[str, int] = {}
    accounts = []

    for r in acc_rows:
        acc_id, participant = r[0], r[1]
        views, replies, delta, current = int(r[2]), int(r[3]), int(r[4]), int(r[5])
        total_views += views
        total_replies += replies
        total_followers_delta += delta
        operators.add(participant)
        participant_views[participant] = participant_views.get(participant, 0) + views
        accounts.append({
            "account_id": acc_id,
            "participant": participant,
            "views_30d": views,
            "replies_30d": replies,
            "followers_delta_30d": delta,
            "followers_count": current,
        })

    return {
        "ok": True,
        "data": {
            "summary": {
                "views_30d": total_views,
                "posts_30d": int(posts_row[0][0]) if posts_row else 0,
                "replies_30d": total_replies,
                "followers_delta_30d": total_followers_delta,
                "accounts_count": len(accounts),
                "operators_count": len(operators),
            },
            "accounts": accounts,
            "participant_views": participant_views,
        },
    }


@router.get("/queue-stats")
def queue_stats():
    result: dict[str, dict] = {}
    for participant, config in PARTICIPANTS.items():
        db_path = config["db_path"]
        if not os.path.exists(db_path):
            continue
        rows = query_data(
            "SELECT account_id, status, COUNT(*) FROM posts GROUP BY account_id, status ORDER BY account_id, status",
            db_path=db_path,
        )
        for account_id, status, count in rows:
            if account_id not in result:
                result[account_id] = {"participant": participant}
            result[account_id][status] = count
    return {"ok": True, "data": result}
