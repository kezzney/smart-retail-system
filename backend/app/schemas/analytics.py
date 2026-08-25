"""Analytics and Dashboard KPI Schemas."""

from typing import List, Optional
from pydantic import BaseModel, Field


class TopStoreItem(BaseModel):
    """Top performing store item."""

    store_id: int
    store_type: str
    total_sales: float
    total_customers: int
    avg_daily_sales: float


class CategorySummaryItem(BaseModel):
    """Product category summary item."""

    category: str
    product_count: int
    avg_price: float
    min_price: float
    max_price: float


class AnalyticsOverviewResponse(BaseModel):
    """Dashboard executive summary KPI response."""

    total_sales: float = Field(..., description="Overall sales revenue")
    total_customers: int = Field(..., description="Overall customer footfall")
    number_of_stores: int = Field(..., description="Total monitored retail stores")
    number_of_products: int = Field(..., description="Total catalog products")
    average_daily_sales: float = Field(..., description="Average daily network sales")
    active_promotions: int = Field(..., description="Number of stores currently running promotions")
    promo_sales_lift_pct: float = Field(..., description="Percentage lift in sales during promotions")
    top_performing_store: TopStoreItem = Field(..., description="Highest grossing store")
    top_categories: List[CategorySummaryItem] = Field(default_factory=list, description="Top product categories")


class SalesTrendItem(BaseModel):
    """Time-series data point for sales and traffic trends."""

    date: str
    sales: float
    customers: int
    open_stores: int
    promo_active: bool
    avg_sales_per_store: float


class SalesTrendResponse(BaseModel):
    """Sales trend response."""

    start_date: str
    end_date: str
    total_points: int
    data: List[SalesTrendItem]
