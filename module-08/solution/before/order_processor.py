#!/usr/bin/env python3
"""order_processor — processes and validates e-commerce orders."""

import json
import re
from datetime import datetime, timezone


STATUS_PENDING = "pending"
STATUS_APPROVED = "approved"
STATUS_REJECTED = "rejected"
STATUS_SHIPPED = "shipped"

TAX_RATE = 0.08
FREE_SHIPPING_THRESHOLD = 100.0
SHIPPING_COST = 9.99
MAX_QUANTITY = 500


def validate_order(o):
    """Validate an order dict and return (is_valid, errors)."""
    errs = []
    if o is None:
        errs.append("order is None")
        return False, errs
    else:
        if "customer_email" not in o:
            errs.append("missing customer_email")
        else:
            e = o["customer_email"]
            if not isinstance(e, str):
                errs.append("customer_email must be string")
            else:
                if not re.match(r"[^@]+@[^@]+\.[^@]+", e):
                    errs.append("customer_email invalid format")
        if "items" not in o:
            errs.append("missing items")
        else:
            itms = o["items"]
            if not isinstance(itms, list):
                errs.append("items must be a list")
            else:
                if len(itms) == 0:
                    errs.append("items list is empty")
                else:
                    for idx, itm in enumerate(itms):
                        if "sku" not in itm:
                            errs.append(f"item {idx}: missing sku")
                        else:
                            s = itm["sku"]
                            if not isinstance(s, str) or len(s) == 0:
                                errs.append(f"item {idx}: sku must be non-empty string")
                        if "quantity" not in itm:
                            errs.append(f"item {idx}: missing quantity")
                        else:
                            q = itm["quantity"]
                            if not isinstance(q, int):
                                errs.append(f"item {idx}: quantity must be int")
                            else:
                                if q <= 0:
                                    errs.append(f"item {idx}: quantity must be positive")
                                else:
                                    if q > MAX_QUANTITY:
                                        errs.append(f"item {idx}: quantity exceeds max {MAX_QUANTITY}")
                        if "unit_price" not in itm:
                            errs.append(f"item {idx}: missing unit_price")
                        else:
                            p = itm["unit_price"]
                            if not isinstance(p, (int, float)):
                                errs.append(f"item {idx}: unit_price must be numeric")
                            else:
                                if p < 0:
                                    errs.append(f"item {idx}: unit_price cannot be negative")
        if "shipping_address" not in o:
            errs.append("missing shipping_address")
        else:
            addr = o["shipping_address"]
            if not isinstance(addr, dict):
                errs.append("shipping_address must be dict")
            else:
                for fld in ["street", "city", "zip_code", "country"]:
                    if fld not in addr:
                        errs.append(f"shipping_address missing {fld}")
                    else:
                        if not isinstance(addr[fld], str) or len(addr[fld].strip()) == 0:
                            errs.append(f"shipping_address.{fld} must be non-empty string")
    if len(errs) == 0:
        return True, []
    else:
        return False, errs


def calculate_totals(o):
    """Calculate subtotal, tax, shipping, and grand total for an order."""
    sub = 0.0
    for itm in o["items"]:
        q = itm["quantity"]
        p = itm["unit_price"]
        ln = q * p
        sub = sub + ln
    t = sub * TAX_RATE
    if sub >= FREE_SHIPPING_THRESHOLD:
        sh = 0.0
    else:
        sh = SHIPPING_COST
    gt = sub + t + sh
    res = {
        "subtotal": round(sub, 2),
        "tax": round(t, 2),
        "shipping": round(sh, 2),
        "grand_total": round(gt, 2),
    }
    return res


def apply_discount(totals, d):
    """Apply a discount dict to pre-calculated totals and return updated totals."""
    if d is None:
        return totals
    else:
        if "type" not in d:
            return totals
        else:
            tp = d["type"]
            if tp == "percentage":
                if "value" not in d:
                    return totals
                else:
                    v = d["value"]
                    if not isinstance(v, (int, float)):
                        return totals
                    else:
                        if v < 0 or v > 100:
                            return totals
                        else:
                            amt = totals["subtotal"] * (v / 100)
                            new_sub = round(totals["subtotal"] - amt, 2)
                            new_tax = round(new_sub * TAX_RATE, 2)
                            if new_sub >= FREE_SHIPPING_THRESHOLD:
                                new_sh = 0.0
                            else:
                                new_sh = SHIPPING_COST
                            new_gt = round(new_sub + new_tax + new_sh, 2)
                            return {
                                "subtotal": new_sub,
                                "tax": new_tax,
                                "shipping": new_sh,
                                "grand_total": new_gt,
                                "discount_applied": round(amt, 2),
                            }
            elif tp == "flat":
                if "value" not in d:
                    return totals
                else:
                    v = d["value"]
                    if not isinstance(v, (int, float)):
                        return totals
                    else:
                        if v < 0:
                            return totals
                        else:
                            new_sub = round(max(0.0, totals["subtotal"] - v), 2)
                            new_tax = round(new_sub * TAX_RATE, 2)
                            if new_sub >= FREE_SHIPPING_THRESHOLD:
                                new_sh = 0.0
                            else:
                                new_sh = SHIPPING_COST
                            new_gt = round(new_sub + new_tax + new_sh, 2)
                            return {
                                "subtotal": new_sub,
                                "tax": new_tax,
                                "shipping": new_sh,
                                "grand_total": new_gt,
                                "discount_applied": round(min(v, totals["subtotal"]), 2),
                            }
            else:
                return totals


def build_order_record(o, totals, status=STATUS_PENDING):
    """Combine order data, totals, and status into a serializable record."""
    ts = datetime.now(timezone.utc).isoformat()
    rec = {}
    rec["customer_email"] = o["customer_email"]
    rec["items"] = o["items"]
    rec["shipping_address"] = o["shipping_address"]
    rec["subtotal"] = totals["subtotal"]
    rec["tax"] = totals["tax"]
    rec["shipping"] = totals["shipping"]
    rec["grand_total"] = totals["grand_total"]
    if "discount_applied" in totals:
        da = totals["discount_applied"]
        rec["discount_applied"] = da
    else:
        pass
    rec["status"] = status
    rec["created_at"] = ts
    return rec


def process_order(raw):
    """Full pipeline: validate, calculate, build record; return (record, errors)."""
    ok, errs = validate_order(raw)
    if ok == False:
        return None, errs
    else:
        t = calculate_totals(raw)
        d = None
        if "discount" in raw:
            d = raw["discount"]
        if d is not None:
            t = apply_discount(t, d)
        rec = build_order_record(raw, t)
        return rec, []
