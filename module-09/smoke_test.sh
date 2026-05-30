#!/usr/bin/env bash
# notes-api-smoke — standalone runner
# Usage: bash smoke_test.sh <module_path> <port>
# Example: bash smoke_test.sh /path/to/module-09 8099

set -euo pipefail

MODULE_PATH="${1:-.}"
PORT="${2:-8099}"
PASS=0
FAIL=0

# Start server
cd "$MODULE_PATH"
uv run --with fastapi --with uvicorn --with httpx uvicorn notes_api:app --port "$PORT" --log-level warning &
SERVER_PID=$!
trap "kill $SERVER_PID 2>/dev/null; rm -f notes.db" EXIT

# Wait for startup
for i in $(seq 1 15); do
  if curl -sf "http://localhost:$PORT/notes" >/dev/null 2>&1; then
    break
  fi
  sleep 0.5
done

check() {
  local label="$1"
  local expected="$2"
  local actual
  actual=$(curl -s -o /dev/null -w "%{http_code}" "${@:3}")
  if [ "$actual" = "$expected" ]; then
    echo "PASS  $label  (got $actual)"
    PASS=$((PASS + 1))
  else
    echo "FAIL  $label  (expected $expected, got $actual)"
    FAIL=$((FAIL + 1))
  fi
}

BASE="http://localhost:$PORT"

# POST /notes → 201
NOTE_ID=$(curl -s -X POST "$BASE/notes" \
  -H "Content-Type: application/json" \
  -d '{"title":"smoke","body":"test"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

check "POST   /notes          → 201" "201" \
  -X POST "$BASE/notes" -H "Content-Type: application/json" -d '{"title":"hello","body":"world"}'

check "GET    /notes          → 200" "200" \
  "$BASE/notes"

check "GET    /notes/$NOTE_ID → 200" "200" \
  "$BASE/notes/$NOTE_ID"

check "PATCH  /notes/$NOTE_ID → 200" "200" \
  -X PATCH "$BASE/notes/$NOTE_ID" -H "Content-Type: application/json" -d '{"title":"updated"}'

check "DELETE /notes/$NOTE_ID → 204" "204" \
  -X DELETE "$BASE/notes/$NOTE_ID"

check "GET    /notes/999      → 404" "404" \
  "$BASE/notes/999"

echo ""
echo "Results: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
