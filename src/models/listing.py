from typing import Optional

from sqlmodel import SQLModel, Field


class Listing(SQLModel, table=True):
    __tablename__ = "listings"

    lpn: str = Field(primary_key=True, max_length=50)
    account_id: Optional[str] = Field(default=None, max_length=50, index=True)
    product_id: Optional[str] = Field(default=None, max_length=100)
    title: Optional[str] = Field(default=None, max_length=500)
    description: Optional[str] = Field(default=None)
    sale_price: Optional[float] = Field(default=None)
    category_id: Optional[int] = Field(default=None)
    is_reserved: bool = Field(default=False)
    is_sold: bool = Field(default=False)
    is_banned: bool = Field(default=False)
    conversations_count: int = Field(default=0)
    favorites_count: int = Field(default=0)
    views_count: int = Field(default=0)
    platform: Optional[str] = Field(default=None, max_length=50, index=True)
