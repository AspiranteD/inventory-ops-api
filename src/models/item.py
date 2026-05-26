from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field, Column
import sqlalchemy as sa


class PhysicalItem(SQLModel, table=True):
    __tablename__ = "physical_items"

    lpn: str = Field(primary_key=True, max_length=50)
    asin: Optional[str] = Field(default=None, max_length=20, index=True)
    amazon_description: Optional[str] = Field(default=None)
    image_urls: Optional[str] = Field(default=None, sa_column=Column(sa.Text))
    scraped_price: Optional[float] = Field(default=None)
    sale_price: Optional[float] = Field(default=None)
    condition: Optional[str] = Field(default=None, max_length=30, index=True)
    available: bool = Field(default=True, index=True)
    truckload_id: Optional[str] = Field(default=None, max_length=50, index=True)
    scraping_attempts: int = Field(default=0)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(sa.DateTime, default=sa.func.now()),
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(sa.DateTime, default=sa.func.now(), onupdate=sa.func.now()),
    )
