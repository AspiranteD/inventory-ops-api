"""Tests for SearchService."""
import pytest
from datetime import date
from decimal import Decimal
from src.models.item import PhysicalItem
from src.models.sale import Sale
from src.models.order import Order
from src.services.search_service import SearchService


class FakeSearchRepo:
    def __init__(self):
        self.items = []
        self.sales = []
        self.orders = []

    def search_items(self, q, limit):
        return [i for i in self.items
                if q.lower() in (i.lpn + (i.asin or "") + (i.brand or "")).lower()
                ][:limit]

    def search_sales(self, q, limit):
        return [s for s in self.sales if q in str(s.id)][:limit]

    def search_orders(self, q, limit):
        return [o for o in self.orders
                if q.lower() in (o.request_id + (o.buyer_name or "")).lower()
                ][:limit]


@pytest.fixture
def svc():
    repo = FakeSearchRepo()
    return SearchService(repo), repo


def test_search_empty_query(svc):
    service, _ = svc
    result = service.global_search("")
    assert result == {"items": [], "sales": [], "orders": []}


def test_search_whitespace(svc):
    service, _ = svc
    result = service.global_search("   ")
    assert result == {"items": [], "sales": [], "orders": []}


def test_search_items_by_lpn(svc):
    service, repo = svc
    repo.items.append(PhysicalItem(
        lpn="LPN001", asin="B08XYZ",
        purchase_price=Decimal("50"), purchase_date=date.today(),
    ))
    result = service.global_search("LPN001")
    assert len(result["items"]) == 1
    assert result["items"][0].lpn == "LPN001"


def test_search_items_by_brand(svc):
    service, repo = svc
    repo.items.append(PhysicalItem(
        lpn="A", asin="X", brand="Sony",
        purchase_price=Decimal("50"), purchase_date=date.today(),
    ))
    result = service.global_search("sony")
    assert len(result["items"]) == 1


def test_search_orders_by_buyer(svc):
    service, repo = svc
    repo.orders.append(Order(
        request_id="REQ001", status_id=1, buyer_name="John Doe",
    ))
    result = service.global_search("John")
    assert len(result["orders"]) == 1


def test_search_with_limit(svc):
    service, repo = svc
    for i in range(10):
        repo.items.append(PhysicalItem(
            lpn=f"TEST{i}", asin="X",
            purchase_price=Decimal("50"), purchase_date=date.today(),
        ))
    result = service.global_search("TEST", limit=3)
    assert len(result["items"]) == 3


def test_search_no_results(svc):
    service, _ = svc
    result = service.global_search("NONEXISTENT")
    assert result["items"] == []
    assert result["sales"] == []
    assert result["orders"] == []
