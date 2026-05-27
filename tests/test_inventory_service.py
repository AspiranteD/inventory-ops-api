"""Tests for InventoryService."""
import pytest
from datetime import date
from decimal import Decimal
from src.models.item import PhysicalItem
from src.services.inventory_service import (
    InventoryService, ItemNotFoundError, DuplicateLPNError, ValidationError,
)


class FakeItemRepo:
    def __init__(self):
        self.items: dict[str, PhysicalItem] = {}

    def get(self, lpn):
        return self.items.get(lpn)

    def list(self, **filters):
        result = list(self.items.values())
        if "available" in filters:
            result = [i for i in result if i.available == filters["available"]]
        if "brand" in filters:
            result = [i for i in result
                      if filters["brand"].lower() in (i.brand or "").lower()]
        if "category" in filters:
            result = [i for i in result if i.amazon_category == filters["category"]]
        if "location" in filters:
            result = [i for i in result
                      if filters["location"].lower() in (i.current_location or "").lower()]
        skip = filters.get("skip", 0)
        limit = filters.get("limit", 100)
        return result[skip:skip + limit]

    def save(self, item):
        self.items[item.lpn] = item
        return item

    def delete(self, lpn):
        return self.items.pop(lpn, None) is not None

    def count(self, **filters):
        if "available" in filters:
            return len([i for i in self.items.values()
                        if i.available == filters["available"]])
        return len(self.items)


def _item(lpn="LPN001", **kw):
    defaults = dict(asin="B08XYZ", purchase_price=Decimal("50"),
                    purchase_date=date.today())
    defaults.update(kw)
    return PhysicalItem(lpn=lpn, **defaults)


@pytest.fixture
def svc():
    repo = FakeItemRepo()
    return InventoryService(repo), repo


def test_create_item(svc):
    service, repo = svc
    item = _item()
    result = service.create_item(item)
    assert result.lpn == "LPN001"
    assert "LPN001" in repo.items


def test_create_duplicate(svc):
    service, repo = svc
    repo.items["LPN001"] = _item()
    with pytest.raises(DuplicateLPNError):
        service.create_item(_item())


def test_create_invalid(svc):
    service, _ = svc
    item = _item(purchase_price=Decimal("-1"))
    with pytest.raises(ValidationError):
        service.create_item(item)


def test_get_item(svc):
    service, repo = svc
    repo.items["LPN001"] = _item()
    assert service.get_item("LPN001").lpn == "LPN001"


def test_get_not_found(svc):
    service, _ = svc
    with pytest.raises(ItemNotFoundError):
        service.get_item("NONEXISTENT")


def test_update_item(svc):
    service, repo = svc
    repo.items["LPN001"] = _item()
    result = service.update_item("LPN001", {"brand": "Sony"})
    assert result.brand == "Sony"


def test_update_location(svc):
    service, repo = svc
    repo.items["LPN001"] = _item()
    result = service.update_location("LPN001", "Shelf A-12")
    assert result.current_location == "Shelf A-12"


def test_delete_item(svc):
    service, repo = svc
    repo.items["LPN001"] = _item()
    service.delete_item("LPN001")
    assert "LPN001" not in repo.items


def test_delete_not_found(svc):
    service, _ = svc
    with pytest.raises(ItemNotFoundError):
        service.delete_item("NONEXISTENT")


def test_list_items_filter_available(svc):
    service, repo = svc
    repo.items["A"] = _item("A", available=True)
    repo.items["B"] = _item("B", available=False)
    result = service.list_items(available=True)
    assert len(result) == 1
    assert result[0].lpn == "A"


def test_list_items_pagination(svc):
    service, repo = svc
    for i in range(10):
        repo.items[f"LPN{i:03d}"] = _item(f"LPN{i:03d}")
    result = service.list_items(skip=2, limit=3)
    assert len(result) == 3


def test_update_image_urls(svc):
    service, repo = svc
    repo.items["LPN001"] = _item()
    result = service.update_image_urls("LPN001", [
        "https://img.com/1.jpg", "https://img.com/2.jpg",
    ])
    assert result["updated_count"] == 2
    assert "https://img.com/1.jpg" in result["image_urls"]


def test_update_image_urls_invalid(svc):
    service, repo = svc
    repo.items["LPN001"] = _item()
    with pytest.raises(ValidationError):
        service.update_image_urls("LPN001", ["not-a-url"])


def test_update_image_urls_empty(svc):
    service, repo = svc
    repo.items["LPN001"] = _item(image_urls="https://old.com/1.jpg")
    result = service.update_image_urls("LPN001", [])
    assert result["updated_count"] == 0


def test_availability_stats(svc):
    service, repo = svc
    repo.items["A"] = _item("A", available=True)
    repo.items["B"] = _item("B", available=True)
    repo.items["C"] = _item("C", available=False)
    stats = service.get_availability_stats()
    assert stats["total_items"] == 3
    assert stats["available"] == 2
    assert stats["unavailable"] == 1
    assert stats["availability_rate"] == pytest.approx(66.67, rel=0.01)


def test_availability_stats_empty(svc):
    service, _ = svc
    stats = service.get_availability_stats()
    assert stats["total_items"] == 0
    assert stats["availability_rate"] == 0


def test_record_scraping_success(svc):
    service, repo = svc
    repo.items["LPN001"] = _item(scraping_attempts=3)
    result = service.record_scraping_result("LPN001", True, Decimal("99"))
    assert result.scraped_price == Decimal("99")
    assert result.scraping_attempts == 0


def test_record_scraping_failure(svc):
    service, repo = svc
    repo.items["LPN001"] = _item(scraping_attempts=0)
    result = service.record_scraping_result("LPN001", False)
    assert result.scraping_attempts == 1


def test_condition_validation_con_tara(svc):
    service, _ = svc
    item = _item(condition_id=2, condition_description="short")
    with pytest.raises(ValidationError) as exc:
        service.create_item(item)
    assert "CON_TARA" in str(exc.value)


def test_condition_validation_con_tara_ok(svc):
    service, _ = svc
    desc = "A" * 50
    item = _item(condition_id=2, condition_description=desc)
    result = service.create_item(item)
    assert result.condition_description == desc


def test_condition_validation_perfecto_no_desc(svc):
    service, _ = svc
    item = _item(condition_id=1, condition_description=None)
    result = service.create_item(item)
    assert result.lpn == "LPN001"
