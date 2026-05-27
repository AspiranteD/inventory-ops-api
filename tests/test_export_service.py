"""Tests for ExportService."""
import pytest
from datetime import date
from decimal import Decimal
from src.models.item import PhysicalItem
from src.services.export_service import ExportService, CSV_HEADERS


class FakeItemRepo:
    def __init__(self):
        self.items = []

    def list_all_sorted(self):
        return sorted(self.items, key=lambda i: i.lpn)


def _item(lpn, **kw):
    defaults = dict(asin="B08XYZ", purchase_price=Decimal("50"),
                    purchase_date=date.today())
    defaults.update(kw)
    return PhysicalItem(lpn=lpn, **defaults)


@pytest.fixture
def svc():
    repo = FakeItemRepo()
    return ExportService(repo), repo


def test_csv_headers(svc):
    service, repo = svc
    repo.items.append(_item("LPN001", brand="Sony"))
    result = service.export_csv()
    assert result["format"] == "csv"
    assert result["count"] == 1
    for header in CSV_HEADERS:
        assert header in result["data"]


def test_csv_data_content(svc):
    service, repo = svc
    repo.items.append(_item("LPN001", brand="Sony", model="X100",
                            current_location="A-12", available=True))
    result = service.export_csv()
    assert "LPN001" in result["data"]
    assert "Sony" in result["data"]
    assert "X100" in result["data"]
    assert "A-12" in result["data"]
    assert "Yes" in result["data"]


def test_csv_unavailable():
    repo = type("R", (), {"list_all_sorted": lambda self: [
        _item("A", available=False),
    ]})()
    service = ExportService(repo)
    result = service.export_csv()
    assert "No" in result["data"]


def test_csv_empty(svc):
    service, _ = svc
    result = service.export_csv()
    assert result["count"] == 0


def test_json_format(svc):
    service, repo = svc
    repo.items.append(_item("LPN001", brand="Sony"))
    result = service.export_json()
    assert result["format"] == "json"
    assert result["count"] == 1
    assert result["data"][0]["lpn"] == "LPN001"
    assert result["data"][0]["brand"] == "Sony"


def test_json_empty(svc):
    service, _ = svc
    result = service.export_json()
    assert result["count"] == 0
    assert result["data"] == []


def test_json_null_fields(svc):
    service, repo = svc
    repo.items.append(_item("A"))
    result = service.export_json()
    assert result["data"][0]["brand"] is None


def test_export_csv_default(svc):
    service, repo = svc
    repo.items.append(_item("A"))
    result = service.export("csv")
    assert result["format"] == "csv"


def test_export_json(svc):
    service, repo = svc
    repo.items.append(_item("A"))
    result = service.export("json")
    assert result["format"] == "json"


def test_sorted_output(svc):
    service, repo = svc
    repo.items.extend([_item("C"), _item("A"), _item("B")])
    result = service.export_json()
    lpns = [d["lpn"] for d in result["data"]]
    assert lpns == ["A", "B", "C"]


def test_csv_multiple_items(svc):
    service, repo = svc
    repo.items.extend([_item("A"), _item("B"), _item("C")])
    result = service.export_csv()
    assert result["count"] == 3
    lines = result["data"].strip().split("\n")
    assert len(lines) == 4  # header + 3 data rows
