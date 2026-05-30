# Candidates — Bookmarks API Best-of-2

Both candidates were generated from the same PROMPT.md in independent chats with fresh context.

---

## Candidate A — Plain `str` URL field

**Key design choices:**
- `url` stored as a plain `str`; a Pydantic `field_validator` rejects blank/whitespace at the boundary.
- Tag filter: `WHERE tag = ?` — exact match, parameterized.
- `_fetch_one()` helper identical in shape to the Notes API pattern.
- No extra imports beyond what Notes API uses.
- `created_at` only; no `updated_at` (no PATCH endpoint).
- `tag` defaults to `""`, stored as-is.

**Rubric scores (Correctness · Simplicity · Fit):**
- Correctness: **Pass** — all five endpoints, 404 on unknown id, 422 on blank fields, exact tag match.
- Simplicity: **Pass** — 90 lines, zero new imports, no abstractions beyond what the spec requires.
- Fit: **Pass** — mirrors Notes API structure line-for-line; a maintainer familiar with module-04 can orient instantly.

---

## Candidate B — Pydantic `AnyUrl` for URL validation

**Key design choices:**
- `url` typed as `pydantic.AnyUrl`, giving automatic scheme/host validation.
- Everything else identical to Candidate A.

**Rubric scores:**
- Correctness: **Conditional pass** — `AnyUrl` normalizes the stored URL: `"https://example.com"` becomes `"https://example.com/"` (trailing slash added). The smoke test POSTs the un-normalized form and then GETs it back — the round-trip value silently changes, which a downstream caller would not expect.
- Simplicity: **Fail** — imports `pydantic.AnyUrl` and triggers Pydantic's URL parsing machinery for a field that the spec describes as a plain string. The validation benefit (scheme check) is real but out-of-scope.
- Fit: **Partial** — the Notes API uses only `str` fields; introducing a semantic type for one field is inconsistent.

---

## Winner: Candidate A

Candidate B's URL normalization is the deciding defect: it changes the stored value from what the user submitted, breaking round-trip fidelity without any spec requirement to do so. Candidate A is also simpler and consistent with the established Notes API pattern, which scores higher on Fit. The only capability Candidate A lacks — scheme validation — is not in the functional contract.
