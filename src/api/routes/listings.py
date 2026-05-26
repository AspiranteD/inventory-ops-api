from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select, func

from src.api.deps import get_db
from src.models.listing import Listing
from src.schemas.listing import (
    ListingResponse,
    ListingListResponse,
    PerformanceMetrics,
)

router = APIRouter(prefix="/api/v1/listings", tags=["listings"])


@router.get("/performance", response_model=PerformanceMetrics)
def get_performance(db: Session = Depends(get_db)):
    total = db.exec(select(func.count()).select_from(Listing)).one()

    if total == 0:
        return PerformanceMetrics(
            total_listings=0,
            total_views=0,
            total_favorites=0,
            total_conversations=0,
            avg_views=0.0,
            avg_favorites=0.0,
            conversion_rate=0.0,
            platforms={},
        )

    total_views = db.exec(select(func.sum(Listing.views_count))).one() or 0
    total_favorites = db.exec(select(func.sum(Listing.favorites_count))).one() or 0
    total_conversations = db.exec(
        select(func.sum(Listing.conversations_count))
    ).one() or 0

    sold_count = db.exec(
        select(func.count())
        .select_from(Listing)
        .where(Listing.is_sold == True)  # noqa: E712
    ).one()

    platforms_query = (
        select(Listing.platform, func.count())
        .where(Listing.platform.isnot(None))  # type: ignore
        .group_by(Listing.platform)
    )
    platform_results = db.exec(platforms_query).all()
    platforms = {p: c for p, c in platform_results}

    return PerformanceMetrics(
        total_listings=total,
        total_views=int(total_views),
        total_favorites=int(total_favorites),
        total_conversations=int(total_conversations),
        avg_views=round(int(total_views) / total, 2),
        avg_favorites=round(int(total_favorites) / total, 2),
        conversion_rate=round(sold_count / total * 100, 2) if total > 0 else 0.0,
        platforms=platforms,
    )


@router.get("", response_model=ListingListResponse)
def list_listings(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    platform: Optional[str] = None,
    is_sold: Optional[bool] = None,
    is_reserved: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    query = select(Listing)

    if platform is not None:
        query = query.where(Listing.platform == platform)
    if is_sold is not None:
        query = query.where(Listing.is_sold == is_sold)
    if is_reserved is not None:
        query = query.where(Listing.is_reserved == is_reserved)

    count_query = select(func.count()).select_from(query.subquery())
    total = db.exec(count_query).one()

    query = query.offset((page - 1) * page_size).limit(page_size)
    listings = db.exec(query).all()

    return ListingListResponse(
        listings=[ListingResponse.model_validate(l) for l in listings],
        total=total,
        page=page,
        page_size=page_size,
    )
