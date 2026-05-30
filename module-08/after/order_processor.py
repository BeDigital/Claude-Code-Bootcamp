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


def validate_order(order):
    """Validate an order dict and return (is_valid, errors)."""
    errors = []
    if order is None:
        errors.append("order is None")
        return False, errors

    if "customer_email" not in order:
        errors.append("missing customer_email")
    else:
        email = order["customer_email"]
        if not isinstance(email, str):
            errors.append("customer_email must be string")
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            errors.append("customer_email invalid format")

    if "items" not in order:
        errors.append("missing items")
    else:
        items = order["items"]
        if not isinstance(items, list):
            errors.append("items must be a list")
        elif len(items) == 0:
            errors.append("items list is empty")
        else:
            for i, item in enumerate(items):
                if "sku" not in item:
                    errors.append(f"item {i}: missing sku")
                else:
                    sku = item["sku"]
                    if not isinstance(sku, str) or len(sku) == 0:
                        errors.append(f"item {i}: sku must be non-empty string")

                if "quantity" not in item:
                    errors.append(f"item {i}: missing quantity")
                else:
                    qty = item["quantity"]
                    if not isinstance(qty, int):
                        errors.append(f"item {i}: quantity must be int")
                    elif qty <= 0:
                        errors.append(f"item {i}: quantity must be positive")
                    elif qty > MAX_QUANTITY:
                        errors.append(f"item {i}: quantity exceeds max {MAX_QUANTITY}")

                if "unit_price" not in item:
                    errors.append(f"item {i}: missing unit_price")
                else:
                    price = item["unit_price"]
                    if not isinstance(price, (int, float)):
                        errors.append(f"item {i}: unit_price must be numeric")
                    elif price < 0:
                        errors.append(f"item {i}: unit_price cannot be negative")

    if "shipping_address" not in order:
        errors.append("missing shipping_address")
    else:
        address = order["shipping_address"]
        if not isinstance(address, dict):
            errors.append("shipping_address must be dict")
        else:
            for field in ["street", "city", "zip_code", "country"]:
                if field not in address:
                    errors.append(f"shipping_address missing {field}")
                elif not isinstance(address[field], str) or len(address[field].strip()) == 0:
                    errors.append(f"shipping_address.{field} must be non-empty string")

    if len(errors) == 0:
        return True, []
    return False, errors


def calculate_totals(order):
    """Calculate subtotal, tax, shipping, and grand total for an order."""
    subtotal = 0.0
    for item in order["items"]:
        line_total = item["quantity"] * item["unit_price"]
        subtotal += line_total
    tax = subtotal * TAX_RATE
    shipping = 0.0 if subtotal >= FREE_SHIPPING_THRESHOLD else SHIPPING_COST
    grand_total = subtotal + tax + shipping
    return {
        "subtotal": round(subtotal, 2),
        "tax": round(tax, 2),
        "shipping": round(shipping, 2),
        "grand_total": round(grand_total, 2),
    }


def apply_discount(totals, discount):
    """Apply a discount dict to pre-calculated totals and return updated totals."""
    if discount is None:
        return totals
    if "type" not in discount:
        return totals

    discount_type = discount["type"]

    if discount_type == "percentage":
        if "value" not in discount:
            return totals
        value = discount["value"]
        if not isinstance(value, (int, float)):
            return totals
        if value < 0 or value > 100:
            return totals
        discount_amount = totals["subtotal"] * (value / 100)
        new_subtotal = round(totals["subtotal"] - discount_amount, 2)
        new_tax = round(new_subtotal * TAX_RATE, 2)
        new_shipping = 0.0 if new_subtotal >= FREE_SHIPPING_THRESHOLD else SHIPPING_COST
        new_grand_total = round(new_subtotal + new_tax + new_shipping, 2)
        return {
            "subtotal": new_subtotal,
            "tax": new_tax,
            "shipping": new_shipping,
            "grand_total": new_grand_total,
            "discount_applied": round(discount_amount, 2),
        }

    if discount_type == "flat":
        if "value" not in discount:
            return totals
        value = discount["value"]
        if not isinstance(value, (int, float)):
            return totals
        if value < 0:
            return totals
        new_subtotal = round(max(0.0, totals["subtotal"] - value), 2)
        new_tax = round(new_subtotal * TAX_RATE, 2)
        new_shipping = 0.0 if new_subtotal >= FREE_SHIPPING_THRESHOLD else SHIPPING_COST
        new_grand_total = round(new_subtotal + new_tax + new_shipping, 2)
        return {
            "subtotal": new_subtotal,
            "tax": new_tax,
            "shipping": new_shipping,
            "grand_total": new_grand_total,
            "discount_applied": round(min(value, totals["subtotal"]), 2),
        }

    return totals


def build_order_record(order, totals, status=STATUS_PENDING):
    """Combine order data, totals, and status into a serializable record."""
    record = {
        "customer_email": order["customer_email"],
        "items": order["items"],
        "shipping_address": order["shipping_address"],
        "subtotal": totals["subtotal"],
        "tax": totals["tax"],
        "shipping": totals["shipping"],
        "grand_total": totals["grand_total"],
        "status": status,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    if "discount_applied" in totals:
        record["discount_applied"] = totals["discount_applied"]
    return record


def process_order(raw):
    """Full pipeline: validate, calculate, build record; return (record, errors)."""
    ok, errors = validate_order(raw)
    if not ok:
        return None, errors
    totals = calculate_totals(raw)
    discount = raw.get("discount")
    if discount is not None:
        totals = apply_discount(totals, discount)
    record = build_order_record(raw, totals)
    return record, []
