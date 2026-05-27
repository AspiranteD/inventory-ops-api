"""Tests for Incident model."""
import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from src.models.incident import Incident, INCIDENT_TYPES, INCIDENT_STATUSES


def _incident(**kw):
    defaults = dict(
        incident_id=1, sale_id=100,
        buyer_problem_description="Product arrived damaged",
        platform_account_id=1,
    )
    defaults.update(kw)
    return Incident(**defaults)


def test_validate_ok():
    inc = _incident()
    assert inc.validate() == []


def test_validate_empty_description():
    inc = _incident(buyer_problem_description="  ")
    assert any("empty" in e for e in inc.validate())


def test_validate_negative_refund():
    inc = _incident(refund_amount=Decimal("-1"))
    assert any("refund_amount" in e for e in inc.validate())


def test_validate_negative_discount():
    inc = _incident(discount_amount=Decimal("-5"))
    assert any("discount_amount" in e for e in inc.validate())


def test_validate_resolved_before_opened():
    inc = _incident(
        opened_at=datetime(2026, 5, 20),
        resolved_at=datetime(2026, 5, 19),
    )
    assert any("resolved_at" in e for e in inc.validate())


def test_validate_invalid_type():
    inc = _incident(incident_type="INVALID")
    assert any("incident_type" in e for e in inc.validate())


def test_validate_invalid_status():
    inc = _incident(status="INVALID")
    assert any("status" in e for e in inc.validate())


def test_has_pending_return_true():
    inc = _incident(pending_condition_id=2, article_data_applied=False)
    assert inc.has_pending_return


def test_has_pending_return_false_applied():
    inc = _incident(pending_condition_id=2, article_data_applied=True)
    assert not inc.has_pending_return


def test_has_pending_return_false_not_received():
    inc = _incident(pending_condition_id=2, not_received_at=datetime.utcnow())
    assert not inc.has_pending_return


def test_has_pending_return_false_no_condition():
    inc = _incident(pending_condition_id=None)
    assert not inc.has_pending_return


def test_apply_return_data():
    inc = _incident(
        pending_condition_id=2,
        pending_condition_description="Scratched",
        pending_available=True,
        pending_purchase_price=Decimal("30"),
    )
    result = inc.apply_return_data()
    assert result["condition_id"] == 2
    assert result["condition_description"] == "Scratched"
    assert result["available"] is True
    assert result["purchase_price"] == Decimal("30")
    assert inc.article_data_applied is True


def test_apply_return_data_idempotent():
    inc = _incident(pending_condition_id=2)
    inc.apply_return_data()
    result2 = inc.apply_return_data()
    assert result2 == {}


def test_apply_return_data_no_pending():
    inc = _incident(pending_condition_id=None)
    assert inc.apply_return_data() == {}


def test_mark_not_received():
    inc = _incident(pending_condition_id=2)
    inc.mark_not_received()
    assert inc.not_received_at is not None
    assert not inc.has_pending_return


def test_all_types_valid():
    for t in INCIDENT_TYPES:
        inc = _incident(incident_type=t)
        errors = [e for e in inc.validate() if "incident_type" in e]
        assert errors == []


def test_all_statuses_valid():
    for s in INCIDENT_STATUSES:
        inc = _incident(status=s)
        errors = [e for e in inc.validate() if "status" in e]
        assert errors == []
