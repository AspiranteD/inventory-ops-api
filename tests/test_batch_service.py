"""Tests for BatchService."""
import pytest
from datetime import date
from decimal import Decimal
from src.models.item import PhysicalItem
from src.services.batch_service import BatchService, BatchResult


class FakeItemRepo:
    def __init__(self):
        self.items: dict[str, PhysicalItem] = {}

    def get(self, lpn):
        return self.items.get(lpn)

    def save(self, item):
        self.items[item.lpn] = item
        return item


def _item(lpn):
    return PhysicalItem(
        lpn=lpn, asin="X",
        purchase_price=Decimal("10"), purchase_date=date.today(),
    )


@pytest.fixture
def svc():
    repo = FakeItemRepo()
    return BatchService(repo), repo


def test_batch_all_success(svc):
    service, repo = svc
    repo.items["A"] = _item("A")
    repo.items["B"] = _item("B")
    result = service.batch_update_location([
        {"lpn": "A", "location": "Shelf-1"},
        {"lpn": "B", "location": "Shelf-2"},
    ])
    assert result.updated_count == 2
    assert result.failed_count == 0
    assert repo.items["A"].current_location == "Shelf-1"
    assert repo.items["B"].current_location == "Shelf-2"


def test_batch_partial_failure(svc):
    service, repo = svc
    repo.items["A"] = _item("A")
    result = service.batch_update_location([
        {"lpn": "A", "location": "Shelf-1"},
        {"lpn": "NOPE", "location": "Shelf-2"},
    ])
    assert result.updated_count == 1
    assert result.failed_count == 1
    assert "NOPE" in result.errors[0]


def test_batch_missing_lpn(svc):
    service, _ = svc
    result = service.batch_update_location([
        {"location": "Shelf-1"},
    ])
    assert result.failed_count == 1
    assert "Missing lpn" in result.errors[0]


def test_batch_empty(svc):
    service, _ = svc
    result = service.batch_update_location([])
    assert result.updated_count == 0
    assert result.failed_count == 0


def test_batch_error_handling(svc):
    service, repo = svc

    class BrokenRepo:
        def get(self, lpn):
            return _item(lpn)
        def save(self, item):
            raise RuntimeError("DB connection lost")

    service._repo = BrokenRepo()
    result = service.batch_update_location([
        {"lpn": "A", "location": "X"},
    ])
    assert result.failed_count == 1
    assert "DB connection" in result.errors[0]


def test_batch_result_to_dict(svc):
    service, repo = svc
    repo.items["A"] = _item("A")
    result = service.batch_update_location([
        {"lpn": "A", "location": "Shelf-1"},
    ])
    d = result.to_dict()
    assert d["updated"] == 1
    assert d["failed"] == 0
    assert d["updated_items"] == ["A"]
