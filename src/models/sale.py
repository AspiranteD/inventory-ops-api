"""
Sale model with computed fields and referential integrity constraints.

Supports online (via listing) and in-person (via direct LPN) sales.
amount_due is computed as MAX(total - paid, 0).
"""
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import Optional


PAID_STATUS_CODE = "PAID"


@dataclass
class Sale:
    id: int
    final_price: Decimal
    sale_date: date = field(default_factory=date.today)

    request_id: Optional[str] = None
    listing_id: Optional[int] = None
    lpn: Optional[str] = None
    account_id: Optional[int] = None

    shipping_cost: Decimal = Decimal("0")
    platform_fee: Decimal = Decimal("0")

    payment_status_id: Optional[int] = None
    payment_method_id: Optional[int] = None
    buyer_info: Optional[str] = None
    payment_received_date: Optional[date] = None
    amount_paid: Decimal = Decimal("0")
    invoice_id: Optional[int] = None

    in_person: bool = False
    smile_face: bool = False
    created_at: Optional[datetime] = None

    @property
    def amount_due(self) -> Decimal:
        """Computed: MAX((final_price + shipping_cost + platform_fee) - amount_paid, 0)."""
        total = self.final_price + self.shipping_cost + self.platform_fee
        return max(total - self.amount_paid, Decimal("0"))

    def validate(self) -> list[str]:
        errors = []
        if self.final_price < 0:
            errors.append("final_price must be >= 0")
        if self.shipping_cost < 0:
            errors.append("shipping_cost must be >= 0")
        if self.platform_fee < 0:
            errors.append("platform_fee must be >= 0")
        if self.amount_paid < 0:
            errors.append("amount_paid must be >= 0")
        total = self.final_price + self.shipping_cost + self.platform_fee
        if self.amount_paid > total:
            errors.append("amount_paid cannot exceed total (price + shipping + fee)")
        if self.payment_received_date and self.payment_received_date > date.today():
            errors.append("payment_received_date cannot be in the future")
        if self.sale_date > date.today():
            errors.append("sale_date cannot be in the future")

        if self.in_person:
            if self.listing_id is not None:
                errors.append("in_person sale cannot have listing_id")
            if not self.lpn:
                errors.append("in_person sale requires lpn")
        else:
            if not self.listing_id and not self.lpn:
                errors.append("online sale requires listing_id or lpn")
        return errors

    def mark_paid(self, status_code: str) -> None:
        """If status code is PAID, set payment_received_date to today."""
        if status_code == PAID_STATUS_CODE:
            self.payment_received_date = date.today()
