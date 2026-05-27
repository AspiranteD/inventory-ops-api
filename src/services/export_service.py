"""
Inventory export service supporting CSV and JSON formats.
"""
import csv
from io import StringIO
from typing import Protocol

from src.models.item import PhysicalItem


class ItemRepository(Protocol):
    def list_all_sorted(self) -> list[PhysicalItem]: ...


CSV_HEADERS = [
    "LPN", "ASIN", "Brand", "Model", "Condition",
    "Purchase Price", "Location", "Available",
]


class ExportService:
    def __init__(self, repo: ItemRepository):
        self._repo = repo

    def export_csv(self) -> dict:
        items = self._repo.list_all_sorted()
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(CSV_HEADERS)

        for item in items:
            writer.writerow([
                item.lpn,
                item.asin,
                item.brand or "",
                item.model or "",
                item.condition_id or "",
                float(item.purchase_price) if item.purchase_price else 0,
                item.current_location or "",
                "Yes" if item.available else "No",
            ])

        return {
            "format": "csv",
            "data": output.getvalue(),
            "count": len(items),
        }

    def export_json(self) -> dict:
        items = self._repo.list_all_sorted()
        return {
            "format": "json",
            "data": [
                {
                    "lpn": item.lpn,
                    "asin": item.asin,
                    "brand": item.brand,
                    "model": item.model,
                    "condition_id": item.condition_id,
                    "purchase_price": (
                        float(item.purchase_price) if item.purchase_price else 0
                    ),
                    "location": item.current_location,
                    "available": item.available,
                }
                for item in items
            ],
            "count": len(items),
        }

    def export(self, fmt: str = "csv") -> dict:
        if fmt == "json":
            return self.export_json()
        return self.export_csv()
