# feat(practical): add Bookmarks REST API

## What
Single-file FastAPI + SQLite bookmarks service with a full pytest suite.

## Why
Demonstrates the full Tech Lead workflow: GCOE prompt, Best-of-2 candidate selection,
test generation, code review with applied fixes, and PR documentation — following the
Notes API (module-04) patterns.

## Changes
- `service/app.py` — `/health` + five bookmark endpoints; SQLite WAL; Pydantic validators;
  `_fetch_one()` 404 guard.
- `tests/test_bookmarks_api.py` — 23 tests: 11 happy-path, 7 error (404 + 422), 5 boundary.
- `PROMPT.md` — GCOE prompt; context gathered via GitHub MCP server before writing.
- `candidates.md` — Candidate A (plain `str`) beats B (`AnyUrl`): URL normalization breaks
  round-trip fidelity.
- `REVIEW.md` — two fixes: `/health` added to service; 404 body assertions added to tests.

## Risks
- No auth — any caller can delete all bookmarks (module-10 Security: add `x-api-key`).
- SQLite WAL persists on crash; safe to delete on restart.

## Rollback
`git revert HEAD` removes the service. Delete `bookmarks.db` to reset. No downstream callers.

## @claude review
Add `@claude` as a reviewer. It should run the smoke script on the PR branch and flag any
endpoint returning an unexpected status code before merging to main.

## Test plan
- [ ] `pytest assessments/practical/tests/ -v` → 23 passed
- [ ] Smoke: POST → 201, GET list → 200, GET ?tag= → 200, GET /:id → 200, DELETE → 204, GET /99 → 404
- [ ] `GET /health` → 200 `{"status":"ok","db":"connected"}`
- [ ] `GET /bookmarks?tag=py` returns `[]` when only `python`-tagged bookmarks exist
