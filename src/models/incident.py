"""
Post-sale incident model for returns, disputes, and claims.

Unique constraint: one incident per sale (1:1 relationship).
Includes pending return data fields that are applied to the item
only when the return is physically received.
"""
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional


INCIDENT_TYPES = ["GENERAL", "DEVOLUCION", "DISPUTA", "RECLAMACION"]
INCIDENT_STATUSES = ["ABIERTA", "EN_GESTION", "RESUELTA", "CERRADA"]
PRIORITY_LEVELS = ["BAJA", "MEDIA", "ALTA", "URGENTE"]


@dataclass
class Incident:
    incident_id: int
    sale_id: int
    buyer_problem_description: str
    platform_account_id: int

    incident_type: str = "GENERAL"
    status: str = "ABIERTA"
    priority: Optional[str] = None

    item_defect_details: Optional[str] = None
    resolution_type: Optional[str] = None
    resolution_description: Optional[str] = None

    refund_amount: Decimal = Decimal("0")
    discount_amount: Decimal = Decimal("0")

    assigned_to_employee_id: Optional[int] = None

    opened_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None

    client_communication_summary: Optional[str] = None
    platform_case_url: Optional[str] = None

    pending_condition_id: Optional[int] = None
    pending_condition_description: Optional[str] = None
    pending_available: bool = True
    pending_purchase_price: Optional[Decimal] = None
    article_data_applied: bool = False
    not_received_at: Optional[datetime] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def validate(self) -> list[str]:
        errors = []
        if not self.buyer_problem_description.strip():
            errors.append("buyer_problem_description cannot be empty")
        if self.refund_amount < 0:
            errors.append("refund_amount must be >= 0")
        if self.discount_amount < 0:
            errors.append("discount_amount must be >= 0")
        if self.resolved_at and self.opened_at and self.resolved_at < self.opened_at:
            errors.append("resolved_at must be >= opened_at")
        if self.incident_type not in INCIDENT_TYPES:
            errors.append(f"invalid incident_type: {self.incident_type}")
        if self.status not in INCIDENT_STATUSES:
            errors.append(f"invalid status: {self.status}")
        return errors

    @property
    def has_pending_return(self) -> bool:
        """True if there's pending return data not yet applied."""
        return (
            self.pending_condition_id is not None
            and not self.article_data_applied
            and self.not_received_at is None
        )

    def apply_return_data(self) -> dict:
        """Extract pending data to apply to the physical item."""
        if not self.has_pending_return:
            return {}
        self.article_data_applied = True
        result = {"available": self.pending_available}
        if self.pending_condition_id is not None:
            result["condition_id"] = self.pending_condition_id
        if self.pending_condition_description:
            result["condition_description"] = self.pending_condition_description
        if self.pending_purchase_price is not None:
            result["purchase_price"] = self.pending_purchase_price
        return result

    def mark_not_received(self) -> None:
        """Mark that the buyer did not return the item."""
        self.not_received_at = datetime.utcnow()
