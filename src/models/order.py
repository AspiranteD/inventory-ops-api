from datetime import datetime, date
from typing import Optional

from sqlmodel import SQLModel, Field, Column, Relationship
import sqlalchemy as sa


class OrderItem(SQLModel, table=True):
    __tablename__ = "order_items"

    id: Optional[int] = Field(default=None, primary_key=True)
    request_id: str = Field(foreign_key="orders.request_id", index=True)
    lpn: str = Field(foreign_key="physical_items.lpn", index=True)
    price: float = Field(default=0.0)
    web_url: Optional[str] = Field(default=None)
    warehouse_status_id: Optional[int] = Field(default=None)

    order: Optional["Order"] = Relationship(back_populates="items")


class Order(SQLModel, table=True):
    __tablename__ = "orders"

    request_id: str = Field(primary_key=True, max_length=50)
    account_id: Optional[str] = Field(default=None, max_length=50, index=True)
    buyer_name: Optional[str] = Field(default=None, max_length=200)
    buyer_hash: Optional[str] = Field(default=None, max_length=64)
    buyer_country: Optional[str] = Field(default=None, max_length=5)
    order_date: Optional[date] = Field(default=None, index=True)
    due_date: Optional[date] = Field(default=None)
    status_id: int = Field(default=1, index=True)
    active: bool = Field(default=True)
    shipping_code: Optional[str] = Field(default=None, max_length=100)
    shipping_company_id: Optional[int] = Field(default=None)
    notes: Optional[str] = Field(default=None)
    buyer_address: Optional[str] = Field(
        default=None, sa_column=Column(sa.Text)
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(sa.DateTime, default=sa.func.now()),
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(sa.DateTime, default=sa.func.now(), onupdate=sa.func.now()),
    )

    items: list[OrderItem] = Relationship(back_populates="order")
