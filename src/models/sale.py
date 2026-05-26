from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field, Column
import sqlalchemy as sa


class Sale(SQLModel, table=True):
    __tablename__ = "sales"

    id: Optional[int] = Field(default=None, primary_key=True)
    lpn: str = Field(foreign_key="physical_items.lpn", index=True)
    account_id: Optional[str] = Field(default=None, max_length=50)
    final_price: float = Field(default=0.0)
    shipping_cost: float = Field(default=0.0)
    platform_fee: float = Field(default=0.0)
    sale_date: Optional[datetime] = Field(default=None)
    buyer_info: Optional[str] = Field(default=None)
    payment_status_id: int = Field(default=1)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(sa.DateTime, default=sa.func.now()),
    )
