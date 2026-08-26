"""Production Seed Service.

Seeds the database from pre-processed CSV files bundled with the repository
(data/processed/). This is designed to run at application startup when the
database is empty, enabling Railway production deployments to start with
functional demo data without requiring the full raw datasets.

Seeding is skipped when the database already contains records to preserve
any data loaded via the full ETL pipeline.
"""

import os
import logging
from typing import Optional

import pandas as pd
from sqlalchemy.orm import Session

from app.config import settings
from app.models.product import Product
from app.models.store import Store
from app.models.analytics import DailySalesMetric

logger = logging.getLogger(__name__)

# Paths to committed processed CSVs (relative to PROCESSED_DATA_DIR)
_PRODUCTS_CSV = "inventory/cleaned_products.csv"
_STORES_CSV = "sales/store_performance.csv"
_DAILY_CSV = "sales/daily_sales_summary.csv"


def _seed_products(db: Session, products_csv: str) -> int:
    """Seed the products table from cleaned_products.csv."""
    if not os.path.exists(products_csv):
        logger.warning("Products seed CSV not found at %s — skipping product seed", products_csv)
        return 0

    df = pd.read_csv(products_csv)
    records = []
    for _, row in df.iterrows():
        product = Product(
            title=str(row.get("title", "Unknown Item")),
            sub_category=str(row.get("sub_category", "General")),
            price=float(row.get("price", 0.0)) if pd.notna(row.get("price")) else 0.0,
            discount=str(row.get("discount", "No Discount")) if pd.notna(row.get("discount")) else "No Discount",
            discount_pct=float(row.get("discount_pct", 0.0)) if pd.notna(row.get("discount_pct")) else 0.0,
            rating=float(row.get("rating")) if pd.notna(row.get("rating")) else None,
            currency=str(row.get("currency", "$"))[:16] if pd.notna(row.get("currency")) else "$",
            feature=str(row.get("feature")) if pd.notna(row.get("feature")) else None,
            description=str(row.get("description")) if pd.notna(row.get("description")) else None,
        )
        records.append(product)

    db.bulk_save_objects(records)
    db.commit()
    logger.info("Seeded %d products from processed CSV", len(records))
    return len(records)


def _seed_stores(db: Session, stores_csv: str) -> int:
    """Seed the stores table from store_performance.csv."""
    if not os.path.exists(stores_csv):
        logger.warning("Stores seed CSV not found at %s — skipping store seed", stores_csv)
        return 0

    df = pd.read_csv(stores_csv)
    records = []
    for _, row in df.iterrows():
        store = Store(
            id=int(row["Store"]),
            store_type=str(row.get("StoreType", "a")),
            assortment=str(row.get("Assortment", "a")),
            competition_distance=float(row["CompetitionDistance"]) if pd.notna(row.get("CompetitionDistance")) else None,
            competition_open_year=int(row["CompetitionOpenSinceYear"]) if pd.notna(row.get("CompetitionOpenSinceYear")) else None,
            promo2=int(row.get("Promo2", 0)) if pd.notna(row.get("Promo2")) else 0,
            total_sales=float(row.get("total_sales", 0.0)) if pd.notna(row.get("total_sales")) else 0.0,
            total_customers=int(row.get("total_customers", 0)) if pd.notna(row.get("total_customers")) else 0,
            avg_daily_sales=float(row.get("avg_daily_sales", 0.0)) if pd.notna(row.get("avg_daily_sales")) else 0.0,
            avg_daily_customers=float(row.get("avg_daily_customers", 0.0)) if pd.notna(row.get("avg_daily_customers")) else 0.0,
        )
        records.append(store)

    db.bulk_save_objects(records)
    db.commit()
    logger.info("Seeded %d stores from processed CSV", len(records))
    return len(records)


def _seed_daily_metrics(db: Session, daily_csv: str) -> int:
    """Seed DailySalesMetric table from daily_sales_summary.csv."""
    if not os.path.exists(daily_csv):
        logger.warning("Daily sales CSV not found at %s — skipping daily metrics seed", daily_csv)
        return 0

    df = pd.read_csv(daily_csv)
    records = []
    for _, row in df.iterrows():
        metric = DailySalesMetric(
            date=str(row.get("Date", "")),
            year=int(row.get("year", 0)) if pd.notna(row.get("year")) else 0,
            month=int(row.get("month", 0)) if pd.notna(row.get("month")) else 0,
            day_of_week=int(row.get("day_of_week", 0)) if pd.notna(row.get("day_of_week")) else 0,
            total_sales=float(row.get("total_sales", 0.0)) if pd.notna(row.get("total_sales")) else 0.0,
            total_customers=int(row.get("total_customers", 0)) if pd.notna(row.get("total_customers")) else 0,
            open_stores=int(row.get("open_stores", 0)) if pd.notna(row.get("open_stores")) else 0,
            promo_stores=int(row.get("promo_stores", 0)) if pd.notna(row.get("promo_stores")) else 0,
            avg_sales_per_store=float(row.get("avg_sales_per_store", 0.0)) if pd.notna(row.get("avg_sales_per_store")) else 0.0,
        )
        records.append(metric)

    db.bulk_save_objects(records)
    db.commit()
    logger.info("Seeded %d daily sales metrics from processed CSV", len(records))
    return len(records)


def seed_database_if_empty(db: Session) -> dict:
    """Seed the database from processed CSVs if tables are empty.

    This function is idempotent — it checks record counts before seeding
    and skips any table that already contains data.

    Returns:
        dict with counts of records seeded per table (0 means table was already populated).
    """
    result = {"products": 0, "stores": 0, "daily_metrics": 0}

    products_csv = os.path.join(settings.PROCESSED_DATA_DIR, _PRODUCTS_CSV)
    stores_csv = os.path.join(settings.PROCESSED_DATA_DIR, _STORES_CSV)
    daily_csv = os.path.join(settings.PROCESSED_DATA_DIR, _DAILY_CSV)

    # --- Products ---
    if db.query(Product).count() == 0:
        try:
            result["products"] = _seed_products(db, products_csv)
        except Exception as exc:
            logger.error("Product seeding failed: %s", exc)
    else:
        logger.info("Products table already populated — skipping seed")

    # --- Stores ---
    if db.query(Store).count() == 0:
        try:
            result["stores"] = _seed_stores(db, stores_csv)
        except Exception as exc:
            logger.error("Store seeding failed: %s", exc)
    else:
        logger.info("Stores table already populated — skipping seed")

    # --- Daily Sales Metrics ---
    if db.query(DailySalesMetric).count() == 0:
        try:
            result["daily_metrics"] = _seed_daily_metrics(db, daily_csv)
        except Exception as exc:
            logger.error("Daily metrics seeding failed: %s", exc)
    else:
        logger.info("DailySalesMetric table already populated — skipping seed")

    return result
