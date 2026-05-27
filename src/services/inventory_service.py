"""
Inventory service with CRUD, filtering, availability management,
image URL validation, and scraping status tracking.

Database-agnostic: receives a repository dict for data access.
"""
import re
from decimal import Decimal
from typing import Optional, Protocol

from src.models.item import (
    PhysicalItem, CONDITION_REQUIRES_DESCRIPTION,
    MIN_CONDITION_DESC_LENGTH,
)


URL_PATTERN = re.compile(r"^https?://[^\s]+$", re.IGNORECASE)


class ItemNotFoundError(Exception):
    pass


class DuplicateLPNError(Exception):
    pass


class ValidationError(Exception):
    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__(", ".join(errors))


class ItemRepository(Protocol):
    def get(self, lpn: str) -> Optional[PhysicalItem]: ...
    def list(self, **filters) -> list[PhysicalItem]: ...
    def save(self, item: PhysicalItem) -> PhysicalItem: ...
    def delete(self, lpn: str) -> bool: ...
    def count(self, **filters) -> int: ...


class InventoryService:
    def __init__(self, repo: ItemRepository):
        self._repo = repo

    def get_item(self, lpn: str) -> PhysicalItem:
        item = self._repo.get(lpn)
        if not item:
            raise ItemNotFoundError(f"Item not found: {lpn}")
        return item

    def list_items(
        self,
        skip: int = 0,
        limit: int = 100,
        available: Optional[bool] = None,
        brand: Optional[str] = None,
        category: Optional[str] = None,
        location: Optional[str] = None,
    ) -> list[PhysicalItem]:
        filters = {}
        if available is not None:
            filters["available"] = available
        if brand:
            filters["brand"] = brand
        if category:
            filters["category"] = category
        if location:
            filters["location"] = location
        filters["skip"] = skip
        filters["limit"] = limit
        return self._repo.list(**filters)

    def create_item(self, item: PhysicalItem) -> PhysicalItem:
        existing = self._repo.get(item.lpn)
        if existing:
            raise DuplicateLPNError(f"Item already exists: {item.lpn}")

        errors = item.validate()
        errors.extend(self._validate_condition(item))
        if errors:
            raise ValidationError(errors)

        return self._repo.save(item)

    def update_item(self, lpn: str, updates: dict) -> PhysicalItem:
        item = self.get_item(lpn)
        for field_name, value in updates.items():
            if hasattr(item, field_name) and field_name != "lpn":
                setattr(item, field_name, value)

        errors = item.validate()
        errors.extend(self._validate_condition(item))
        if errors:
            raise ValidationError(errors)

        return self._repo.save(item)

    def update_location(self, lpn: str, location: str) -> PhysicalItem:
        item = self.get_item(lpn)
        item.current_location = location
        return self._repo.save(item)

    def delete_item(self, lpn: str) -> None:
        item = self._repo.get(lpn)
        if not item:
            raise ItemNotFoundError(f"Item not found: {lpn}")
        self._repo.delete(lpn)

    def update_image_urls(self, lpn: str, urls: list[str]) -> dict:
        """Validate and replace image URLs for an item."""
        item = self.get_item(lpn)

        validated = []
        for url in urls:
            url = url.strip()
            if not url:
                continue
            if not URL_PATTERN.match(url):
                raise ValidationError([f"Invalid URL format: {url[:80]}"])
            validated.append(url)

        item.image_urls = ",".join(validated) if validated else None
        self._repo.save(item)

        return {
            "lpn": lpn,
            "image_urls": item.image_urls or "",
            "updated_count": len(validated),
        }

    def get_availability_stats(self) -> dict:
        total = self._repo.count()
        available = self._repo.count(available=True)
        unavailable = total - available
        return {
            "total_items": total,
            "available": available,
            "unavailable": unavailable,
            "availability_rate": (available / total * 100) if total > 0 else 0,
        }

    def record_scraping_result(
        self, lpn: str, success: bool, price: Optional[Decimal] = None
    ) -> PhysicalItem:
        """Record scraping outcome with auto-pause on repeated failures."""
        item = self.get_item(lpn)
        if success and price is not None:
            item.reset_scraping(price)
        else:
            item.increment_scraping()
        return self._repo.save(item)

    def _validate_condition(self, item: PhysicalItem) -> list[str]:
        """Validate condition-specific description requirements."""
        errors = []
        if item.condition_id is not None:
            condition_name = self._condition_name_for_id(item.condition_id)
            if condition_name in CONDITION_REQUIRES_DESCRIPTION:
                desc = (item.condition_description or "").strip()
                if len(desc) < MIN_CONDITION_DESC_LENGTH:
                    errors.append(
                        f"Condition {condition_name} requires description "
                        f">= {MIN_CONDITION_DESC_LENGTH} chars"
                    )
        return errors

    def _condition_name_for_id(self, cid: int) -> str:
        """Map condition_id to name. Override for DB lookup."""
        _map = {1: "PERFECTO", 2: "CON_TARA", 3: "PARA_PIEZAS"}
        return _map.get(cid, "UNKNOWN")
