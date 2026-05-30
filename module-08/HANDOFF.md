# HANDOFF — order_processor refactor

## What changed
- **Early returns replaced nested else-chains.** Five functions had 3-6 levels of nesting; guard
  clauses now short-circuit immediately, cutting max indentation from 8 levels to 4.
- **Local variables renamed throughout.** Single-letter and abbreviated names (`o`, `errs`, `itm`,
  `idx`, `s`, `q`, `p`, `ln`, `sub`, `t`, `sh`, `gt`, `res`, `tp`, `v`, `amt`, `d`, `rec`, `ts`,
  `da`, `fld`, `addr`) replaced with self-describing names across all five functions.
- **Dead code removed.** The bare `else: pass` in `build_order_record` and the unnecessary
  `else` branch after `if ok == False` in `process_order` were deleted.

## Why
The original was correct but unreadable: heavy nesting forced readers to track 5+ open braces to
understand a single conditional path. A 24-minute timed exercise with 30 passing tests was the
ideal moment to make the logic visible without touching behavior.

## Risk + how to roll back
Risk is low — public signatures and all 30 tests are unchanged. To roll back:
```
cp module-08/solution/before/order_processor.py module-08/after/order_processor.py
```
The `before/` snapshot is committed; `git checkout` also works.

## Watch-outs for the next engineer
- `apply_discount` still duplicates the tax/shipping recalculation block for `percentage` and
  `flat` types. It was left as-is because extracting a helper was not in `constraints.md`; add
  it next time if you touch both branches.
- `validate_order` accumulates *all* errors before returning — it intentionally does not stop
  at the first failure. Don't add an early `return` inside the item loop.
- `if len(errors) == 0` at the end of `validate_order` is the only place that decides validity;
  error presence is the single source of truth, not a separate boolean flag.
