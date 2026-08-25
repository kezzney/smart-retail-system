"""Products Catalog API Endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.connection import get_db
from app.models.product import Product
from app.schemas.product import ProductResponse, ProductListResponse

router = APIRouter(prefix="/products", tags=["Products"])


@router.get(
    "",
    response_model=ProductListResponse,
    summary="List Catalog Products",
    description="Returns paginated list of catalog products with optional category and search filters.",
)
def list_products(
    skip: int = Query(0, ge=0, description="Offset record index"),
    limit: int = Query(50, ge=1, le=200, description="Page limit"),
    category: Optional[str] = Query(None, description="Filter by sub-category"),
    search: Optional[str] = Query(None, description="Search product titles"),
    db: Session = Depends(get_db),
):
    """Retrieve catalog products with pagination and filters."""
    query = db.query(Product)

    if category:
        query = query.filter(Product.sub_category.ilike(f"%{category}%"))
    if search:
        query = query.filter(Product.title.ilike(f"%{search}%"))

    total = query.count()
    items = query.order_by(Product.id.asc()).offset(skip).limit(limit).all()

    return ProductListResponse(
        total=total,
        skip=skip,
        limit=limit,
        items=items,
    )


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Get Product by ID",
    description="Returns detailed metadata for a single product.",
)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Retrieve a single product by ID."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found",
        )
    return product
