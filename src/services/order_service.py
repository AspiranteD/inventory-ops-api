from datetime import date
from typing import Optional

from sqlmodel import Session, select, func

from src.models.order import Order, OrderItem
from src.schemas.order import StatusUpdate


VALID_TRANSITIONS = {
    1: [2, 5],      # pending -> processing, cancelled
    2: [3, 5],      # processing -> shipped, cancelled
    3: [4, 6],      # shipped -> delivered, returned
    4: [],          # delivered (terminal)
    5: [],          # cancelled (terminal)
    6: [1],         # returned -> pending (re-process)
}


class OrderService:
    def __init__(self, session: Session):
        self.session = session

    def list_orders(
        self,
        page: int = 1,
        page_size: int = 20,
        status_id: Optional[int] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        account_id: Optional[str] = None,
    ) -> tuple[list[Order], int]:
        query = select(Order)

        if status_id is not None:
            query = query.where(Order.status_id == status_id)
        if date_from is not None:
            query = query.where(Order.order_date >= date_from)
        if date_to is not None:
            query = query.where(Order.order_date <= date_to)
        if account_id is not None:
            query = query.where(Order.account_id == account_id)

        count_query = select(func.count()).select_from(query.subquery())
        total = self.session.exec(count_query).one()

        query = query.offset((page - 1) * page_size).limit(page_size)
        orders = self.session.exec(query).all()

        return list(orders), total

    def get_order(self, request_id: str) -> Optional[Order]:
        order = self.session.get(Order, request_id)
        if order:
            _ = order.items  # eager load
        return order

    def update_status(
        self, request_id: str, data: StatusUpdate
    ) -> tuple[Optional[Order], Optional[str]]:
        order = self.session.get(Order, request_id)
        if not order:
            return None, "Order not found"

        allowed = VALID_TRANSITIONS.get(order.status_id, [])
        if data.status_id not in allowed:
            return None, (
                f"Invalid transition from status {order.status_id} "
                f"to {data.status_id}. Allowed: {allowed}"
            )

        order.status_id = data.status_id
        if data.notes:
            order.notes = data.notes

        self.session.add(order)
        self.session.commit()
        self.session.refresh(order)
        return order, None
