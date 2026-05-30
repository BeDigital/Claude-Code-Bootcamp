#!/usr/bin/env python3
"""test_order_processor — tests for order_processor module."""

import pytest
from order_processor import (
    validate_order,
    calculate_totals,
    apply_discount,
    build_order_record,
    process_order,
    STATUS_PENDING,
    STATUS_APPROVED,
    TAX_RATE,
    FREE_SHIPPING_THRESHOLD,
    SHIPPING_COST,
)

VALID_ORDER = {
    "customer_email": "alice@example.com",
    "items": [
        {"sku": "WIDGET-A", "quantity": 2, "unit_price": 25.00},
        {"sku": "WIDGET-B", "quantity": 1, "unit_price": 15.00},
    ],
    "shipping_address": {
        "street": "123 Main St",
        "city": "Springfield",
        "zip_code": "12345",
        "country": "US",
    },
}

SMALL_ORDER = {
    "customer_email": "bob@example.com",
    "items": [{"sku": "TINY", "quantity": 1, "unit_price": 5.00}],
    "shipping_address": {
        "street": "1 Side St",
        "city": "Shelbyville",
        "zip_code": "67890",
        "country": "US",
    },
}


class TestValidateOrder:
    def test_valid_order_passes(self):
        ok, errs = validate_order(VALID_ORDER)
        assert ok is True
        assert errs == []

    def test_none_order_fails(self):
        ok, errs = validate_order(None)
        assert ok is False
        assert "order is None" in errs

    def test_missing_email(self):
        o = {**VALID_ORDER}
        del o["customer_email"]
        ok, errs = validate_order(o)
        assert ok is False
        assert "missing customer_email" in errs

    def test_invalid_email_format(self):
        o = {**VALID_ORDER, "customer_email": "not-an-email"}
        ok, errs = validate_order(o)
        assert ok is False
        assert "customer_email invalid format" in errs

    def test_missing_items(self):
        o = {**VALID_ORDER}
        del o["items"]
        ok, errs = validate_order(o)
        assert ok is False
        assert "missing items" in errs

    def test_empty_items(self):
        o = {**VALID_ORDER, "items": []}
        ok, errs = validate_order(o)
        assert ok is False
        assert "items list is empty" in errs

    def test_item_missing_sku(self):
        o = {**VALID_ORDER, "items": [{"quantity": 1, "unit_price": 10.0}]}
        ok, errs = validate_order(o)
        assert ok is False
        assert "item 0: missing sku" in errs

    def test_item_quantity_zero(self):
        o = {**VALID_ORDER, "items": [{"sku": "X", "quantity": 0, "unit_price": 10.0}]}
        ok, errs = validate_order(o)
        assert ok is False
        assert "item 0: quantity must be positive" in errs

    def test_item_quantity_exceeds_max(self):
        o = {**VALID_ORDER, "items": [{"sku": "X", "quantity": 501, "unit_price": 1.0}]}
        ok, errs = validate_order(o)
        assert ok is False
        assert "item 0: quantity exceeds max 500" in errs

    def test_item_negative_price(self):
        o = {**VALID_ORDER, "items": [{"sku": "X", "quantity": 1, "unit_price": -1.0}]}
        ok, errs = validate_order(o)
        assert ok is False
        assert "item 0: unit_price cannot be negative" in errs

    def test_missing_shipping_address(self):
        o = {**VALID_ORDER}
        del o["shipping_address"]
        ok, errs = validate_order(o)
        assert ok is False
        assert "missing shipping_address" in errs

    def test_shipping_address_missing_field(self):
        addr = {**VALID_ORDER["shipping_address"]}
        del addr["zip_code"]
        o = {**VALID_ORDER, "shipping_address": addr}
        ok, errs = validate_order(o)
        assert ok is False
        assert "shipping_address missing zip_code" in errs


