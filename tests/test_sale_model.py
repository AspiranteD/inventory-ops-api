"""Tests for Sale model."""
import pytest
from datetime import date, timedelta
from decimal import Decimal
from src.models.sale import Sale, PAID_STATUS_CODE


def _sale(**kw):
    defaults = dict(id=1, final_price=Decimal("100.00"))
    defaults.update(kw)
    return Sale(**defaults)


def test_amount_due_basic():
    s = _sale(amount_paid=Decimal("40"))
    assert s.amount_due == Decimal("60")


def test_amount_due_with_fees():
    s = _sale(shipping_cost=Decimal("5"), platform_fee=Decimal("10"),
              amount_paid=Decimal("50"))
    assert s.amount_due == Decimal("65")


def test_amount_due_never_negative():
    s = _sale(amount_paid=Decimal("200"))
    assert s.amount_due == Decimal("0")


def test_validate_ok_online():
    s = _sale(listing_id=10)
    assert s.validate() == []


def test_validate_ok_in_person():
    s = _sale(in_person=True, lpn="LPN001")
    assert s.validate() == []


def test_validate_negative_price():
    s = _sale(final_price=Decimal("-1"))
    assert any("final_price" in e for e in s.validate())


def test_validate_negative_shipping():
    s = _sale(shipping_cost=Decimal("-1"), listing_id=1)
    assert any("shipping_cost" in e for e in s.validate())


def test_validate_paid_exceeds_total():
    s = _sale(amount_paid=Decimal("200"), listing_id=1)
    assert any("exceed" in e for e in s.validate())


def test_validate_in_person_with_listing():
    s = _sale(in_person=True, listing_id=1, lpn="LPN001")
    assert any("listing_id" in e for e in s.validate())


def test_validate_in_person_no_lpn():
    s = _sale(in_person=True, lpn=None)
    assert any("lpn" in e for e in s.validate())


def test_validate_online_no_ref():
    s = _sale(listing_id=None, lpn=None)
    assert any("listing_id or lpn" in e for e in s.validate())


def test_validate_future_sale_date():
    s = _sale(sale_date=date.today() + timedelta(days=1), listing_id=1)
    assert any("sale_date" in e for e in s.validate())


def test_validate_future_payment_date():
    s = _sale(payment_received_date=date.today() + timedelta(days=1), listing_id=1)
    assert any("payment_received_date" in e for e in s.validate())


def test_mark_paid():
    s = _sale()
    s.mark_paid(PAID_STATUS_CODE)
    assert s.payment_received_date == date.today()


def test_mark_paid_other_code():
    s = _sale()
    s.mark_paid("PENDING")
    assert s.payment_received_date is None
