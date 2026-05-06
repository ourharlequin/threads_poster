import os
import json
import httpx
import docker
from fastapi import APIRouter, HTTPException

router = APIRouter()

SUPERSET_URL  = os.getenv("SUPERSET_URL", "http://threads_superset:8088")
SUPERSET_USER = os.getenv("SUPERSET_ADMIN_USER", "admin")
SUPERSET_PASS = os.getenv("SUPERSET_ADMIN_PASSWORD", "admin")

SUPERSET_CONTAINERS = ["threads_superset", "threads_merger", "threads_superset_redis"]


def _docker_client():
    return docker.from_env()


def _container_info(client, name: str) -> dict:
    try:
        c = client.containers.get(name)
        return {"name": name, "status": c.status, "id": c.short_id}
    except docker.errors.NotFound:
        return {"name": name, "status": "not_found", "id": None}


def _superset_session() -> tuple[httpx.Client, str]:
    """Returns authenticated httpx.Client + CSRF token."""
    client = httpx.Client(base_url=SUPERSET_URL, timeout=30)
    r = client.post("/api/v1/security/login", json={
        "username": SUPERSET_USER,
        "password": SUPERSET_PASS,
        "provider": "db",
    })
    if not r.is_success:
        raise HTTPException(502, f"Superset login failed: {r.text[:200]}")
    token = r.json()["access_token"]
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Referer": SUPERSET_URL,
    }
    client.headers.update(headers)
    csrf_r = client.get("/api/v1/security/csrf_token/")
    csrf = csrf_r.json()["result"]
    client.headers["X-CSRFToken"] = csrf
    return client, csrf


def _get_dataset_ids(client: httpx.Client) -> dict[str, int]:
    r = client.get("/api/v1/dataset/")
    return {d["table_name"]: d["id"] for d in r.json().get("result", [])}


def _metric(aggregate: str, column: str | None, label: str) -> dict:
    return {
        "expressionType": "SIMPLE",
        "aggregate": aggregate,
        "column": {"column_name": column} if column else None,
        "label": label,
        "hasCustomLabel": bool(label),
    }


def _create_chart(client: httpx.Client, ds_ids: dict, name: str, viz_type: str, ds_name: str, params: dict) -> int | None:
    ds_id = ds_ids.get(ds_name)
    if not ds_id:
        return None
    params.update({"viz_type": viz_type, "datasource": f"{ds_id}__table"})
    r = client.post("/api/v1/chart/", json={
        "slice_name": name,
        "viz_type": viz_type,
        "datasource_id": ds_id,
        "datasource_type": "table",
        "params": json.dumps(params),
    })
    return r.json().get("id") if r.is_success else None


def _build_layout(ids: list[int]) -> dict:
    layout: dict = {
        "DASHBOARD_VERSION_KEY": "v2",
        "ROOT_ID": {"type": "ROOT", "id": "ROOT_ID", "children": ["GRID_ID"]},
        "GRID_ID": {"type": "GRID", "id": "GRID_ID", "children": [], "parents": ["ROOT_ID"]},
    }
    row_ids = []
    pairs = [ids[i:i + 2] for i in range(0, len(ids), 2)]
    for ri, pair in enumerate(pairs):
        row_id = f"ROW-{ri}"
        width = 24 // len(pair)
        children = []
        for chart_id in pair:
            elem_id = f"CHART-{chart_id}"
            layout[elem_id] = {
                "type": "CHART", "id": elem_id, "children": [],
                "parents": ["ROOT_ID", "GRID_ID", row_id],
                "meta": {"width": width, "height": 52, "chartId": chart_id},
            }
            children.append(elem_id)
        layout[row_id] = {
            "type": "ROW", "id": row_id, "children": children,
            "parents": ["ROOT_ID", "GRID_ID"],
            "meta": {"background": "BACKGROUND_TRANSPARENT"},
        }
        row_ids.append(row_id)
    layout["GRID_ID"]["children"] = row_ids
    return layout


