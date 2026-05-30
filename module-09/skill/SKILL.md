---
name: notes-api-smoke
description: Boot a single-file FastAPI notes app and assert all 5 CRUD endpoints plus a 404 probe return correct HTTP status codes.
---

## Purpose

Verify that a FastAPI notes API is healthy before committing, deploying, or handing off. Asserts six HTTP contracts: POST /notes → 201, GET /notes → 200, GET /notes/{id} → 200, PATCH /notes/{id} → 200, DELETE /notes/{id} → 204, and GET /notes/999 → 404. Prints PASS or FAIL per check and exits non-zero if any check fails.

## When to use

- Before any `git commit` that touches the notes API source file
- After pulling changes from a teammate to confirm the API still works
- As a CI smoke gate before a staging deploy
- Any time you need a quick sanity check without standing up the full test suite

## Body

1. Change into `$MODULE_PATH` (the directory containing `notes_api.py`).
2. Start the server in the background:
   ```
   uv run --with fastapi --with uvicorn uvicorn notes_api:app --port $PORT --log-level warning &
   SERVER_PID=$!
   ```
3. Poll `GET /notes` up to 15 times (0.5 s apart) until the server responds, then proceed.
4. For each of the six checks below, run `curl -s -o /dev/null -w "%{http_code}"` and compare to the expected code. Print `PASS <label>` or `FAIL <label> (expected X, got Y)`.
   - POST `/notes` with `{"title":"smoke","body":"test"}` → **201**
   - GET `/notes` → **200**
   - GET `/notes/$NOTE_ID` (id from the POST response) → **200**
   - PATCH `/notes/$NOTE_ID` with `{"title":"updated"}` → **200**
   - DELETE `/notes/$NOTE_ID` → **204**
   - GET `/notes/999` → **404**
5. Print a summary line: `Results: N passed, M failed`.
6. Kill the server (`kill $SERVER_PID`) and remove any test database created (`notes.db`).
7. Exit 0 if all checks passed; exit 1 if any failed.

## Inputs

| Name          | Required | Default | Description                                              |
|---------------|----------|---------|----------------------------------------------------------|
| `MODULE_PATH` | yes      | —       | Absolute or relative path to the directory containing `notes_api.py` |
| `PORT`        | yes      | —       | Local TCP port to bind the server on (must be free)      |

## Outputs

- One `PASS` or `FAIL` line per check, printed to stdout
- A summary line: `Results: N passed, M failed`
- Exit code 0 (all pass) or 1 (any fail)

## Worked example

The following bash block starts the API from `module-09/notes_api.py` on port 8099 and runs all six checks. Run it from the repo root.

```bash
#!/usr/bin/env bash
set -euo pipefail

MODULE_PATH="module-09"
PORT="8099"
PASS=0
FAIL=0

cd "$MODULE_PATH"
uv run --with fastapi --with uvicorn uvicorn notes_api:app --port "$PORT" --log-level warning &
SERVER_PID=$!
trap "kill $SERVER_PID 2>/dev/null; rm -f notes.db" EXIT

for i in $(seq 1 15); do
  if curl -sf "http://localhost:$PORT/notes" >/dev/null 2>&1; then break; fi
  sleep 0.5
done

check() {
  local label="$1" expected="$2" actual
  actual=$(curl -s -o /dev/null -w "%{http_code}" "${@:3}")
  if [ "$actual" = "$expected" ]; then
    echo "PASS  $label  (got $actual)"; PASS=$((PASS + 1))
  else
    echo "FAIL  $label  (expected $expected, got $actual)"; FAIL=$((FAIL + 1))
  fi
}

BASE="http://localhost:$PORT"
NOTE_ID=$(curl -s -X POST "$BASE/notes" \
  -H "Content-Type: application/json" \
  -d '{"title":"smoke","body":"test"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

check "POST   /notes          → 201" "201" -X POST "$BASE/notes" -H "Content-Type: application/json" -d '{"title":"hello","body":"world"}'
check "GET    /notes          → 200" "200" "$BASE/notes"
check "GET    /notes/$NOTE_ID → 200" "200" "$BASE/notes/$NOTE_ID"
check "PATCH  /notes/$NOTE_ID → 200" "200" -X PATCH "$BASE/notes/$NOTE_ID" -H "Content-Type: application/json" -d '{"title":"updated"}'
check "DELETE /notes/$NOTE_ID → 204" "204" -X DELETE "$BASE/notes/$NOTE_ID"
check "GET    /notes/999      → 404" "404" "$BASE/notes/999"

echo ""
echo "Results: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
```

Expected output (all passing):

```
PASS  POST   /notes          → 201  (got 201)
PASS  GET    /notes          → 200  (got 200)
PASS  GET    /notes/2 → 200  (got 200)
PASS  PATCH  /notes/2 → 200  (got 200)
PASS  DELETE /notes/2 → 204  (got 204)
PASS  GET    /notes/999      → 404  (got 404)

Results: 6 passed, 0 failed
```
