# Module 06 — Commit Splitter Output

## Proposed commits (Claude-generated, accepted as-is)

### Commit 1 — `chore: add .gitignore for Python and macOS artifacts`

**Subject:** `chore: add .gitignore for Python and macOS artifacts`

**Body:**
> Establishing this before staging application code prevents build
> artifacts (.venv/, __pycache__, .pytest_cache, *.db) and OS
> metadata (.DS_Store) from polluting the tree in every subsequent
> commit on this branch and on main going forward.

**Paths:** `.gitignore`

**Decision:** Accepted as-is. Must come first so subsequent git add
commands don't accidentally pull in .venv or __pycache__ directories.

---

### Commit 2 — `feat(module-02): persist task store to JSON`

**Subject:** `feat(module-02): persist task store to JSON`

**Body:**
> Landing the runtime store in the repo makes the CLI's end-state
> reproducible and verifiable — reviewers can confirm the task
> manager wrote well-formed JSON (correct schema, UTC timestamps,
> auto-incrementing IDs) without having to re-run the tool.

**Paths:** `module-02/tasks.json`

**Decision:** Accepted as-is. Isolated from the module-04 work because
it belongs to a different module's scope.

---

### Commit 3 — `docs(module-04): record Best-of-N evaluation with both candidates`

**Subject:** `docs(module-04): record Best-of-N evaluation with both candidates`

**Body:**
> Preserving both candidates (not just the winner) makes the
> evaluation auditable: reviewers can see exactly where candidate-b
> diverged from spec (PUT instead of PATCH, missing blank-title
> validation) and confirm the rubric scores are defensible, not
> just declared. scoring.md captures the decision rationale so it
> doesn't live only in someone's memory.

**Paths:** `module-04/candidates/scoring.md`,
`module-04/candidates/candidate-b/app.py`,
`module-04/candidates/candidate-b/conftest.py`,
`module-04/candidates/candidate-b/pyproject.toml`,
`module-04/candidates/candidate-b/README.md`,
`module-04/candidates/candidate-b/test_notes_api.py`

**Decision:** Accepted as-is. Grouped candidate-b source with scoring.md
because both exist to document the evaluation, not to ship production code.

---

### Commit 4 — `feat(module-04): add winning FastAPI notes API with SQLite backend`

**Subject:** `feat(module-04): add winning FastAPI notes API with SQLite backend`

**Body:**
> Candidate A scored 8/9 in the Best-of-N evaluation — it was the
> only candidate to implement PATCH partial-update correctly and
> enforce blank-title 422 validation. Promoting it to winner/ makes
> it the canonical deliverable while keeping the losing candidate in
> candidates/ as evidence of the variance Best-of-N is designed to catch.
> pyproject.toml is included so the project is self-contained for
> anyone who clones and wants to run the tests directly.

**Paths:** `module-04/winner/notes_api.py`,
`module-04/winner/README.md`,
`module-04/winner/pyproject.toml`

**Decision:** Accepted as-is. Separated from tests so the implementation
commit is reviewable on its own (no test noise in the diff).

---

### Commit 5 — `test(module-04): add pytest suite covering all CRUD paths and error codes`

**Subject:** `test(module-04): add pytest suite covering all CRUD paths and error codes`

**Body:**
> Each test function receives its own isolated SQLite file via
> monkeypatch so failures cannot bleed between runs — this was
> critical because the lifespan-managed init_db() fires inside the
> TestClient context, not at module load time. The suite covers
> CREATE/LIST/SEARCH/GET/PATCH/DELETE happy paths plus 404 and 422
> error branches, giving reviewers confidence that the winner's
> implementation is correct end-to-end, not just smoke-tested.

**Paths:** `module-04/winner/test_notes_api.py`,
`module-04/winner/conftest.py`

**Decision:** Accepted as-is. Keeping tests in a separate commit follows
the convention that `test(...)` commits are distinct from `feat(...)` commits,
making `git log --all-match --grep=test` useful later.
