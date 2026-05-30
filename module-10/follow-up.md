# Stretch Challenge — Observability Axis Follow-Up

**Axis addressed:** Observability (RED)  
**Change made:** Added `GET /health` endpoint to `module-04/winner/notes_api.py`

---

## What was added

```python
@app.get("/health")
def health_check():
    """Return 200 with a live DB ping if the service is operational."""
    with get_db() as conn:
        conn.execute("SELECT 1")
    return {"status": "ok", "db": "connected"}
```

The endpoint:
- Returns `200 {"status": "ok", "db": "connected"}` when the SQLite connection is healthy.
- Returns `500` if the DB is unreachable (e.g., locked, disk full, path missing) — the exception propagates naturally from `get_db()`.
- Costs nothing: re-uses the existing `get_db()` helper, no new dependencies.

## Why this axis, why this step

Observability was rated RED because the service had zero operational visibility.  
A `/health` endpoint is the minimum surface needed for:
- Load balancer / container orchestrator liveness probes.
- On-call engineers to distinguish "is the process up?" from "is the DB reachable?".
- Any uptime monitoring tool (UptimeRobot, Datadog synthetics, k8s readinessProbe).

It does not require authentication (health checks are public by convention), introduces no new dependencies, and is 4 lines of code.

## Verification

All 32 existing tests still pass after the change:

```
pytest test_notes_api.py -q
................................
32 passed in 1.38s
```

## What remains on the Observability axis

- Structured request logging (e.g., `uvicorn` JSON log format or a middleware).
- A `/metrics` endpoint or Prometheus scraping.
- Distributed tracing (`opentelemetry-sdk`).

These are real next steps, but the health endpoint unblocks deployment-time probing immediately — the highest-value/lowest-effort improvement available.
