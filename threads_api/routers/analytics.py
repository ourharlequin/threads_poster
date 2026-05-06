import os
from fastapi import APIRouter, Query, HTTPException
from db import query_data, query_analytics
from registry import PARTICIPANTS

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
        SELECT SUM(views), SUM(likes), SUM(replies), SUM(reposts), SUM(quotes),
               MAX(followers_count), COUNT(*)
        FROM account_insights
        WHERE account_id = ?
          AND date >= (CURRENT_DATE - INTERVAL '{days}' DAY)
        """,
        [account_id],
    )
    if not rows or rows[0][0] is None:
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
