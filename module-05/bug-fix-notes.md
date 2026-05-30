# Bug Fix Notes — Module 5

## Bug 1 — OR → AND in search SQL

**File:** `module-04/winner/notes_api.py`, `list_notes()`

**Symptom:** `GET /notes?q=FastAPI` returns empty list when the substring appears
only in the title (not also in the body). Search silently returns nothing for
most real queries.

**Cause:** SQL clause was changed from `OR` to `AND`:
```sql
-- buggy
WHERE title LIKE ? AND body LIKE ?
-- correct
WHERE title LIKE ? OR body LIKE ?
```
With `AND`, a note only appears if `q` matches *both* title and body, which is
almost never true for a targeted search.

**Tests that caught it:**
- `test_search_by_title` — q matches title only → expected 1 result, got 0
- `test_search_by_body` — q matches body only → expected 1 result, got 0

**Fix:** Restore `OR`. One character change.

---

## Bug 2 — Missing 404 guard on PATCH

**File:** `module-04/winner/notes_api.py`, `update_note()`

**Symptom:** `PATCH /notes/999` (unknown id) raises `TypeError: 'NoneType' object
is not subscriptable` (500) instead of returning 404.

**Cause:** `_fetch_one()` (which raises HTTPException on missing row) was replaced
with a raw `conn.execute(...).fetchone()` that returns `None`. The handler then
tries to index `None` on the next line (`row["title"]`), crashing with a 500.

**Tests that caught it:**
- `test_patch_missing_returns_404` — expected 404, got 500 (TypeError)

**Fix:** Restore the `_fetch_one(conn, note_id)` call. It already handles the
None case by raising `HTTPException(status_code=404)`.