@router.get("/status")
def superset_status():
    client = _docker_client()
    containers = [_container_info(client, name) for name in SUPERSET_CONTAINERS]
    return {"ok": True, "data": {"containers": containers}}


@router.post("/merger-run")
def merger_run():
    try:
        client = _docker_client()
        container = client.containers.get("threads_merger")
        exit_code, output = container.exec_run(
            "python -c 'from merger import merge; merge()'",
            workdir="/app",
        )
        text = output.decode("utf-8", errors="replace") if isinstance(output, bytes) else str(output)
    except docker.errors.NotFound:
        raise HTTPException(404, "Container 'threads_merger' not found")
    except Exception as e:
        raise HTTPException(500, str(e))
    return {
        "ok": exit_code == 0,
        "data": {"returncode": exit_code, "output": text[-2000:] if text else ""},
    }


@router.post("/rebuild")
def rebuild():
    try:
        superset_client, _ = _superset_session()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(502, f"Cannot reach Superset: {e}")

    ds_ids = _get_dataset_ids(superset_client)
    if not ds_ids:
        raise HTTPException(502, "No datasets found in Superset — run setup_db.py first")

    chart_ids = []

    specs = [
        ("Просмотры по аккаунтам", "echarts_timeseries_line", "account_insights", {
            "time_range": "No filter", "x_axis": "date",
            "metrics": [_metric("SUM", "views", "Просмотры")],
            "groupby": ["account_id"], "smooth": True, "show_legend": True, "row_limit": 10000,
        }),
        ("Рост фолловеров", "echarts_timeseries_line", "account_insights", {
            "time_range": "No filter", "x_axis": "date",
            "metrics": [_metric("MAX", "followers_count", "Фолловеры")],
            "groupby": ["account_id"], "smooth": True, "show_legend": True, "row_limit": 10000,
        }),
        ("Вовлечённость по аккаунтам", "echarts_timeseries_bar", "account_insights", {
            "time_range": "No filter", "x_axis": "date",
            "metrics": [
                _metric("SUM", "likes",   "Лайки"),
                _metric("SUM", "replies", "Ответы"),
                _metric("SUM", "reposts", "Репосты"),
                _metric("SUM", "quotes",  "Цитаты"),
            ],
            "groupby": ["account_id"], "show_legend": True, "row_limit": 10000,
        }),
        ("Постов опубликовано по дням", "echarts_timeseries_bar", "posts", {
            "time_range": "No filter", "x_axis": "posted_at", "time_grain_sqla": "P1D",
            "metrics": [{"expressionType": "SIMPLE", "aggregate": "COUNT", "column": None, "label": "Постов"}],
            "groupby": ["account_id"], "show_legend": True, "row_limit": 10000,
        }),
        ("Топ постов по просмотрам", "table", "post_insights", {
            "time_range": "No filter", "query_mode": "raw",
            "columns": ["post_id", "views", "likes", "replies", "reposts", "quotes", "fetched_at"],
            "order_by_cols": [json.dumps(["views", False])],
            "page_length": 25, "show_cell_bars": True, "include_search": True,
        }),
        ("Статус постов", "pie", "posts", {
            "time_range": "No filter",
            "metric": _metric("COUNT", None, "Постов"),
            "groupby": ["status"], "show_legend": True, "show_labels": True,
        }),
    ]

    created, failed = 0, 0
    for name, viz, ds, params in specs:
        cid = _create_chart(superset_client, ds_ids, name, viz, ds, params)
        if cid:
            chart_ids.append(cid)
            created += 1
        else:
            failed += 1

    dash_id = None
    if chart_ids:
        r = superset_client.post("/api/v1/dashboard/", json={
            "dashboard_title": "Threads Analytics",
            "published": True,
            "position_json": json.dumps(_build_layout(chart_ids)),
        })
        if r.is_success:
            dash_id = r.json().get("id")

    return {
        "ok": True,
        "data": {
            "charts_created": created,
            "charts_failed": failed,
            "dashboard_id": dash_id,
            "dashboard_url": f"{SUPERSET_URL}/superset/dashboard/{dash_id}/" if dash_id else None,
        },
    }
