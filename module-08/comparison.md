# Constrained vs. Unconstrained Refactor — comparison

## Line counts

| Version | Lines | +added | -removed | Net change |
|---------|------:|-------:|---------:|-----------:|
| before  |   214 |      — |        — |          — |
| constrained (after/) | 189 | 147 | 172 | −25 |
| unconstrained | 186 | 151 | 179 | −28 |

The totals are nearly identical. The unconstrained version is 3 lines shorter, which shows
that constraints alone didn't inflate the result — the readability wins were the same.

## Function counts

| Version | Public functions | Private helpers |
|---------|----------------:|----------------:|
| before  | 5               | 0               |
| constrained | 5           | 0               |
| unconstrained | 5         | 4               |

The unconstrained version extracted `_validate_email`, `_validate_item`, `_validate_address`,
`_compute_shipping`, and `_build_totals` (5 new private helpers). Each is genuinely useful, but
none was *required* to fix the readability problem — they were speculative future-proofing.

## What changed unnecessarily in the unconstrained version

1. **New imports** — added `dataclasses`, `typing.Optional`. The `dataclasses` import was used
   for a `ValidationResult` class that nothing in the module actually returns (the public
   function still returns a plain tuple). The class was written but never wired in.

2. **`ValidationResult` dataclass** — defined but unused. A classic "I might need this later"
   artefact. It would change the public API if adopted; it's dead code otherwise.

3. **`_EMAIL_RE` module-level precompile** — `re.compile()` moved to module scope. A real
   performance win for hot paths, but the before/after tests can't distinguish it, and the
   before version calls `re.match()` which compiles internally anyway.

4. **Type annotations on all signatures** — e.g., `validate_order(order: object) -> tuple[bool, list[str]]`.
   Not wrong, but the constraints exercise was about readability, not type coverage. Adding
   annotations without a mypy run in CI just adds noise with no enforcement.

5. **`**totals` dict splat in `build_order_record`** — clever one-liner, but it silently passes
   every key in totals into the record (including future keys the caller didn't expect). The
   constrained version is explicit about which fields it copies.

6. **`process_order` unconditionally passes `raw.get("discount")` to `apply_discount`** —
   simplified to one line by removing the `if discount is not None` guard inside the pipeline.
   Works because `apply_discount` handles `None`, but hides the intent; constrained version
   keeps the guard visible.

## Where the unconstrained version was genuinely better

- **`_validate_item` / `_validate_email` / `_validate_address` helpers** — each is small,
  testable in isolation, and removes the one remaining deep nesting block from `validate_order`.
  The constrained version still nests 4 levels in the item-validation loop; the unconstrained
  version flattens it to 2.
- **`_build_totals` helper** — eliminates the copy-paste tax/shipping recalculation between the
  `percentage` and `flat` branches of `apply_discount`. This was the one DRY violation the
  constrained version deliberately left because the constraint list didn't cover it.
- **`sum()` in `calculate_totals`** — replacing the accumulator loop with a generator expression
  is idiomatic Python and shorter; the constrained version stayed with the loop because it wasn't
  called out in constraints.

## Lesson

The constraints prevented ~5 unnecessary changes (unused dataclass, premature type annotations,
risky dict splat, implicit None handling) while leaving 3 genuine improvements on the table
(helper extraction, DRY fix, `sum()`). A tighter constraint list — one that explicitly permitted
private helpers for shared logic — would have captured the wins and blocked the waste.

The diff sizes are nearly identical, which confirms the real risk of unconstrained refactoring is
not bloat in line count but **surface-area expansion**: new imports, new names, new contracts that
future callers may depend on and that may never be intentional.
