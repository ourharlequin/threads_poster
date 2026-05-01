"""Создаёт подключение к analytics.duckdb в Superset при первом запуске."""
from superset import create_app

DB_NAME = "Threads Analytics"
DB_URI  = "duckdb:////app/data/analytics/analytics.duckdb"
DB_EXTRA = '{"engine_params": {"connect_args": {"read_only": true}}}'

app = create_app()
with app.app_context():
    from superset.extensions import db
    from superset.models.core import Database

    existing = db.session.query(Database).filter_by(database_name=DB_NAME).first()
    if existing:
        existing.sqlalchemy_uri = DB_URI
        existing.extra = DB_EXTRA
        db.session.commit()
        print(f"[setup_db] '{DB_NAME}' обновлена")
    else:
        conn = Database(
            database_name=DB_NAME,
            sqlalchemy_uri=DB_URI,
            extra=DB_EXTRA,
            expose_in_sqllab=True,
        )
        db.session.add(conn)
        db.session.commit()
        print(f"[setup_db] ✅ '{DB_NAME}' добавлена")
