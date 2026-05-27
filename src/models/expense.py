"""
Expense model with recurring expense support and payment status tracking.
"""
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Optional


EXPENSE_CATEGORIES = [
    "ALQUILER", "SUMINISTROS", "TRANSPORTE", "MATERIAL",
    "SUSCRIPCIONES", "IMPUESTOS", "REPARACIONES", "OTROS",
]


@dataclass
class Expense:
    expense_id: int
    description: str
    total_amount: Decimal
    expense_date: date = None
    category: str = "OTROS"
    payment_method: str = "EFECTIVO"
    payment_method_id: Optional[int] = None
    supplier_name: Optional[str] = None
    supplier_invoice: Optional[str] = None
    payment_status: str = "PAGADO"
    payment_status_id: Optional[int] = None
    invoice_number: Optional[str] = None
    notes: Optional[str] = None
    payment_date: Optional[date] = None
    is_recurring: bool = False
    recurrence_pattern: Optional[str] = None
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        if self.expense_date is None:
            self.expense_date = date.today()

    def validate(self) -> list[str]:
        errors = []
        if not self.description.strip():
            errors.append("description cannot be empty")
        if self.total_amount <= 0:
            errors.append("total_amount must be > 0")
        if self.expense_date > date.today():
            errors.append("expense_date cannot be in the future")
        if self.payment_date and self.payment_date > date.today():
            errors.append("payment_date cannot be in the future")
        if self.payment_status == "PAGADO" and not self.payment_date:
            errors.append("PAGADO status requires payment_date")
        if self.payment_status != "PAGADO" and self.payment_date:
            errors.append("payment_date only allowed for PAGADO status")
        if self.is_recurring and not self.recurrence_pattern:
            errors.append("recurring expenses require recurrence_pattern")
        if not self.is_recurring and self.recurrence_pattern:
            errors.append("recurrence_pattern only for recurring expenses")
        return errors
