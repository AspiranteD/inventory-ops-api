from typing import Optional

from pydantic import BaseModel


class ListingResponse(BaseModel):
    lpn: str
    account_id: Optional[str] = None
    product_id: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    sale_price: Optional[float] = None
    category_id: Optional[int] = None
    is_reserved: bool
    is_sold: bool
    is_banned: bool
    conversations_count: int
    favorites_count: int
    views_count: int
    platform: Optional[str] = None

    model_config = {"from_attributes": True}


class ListingListResponse(BaseModel):
    listings: list[ListingResponse]
    total: int
    page: int
    page_size: int


class PerformanceMetrics(BaseModel):
    total_listings: int
    total_views: int
    total_favorites: int
    total_conversations: int
    avg_views: float
    avg_favorites: float
    conversion_rate: float
    platforms: dict[str, int]