class TestCalculateTotals:
    def test_above_free_shipping_threshold(self):
        totals = calculate_totals(VALID_ORDER)
        # 2*25 + 1*15 = 65; below 100 threshold
        assert totals["subtotal"] == 65.00
        assert totals["tax"] == round(65.00 * TAX_RATE, 2)
        assert totals["shipping"] == SHIPPING_COST
        assert totals["grand_total"] == round(65.00 + 65.00 * TAX_RATE + SHIPPING_COST, 2)

    def test_free_shipping_at_threshold(self):
        order = {
            **VALID_ORDER,
            "items": [{"sku": "BIG", "quantity": 4, "unit_price": 25.0}],
        }
        totals = calculate_totals(order)
        assert totals["subtotal"] == 100.00
        assert totals["shipping"] == 0.0

    def test_small_order_has_shipping(self):
        totals = calculate_totals(SMALL_ORDER)
        assert totals["subtotal"] == 5.00
        assert totals["shipping"] == SHIPPING_COST


class TestApplyDiscount:
    def test_none_discount_returns_unchanged(self):
        totals = calculate_totals(VALID_ORDER)
        result = apply_discount(totals, None)
        assert result == totals

    def test_percentage_discount(self):
        totals = calculate_totals(VALID_ORDER)
        result = apply_discount(totals, {"type": "percentage", "value": 10})
        expected_sub = round(65.00 * 0.90, 2)
        assert result["subtotal"] == expected_sub
        assert result["discount_applied"] == round(65.00 * 0.10, 2)

    def test_flat_discount(self):
        totals = calculate_totals(VALID_ORDER)
        result = apply_discount(totals, {"type": "flat", "value": 10.00})
        assert result["subtotal"] == 55.00
        assert result["discount_applied"] == 10.00

    def test_flat_discount_cannot_go_below_zero(self):
        totals = calculate_totals(SMALL_ORDER)
        result = apply_discount(totals, {"type": "flat", "value": 999.00})
        assert result["subtotal"] == 0.0
        assert result["discount_applied"] == 5.00

    def test_invalid_discount_type_returns_unchanged(self):
        totals = calculate_totals(VALID_ORDER)
        result = apply_discount(totals, {"type": "mystery"})
        assert result == totals

    def test_percentage_out_of_range_returns_unchanged(self):
        totals = calculate_totals(VALID_ORDER)
        result = apply_discount(totals, {"type": "percentage", "value": 150})
        assert result == totals


class TestBuildOrderRecord:
    def test_record_has_required_fields(self):
        totals = calculate_totals(VALID_ORDER)
        rec = build_order_record(VALID_ORDER, totals)
        for field in ["customer_email", "items", "shipping_address",
                      "subtotal", "tax", "shipping", "grand_total",
                      "status", "created_at"]:
            assert field in rec

    def test_record_default_status(self):
        totals = calculate_totals(VALID_ORDER)
        rec = build_order_record(VALID_ORDER, totals)
        assert rec["status"] == STATUS_PENDING

    def test_record_custom_status(self):
        totals = calculate_totals(VALID_ORDER)
        rec = build_order_record(VALID_ORDER, totals, status=STATUS_APPROVED)
        assert rec["status"] == STATUS_APPROVED

    def test_record_includes_discount_when_present(self):
        totals = calculate_totals(VALID_ORDER)
        discounted = apply_discount(totals, {"type": "flat", "value": 5.00})
        rec = build_order_record(VALID_ORDER, discounted)
        assert "discount_applied" in rec
        assert rec["discount_applied"] == 5.00

    def test_record_no_discount_field_when_absent(self):
        totals = calculate_totals(VALID_ORDER)
        rec = build_order_record(VALID_ORDER, totals)
        assert "discount_applied" not in rec


class TestProcessOrder:
    def test_valid_order_returns_record(self):
        rec, errs = process_order(VALID_ORDER)
        assert errs == []
        assert rec is not None
        assert rec["customer_email"] == "alice@example.com"
        assert rec["grand_total"] == round(65.00 + 65.00 * TAX_RATE + SHIPPING_COST, 2)

    def test_invalid_order_returns_errors(self):
        rec, errs = process_order(None)
        assert rec is None
        assert len(errs) > 0

    def test_order_with_discount_applied(self):
        order = {**VALID_ORDER, "discount": {"type": "flat", "value": 10.00}}
        rec, errs = process_order(order)
        assert errs == []
        assert rec["discount_applied"] == 10.00
        assert rec["subtotal"] == 55.00

    def test_order_without_discount(self):
        rec, errs = process_order(VALID_ORDER)
        assert errs == []
        assert "discount_applied" not in rec
