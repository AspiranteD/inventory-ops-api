"""
Global search service: multi-table search across items, sales, and orders.
"""
from typing import Protocol, Optional

from src.models.item import PhysicalItem
from src.models.sale import Sale
from src.models.order import Order


class SearchRepository(Protocol):
    def search_items(self, q: str, limit: int) -> list[PhysicalItem]: ...
    def search_sales(self, q: str, limit: int) -> list[Sale]: ...
    def search_orders(self, q: str, limit: int) -> list[Order]: ...


class SearchService:
    def __init__(self, repo: SearchRepository):
        self._repo = repo

    def global_search(self, q: str, limit: int = 20) -> dict:
        """
        Search across items (LPN, ASIN, brand, model, description),
        sales (by ID), and orders (request_id, buyer_name).
        """
        q = q.strip()
        if not q:
            return {"items": [], "sales": [], "orders": []}

        return {
            "items": self._repo.search_items(q, limit),
            "sales": self._repo.search_sales(q, limit),
            "orders": self._repo.search_orders(q, limit),
        }
