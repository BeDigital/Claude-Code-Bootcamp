# notes-api-smoke Invocation

**Skill:** `module-09/skill/SKILL.md`
**Target:** `module-09/notes_api.py`
**Port:** 8099
**Date:** 2026-05-30

## Command

```bash
cd /Users/brianuckert/Working/Learning-Courses/claude-test
bash module-09/smoke_test.sh module-09 8099
```

## Output

```
PASS  POST   /notes          → 201  (got 201)
PASS  GET    /notes          → 200  (got 200)
PASS  GET    /notes/1 → 200  (got 200)
PASS  PATCH  /notes/1 → 200  (got 200)
PASS  DELETE /notes/1 → 204  (got 204)
PASS  GET    /notes/999      → 404  (got 404)

Results: 6 passed, 0 failed
```

Exit code: 0
