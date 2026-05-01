"""
Создаёт чарты и дашборд в Superset через REST API.
Запускать: python create_charts.py
"""
import json
import sys
import requests

BASE = "http://localhost:8088"

# ── Auth ──────────────────────────────────────────────────────────────────────
session = requests.Session()

r = session.post(f"{BASE}/api/v1/security/login", json={
    "username": "admin", "password": "admin", "provider": "db",
})
if not r.ok:
    sys.exit(f"Ошибка авторизации: {r.text}")

TOKEN = r.json()["access_token"]

csrf_r = session.get(f"{BASE}/api/v1/security/csrf_token/",
                     headers={"Authorization": f"Bearer {TOKEN}"})
CSRF = csrf_r.json()["result"]

H = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
    "X-CSRFToken": CSRF,
    "Referer": BASE,
}

def post(url, **kw):
    return session.post(url, headers=H, **kw)

def get(url, **kw):
    return session.get(url, headers=H, **kw)

# ── Dataset IDs ───────────────────────────────────────────────────────────────
datasets_r = get(f"{BASE}/api/v1/dataset/").json()
DS = {d["table_name"]: d["id"] for d in datasets_r.get("result", [])}
print(f"Датасеты: {DS}")

def metric(aggregate, column_name, label):
    return {
        "expressionType": "SIMPLE",
        "aggregate": aggregate,
        "column": {"column_name": column_name} if column_name else None,
        "label": label,
        "hasCustomLabel": bool(label),
    }

def create_chart(name, viz_type, ds_name, params):
    ds_id = DS.get(ds_name)
    if not ds_id:
        print(f"  ⚠️  Датасет '{ds_name}' не найден")
        return None
    params.update({"viz_type": viz_type, "datasource": f"{ds_id}__table"})
    r = post(f"{BASE}/api/v1/chart/", json={
        "slice_name": name,
        "viz_type": viz_type,
        "datasource_id": ds_id,
        "datasource_type": "table",
        "params": json.dumps(params),
    })
    if r.ok:
        cid = r.json()["id"]
        print(f"  ✅ {name!r}  →  id={cid}")
        return cid
    print(f"  ❌ {name}: {r.status_code} {r.text[:300]}")
    return None

# ── Чарты ─────────────────────────────────────────────────────────────────────
print("\nСоздаю чарты...")
chart_ids = []

# 1. Просмотры по аккаунтам
cid = create_chart("Просмотры по аккаунтам", "echarts_timeseries_line", "account_insights", {
    "time_range": "No filter",
    "x_axis": "date",
    "metrics": [metric("SUM", "views", "Просмотры")],
    "groupby": ["account_id"],
    "smooth": True,
    "show_legend": True,
    "row_limit": 10000,
})
if cid: chart_ids.append(cid)

# 2. Рост фолловеров
cid = create_chart("Рост фолловеров", "echarts_timeseries_line", "account_insights", {
    "time_range": "No filter",
    "x_axis": "date",
    "metrics": [metric("MAX", "followers_count", "Фолловеры")],
    "groupby": ["account_id"],
    "smooth": True,
    "show_legend": True,
    "row_limit": 10000,
})
if cid: chart_ids.append(cid)

# 3. Вовлечённость (лайки + ответы + репосты + цитаты)
cid = create_chart("Вовлечённость по аккаунтам", "echarts_timeseries_bar", "account_insights", {
    "time_range": "No filter",
    "x_axis": "date",
    "metrics": [
        metric("SUM", "likes",   "Лайки"),
        metric("SUM", "replies", "Ответы"),
        metric("SUM", "reposts", "Репосты"),
        metric("SUM", "quotes",  "Цитаты"),
    ],
    "groupby": ["account_id"],
    "show_legend": True,
    "row_limit": 10000,
})
if cid: chart_ids.append(cid)

# 4. Постов опубликовано по дням
cid = create_chart("Постов опубликовано по дням", "echarts_timeseries_bar", "posts", {
    "time_range": "No filter",
    "x_axis": "posted_at",
    "time_grain_sqla": "P1D",
    "metrics": [{"expressionType": "SIMPLE", "aggregate": "COUNT", "column": None, "label": "Постов"}],
    "groupby": ["account_id"],
    "show_legend": True,
    "row_limit": 10000,
})
if cid: chart_ids.append(cid)

# 5. Топ постов по просмотрам (таблица)
cid = create_chart("Топ постов по просмотрам", "table", "post_insights", {
    "time_range": "No filter",
    "query_mode": "raw",
    "columns": ["post_id", "views", "likes", "replies", "reposts", "quotes", "fetched_at"],
    "order_by_cols": [json.dumps(["views", False])],
    "page_length": 25,
    "show_cell_bars": True,
    "include_search": True,
})
if cid: chart_ids.append(cid)

# 6. Статус постов (pie)
cid = create_chart("Статус постов", "pie", "posts", {
    "time_range": "No filter",
    "metric": metric("COUNT", None, "Постов"),
    "groupby": ["status"],
    "show_legend": True,
    "show_labels": True,
    "show_labels_threshold": 5,
})
if cid: chart_ids.append(cid)

# ── Dashboard ─────────────────────────────────────────────────────────────────
print(f"\nСоздаю дашборд из {len(chart_ids)} чартов...")

def build_layout(ids):
    layout = {
        "DASHBOARD_VERSION_KEY": "v2",
        "ROOT_ID":  {"type": "ROOT", "id": "ROOT_ID",  "children": ["GRID_ID"]},
        "GRID_ID":  {"type": "GRID", "id": "GRID_ID",  "children": [], "parents": ["ROOT_ID"]},
    }
    row_ids = []
    # Пары чартов в строки (по 2 в ряд), последний одиночный — на полную ширину
    pairs = [ids[i:i+2] for i in range(0, len(ids), 2)]
    for ri, pair in enumerate(pairs):
        row_id = f"ROW-{ri}"
        width = 24 // len(pair)
        children = []
        for ci, chart_id in enumerate(pair):
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

r = post(f"{BASE}/api/v1/dashboard/", json={
    "dashboard_title": "Threads Analytics",
    "published": True,
    "position_json": json.dumps(build_layout(chart_ids)),
})
if r.ok:
    dash_id = r.json()["id"]
    print(f"  ✅ Dashboard 'Threads Analytics'  →  id={dash_id}")
    print(f"\n  Открыть: http://localhost:8088/superset/dashboard/{dash_id}/")
else:
    print(f"  ❌ Dashboard: {r.status_code} {r.text[:400]}")
