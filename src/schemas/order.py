from datetime import datetime, date
from typing import Optional

from pydantic import BaseModel, Field


class OrderItemResponse(BaseModel):
    id: int
    request_id: str
    lpn: str
    price: float
    web_url: Optional[str] = None
    warehouse_status_id: Optional[int] = None

    model_config = {"from_attributes": True}


class OrderResponse(BaseModel):
    request_id: str
    account_id: Optional[str] = None
    buyer_name: Optional[str] = None
    buyer_hash: Optional[str] = None
    buyer_country: Optional[str] = None
    order_date: Optional[date] = None
    due_date: Optional[date] = None
    status_id: int
    active: bool
    shipping_code: Optional[str] = None
    shipping_company_id: Optional[int] = None
    notes: Optional[str] = None
    buyer_address: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class OrderDetailResponse(OrderResponse):
    items: list[OrderItemResponse] = []


class OrderListResponse(BaseModel):
    orders: list[OrderResponse]
    total: int
    page: int
    page_size: int


class StatusUpdate(BaseModel):
    status_id: int = Field(..., ge=1, le=10)
    notes: Optional[str] = None
