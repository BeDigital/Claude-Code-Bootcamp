# Production Readiness Report — Notes API (module-04/winner)

**Date:** 2026-05-30  
**Reviewer:** Brian Uckert  
**Target:** `module-04/winner/notes_api.py` — FastAPI + SQLite, single-file REST API

---

## Security — YELLOW

**Status:** Parameterized queries prevent SQL injection; Pydantic validates shape and title constraints. However, there is zero authentication — any caller on the network can create, modify, or delete all notes. No rate limiting. No input-size cap on `title` or `body`.

**Biggest risk:** Unauthenticated write access — a single curl call deletes all notes.

**Smallest next step:** Add an `x-api-key` FastAPI dependency that reads a secret from the `NOTES_API_KEY` env var and returns 401 on mismatch.

---

## Observability — RED

**Status:** No logging, no metrics, no health endpoint, no request tracing. FastAPI's auto `/docs` is the only visibility surface. Errors are silently swallowed by the framework's default 500 handler.

**Biggest risk:** A DB-locked or disk-full failure is completely invisible until a user reports a 500.

**Smallest next step:** Add `GET /health` returning `{"status": "ok", "db": "connected"}` with a live SQLite ping.

---

## Deployment — RED

**Status:** No Dockerfile, no compose file, no env-var config. `DB_PATH` is hardcoded to `Path(__file__).parent / "notes.db"` — the DB lives next to the source file. `pip install fastapi uvicorn` is underpinned by no lockfile (`pyproject.toml` has no dependencies listed).

**Biggest risk:** `DB_PATH` next to the app binary means data is destroyed on any container image rebuild or restart.

**Smallest next step:** Read `DB_PATH` from env var `NOTES_DB_PATH`, falling back to the current default — one `os.environ.get` call.

---

## Runbooks — YELLOW

**Status:** `README.md` covers run commands and the endpoint table. Nothing covers ops: how to restart a crashed process, what to do when the DB is locked, or where logs live (answer: nowhere).

**Biggest risk:** No on-call guidance — an engineer paged at 2 AM has no playbook.

**Smallest next step:** Add a "Troubleshooting" section to README with the three most likely failure modes: DB locked (WAL stale), port already in use, and 500 on startup.

---

## Rollback — RED

**Status:** No schema versioning, no migration history, no backup strategy. The `CREATE TABLE IF NOT EXISTS` pattern is idempotent for the happy path but provides no path to roll back a column addition or rename.

**Biggest risk:** A schema change (e.g., adding a NOT NULL column) in production leaves the DB in a state with no automated recovery path.

**Smallest next step:** Add a `schema_migrations` table with a single row tracking the current schema version, and document the version in README.

---

## Verdict

**No-Go.**

Unauthenticated API, hardcoded DB path, and zero observability make this unsafe to run in any shared environment.
