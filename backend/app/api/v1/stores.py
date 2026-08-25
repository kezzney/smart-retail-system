"""Stores API Endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.store import Store
from app.schemas.store import StoreResponse, StoreListResponse

router = APIRouter(prefix="/stores", tags=["Stores"])


@router.get(
    "",
    response_model=StoreListResponse,
    summary="List Store Summaries",
    description="Returns store list with sales, customer count, and operational performance metrics.",
)
def list_stores(
    limit: int = Query(50, ge=1, le=500, description="Max stores to return"),
    sort_by: str = Query("total_sales", description="Sort field: total_sales, avg_daily_sales, total_customers"),
    db: Session = Depends(get_db),
):
    """Retrieve store-level summaries."""
    query = db.query(Store)

    if sort_by == "avg_daily_sales":
        query = query.order_by(Store.avg_daily_sales.desc())
    elif sort_by == "total_customers":
        query = query.order_by(Store.total_customers.desc())
    else:
        query = query.order_by(Store.total_sales.desc())

    total = db.query(Store).count()
    items = query.limit(limit).all()

    return StoreListResponse(
        total=total,
        items=items,
    )


@router.get(
    "/{store_id}",
    response_model=StoreResponse,
    summary="Get Store by ID",
    description="Returns performance and structural metadata for a single retail store.",
)
def get_store(store_id: int, db: Session = Depends(get_db)):
    """Retrieve a single store by ID."""
    store = db.query(Store).filter(Store.id == store_id).first()
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Store with ID {store_id} not found",
        )
    return store
