# feat/module04-notes-api-fastapi-sqlite → main

## Summary

Adds the module-04 Best-of-N deliverable: a FastAPI + SQLite notes API
selected from two AI-generated candidates, with a full pytest suite and
an auditable scoring record. Also lands the module-02 task store and a
repo-wide `.gitignore` that was missing from the initial commits.

## Why

The working tree accumulated all of module-04's outputs in a single
untracked blob. Splitting into atomic commits makes each concern
independently reviewable — the evaluation rationale, the API
implementation, and the test coverage are separate concerns that
shouldn't be coupled in a single diff.

## What changed

**Repo hygiene**
- Added `.gitignore` covering Python artifacts (`.venv/`, `__pycache__/`,
  `.pytest_cache/`, `*.db`) and macOS metadata (`.DS_Store`)

**module-02**
- Added `tasks.json` — runtime state produced by the CLI task manager,
  confirming correct schema and auto-incrementing IDs

**module-04 / evaluation**
- Added `candidates/scoring.md` — rubric scores (Correctness / Simplicity / Fit)
  and decision record (A: 8/9, B: 4/9)
- Added `candidates/candidate-b/` — losing candidate source preserved as
  evidence of Best-of-N variance (wrong HTTP verb, missing validation)

**module-04 / winner**
- Added `winner/notes_api.py` — FastAPI app with CRUD routes, SQLite WAL,
  Pydantic v2 validation, partial PATCH, and modern lifespan handler
- Added `winner/README.md` + `pyproject.toml` — endpoint reference and
  self-contained test runner config
- Added `winner/test_notes_api.py` + `conftest.py` — 27 tests across
  CREATE / LIST / SEARCH / GET / PATCH / DELETE / 404 / 422 paths;
  each test gets its own isolated SQLite file via monkeypatch

## How to test

```bash
cd module-04/winner
python -m venv .venv && source .venv/bin/activate
pip install fastapi httpx pytest
pytest test_notes_api.py -v
# Expected: 27 passed

# Smoke test the live server
uvicorn notes_api:app --reload &
curl -s -X POST http://localhost:8000/notes \
     -H 'Content-Type: application/json' \
     -d '{"title":"hello","body":"world"}' | python3 -m json.tool
curl -s http://localhost:8000/notes
curl -s -X DELETE http://localhost:8000/notes/1 -w "%{http_code}"
```

## Risk

Low. All new files in module-scoped directories; no existing code
modified. The `.gitignore` retroactively excludes artifacts that were
never tracked, so no history is rewritten.

## Rollback

```bash
git revert faa093f ee949bf 8577d4e 999d8b3 f04ea7e --no-commit
git commit -m "revert: remove module-04 notes API deliverables"
```

---

## Reviewer checklist

- [ ] Does `pytest test_notes_api.py -v` pass with 27 tests green?
- [ ] Does `scoring.md` document both the winning and losing scores with
      a clear rationale for the decision?
- [ ] Are `.venv/`, `__pycache__/`, and `.DS_Store` absent from the diff?
- [ ] Does each commit have a Conventional Commit subject and a "why" body?
- [ ] Is candidate-b source present alongside scoring.md so the evaluation
      is independently verifiable?
