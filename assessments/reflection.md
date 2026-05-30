# Code Review Reflection

## Bugs

**Bug 1 — OR→AND in SQL search (`module-04/winner/notes_api.py`, `list_notes`)**

Symptom: `GET /notes?q=FastAPI` returned an empty list whenever the search term appeared only in the title and not also in the body. The response was HTTP 200 with `[]` — no error, no signal, just silence.

Root cause: Claude assumed the search should require a match in *both* columns, emitting `WHERE title LIKE ? AND body LIKE ?` instead of `OR` — a logical-operator confusion dressed up as a correctness choice.

Fix: one character, `AND` → `OR`. The `_search_notes` helper already existed; the operator was the only wrong thing.

Detection: the test suite. `test_search_by_title` and `test_search_by_body` each seeded a note that matched only one column, then asserted a non-empty result. Both failed immediately.

---

**Bug 2 — Missing 404 guard on PATCH (`module-04/winner/notes_api.py`, `update_note`)**

Symptom: `PATCH /notes/999` on a non-existent note returned HTTP 500 with a `TypeError: 'NoneType' object is not subscriptable` traceback instead of a clean 404.

Root cause: Claude replaced the shared `_fetch_one()` call with a raw `conn.execute(...).fetchone()` — an implicit assumption that the row would always exist, leaving the `None` case unhandled one line later.

Fix: restore the `_fetch_one(conn, note_id)` call. It already raises `HTTPException(404)` on a missing row; nothing else needed to change.

Detection: the test suite. `test_patch_missing_returns_404` expected 404, received 500, and named the symptom exactly.

---

## Rubric

The rubric item that earned its place: **"Does every SQL query with OR/AND use the right logical operator?"** It was written specifically because Bug 1 had already burned me once, and it fired again on the next review pass — which is precisely the kind of return that justifies a permanent checklist entry.

The item I am considering dropping: **"Do 404 tests assert the response body, not just the status code?"** In practice, every 404 check I ran cared only whether the endpoint *crashed* (500) or *acknowledged a miss* (404). The body shape is a useful contract, but auditing it adds thirty seconds per endpoint on a list designed to be thirty seconds *total*. I would demote it to a separate API-contract checklist rather than keep it in the quick-pass rubric.

The item I would add tomorrow: **"Does any generated code define a class, function, or import that is never referenced?"** The module-08 unconstrained refactor produced a `ValidationResult` dataclass that was fully defined but never returned by any public function. Dead code from Claude is common precisely because the model fills in what *might* be needed rather than what *is* needed.

---

## Carry-Over

The skill I will reach for first on Monday morning is **release-notes**.

At Mizuho I cut deployment packages weekly and hand off change summaries to a downstream infrastructure team that does not read commit history. Today I do that by scanning `git log --oneline` and rewriting it manually — a fifteen-minute task that produces inconsistent output depending on how rushed I am. The `release-notes` skill enforces the four-bucket structure (Highlights / Added / Changed / Fixed) every time and forces me to state the migration path explicitly, which is the one piece my current summaries most often omit.

The `notes-api-smoke` skill is also a natural PreToolUse hook on Bash: `module-09/hook-fired.md` proved it catches a forced-500 before it reaches the remote — fifteen seconds of gate that would have prevented a rollback.

Fan-out is the wrong tool when candidates share state or when the lead needs each result before constructing the next prompt; in those cases a sequential chain is safer and easier to debug.

---

## Constraint

Writing constraints.md before touching module-08 changed one concrete habit: I now distinguish between *what I want to stop* and *what I want to allow*. The unconstrained refactor introduced a `ValidationResult` dataclass, premature type annotations, and a `**totals` dict splat — none of which were in `constraints.md`'s "must NOT change" list, because I hadn't thought to permit or forbid them. The constrained version blocked all three. Going forward I will write an explicit "what may change" list alongside every refactor brief I give Claude, because the model will fill any unspecified space with plausible-looking additions that expand surface area without being wrong enough to trigger a test failure.
