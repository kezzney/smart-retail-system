"""Store Database Model."""

from sqlalchemy import Column, Integer, String, Float
from app.database.base import Base


class Store(Base):
    """Store entity model containing store metadata and aggregated performance."""

    __tablename__ = "stores"

    id = Column(Integer, primary_key=True, index=True)  # Store ID from Rossmann (1..1115)
    store_type = Column(String(16), nullable=False, default="a")
    assortment = Column(String(16), nullable=False, default="a")
    competition_distance = Column(Float, nullable=True)
    competition_open_year = Column(Integer, nullable=True)
    promo2 = Column(Integer, nullable=False, default=0)
    total_sales = Column(Float, nullable=False, default=0.0)
    total_customers = Column(Integer, nullable=False, default=0)
    avg_daily_sales = Column(Float, nullable=False, default=0.0)
    avg_daily_customers = Column(Float, nullable=False, default=0.0)
