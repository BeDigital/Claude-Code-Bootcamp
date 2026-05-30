# Multi-Agent Fan-Out — Candidate Comparison

**Date:** 2026-05-30
**Pattern:** Lead + 2 parallel workers
**Task:** Smoke-test two candidate Notes API implementations; lead picks the winner.

---

## Architecture

```
Lead (this agent)
├── Worker A  → module-04/candidates/candidate-a  port 8100  notes_api:app
└── Worker B  → module-04/candidates/candidate-b  port 8101  app:app
```

Workers ran in parallel (single `Agent()` call with two concurrent subagents). Each received only the path, port, and module name for their candidate — no access to the other candidate's code.

---

## Worker A — candidate-a results

```
PASS  POST   /notes          → 201  (got 201)
PASS  GET    /notes          → 200  (got 200)
PASS  GET    /notes/1 → 200  (got 200)
PASS  PATCH  /notes/1 → 200  (got 200)
PASS  DELETE /notes/1 → 204  (got 204)
PASS  GET    /notes/999      → 404  (got 404)

Results: 6 passed, 0 failed
```

Exit code: **0**

---

## Worker B — candidate-b results

```
PASS  POST   /notes          → 201  (got 201)
PASS  GET    /notes          → 200  (got 200)
PASS  GET    /notes/1 → 200  (got 200)
FAIL  PATCH  /notes/1 → 200  (expected 200, got 405)
PASS  DELETE /notes/1 → 204  (got 204)
PASS  GET    /notes/999      → 404  (got 404)

Results: 5 passed, 1 failed
```

Exit code: **1**

Failure: `PATCH /notes/{id}` returns 405 (Method Not Allowed) — the endpoint is not implemented or is registered under a different HTTP verb in `app.py`.

---

## Lead decision

**Winner: candidate-a** — 6/6 checks pass. Candidate-b fails the PATCH contract, which is a hard API requirement. No tie-breaking needed.

This matches the original module-04 Best-of-N evaluation (`module-04/candidates/scoring.md`), which also selected candidate-a.

---

## Diagnostic: first attempt failure

Both workers initially failed with:

```
error: No `project` table found in: .../pyproject.toml
JSONDecodeError: Expecting value: line 1 column 1 (char 0)
```

**Root cause:** `uv run` found `pyproject.toml` in each candidate directory (pytest config only, no `[project]` table) and refused to start. Fix: add `--no-project` flag so uv uses only the `--with` deps and ignores local project config. The script was updated and both workers re-ran successfully.

This is a real fan-out benefit: the failure mode appeared simultaneously in both workers, making the common cause obvious. A sequential run would have shown the same thing but taken twice as long to surface.

---

## When fan-out is worse than a single agent

**Fan-out added value here** because the two candidates are genuinely independent — different ports, different code paths, no shared state. Running them in parallel halved wall-clock time.

**Fan-out would be worse** in these cases:

| Situation | Why fan-out loses |
|-----------|-------------------|
| Candidates share a port or database file | Race conditions; tests interfere with each other |
| One candidate depends on the other's output | Sequential dependency defeats parallelism |
| The comparison logic is complex | Synthesizing two agents' results is harder than reading one clean output |
| Setup cost dominates (e.g., slow `uv` installs) | Each worker pays the install cost separately; a single agent reuses the cache |
| N=2 with trivial test duration | Subagent overhead (context window, tool latency) can exceed the time saved |

**The real learning:** Fan-out is a throughput tool, not a correctness tool. It did not find anything that sequential runs would have missed — it just found it faster. The diagnostic value came from seeing the same error in both workers at once, which confirmed the bug was environmental (uv config), not candidate-specific. That pattern — correlated failures pointing to shared infrastructure — is the clearest signal that fan-out is earning its overhead.
