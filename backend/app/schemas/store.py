"""Store Schemas."""

from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class StoreResponse(BaseModel):
    """Store summary information schema."""

    id: int = Field(..., description="Store Identifier")
    store_type: str = Field(..., description="Store classification code")
    assortment: str = Field(..., description="Assortment level code")
    competition_distance: Optional[float] = Field(None, description="Distance to competitor in meters")
    competition_open_year: Optional[int] = Field(None, description="Year competitor opened")
    promo2: int = Field(..., description="Continuous promotion participation flag")
    total_sales: float = Field(..., description="Historical total sales revenue")
    total_customers: int = Field(..., description="Historical total customer count")
    avg_daily_sales: float = Field(..., description="Average sales per operating day")
    avg_daily_customers: float = Field(..., description="Average customers per operating day")

    model_config = ConfigDict(from_attributes=True)


class StoreListResponse(BaseModel):
    """List of stores response."""

    total: int
    items: List[StoreResponse]
