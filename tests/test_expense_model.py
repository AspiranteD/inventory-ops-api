"""Tests for Expense model."""
import pytest
from datetime import date, timedelta
from decimal import Decimal
from src.models.expense import Expense


def _expense(**kw):
    defaults = dict(
        expense_id=1, description="Office supplies",
        total_amount=Decimal("100"), expense_date=date.today(),
        payment_date=date.today(),
    )
    defaults.update(kw)
    return Expense(**defaults)


def test_validate_ok():
    e = _expense()
    assert e.validate() == []


def test_validate_empty_description():
    e = _expense(description="   ")
    assert any("description" in err for err in e.validate())


def test_validate_zero_amount():
    e = _expense(total_amount=Decimal("0"))
    assert any("total_amount" in err for err in e.validate())


def test_validate_negative_amount():
    e = _expense(total_amount=Decimal("-5"))
    assert any("total_amount" in err for err in e.validate())


def test_validate_future_expense_date():
    e = _expense(expense_date=date.today() + timedelta(days=1))
    assert any("expense_date" in err for err in e.validate())


def test_validate_future_payment_date():
    e = _expense(payment_date=date.today() + timedelta(days=1))
    assert any("payment_date" in err for err in e.validate())


def test_validate_pagado_no_payment_date():
    e = _expense(payment_status="PAGADO", payment_date=None)
    assert any("PAGADO" in err for err in e.validate())


def test_validate_not_pagado_with_payment_date():
    e = _expense(payment_status="PENDIENTE", payment_date=date.today())
    assert any("PAGADO" in err for err in e.validate())


def test_validate_recurring_no_pattern():
    e = _expense(is_recurring=True, recurrence_pattern=None)
    assert any("recurrence_pattern" in err for err in e.validate())


def test_validate_not_recurring_with_pattern():
    e = _expense(is_recurring=False, recurrence_pattern="monthly")
    assert any("recurrence_pattern" in err for err in e.validate())


def test_validate_recurring_ok():
    e = _expense(is_recurring=True, recurrence_pattern="monthly")
    assert e.validate() == []


def test_default_expense_date():
    e = Expense(expense_id=1, description="Test", total_amount=Decimal("10"),
                payment_status="PENDIENTE")
    assert e.expense_date == date.today()
