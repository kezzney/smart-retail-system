"""Product Database Model."""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from app.database.base import Base


class Product(Base):
    """Product entity model sourced from the retail product catalog."""

    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(512), nullable=False, index=True)
    sub_category = Column(String(128), nullable=False, index=True)
    price = Column(Float, nullable=False, default=0.0)
    discount = Column(String(64), nullable=True, default="No Discount")
    discount_pct = Column(Float, nullable=False, default=0.0)
    rating = Column(Float, nullable=True)
    currency = Column(String(16), nullable=False, default="$")
    feature = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
