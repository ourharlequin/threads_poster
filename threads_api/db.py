import asyncio
import duckdb

ANALYTICS_DB = "/app/data/analytics/analytics.duckdb"

_write_lock = asyncio.Lock()


def query_data(sql: str, params: list | None = None, db_path: str = "") -> list:
    with duckdb.connect(db_path, read_only=True) as conn:
        return conn.execute(sql, params or []).fetchall()


def query_analytics(sql: str, params: list | None = None) -> list:
    with duckdb.connect(ANALYTICS_DB, read_only=True) as conn:
        return conn.execute(sql, params or []).fetchall()


async def write_data(sql: str, params: list | None = None, db_path: str = "") -> None:
    async with _write_lock:
        for attempt in range(3):
            try:
                with duckdb.connect(db_path) as conn:
                    conn.execute(sql, params or [])
                return
            except duckdb.IOException:
                if attempt < 2:
                    await asyncio.sleep(0.2)
                else:
                    raise
