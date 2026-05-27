"""
Order (Pedido) and OrderItem (PedidoItem) models.

Orders represent shipment requests from platforms. Each order contains
multiple items, each with a warehouse status tracking the fulfillment
pipeline: BUSCAR -> ENCONTRADO -> PREPARADO -> ESPERANDO -> CANCELAR.
"""
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Optional


WAREHOUSE_STATES = ["BUSCAR", "ENCONTRADO", "PREPARADO", "ESPERANDO", "CANCELAR"]
CANCEL_STATE = "CANCELAR"
MAX_EXTRACTION_ATTEMPTS = 3


@dataclass
class OrderItem:
    request_id: str
    lpn: str
    warehouse_status_id: int
    price: Optional[Decimal] = None
    web_url: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def validate(self) -> list[str]:
        errors = []
        if self.price is not None and self.price < 0:
            errors.append("price must be >= 0")
        return errors


@dataclass
class Order:
    request_id: str
    status_id: int
    account_id: Optional[int] = None

    buyer_name: Optional[str] = None
    buyer_hash: Optional[str] = None
    buyer_country: Optional[str] = None

    order_date: Optional[datetime] = None
    due_date: Optional[datetime] = None

    shipping_company_id: Optional[int] = None
    instructions_url: Optional[str] = None
    shipping_label_url: Optional[str] = None
    shipping_code: Optional[str] = None

    active: bool = True
    extraction_failed: bool = False
    extraction_attempts: int = 0

    order_name: Optional[str] = None
    order_image: Optional[str] = None
    handover_mode: Optional[str] = None
    notes: Optional[str] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    items: list[OrderItem] = field(default_factory=list)

    def validate(self) -> list[str]:
        errors = []
        if self.due_date and self.order_date and self.due_date < self.order_date:
            errors.append("due_date must be >= order_date")
        return errors

    @property
    def is_overdue(self) -> bool:
        if not self.due_date or not self.active:
            return False
        return datetime.utcnow() > self.due_date

    def record_extraction_failure(self) -> None:
        """Increment extraction_attempts; auto-mark failed after MAX."""
        self.extraction_attempts += 1
        if self.extraction_attempts >= MAX_EXTRACTION_ATTEMPTS:
            self.extraction_failed = True

    def reset_extraction(self) -> None:
        self.extraction_attempts = 0
        self.extraction_failed = False
