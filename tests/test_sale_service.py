"""Tests for SaleService with side effects."""
import pytest
from datetime import date
from decimal import Decimal
from src.models.item import PhysicalItem
from src.models.sale import Sale
from src.models.incident import Incident
from src.services.sale_service import SaleService, SaleNotFoundError, ValidationError


class FakeSaleRepo:
    def __init__(self):
        self.sales: dict[int, Sale] = {}

    def get(self, sale_id):
        return self.sales.get(sale_id)

    def list(self, **filters):
        return list(self.sales.values())

    def save(self, sale):
        self.sales[sale.id] = sale
        return sale


class FakeItemRepo:
    def __init__(self):
        self.items: dict[str, PhysicalItem] = {}

    def get(self, lpn):
        return self.items.get(lpn)

    def save(self, item):
        self.items[item.lpn] = item
        return item


class FakeAccountRepo:
    def __init__(self, existing=None):
        self._existing = existing or set()

    def exists(self, account_id):
        return account_id in self._existing


def _item(lpn="LPN001"):
    return PhysicalItem(
        lpn=lpn, asin="B08XYZ",
        purchase_price=Decimal("50"), purchase_date=date.today(),
    )


def _sale(sid=1, **kw):
    defaults = dict(final_price=Decimal("100"), listing_id=10)
    defaults.update(kw)
    return Sale(id=sid, **defaults)


@pytest.fixture
def svc():
    sr = FakeSaleRepo()
    ir = FakeItemRepo()
    ar = FakeAccountRepo({1, 2})
    return SaleService(sr, ir, ar), sr, ir


def test_create_sale(svc):
    service, sr, ir = svc
    result = service.create_sale(_sale())
    assert result.id == 1
    assert 1 in sr.sales


def test_create_sale_marks_unavailable(svc):
    service, sr, ir = svc
    ir.items["LPN001"] = _item()
    sale = _sale(lpn="LPN001", listing_id=None)
    service.create_sale(sale)
    assert ir.items["LPN001"].available is False


def test_create_sale_item_not_found(svc):
    service, sr, ir = svc
    with pytest.raises(ValidationError, match="Item does not exist"):
        service.create_sale(_sale(lpn="NOPE", listing_id=None))


def test_create_sale_account_not_found(svc):
    service, sr, ir = svc
    with pytest.raises(ValidationError, match="Platform account"):
        service.create_sale(_sale(account_id=999))


def test_create_sale_invalid(svc):
    service, sr, ir = svc
    with pytest.raises(ValidationError):
        service.create_sale(_sale(final_price=Decimal("-1")))


def test_update_payment_status(svc):
    service, sr, ir = svc
    sr.sales[1] = _sale()
    result = service.update_payment_status(1, 2, "PAID", Decimal("100"))
    assert result.payment_status_id == 2
    assert result.amount_paid == Decimal("100")
    assert result.payment_received_date == date.today()


def test_update_payment_status_pending(svc):
    service, sr, ir = svc
    sr.sales[1] = _sale()
    result = service.update_payment_status(1, 1, "PENDING")
    assert result.payment_received_date is None


def test_update_payment_not_found(svc):
    service, sr, ir = svc
    with pytest.raises(SaleNotFoundError):
        service.update_payment_status(999, 1, "PAID")


def test_apply_incident_return(svc):
    service, sr, ir = svc
    ir.items["LPN001"] = _item()
    sr.sales[100] = _sale(sid=100, lpn="LPN001", listing_id=None)
    incident = Incident(
        incident_id=1, sale_id=100,
        buyer_problem_description="Damaged",
        platform_account_id=1,
        pending_condition_id=2,
        pending_condition_description="Scratched",
        pending_available=True,
        pending_purchase_price=Decimal("30"),
    )
    result = service.apply_incident_return(incident)
    assert result["condition_id"] == 2
    assert ir.items["LPN001"].condition_id == 2
    assert ir.items["LPN001"].available is True
    assert ir.items["LPN001"].purchase_price == Decimal("30")


def test_apply_incident_no_pending(svc):
    service, sr, ir = svc
    incident = Incident(
        incident_id=1, sale_id=100,
        buyer_problem_description="Issue",
        platform_account_id=1,
    )
    assert service.apply_incident_return(incident) is None


def test_apply_incident_already_applied(svc):
    service, sr, ir = svc
    incident = Incident(
        incident_id=1, sale_id=100,
        buyer_problem_description="Damaged",
        platform_account_id=1,
        pending_condition_id=2,
        article_data_applied=True,
    )
    assert service.apply_incident_return(incident) is None


def test_get_daily_sales(svc):
    service, sr, ir = svc
    sr.sales[1] = _sale()
    result = service.get_daily_sales(date.today())
    assert len(result) == 1
