from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from src.api.deps import get_db
from src.schemas.order import (
    OrderResponse,
    OrderDetailResponse,
    OrderItemResponse,
    OrderListResponse,
    StatusUpdate,
)
from src.services.order_service import OrderService

router = APIRouter(prefix="/api/v1/orders", tags=["orders"])


@router.get("", response_model=OrderListResponse)
def list_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_id: Optional[int] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    account_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    service = OrderService(db)
    orders, total = service.list_orders(
        page=page,
        page_size=page_size,
        status_id=status_id,
        date_from=date_from,
        date_to=date_to,
        account_id=account_id,
    )
    return OrderListResponse(
        orders=[OrderResponse.model_validate(o) for o in orders],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{request_id}", response_model=OrderDetailResponse)
def get_order(request_id: str, db: Session = Depends(get_db)):
    service = OrderService(db)
    order = service.get_order(request_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return OrderDetailResponse(
        **OrderResponse.model_validate(order).model_dump(),
        items=[OrderItemResponse.model_validate(i) for i in order.items],
    )


@router.patch("/{request_id}/status", response_model=OrderResponse)
def update_order_status(
    request_id: str,
    data: StatusUpdate,
    db: Session = Depends(get_db),
):
    service = OrderService(db)
    order, error = service.update_status(request_id, data)
    if error:
        status_code = 404 if "not found" in error.lower() else 422
        raise HTTPException(status_code=status_code, detail=error)
    return order
