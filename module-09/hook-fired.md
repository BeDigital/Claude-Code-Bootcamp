# Hook Fired — Blocked Commit Proof

**Date:** 2026-05-30
**Hook:** `.git/hooks/pre-commit` (runs `module-09/smoke_test.sh`)
**Claude Code hook:** `module-09/.claude/hooks.json` (PreToolUse on Bash, same script)

## Bug introduced

One line added to `module-09/notes_api.py` at `GET /notes`:

```python
@app.get("/notes", response_model=list[NoteOut])
def list_notes(q: Optional[str] = Query(default=None)):  # BUG: force 500
    raise HTTPException(status_code=500, detail="forced error")
```

## Commands run

```bash
cd /Users/brianuckert/Working/Learning-Courses/claude-test
git add module-09/notes_api.py
git commit -m "test: trigger hook"
```

## Terminal output (hook blocked the commit)

```
==> notes-api-smoke: running smoke test before commit...
PASS  POST   /notes          → 201  (got 201)
FAIL  GET    /notes          → 200  (expected 200, got 500)
PASS  GET    /notes/1 → 200  (got 200)
PASS  PATCH  /notes/1 → 200  (got 200)
PASS  DELETE /notes/1 → 204  (got 204)
PASS  GET    /notes/999      → 404  (got 404)

Results: 5 passed, 1 failed
==> notes-api-smoke: FAIL — commit blocked
EXIT CODE: 1
```

The commit was rejected. `git commit` exited 1 and no commit was created.

## Bug reverted

The forced-500 line was removed and `notes_api.py` restored to its passing state.
