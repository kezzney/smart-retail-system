"""Product Schemas."""

from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class ProductBase(BaseModel):
    """Base product attributes."""

    title: str = Field(..., description="Product name/title")
    sub_category: str = Field(..., description="Product sub-category")
    price: float = Field(..., description="Regular unit price")
    discount: Optional[str] = Field("No Discount", description="Raw discount text")
    discount_pct: float = Field(0.0, description="Normalized discount percentage")
    rating: Optional[float] = Field(None, description="Average customer rating")
    currency: str = Field("$", description="Currency symbol")
    feature: Optional[str] = Field(None, description="Product feature summary")
    description: Optional[str] = Field(None, description="Detailed product description")


class ProductCreate(ProductBase):
    """Schema for product creation."""
    pass


class ProductResponse(ProductBase):
    """Schema for product query response."""

    id: int
    model_config = ConfigDict(from_attributes=True)


class ProductListResponse(BaseModel):
    """Paginated product list response."""

    total: int
    skip: int
    limit: int
    items: List[ProductResponse]
