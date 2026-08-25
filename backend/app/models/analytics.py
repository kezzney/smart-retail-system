"""Daily Analytics Summary Database Model."""

from sqlalchemy import Column, Integer, String, Float
from app.database.base import Base


class DailySalesMetric(Base):
    """Daily aggregated sales metric across all operational stores."""

    __tablename__ = "daily_sales_metrics"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    date = Column(String(16), nullable=False, unique=True, index=True)  # YYYY-MM-DD
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    day_of_week = Column(Integer, nullable=False)
    total_sales = Column(Float, nullable=False, default=0.0)
    total_customers = Column(Integer, nullable=False, default=0)
    open_stores = Column(Integer, nullable=False, default=0)
    promo_stores = Column(Integer, nullable=False, default=0)
    avg_sales_per_store = Column(Float, nullable=False, default=0.0)
