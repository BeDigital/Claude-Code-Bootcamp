# Refactor Constraints — module-08

Written before any refactoring. Every change in `after/` must be justified by a line here.

## Hard constraints (non-negotiable)

1. **No new files.** All code stays in `order_processor.py`; test file is not modified.
2. **No new dependencies.** Imports at module level are unchanged.
3. **Public function signatures unchanged.** `validate_order`, `calculate_totals`, `apply_discount`, `build_order_record`, `process_order` keep their exact signatures.
4. **Byte-identical behavior.** All 30 existing tests must pass without modification.
5. **No comments unless they explain a non-obvious *why*.** Remove any comments that just restate the code.

## What may change

6. **Replace nested conditionals with early returns** when doing so shortens the function body. Target: `validate_order` (5+ levels deep), `apply_discount` (4 levels deep), `process_order` (unnecessary `if ok == False` branch).
7. **Rename local variables** only when the new name is materially clearer:
   - `o` → `order` (function parameter in `validate_order`, `calculate_totals`, `build_order_record`)
   - `errs` → `errors`
   - `itms` → `items`
   - `itm` → `item`
   - `idx` → `i`
   - `s` (sku value) → `sku`
   - `q` → `qty`
   - `p` → `price`
   - `ln` (line total) → `line_total`
   - `sub` → `subtotal`
   - `t` (tax) → `tax`
   - `sh` → `shipping`
   - `gt` → `grand_total`
   - `res` → `totals`
   - `tp` → `discount_type`
   - `v` → `value`
   - `amt` → `discount_amount`
   - `new_sub` → `new_subtotal`
   - `new_tax` → (keep, already clear)
   - `new_sh` → `new_shipping`
   - `new_gt` → `new_grand_total`
   - `d` (discount) → `discount`
   - `da` → `discount_amount`
   - `rec` → `record`
   - `fld` → `field`
   - `addr` → `address`
   - `e` (email) → `email`
8. **Remove dead `else` branches** after a `return` statement — they add indentation with no logical value.
9. **Remove the bare `pass` statement** in `build_order_record` (the empty `else` after `discount_applied` check).
10. **Replace `if ok == False`** with `if not ok` in `process_order`.

## What must NOT change

- Module-level constants (`STATUS_*`, `TAX_RATE`, `FREE_SHIPPING_THRESHOLD`, `SHIPPING_COST`, `MAX_QUANTITY`)
- The `__doc__` strings on each function
- Return types and shapes (dicts, tuples, lists)
- The `round()` precision on all monetary values
