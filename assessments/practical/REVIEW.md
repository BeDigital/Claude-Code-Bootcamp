# Code Review — Bookmarks API

Rubric applied: `module-05/code-review-rubric.md`
File reviewed: `assessments/practical/service/app.py`

---

## Checklist

- [x] **Does every SQL query with OR/AND use the right logical operator?**
  N/A — the only multi-condition query is `WHERE tag = ?` (single condition). No OR/AND in this service.

- [x] **Does every handler that fetches a row raise 404 (not 500) when missing?**
  PASS — both `get_bookmark` and `delete_bookmark` call `_fetch_one()`, which raises
  `HTTPException(status_code=404)` on `None`. No raw `fetchone()` without a None guard.

- [x] **Are timestamps generated with `timezone.utc`?**
  PASS — `_now()` returns `datetime.now(timezone.utc).isoformat()`. No bare `datetime.now()` anywhere.

- [x] **Do the tests import the real module, not a copy of it?**
  PASS — `test_bookmarks_api.py` imports `app` and monkeypatches `app.DB_PATH` on the live module
  object. Tests run against the real code; no frozen copy.

- [ ] **Does the service expose a health endpoint?** ← **FAIL — fixed below**
  No `GET /health` endpoint existed in the initial draft. A DB-locked or disk-full failure is
  completely invisible until a caller reports a 500 — identical to the Observability RED finding
  in `module-10/production-readiness-report.md`.

- [ ] **Do 404 tests assert the response body, not just the status code?** ← **FAIL — fixed below**
  Initial `Test404` asserted only `r.status_code == 404`. The body shape
  `{"detail": {"error": "not found"}}` was unverified, making it impossible to catch a handler
  that raises 404 with the wrong detail type.

- [x] **Does PATCH/PUT preserve unchanged fields (no silent nulling)?**
  N/A — no PATCH/PUT in the Bookmarks API (bookmarks are immutable by design).

- [x] **Is input validation applied at the boundary, not assumed internally?**
  PASS — `BookmarkIn` validators reject blank `url` and `title` before any DB access.

---

## Fix 1 — Add `/health` endpoint (service/app.py)

**Item:** No health endpoint; Observability is invisible.

**Before:** No `GET /health` route.

**After** (added to `app.py` before the bookmark routes):
```python
@app.get("/health")
def health_check():
    """Return 200 with a live DB ping if the service is operational."""
    with get_db() as conn:
        conn.execute("SELECT 1")
    return {"status": "ok", "db": "connected"}
```

**Why it matters:** Any on-call engineer or readiness probe needs a single URL to confirm
the service and its DB are reachable. Without it, a crashed DB is invisible until a user
reports a failure. This is the smallest step that gives the service an observable health signal.

---

## Fix 2 — Assert 404 response body, not only status code (tests/)

**Item:** "Do 404 tests assert the response body, not just the status code?"

**Before:**
```python
def test_get_nonexistent_returns_404(self, client):
    assert client.get(f"/bookmarks/{self.GHOST}").status_code == 404
```

**After:**
```python
def test_get_nonexistent_returns_404(self, client):
    r = client.get(f"/bookmarks/{self.GHOST}")
    assert r.status_code == 404
    assert r.json()["detail"] == {"error": "not found"}
```

**Why it matters:** A handler that passes `detail="not found"` (string) instead of
`detail={"error": "not found"}` (dict) would pass status-code-only assertions but break any
caller that parses the body. The body assertion locks the contract.
