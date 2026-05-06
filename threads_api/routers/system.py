import httpx
import docker
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from registry import REGISTRY, PARTICIPANTS
from subprocess_runner import run_sync

router = APIRouter()

_THREADS_ME = "https://graph.threads.net/v1.0/me"

_INFRA_CONTAINERS = {"threads_api", "threads_superset", "threads_merger", "threads_superset_redis"}
ALLOWED_CONTAINERS = _INFRA_CONTAINERS | {
    f"{name}_{role}"
    for name in PARTICIPANTS
    for role in ("publisher", "scheduler")
}


class RefreshTokensRequest(BaseModel):
    participant: str = "budimir"


@router.get("/health")
def health():
    return {"ok": True, "data": {"status": "ok"}}


@router.get("/token-expiry")
def token_expiry():
    results = []
    for acc_id, acc in REGISTRY.items():
        try:
            r = httpx.get(
                _THREADS_ME,
                params={"access_token": acc["token"], "fields": "id"},
                timeout=10,
            )
            valid = r.status_code == 200
        except Exception:
            valid = False
        results.append({
            "account_id":  acc_id,
            "participant": acc["participant"],
            "token_valid": valid,
        })
    return {
        "ok": True,
        "data": {
            "accounts": results,
            "note": "Tokens expire after 60 days; refresh every 58 days",
        },
    }


@router.post("/refresh-tokens")
def refresh_tokens(req: RefreshTokensRequest):
    config = PARTICIPANTS.get(req.participant)
    if not config:
        raise HTTPException(404, f"Unknown participant: '{req.participant}'")
    try:
        code, output = run_sync(
            "refresh_tokens.py",
            config["scripts_dir"],
            config["db_path"],
            timeout=30,
        )
    except Exception as e:
        raise HTTPException(500, str(e))
    return {"ok": code == 0, "data": {"returncode": code, "output": output[-2000:]}}


@router.get("/logs")
def logs(
    container: str = Query(...),
    lines: int = Query(50, ge=1, le=500),
):
    if container not in ALLOWED_CONTAINERS:
        raise HTTPException(400, f"Container '{container}' not in allowed list")
    try:
        client = docker.from_env()
        c = client.containers.get(container)
        raw = c.logs(tail=lines, timestamps=True)
        text = raw.decode("utf-8", errors="replace") if isinstance(raw, bytes) else str(raw)
    except docker.errors.NotFound:
        raise HTTPException(404, f"Container '{container}' not found")
    except Exception as e:
        raise HTTPException(500, str(e))
    return {"ok": True, "data": {"container": container, "logs": text}}


@router.get("/accounts")
def list_accounts():
    accounts = [
        {
            "account_id":  acc_id,
            "participant": v["participant"],
            "user_id":     v["user_id"],
        }
        for acc_id, v in REGISTRY.items()
    ]
    return {"ok": True, "data": {"accounts": accounts, "total": len(accounts)}}
