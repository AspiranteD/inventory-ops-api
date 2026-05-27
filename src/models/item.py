"""
Physical item model - central entity of the inventory system.

Each item is identified by a unique LPN (License Plate Number) and tracks
product data (ASIN, description, category), pricing, condition, warehouse
location, AI-enriched fields, and scraping status with auto-pause logic.
"""
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Optional


CONDITION_REQUIRES_DESCRIPTION = {"CON_TARA", "PARA_PIEZAS"}
MIN_CONDITION_DESC_LENGTH = 50
MAX_SCRAPING_ATTEMPTS = 5


@dataclass
class PhysicalItem:
    lpn: str
    asin: str
    purchase_price: Decimal
    purchase_date: date

    condition_id: Optional[int] = None
    condition_description: Optional[str] = None
    truckload_id: Optional[int] = None

    amazon_description: Optional[str] = None
    amazon_features: Optional[str] = None
    amazon_department: Optional[str] = None
    amazon_category: Optional[str] = None
    amazon_subcategory: Optional[str] = None

    brand: Optional[str] = None
    model: Optional[str] = None
    color: Optional[str] = None
    weight_kg: Optional[Decimal] = None

    current_location: Optional[str] = None
    image_urls: Optional[str] = None
    hashtags: Optional[str] = None
    notas: Optional[str] = None

    available: bool = True
    do_not_list: bool = False

    scraped_price: Optional[Decimal] = None
    scraping_attempts: int = 0
    last_scraped_at: Optional[datetime] = None
    scraping_needs_manual: bool = False

    wallapop_title: Optional[str] = None
    wallapop_description: Optional[str] = None
    keywords: Optional[str] = None
    short_description: Optional[str] = None
    related_keywords: Optional[str] = None
    wallapop_category: Optional[str] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def validate(self) -> list[str]:
        """Business rule validation matching DB CHECK constraints."""
        errors = []
        if self.purchase_price < 0:
            errors.append("purchase_price must be >= 0")
        if self.weight_kg is not None and self.weight_kg < 0:
            errors.append("weight_kg must be >= 0")
        if self.purchase_date > date.today():
            errors.append("purchase_date cannot be in the future")
        return errors

    @property
    def scraping_paused(self) -> bool:
        """Auto-pause after MAX_SCRAPING_ATTEMPTS failed attempts."""
        return self.scraping_attempts >= MAX_SCRAPING_ATTEMPTS

    def increment_scraping(self) -> None:
        """Record a failed scraping attempt; auto-flag for manual review."""
        self.scraping_attempts += 1
        self.last_scraped_at = datetime.utcnow()
        if self.scraping_paused:
            self.scraping_needs_manual = True

    def reset_scraping(self, price: Decimal) -> None:
        """Record a successful scrape result and reset attempt counter."""
        self.scraped_price = price
        self.scraping_attempts = 0
        self.scraping_needs_manual = False
        self.last_scraped_at = datetime.utcnow()

    def image_url_list(self) -> list[str]:
        """Parse comma-separated image_urls into a list."""
        if not self.image_urls:
            return []
        return [u.strip() for u in self.image_urls.split(",") if u.strip()]
