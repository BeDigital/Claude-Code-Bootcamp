# Module 06 — Commit Splitter Output

## Proposed commits (Claude-generated, accepted as-is)

### Commit 1 — `chore: add .gitignore for Python and macOS artifacts`

**Body:**
> Establishing this before staging application code prevents build
> artifacts (.venv/, __pycache__, .pytest_cache, *.db) and OS
> metadata (.DS_Store) from polluting the tree in every subsequent
> commit on this branch and on main going forward.

**Paths:** `.gitignore`

**Decision:** Accepted. Must come first so subsequent git add commands
don't accidentally pull in .venv or __pycache__ directories.

---

### Commit 2 — `feat(module-02): persist task store to JSON`

**Body:**
> Landing the runtime store in the repo makes the CLI's end-state
> reproducible and verifiable — reviewers can confirm the task manager
> wrote well-formed JSON (correct schema, UTC timestamps, auto-
> incrementing IDs) without having to re-run the tool.

**Paths:** `module-02/tasks.json`

**Decision:** Accepted. Isolated from module-04 because it belongs to a
different module's scope.

---

### Commit 3 — `docs(module-04): record Best-of-N evaluation with both candidates`

**Body:**
> Preserving both candidates (not just the winner) makes the evaluation
> auditable: reviewers can see exactly where candidate-b diverged from
> spec (PUT instead of PATCH, missing blank-title validation) and confirm
> the rubric scores are defensible. scoring.md captures the decision
> rationale so it doesn't live only in someone's memory.

**Paths:** `module-04/candidates/scoring.md`,
`module-04/candidates/candidate-b/`

**Decision:** Accepted. Grouped candidate-b source with scoring.md because
both exist to document the evaluation, not to ship production code.

---

### Commit 4 — `feat(module-04): add winning FastAPI notes API with SQLite backend`

**Body:**
> Candidate A scored 8/9 in the Best-of-N evaluation — it was the only
> candidate to implement PATCH partial-update correctly and enforce
> blank-title 422 validation. Promoting it to winner/ makes it the
> canonical deliverable while keeping the losing candidate as evidence of
> variance. pyproject.toml included so the project is self-contained.

**Paths:** `module-04/winner/notes_api.py`, `module-04/winner/README.md`,
`module-04/winner/pyproject.toml`

**Decision:** Accepted. Separated from tests so the implementation commit
is reviewable on its own.

---

### Commit 5 — `test(module-04): add pytest suite covering all CRUD paths and error codes`

**Body:**
> Each test function receives its own isolated SQLite file via monkeypatch
> so failures cannot bleed between runs — this was critical because the
> lifespan-managed init_db() fires inside the TestClient context, not at
> module load time. Covers CREATE/LIST/SEARCH/GET/PATCH/DELETE happy paths
> plus 404 and 422 error branches.

**Paths:** `module-04/winner/test_notes_api.py`, `module-04/winner/conftest.py`

**Decision:** Accepted. Conventional Commit `test(...)` prefix keeps
implementation and test commits cleanly separable in git log.

---

### Commit 6 — `docs(repo): add CLAUDE.md with stack, conventions, commands, do-not, glossary`

**Body:**
> Without CLAUDE.md every prompt requires re-explaining the stack and
> conventions. Each line in this file actively changes Claude's behavior
> on future prompts — lines that are only documentation were omitted.
> The datetime rule (always timezone.utc) is the highest-signal convention
> because it silently corrupts data in downstream systems when violated.

**Paths:** `CLAUDE.md`

**Decision:** Accepted. Repo-root placement ensures Claude Code loads it
automatically on every session.

---

### Commit 7 — `docs(module-03): add proof.png showing Claude obeying datetime convention`

**Body:**
> proof.png captures a fresh-session prompt (no convention re-stated)
> where Claude generated datetime.now(timezone.utc).isoformat() — the
> high-signal rule from CLAUDE.md. This is the required evidence that the
> CLAUDE.md is loaded and steering behavior, not just sitting as docs.

**Paths:** `module-03/proof.png`

**Decision:** Accepted. Kept separate from the CLAUDE.md commit so the
proof is a distinct, independently verifiable artifact.

---

### Commit 8 — `feat(module-05): add test suite, bug fixes, and code review rubric`

**Body:**
> The 19-test suite imports the real notes_api module and patches DB_PATH
> per-test — avoiding the "copied app in test file" trap that produces
> green tests against a frozen snapshot. Seeding and catching both
> BUGS.md issues (OR→AND search, missing PATCH 404 guard) confirmed the
> suite actually detects regressions. The rubric encodes the blind spots
> found during this exercise as a reusable yes/no checklist.

**Paths:** `module-05/tests/`, `module-05/bug-fix-notes.md`,
`module-05/code-review-rubric.md`

**Decision:** Accepted as single commit because all three artifacts are
outputs of one exercise and have no value independently.
