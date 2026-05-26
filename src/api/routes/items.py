from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from src.api.deps import get_db
from src.schemas.item import (
    ItemCreate,
    ItemUpdate,
    ItemResponse,
    ItemStats,
    ItemListResponse,
)
from src.services.item_service import ItemService

router = APIRouter(prefix="/api/v1/items", tags=["items"])


@router.get("/stats", response_model=ItemStats)
def get_item_stats(db: Session = Depends(get_db)):
    service = ItemService(db)
    return service.get_stats()


@router.get("", response_model=ItemListResponse)
def list_items(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    condition: Optional[str] = None,
    available: Optional[bool] = None,
    asin: Optional[str] = None,
    truckload_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    service = ItemService(db)
    items, total = service.list_items(
        page=page,
        page_size=page_size,
        condition=condition,
        available=available,
        asin=asin,
        truckload_id=truckload_id,
    )
    return ItemListResponse(
        items=[ItemResponse.model_validate(i) for i in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{lpn}", response_model=ItemResponse)
def get_item(lpn: str, db: Session = Depends(get_db)):
    service = ItemService(db)
    item = service.get_item(lpn)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.post("", response_model=ItemResponse, status_code=201)
def create_item(data: ItemCreate, db: Session = Depends(get_db)):
    service = ItemService(db)
    existing = service.get_item(data.lpn)
    if existing:
        raise HTTPException(status_code=409, detail="Item already exists")
    return service.create_item(data)


@router.patch("/{lpn}", response_model=ItemResponse)
def update_item(lpn: str, data: ItemUpdate, db: Session = Depends(get_db)):
    service = ItemService(db)
    item = service.update_item(lpn, data)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item
