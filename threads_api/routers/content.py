from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from db import query_data, write_data
from registry import REGISTRY
from subprocess_runner import run_async

router = APIRouter()


def _require_account(account_id: str) -> dict:
    if account_id not in REGISTRY:
        raise HTTPException(404, f"Unknown account_id: '{account_id}'")
    return REGISTRY[account_id]


class GenerateRequest(BaseModel):
    account_id: str
    count: int = 30


class AddPostRequest(BaseModel):
    account_id: str
    content: str


@router.get("/queue")
def list_queue(
    account_id: str = Query(...),
    limit: int = Query(20, ge=1, le=100),
):
    acc = _require_account(account_id)
    rows = query_data(
        f"""
        SELECT id, account_id, LEFT(content, 300) AS content, created_at
        FROM posts
        WHERE account_id = ? AND status = 'pending'
        ORDER BY created_at ASC
        LIMIT {limit}
        """,
        [account_id],
        db_path=acc["db_path"],
    )
    keys = ("id", "account_id", "content", "created_at")
    return {"ok": True, "data": [dict(zip(keys, r)) for r in rows]}


@router.post("/generate")
async def generate_posts(req: GenerateRequest):
    acc = _require_account(req.account_id)
    await run_async(
        "generate_posts.py",
        acc["scripts_dir"],
        acc["db_path"],
        ["--account", req.account_id, "--count", str(req.count)],
    )
    return {"ok": True, "data": {"message": f"Generation started for '{req.account_id}' ({req.count} posts)"}}


@router.post("/add")
async def add_post(req: AddPostRequest):
    acc = _require_account(req.account_id)
    if not req.content.strip():
        raise HTTPException(400, "content cannot be empty")
    await write_data(
        "INSERT INTO posts (account_id, content, status, created_at) VALUES (?, ?, 'pending', now())",
        [req.account_id, req.content.strip()],
        db_path=acc["db_path"],
    )
    return {"ok": True, "data": {"message": f"Post added to queue for '{req.account_id}'"}}


@router.delete("/post/{post_id}")
async def delete_post(post_id: int, account_id: str = Query(...)):
    acc = _require_account(account_id)
    rows = query_data(
        "SELECT id FROM posts WHERE id = ? AND account_id = ? AND status = 'pending'",
        [post_id, account_id],
        db_path=acc["db_path"],
    )
    if not rows:
        raise HTTPException(404, f"Pending post {post_id} not found for '{account_id}'")
    await write_data(
        "DELETE FROM posts WHERE id = ? AND account_id = ? AND status = 'pending'",
        [post_id, account_id],
        db_path=acc["db_path"],
    )
    return {"ok": True, "data": {"deleted": post_id}}


@router.patch("/post/{post_id}/skip")
async def skip_post(post_id: int, account_id: str = Query(...)):
    acc = _require_account(account_id)
    rows = query_data(
        "SELECT id FROM posts WHERE id = ? AND account_id = ? AND status = 'pending'",
        [post_id, account_id],
        db_path=acc["db_path"],
    )
    if not rows:
        raise HTTPException(404, f"Pending post {post_id} not found for '{account_id}'")
    await write_data(
        "UPDATE posts SET status = 'skipped' WHERE id = ? AND account_id = ?",
        [post_id, account_id],
        db_path=acc["db_path"],
    )
    return {"ok": True, "data": {"skipped": post_id}}
