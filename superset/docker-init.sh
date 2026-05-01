#!/bin/bash
set -e

SENTINEL=/app/superset_home/.initialized

if [ ! -f "$SENTINEL" ]; then
  echo "==> Первый запуск — инициализирую Superset..."

  superset db upgrade

  superset fab create-admin \
    --username  "${SUPERSET_ADMIN_USER:-admin}" \
    --firstname "Admin" \
    --lastname  "" \
    --email     "${SUPERSET_ADMIN_EMAIL:-admin@threads.local}" \
    --password  "${SUPERSET_ADMIN_PASSWORD:-admin}"

  superset init

  python /app/pythonpath/setup_db.py

  touch "$SENTINEL"
  echo "==> Инициализация завершена"
fi

exec gunicorn \
  --bind 0.0.0.0:8088 \
  --workers 4 \
  --timeout 120 \
  --limit-request-line 0 \
  --limit-request-field_size 0 \
  "superset.app:create_app()"
