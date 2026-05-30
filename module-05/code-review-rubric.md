# Code Review Rubric — AI-Generated Code

Use for any Claude-generated backend code. Each check is yes/no, ≤ 30 seconds.

---

- [ ] **Does every SQL query with OR/AND use the right logical operator?**
      AI frequently swaps OR↔AND in multi-column searches, producing results that
      are silently empty or too broad.

- [ ] **Does every handler that fetches a row raise 404 (not 500) when missing?**
      AI often handles the happy path correctly but omits the null-row guard,
      turning a missing-resource call into a 500 crash.

- [ ] **Are timestamps generated with `timezone.utc`?**
      `datetime.now()` without timezone produces local time. Any downstream system
      that assumes UTC will silently corrupt time-ordered data.

- [ ] **Do the tests import the real module, not a copy of it?**
      AI frequently pastes a frozen copy of the app into the test file. Green tests
      against a copy are worthless — they never catch changes to the real code.

- [ ] **Do 404 tests assert the response body, not just the status code?**
      `{"detail": {"error": "not found"}}` vs `{"error": "not found"}` is a real
      contract difference that status-code-only tests miss entirely.

- [ ] **Does PATCH/PUT preserve unchanged fields (no silent nulling)?**
      AI partial-update handlers often overwrite omitted fields with null instead
      of keeping the existing value from the DB row.

- [ ] **Is input validation applied at the boundary, not assumed internally?**
      AI skips blank/whitespace checks on string fields that "should never be
      empty", trusting the caller instead of enforcing the invariant itself.
