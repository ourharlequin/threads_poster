from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import docker
from registry import REGISTRY, PARTICIPANTS
from subprocess_runner import run_sync

router = APIRouter()

_PUBLISHER_CONTAINERS = [
    f"{name}_{role}"
    for name in PARTICIPANTS
    for role in ("publisher", "scheduler")
]


def _docker_client():
    return docker.from_env()


def _container_info(client, name: str) -> dict:
    try:
        c = client.containers.get(name)
        return {"name": name, "status": c.status, "id": c.short_id}
    except docker.errors.NotFound:
        return {"name": name, "status": "not_found", "id": None}


class ForcePublishRequest(BaseModel):
    account_id: str


class FetchInsightsRequest(BaseModel):
    participant: str = "budimir"


@router.post("/force")
def force_publish(req: ForcePublishRequest):
    acc = REGISTRY.get(req.account_id)
    if not acc:
        raise HTTPException(404, f"Unknown account_id: '{req.account_id}'")
    try:
        code, output = run_sync(
            "test_publish.py",
            acc["scripts_dir"],
            acc["db_path"],
            ["--account", req.account_id],
            timeout=60,
        )
    except Exception as e:
        raise HTTPException(500, str(e))
    return {"ok": code == 0, "data": {"returncode": code, "output": output[-2000:]}}


@router.get("/status")
def publisher_status():
    client = _docker_client()
    containers = [_container_info(client, name) for name in _PUBLISHER_CONTAINERS]
    return {"ok": True, "data": {"containers": containers}}


@router.post("/fetch-insights")
def fetch_insights(req: FetchInsightsRequest):
    config = PARTICIPANTS.get(req.participant)
    if not config:
        raise HTTPException(404, f"Unknown participant: '{req.participant}'")
    try:
        code, output = run_sync(
            "fetch_insights.py",
            config["scripts_dir"],
            config["db_path"],
            timeout=120,
        )
    except Exception as e:
        raise HTTPException(500, str(e))
    return {"ok": code == 0, "data": {"returncode": code, "output": output[-2000:]}}
