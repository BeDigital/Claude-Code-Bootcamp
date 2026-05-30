# ARCHITECTURE — order_processor

## Data flow

```
raw dict
   |
   v
validate_order(order)
   |-- invalid --> (None, [errors])
   |
   v
calculate_totals(order)
   |
   v
apply_discount(totals, discount)   <-- optional; skipped if no discount key
   |
   v
build_order_record(order, totals, status)
   |
   v
(record dict, [])
```

`process_order(raw)` is the single entry point that orchestrates the four steps above.

---

## Components

**`validate_order(order)`**
Accepts a raw dict; returns `(bool, list[str])`. Checks for presence and type of
`customer_email`, `items` (each with `sku`, `quantity`, `unit_price`), and
`shipping_address` (with `street`, `city`, `zip_code`, `country`). Collects all
errors before returning — does not short-circuit on first failure.

**`calculate_totals(order)`**
Accepts a validated order dict; returns a totals dict with `subtotal`, `tax`,
`shipping`, and `grand_total`. Shipping is free when subtotal ≥ `FREE_SHIPPING_THRESHOLD`.
No side effects; purely computational.

**`apply_discount(totals, discount)`**
Accepts a totals dict and an optional discount dict (`type`: `"percentage"` or `"flat"`,
`value`: numeric). Returns a new totals dict with `discount_applied` added. Returns the
original totals unchanged for any invalid or unrecognised discount.

**`build_order_record(order, totals, status)`**
Merges order fields, totals, a UTC ISO-8601 timestamp, and `status` into a flat
serializable dict. Conditionally includes `discount_applied` only when present in totals.

**`process_order(raw)`**
Pipeline orchestrator. Returns `(None, errors)` on validation failure or
`(record, [])` on success. Callers only need this function for normal use.

---

## Known limitations

1. **No persistence.** `process_order` builds a record dict but provides no storage layer;
   callers must persist the result themselves.
2. **Duplicate tax/shipping logic.** The recalculation block in `apply_discount` is copy-pasted
   for `"percentage"` and `"flat"` branches — a future bug fix must be applied in both places.
3. **`validate_order` does not check for unknown fields.** Extra keys in the order dict are
   silently ignored, which can mask upstream serialisation errors.
4. **Single tax rate.** `TAX_RATE` is a module-level constant; multi-jurisdiction or
   per-item tax rates require an interface change.
5. **No concurrency safety.** `created_at` is stamped inside `build_order_record`; if the
   caller retries on error the two records will have different timestamps for the same order.
