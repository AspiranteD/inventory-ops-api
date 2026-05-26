from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ItemCreate(BaseModel):
    lpn: str = Field(..., max_length=50)
    asin: Optional[str] = None
    amazon_description: Optional[str] = None
    image_urls: Optional[str] = None
    scraped_price: Optional[float] = None
    sale_price: Optional[float] = None
    condition: Optional[str] = None
    available: bool = True
    truckload_id: Optional[str] = None


class ItemUpdate(BaseModel):
    asin: Optional[str] = None
    amazon_description: Optional[str] = None
    image_urls: Optional[str] = None
    scraped_price: Optional[float] = None
    sale_price: Optional[float] = None
    condition: Optional[str] = None
    available: Optional[bool] = None
    truckload_id: Optional[str] = None
    scraping_attempts: Optional[int] = None


class ItemResponse(BaseModel):
    lpn: str
    asin: Optional[str] = None
    amazon_description: Optional[str] = None
    image_urls: Optional[str] = None
    scraped_price: Optional[float] = None
    sale_price: Optional[float] = None
    condition: Optional[str] = None
    available: bool
    truckload_id: Optional[str] = None
    scraping_attempts: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ItemStats(BaseModel):
    total: int
    available: int
    sold: int
    avg_price: Optional[float] = None


class ItemListResponse(BaseModel):
    items: list[ItemResponse]
    total: int
    page: int
    page_size: int
