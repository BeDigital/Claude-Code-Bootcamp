# scoring.md — Module 4 Best-of-N

Two candidates generated from the identical prompt in two separate chats,
then run through the same curl smoke test.

## Smoke-test results

| Smoke case | Spec wants | Candidate A | Candidate B |
|---|---|---|---|
| POST create | 201 | 201 PASS | 201 PASS |
| Blank title `"   "` | 422 | 422 PASS | 201 FAIL (accepts blank) |
| GET list | 200 | 200 PASS | 200 PASS |
| PATCH partial | 200 | 200 PASS | 405 FAIL (has PUT, not PATCH) |
| DELETE | 204 | 204 PASS | 204 PASS |
| 404 body | `{"error":"not found"}` | `{"detail":{…}}` PARTIAL | `{"detail":{…}}` PARTIAL |

## Per-candidate scores

```text
Candidate: a
Correctness (0–3): 3   all 6 codes match spec (201/422/200/200/204/404)
Simplicity   (0–3): 3   single file, PATCH + validator helpers, one glance
Fit          (0–3): 2   only miss is wrapped 404 body {"detail":{…}}
Total: 8 / 9
Notes: Modern lifespan handler, partial PATCH, blank-title 422. Only ding is the
       wrapped 404 envelope vs the spec's bare {"error":"not found"}.
```

```text
Candidate: b
Correctness (0–3): 1   PATCH->405 (implemented PUT not PATCH); blank title->201 not 422
Simplicity   (0–3): 2   clean, but repeats row->Note mapping in every route
Fit          (0–3): 1   wrong update verb, no input validation, wrapped 404, deprecated on_event
Total: 4 / 9
Notes: Functionally close but misses two spec requirements outright (PATCH partial
       update and 422 on invalid body).
```

## Decision

**Winner: Candidate A (8 / 9 vs 4 / 9).**

Not a tie — A satisfies two spec requirements that B fails outright: the `PATCH`
partial-update route (B implemented `PUT`, so partial update returns 405) and
blank-title validation (B accepts `"   "` as 201 instead of 422). Both candidates
share the wrapped `{"detail":{…}}` 404 body, so that axis does not separate them.

Candidate B is kept as evidence of the lift: same prompt, but one run forgot the
`PATCH` verb and input validation entirely — exactly the variance Best-of-N exists
to catch.

The winning source is copied verbatim into `winner/`.
