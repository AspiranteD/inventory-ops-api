"""
Sale service with side effects: creating a sale marks the item unavailable,
payment status updates trigger date tracking, and incident return data
gets applied to physical items.
"""
from datetime import date
from decimal import Decimal
from typing import Optional, Protocol

from src.models.sale import Sale, PAID_STATUS_CODE
from src.models.item import PhysicalItem
from src.models.incident import Incident


class SaleNotFoundError(Exception):
    pass


class ValidationError(Exception):
    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__(", ".join(errors))


class SaleRepository(Protocol):
    def get(self, sale_id: int) -> Optional[Sale]: ...
    def list(self, **filters) -> list[Sale]: ...
    def save(self, sale: Sale) -> Sale: ...


class ItemRepository(Protocol):
    def get(self, lpn: str) -> Optional[PhysicalItem]: ...
    def save(self, item: PhysicalItem) -> PhysicalItem: ...


class AccountRepository(Protocol):
    def exists(self, account_id: int) -> bool: ...


class SaleService:
    def __init__(
        self,
        sale_repo: SaleRepository,
        item_repo: ItemRepository,
        account_repo: AccountRepository,
    ):
        self._sales = sale_repo
        self._items = item_repo
        self._accounts = account_repo

    def create_sale(self, sale: Sale) -> Sale:
        errors = sale.validate()
        if errors:
            raise ValidationError(errors)

        if sale.lpn:
            item = self._items.get(sale.lpn)
            if not item:
                raise ValidationError(["Item does not exist"])
            item.available = False
            self._items.save(item)

        if sale.account_id:
            if not self._accounts.exists(sale.account_id):
                raise ValidationError(["Platform account does not exist"])

        return self._sales.save(sale)

    def list_sales(
        self,
        skip: int = 0,
        limit: int = 100,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        payment_status_id: Optional[int] = None,
        account_id: Optional[int] = None,
        in_person: Optional[bool] = None,
    ) -> list[Sale]:
        filters = {"skip": skip, "limit": limit}
        if start_date:
            filters["start_date"] = start_date
        if end_date:
            filters["end_date"] = end_date
        if payment_status_id is not None:
            filters["payment_status_id"] = payment_status_id
        if account_id:
            filters["account_id"] = account_id
        if in_person is not None:
            filters["in_person"] = in_person
        return self._sales.list(**filters)

    def get_daily_sales(self, target_date: date) -> list[Sale]:
        return self._sales.list(start_date=target_date, end_date=target_date)

    def update_payment_status(
        self,
        sale_id: int,
        payment_status_id: int,
        status_code: str,
        amount_paid: Optional[Decimal] = None,
    ) -> Sale:
        """Update payment state with date tracking side effect."""
        sale = self._sales.get(sale_id)
        if not sale:
            raise SaleNotFoundError(f"Sale not found: {sale_id}")

        sale.payment_status_id = payment_status_id
        if amount_paid is not None:
            sale.amount_paid = amount_paid
        sale.mark_paid(status_code)

        return self._sales.save(sale)

    def apply_incident_return(
        self, incident: Incident
    ) -> Optional[dict]:
        """Apply pending return data from an incident to the physical item."""
        if not incident.has_pending_return:
            return None

        return_data = incident.apply_return_data()
        if not return_data:
            return None

        sale = self._sales.get(incident.sale_id)
        if not sale or not sale.lpn:
            return return_data

        item = self._items.get(sale.lpn)
        if not item:
            return return_data

        for field_name, value in return_data.items():
            if hasattr(item, field_name):
                setattr(item, field_name, value)
        self._items.save(item)
        return return_data
