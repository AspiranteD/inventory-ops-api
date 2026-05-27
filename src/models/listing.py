"""
Marketplace listing model with dual pricing modes, stat accumulation,
product_id oscillation detection, and store assignment.
"""
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional


PRICE_MODE_STANDARD = "standard"
PRICE_MODE_MANUAL = "manual"
PORTALHERO_STORE_MOTOR = 16
PORTALHERO_STORE_EXPENSIVE = 17
PORTALHERO_STORE_CHEAP = 18


@dataclass
class Listing:
    id: Optional[int]
    account_id: int
    product_id: str

    lpn: Optional[str] = None
    previous_product_id: Optional[str] = None

    title: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    web_slug: Optional[str] = None
    category_id: Optional[int] = None

    sale_price: Optional[int] = None
    listing_price: Optional[Decimal] = None
    reference_price: Optional[Decimal] = None
    revised_price: Optional[Decimal] = None
    revised_price_at: Optional[datetime] = None
    price_mode: str = PRICE_MODE_STANDARD

    shipping: bool = True
    free_shipping: bool = False
    portalhero_store: Optional[int] = None

    is_reserved: bool = False
    is_sold: bool = False
    is_pending: bool = False
    is_banned: bool = False
    is_expired: bool = False
    is_on_hold: bool = False

    conversations_count: int = 0
    favorites_count: int = 0
    views_count: int = 0
    conversations_accumulated: int = 0
    favorites_accumulated: int = 0
    views_accumulated: int = 0

    modified_timestamp: Optional[int] = None
    published_timestamp: Optional[int] = None
    extracted_timestamp: Optional[int] = None

    @property
    def status(self) -> str:
        if self.is_sold:
            return "sold"
        if self.is_banned:
            return "banned"
        if self.is_reserved:
            return "reserved"
        if self.is_expired:
            return "expired"
        if self.is_on_hold:
            return "on_hold"
        if self.is_pending:
            return "pending"
        return "published"

    @property
    def total_conversations(self) -> int:
        return self.conversations_count + self.conversations_accumulated

    @property
    def total_favorites(self) -> int:
        return self.favorites_count + self.favorites_accumulated

    @property
    def total_views(self) -> int:
        return self.views_count + self.views_accumulated

    def rotate_product_id(self, new_product_id: str) -> None:
        """Handle product_id change: accumulate current stats, reset counters."""
        if new_product_id == self.product_id:
            return
        self.conversations_accumulated += self.conversations_count
        self.favorites_accumulated += self.favorites_count
        self.views_accumulated += self.views_count
        self.previous_product_id = self.product_id
        self.product_id = new_product_id
        self.conversations_count = 0
        self.favorites_count = 0
        self.views_count = 0

    @property
    def is_oscillating(self) -> bool:
        """Detect product_id oscillation (A->B->A pattern)."""
        return (
            self.previous_product_id is not None
            and self.previous_product_id != self.product_id
        )
