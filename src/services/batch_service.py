"""
Batch operations service for bulk warehouse location updates.
Collects per-item results: updated vs errors.
"""
from dataclasses import dataclass, field
from typing import Optional, Protocol

from src.models.item import PhysicalItem


@dataclass
class BatchResult:
    updated: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def updated_count(self) -> int:
        return len(self.updated)

    @property
    def failed_count(self) -> int:
        return len(self.errors)

    def to_dict(self) -> dict:
        return {
            "message": "Batch update completed",
            "updated": self.updated_count,
            "failed": self.failed_count,
            "updated_items": self.updated,
            "errors": self.errors,
        }


class ItemRepository(Protocol):
    def get(self, lpn: str) -> Optional[PhysicalItem]: ...
    def save(self, item: PhysicalItem) -> PhysicalItem: ...


class BatchService:
    def __init__(self, repo: ItemRepository):
        self._repo = repo

    def batch_update_location(
        self, updates: list[dict[str, str]]
    ) -> BatchResult:
        """
        Update location for multiple items.
        Each entry: {"lpn": "...", "location": "..."}
        """
        result = BatchResult()

        for update in updates:
            lpn = update.get("lpn", "")
            location = update.get("location", "")

            if not lpn:
                result.errors.append("Missing lpn in update entry")
                continue

            try:
                item = self._repo.get(lpn)
                if not item:
                    result.errors.append(f"Item {lpn} not found")
                    continue
                item.current_location = location
                self._repo.save(item)
                result.updated.append(lpn)
            except Exception as e:
                result.errors.append(f"Error updating {lpn}: {str(e)}")

        return result
