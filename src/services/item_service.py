from typing import Optional

from sqlmodel import Session, select, func, col

from src.models.item import PhysicalItem
from src.schemas.item import ItemCreate, ItemUpdate, ItemStats


class ItemService:
    def __init__(self, session: Session):
        self.session = session

    def list_items(
        self,
        page: int = 1,
        page_size: int = 20,
        condition: Optional[str] = None,
        available: Optional[bool] = None,
        asin: Optional[str] = None,
        truckload_id: Optional[str] = None,
    ) -> tuple[list[PhysicalItem], int]:
        query = select(PhysicalItem)

        if condition is not None:
            query = query.where(PhysicalItem.condition == condition)
        if available is not None:
            query = query.where(PhysicalItem.available == available)
        if asin is not None:
            query = query.where(PhysicalItem.asin == asin)
        if truckload_id is not None:
            query = query.where(PhysicalItem.truckload_id == truckload_id)

        count_query = select(func.count()).select_from(query.subquery())
        total = self.session.exec(count_query).one()

        query = query.offset((page - 1) * page_size).limit(page_size)
        items = self.session.exec(query).all()

        return list(items), total

    def get_item(self, lpn: str) -> Optional[PhysicalItem]:
        return self.session.get(PhysicalItem, lpn)

    def create_item(self, data: ItemCreate) -> PhysicalItem:
        item = PhysicalItem(**data.model_dump())
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item

    def update_item(self, lpn: str, data: ItemUpdate) -> Optional[PhysicalItem]:
        item = self.session.get(PhysicalItem, lpn)
        if not item:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(item, key, value)

        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item

    def get_stats(self) -> ItemStats:
        total = self.session.exec(
            select(func.count()).select_from(PhysicalItem)
        ).one()

        available = self.session.exec(
            select(func.count())
            .select_from(PhysicalItem)
            .where(PhysicalItem.available == True)  # noqa: E712
        ).one()

        sold = total - available

        avg_price = self.session.exec(
            select(func.avg(col(PhysicalItem.sale_price))).where(
                PhysicalItem.sale_price.isnot(None)  # type: ignore
            )
        ).one()

        return ItemStats(
            total=total,
            available=available,
            sold=sold,
            avg_price=round(avg_price, 2) if avg_price else None,
        )
