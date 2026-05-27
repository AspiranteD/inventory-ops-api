"""Tests for Order and OrderItem models."""
import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from src.models.order import Order, OrderItem, MAX_EXTRACTION_ATTEMPTS


def _order(**kw):
    defaults = dict(request_id="REQ001", status_id=1)
    defaults.update(kw)
    return Order(**defaults)


def test_validate_ok():
    o = _order()
    assert o.validate() == []


def test_validate_due_before_order():
    o = _order(
        order_date=datetime(2026, 5, 20),
        due_date=datetime(2026, 5, 19),
    )
    assert any("due_date" in e for e in o.validate())


def test_is_overdue_true():
    o = _order(
        active=True,
        due_date=datetime.utcnow() - timedelta(hours=1),
    )
    assert o.is_overdue


def test_is_overdue_false_inactive():
    o = _order(
        active=False,
        due_date=datetime.utcnow() - timedelta(hours=1),
    )
    assert not o.is_overdue


def test_is_overdue_false_no_date():
    o = _order(active=True)
    assert not o.is_overdue


def test_is_overdue_false_future():
    o = _order(
        active=True,
        due_date=datetime.utcnow() + timedelta(days=1),
    )
    assert not o.is_overdue


def test_record_extraction_failure():
    o = _order(extraction_attempts=0)
    o.record_extraction_failure()
    assert o.extraction_attempts == 1
    assert not o.extraction_failed


def test_extraction_auto_fail():
    o = _order(extraction_attempts=MAX_EXTRACTION_ATTEMPTS - 1)
    o.record_extraction_failure()
    assert o.extraction_failed


def test_reset_extraction():
    o = _order(extraction_attempts=3, extraction_failed=True)
    o.reset_extraction()
    assert o.extraction_attempts == 0
    assert not o.extraction_failed


def test_order_item_validate_ok():
    oi = OrderItem(request_id="REQ001", lpn="LPN001", warehouse_status_id=1,
                   price=Decimal("50"))
    assert oi.validate() == []


def test_order_item_negative_price():
    oi = OrderItem(request_id="REQ001", lpn="LPN001", warehouse_status_id=1,
                   price=Decimal("-1"))
    assert any("price" in e for e in oi.validate())


def test_order_item_no_price():
    oi = OrderItem(request_id="REQ001", lpn="LPN001", warehouse_status_id=1)
    assert oi.validate() == []
