# feat/module04-notes-api-fastapi-sqlite → main

## Summary

Delivers modules 2–6 of the Claude Code Bootcamp: a JSON-persisted CLI task
manager, a FastAPI + SQLite notes API selected via Best-of-N evaluation, a
full pytest suite with seeded-bug validation, a repo-wide CLAUDE.md, and
git-workflow submission artifacts with atomic Conventional Commits throughout.

## Why

Each module builds on the last, and keeping them in one feature branch makes
the progression reviewable as a unit — the CLAUDE.md written in module 3
actively steered the output of module 5, which is only visible if both are
in the same diff. Splitting into atomic commits makes each concern
independently reviewable without losing the narrative thread.

## What changed

**Repo hygiene**
- Added `.gitignore` covering Python artifacts and macOS metadata
- Added `CLAUDE.md` at repo root — 5-section file that actively changes
  Claude's behavior (datetime rule, argparse requirement, no multi-line
  docstrings, single-file modules)

**module-02**
- Added `tasks.json` — runtime state confirming correct schema and UTC timestamps

**module-03**
- Added `proof.png` — screenshot proving Claude obeyed the datetime convention
  from CLAUDE.md in a fresh session without being reminded

**module-04**
- Added `candidates/scoring.md` + `candidate-b/` — evaluation record showing
  A (8/9) beat B (4/9); wrong HTTP verb and missing validation in B
- Added `winner/notes_api.py` — FastAPI app: CRUD, SQLite WAL, Pydantic v2,
  partial PATCH, ISO-8601 UTC timestamps, lifespan handler
- Added `winner/test_notes_api.py` + `conftest.py` — 27 tests, isolated
  SQLite per test via monkeypatch

**module-05**
- Added `tests/` — 19-test suite that imports real `notes_api` (not a copy),
  patches `DB_PATH`, pins 404 body shape, not just status code
- Added `bug-fix-notes.md` — both BUGS.md issues documented: OR→AND search
  silencer, missing PATCH 404 guard causing 500
- Added `code-review-rubric.md` — 7-item yes/no checklist targeting AI blind
  spots (SQL logic, null guards, timezone, test copies, body shape)

**module-06**
- Added `branch.txt`, `commits.md`, `pr.md` — git workflow artifacts

## How to test

```bash
# Run module-05 test suite (19 tests)
uv run --python 3.14 --with pytest --with fastapi --with httpx \
  pytest module-05/tests/ -v

# Smoke-test the live API
cd module-04/winner
uvicorn notes_api:app --reload &
curl -s -X POST http://localhost:8000/notes \
  -H 'Content-Type: application/json' \
  -d '{"title":"hello","body":"world"}' | python3 -m json.tool
curl -s "http://localhost:8000/notes?q=hello"
curl -s http://localhost:8000/notes/999
```

## Risk

Low. All changes are additive — new files in module-scoped directories.
The only modification to an existing file is `module-04/winner/notes_api.py`
which had two bugs seeded and then fixed, leaving it identical to the
pre-exercise state.

## Rollback

```bash
git revert a949d56 aee4dd9 0bb758b 3b0a03e faa093f 8577d4e ee949bf 999d8b3 f04ea7e --no-commit
git commit -m "revert: remove modules 2-6 bootcamp deliverables"
```

---

## Reviewer checklist

- [ ] Does `uv run --python 3.14 --with pytest --with fastapi --with httpx pytest module-05/tests/ -v` show 19 passed?
- [ ] Does `module-05/tests/test_notes_api.py` import `notes_api` (not redefine it)?
- [ ] Does at least one 404 test assert the response body shape, not just status code?
- [ ] Is `CLAUDE.md` ≤ 80 lines with all five H1 sections present?
- [ ] Does each commit have a Conventional Commit subject and a "why" body?
