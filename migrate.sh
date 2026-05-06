#!/bin/bash
set -e
cd /root/threads_poster

echo "=== Step 1: Stop participant containers ==="
for dir in Budimir Tanya Slava; do
  if [ -f "$dir/docker-compose.yml" ]; then
    echo "Stopping $dir..."
    (cd "$dir" && docker compose down) || true
  fi
done

echo ""
echo "=== Step 2: Migrate data from named volumes to bind mounts ==="

declare -A VOLUMES=(
  ["Budimir"]="budimir_threads_data"
  ["Tanya"]="tanya_tanya_data"
  ["Slava"]="slava_slava_data"
)

for dir in Budimir Tanya Slava; do
  vol="${VOLUMES[$dir]}"
  dest="$dir/data"

  # Skip if volume doesn't exist
  if ! docker volume inspect "$vol" &>/dev/null; then
    echo "$dir: volume '$vol' not found — skipping"
    continue
  fi

  # Skip if data already migrated (duckdb file exists and is newer than seed)
  if [ -f "$dest/data.duckdb" ] && [ "$(stat -c%s "$dest/data.duckdb" 2>/dev/null || echo 0)" -gt 10000 ]; then
    echo "$dir: data already present in $dest — skipping"
    continue
  fi

  echo "$dir: copying from '$vol' → '$dest'..."
  mkdir -p "$dest"
  docker run --rm \
    -v "${vol}:/src" \
    -v "/root/threads_poster/${dest}:/dst" \
    alpine sh -c "cp -a /src/. /dst/"
  echo "$dir: done ($(ls -lh "$dest" | tail -n +2))"
done

echo ""
echo "=== Step 3: Remove old Budimir container names ==="
docker stop threads_publisher threads_scheduler 2>/dev/null && \
  docker rm   threads_publisher threads_scheduler 2>/dev/null || \
  echo "Old containers not found — skipping"

echo ""
echo "=== Step 4: git pull ==="
git pull

echo ""
echo "=== Step 5: Restart participant containers with new bind mounts ==="
for dir in Budimir Tanya Slava; do
  if [ -f "$dir/docker-compose.yml" ] && [ -f "$dir/.env" ]; then
    echo "Starting $dir..."
    (cd "$dir" && docker compose up -d --build threads_publisher threads_scheduler)
  else
    echo "$dir: no .env — skipping"
  fi
done

echo ""
echo "=== Step 6: Start threads_api ==="
docker compose up -d --build threads_api

echo ""
echo "=== Step 7: Verify ==="
sleep 3
curl -sf http://localhost:7843/system/health && echo " — API OK" || echo " — API not responding"
curl -sf http://localhost:7843/system/accounts | python3 -c "
import json, sys
data = json.load(sys.stdin)
accounts = data.get('data', {}).get('accounts', [])
print(f' — {len(accounts)} accounts loaded: {[a[\"account_id\"] for a in accounts]}')
" 2>/dev/null || true

echo ""
echo "=== Migration complete ==="
