#!/usr/bin/env python3
"""order_processor — processes and validates e-commerce orders."""

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


STATUS_PENDING = "pending"
STATUS_APPROVED = "approved"
STATUS_REJECTED = "rejected"
STATUS_SHIPPED = "shipped"

TAX_RATE = 0.08
FREE_SHIPPING_THRESHOLD = 100.0
SHIPPING_COST = 9.99
MAX_QUANTITY = 500

_EMAIL_RE = re.compile(r"[^@]+@[^@]+\.[^@]+")


@dataclass
class ValidationResult:
    """Outcome of order validation."""
    valid: bool
    errors: list[str] = field(default_factory=list)


def _validate_email(email: object, errors: list[str]) -> None:
    """Append errors if email is missing or malformed."""
    if not isinstance(email, str):
        errors.append("customer_email must be string")
        return
    if not _EMAIL_RE.match(email):
        errors.append("customer_email invalid format")


def _validate_item(item: object, index: int, errors: list[str]) -> None:
    """Append errors for a single line-item dict."""
    prefix = f"item {index}"
    if not isinstance(item, dict):
        errors.append(f"{prefix}: must be a dict")
        return
    if "sku" not in item:
        errors.append(f"{prefix}: missing sku")
    elif not isinstance(item["sku"], str) or not item["sku"]:
        errors.append(f"{prefix}: sku must be non-empty string")

    if "quantity" not in item:
        errors.append(f"{prefix}: missing quantity")
    else:
        qty = item["quantity"]
        if not isinstance(qty, int):
            errors.append(f"{prefix}: quantity must be int")
        elif qty <= 0:
            errors.append(f"{prefix}: quantity must be positive")
        elif qty > MAX_QUANTITY:
            errors.append(f"{prefix}: quantity exceeds max {MAX_QUANTITY}")

    if "unit_price" not in item:
        errors.append(f"{prefix}: missing unit_price")
    else:
        price = item["unit_price"]
        if not isinstance(price, (int, float)):
            errors.append(f"{prefix}: unit_price must be numeric")
        elif price < 0:
            errors.append(f"{prefix}: unit_price cannot be negative")


def _validate_address(address: object, errors: list[str]) -> None:
    """Append errors if shipping address is missing required fields."""
    if not isinstance(address, dict):
        errors.append("shipping_address must be dict")
        return
    for key in ("street", "city", "zip_code", "country"):
        if key not in address:
            errors.append(f"shipping_address missing {key}")
        elif not isinstance(address[key], str) or not address[key].strip():
            errors.append(f"shipping_address.{key} must be non-empty string")


def validate_order(order: object) -> tuple[bool, list[str]]:
    """Validate an order dict and return (is_valid, errors)."""
    errors: list[str] = []
    if order is None:
        return False, ["order is None"]

    if "customer_email" not in order:
        errors.append("missing customer_email")
    else:
        _validate_email(order["customer_email"], errors)

    if "items" not in order:
        errors.append("missing items")
    else:
        items = order["items"]
        if not isinstance(items, list):
            errors.append("items must be a list")
        elif not items:
            errors.append("items list is empty")
        else:
            for i, item in enumerate(items):
                _validate_item(item, i, errors)

    if "shipping_address" not in order:
        errors.append("missing shipping_address")
    else:
        _validate_address(order["shipping_address"], errors)

    return (not errors), errors


def _compute_shipping(subtotal: float) -> float:
    """Return shipping cost based on subtotal."""
    return 0.0 if subtotal >= FREE_SHIPPING_THRESHOLD else SHIPPING_COST


def _build_totals(subtotal: float, discount_applied: Optional[float] = None) -> dict:
    """Assemble a totals dict from a subtotal, optionally including a discount amount."""
    tax = round(subtotal * TAX_RATE, 2)
    shipping = _compute_shipping(subtotal)
    result = {
        "subtotal": round(subtotal, 2),
        "tax": tax,
        "shipping": shipping,
        "grand_total": round(subtotal + tax + shipping, 2),
    }
    if discount_applied is not None:
        result["discount_applied"] = discount_applied
    return result


def calculate_totals(order: dict) -> dict:
    """Calculate subtotal, tax, shipping, and grand total for an order."""
    subtotal = sum(item["quantity"] * item["unit_price"] for item in order["items"])
    return _build_totals(subtotal)


def apply_discount(totals: dict, discount: Optional[dict]) -> dict:
    """Apply a discount dict to pre-calculated totals and return updated totals."""
    if not discount or "type" not in discount:
        return totals

    original = totals["subtotal"]
    discount_type = discount.get("type")
    value = discount.get("value")

    if not isinstance(value, (int, float)):
        return totals

    if discount_type == "percentage":
        if not (0 <= value <= 100):
            return totals
        discount_amount = round(original * (value / 100), 2)
        return _build_totals(round(original - discount_amount, 2), discount_amount)

    if discount_type == "flat":
        if value < 0:
            return totals
        discount_amount = round(min(value, original), 2)
        return _build_totals(round(max(0.0, original - value), 2), discount_amount)

    return totals


def build_order_record(order: dict, totals: dict, status: str = STATUS_PENDING) -> dict:
    """Combine order data, totals, and status into a serializable record."""
    return {
        "customer_email": order["customer_email"],
        "items": order["items"],
        "shipping_address": order["shipping_address"],
        **totals,
        "status": status,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def process_order(raw: Optional[dict]) -> tuple[Optional[dict], list[str]]:
    """Full pipeline: validate, calculate, build record; return (record, errors)."""
    ok, errors = validate_order(raw)
    if not ok:
        return None, errors
    totals = calculate_totals(raw)
    totals = apply_discount(totals, raw.get("discount"))
    return build_order_record(raw, totals), []
