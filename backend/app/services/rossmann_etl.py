"""Rossmann Store Sales ETL and Analytics Aggregation Service.

Processes historical sales transactions and store metadata to compute:
1. Store-level KPIs and performance rankings.
2. Daily network sales and customer footfall time series.
3. Promotional sales lift indicators.
"""

import os
import logging
from typing import Optional, Dict, Any
import pandas as pd
from sqlalchemy.orm import Session

from app.config import settings
from app.models.store import Store
from app.models.analytics import DailySalesMetric

logger = logging.getLogger(__name__)


def process_rossmann_data(
    data_root: Optional[str] = None,
    sample_stores: Optional[int] = None,
) -> Dict[str, pd.DataFrame]:
    """Load, merge, and aggregate Rossmann datasets."""
    root = data_root or settings.SMART_RETAIL_DATA_ROOT
    train_path = os.path.join(root, "03_Rossmann", "raw", "train.csv")
    store_path = os.path.join(root, "03_Rossmann", "raw", "store.csv")

    if not os.path.exists(train_path) or not os.path.exists(store_path):
        raise FileNotFoundError(f"Rossmann datasets not found at {train_path} or {store_path}")

    # Load store metadata
    df_store = pd.read_csv(store_path)

    # Load sales transactions (low_memory=False to prevent dtype warnings)
    df_train = pd.read_csv(train_path, low_memory=False)

    if sample_stores and sample_stores > 0:
        target_stores = df_store["Store"].head(sample_stores).tolist()
        df_train = df_train[df_train["Store"].isin(target_stores)]
        df_store = df_store[df_store["Store"].isin(target_stores)]

    # Filter to operating days for per-day averages
    df_open = df_train[df_train["Open"] == 1].copy()

    # 1. Compute Store-level Aggregations
    store_stats = (
        df_open.groupby("Store")
        .agg(
            total_sales=("Sales", "sum"),
            total_customers=("Customers", "sum"),
            avg_daily_sales=("Sales", "mean"),
            avg_daily_customers=("Customers", "mean"),
            operating_days=("Date", "count"),
        )
        .reset_index()
    )

    merged_stores = pd.merge(df_store, store_stats, on="Store", how="left")
    merged_stores["total_sales"] = merged_stores["total_sales"].fillna(0.0)
    merged_stores["total_customers"] = merged_stores["total_customers"].fillna(0).astype(int)
    merged_stores["avg_daily_sales"] = merged_stores["avg_daily_sales"].fillna(0.0)
    merged_stores["avg_daily_customers"] = merged_stores["avg_daily_customers"].fillna(0.0)

    # 2. Compute Daily Network Aggregations
    daily_stats = (
        df_train.groupby("Date")
        .agg(
            total_sales=("Sales", "sum"),
            total_customers=("Customers", "sum"),
            open_stores=("Open", lambda x: (x == 1).sum()),
            promo_stores=("Promo", lambda x: (x == 1).sum()),
        )
        .reset_index()
    )

    daily_stats["Date_dt"] = pd.to_datetime(daily_stats["Date"])
    daily_stats["year"] = daily_stats["Date_dt"].dt.year
    daily_stats["month"] = daily_stats["Date_dt"].dt.month
    daily_stats["day_of_week"] = daily_stats["Date_dt"].dt.dayofweek + 1
    daily_stats["avg_sales_per_store"] = daily_stats.apply(
        lambda r: (r["total_sales"] / r["open_stores"]) if r["open_stores"] > 0 else 0.0,
        axis=1,
    )
    daily_stats = daily_stats.sort_values("Date_dt").reset_index(drop=True)

    # 3. Save Processed Files into Repository Processed Data Directory
    sales_out_dir = os.path.join(settings.PROCESSED_DATA_DIR, "sales")
    os.makedirs(sales_out_dir, exist_ok=True)

    store_out_path = os.path.join(sales_out_dir, "store_performance.csv")
    merged_stores.to_csv(store_out_path, index=False)

    daily_out_path = os.path.join(sales_out_dir, "daily_sales_summary.csv")
    daily_stats.drop(columns=["Date_dt"]).to_csv(daily_out_path, index=False)

    logger.info("Saved processed sales data to %s and %s", store_out_path, daily_out_path)

    return {
        "stores": merged_stores,
        "daily": daily_stats,
    }


def ingest_rossmann_analytics(
    db: Session,
    data_root: Optional[str] = None,
    sample_stores: Optional[int] = None,
) -> Dict[str, Any]:
    """Ingest processed Rossmann store KPIs and daily sales metrics into the database."""
    processed = process_rossmann_data(data_root=data_root, sample_stores=sample_stores)
    df_stores = processed["stores"]
    df_daily = processed["daily"]

    # 1. Ingest Stores
    db.query(Store).delete()
    db.commit()

    store_records = []
    for _, row in df_stores.iterrows():
        comp_dist = float(row["CompetitionDistance"]) if pd.notna(row["CompetitionDistance"]) else None
        comp_year = int(row["CompetitionOpenSinceYear"]) if pd.notna(row["CompetitionOpenSinceYear"]) else None

        store = Store(
            id=int(row["Store"]),
            store_type=str(row["StoreType"]),
            assortment=str(row["Assortment"]),
            competition_distance=comp_dist,
            competition_open_year=comp_year,
            promo2=int(row.get("Promo2", 0)),
            total_sales=float(row["total_sales"]),
            total_customers=int(row["total_customers"]),
            avg_daily_sales=float(row["avg_daily_sales"]),
            avg_daily_customers=float(row["avg_daily_customers"]),
        )
        store_records.append(store)

    db.bulk_save_objects(store_records)
    db.commit()

    # 2. Ingest Daily Metrics
    db.query(DailySalesMetric).delete()
    db.commit()

    daily_records = []
    for _, row in df_daily.iterrows():
        metric = DailySalesMetric(
            date=str(row["Date"]),
            year=int(row["year"]),
            month=int(row["month"]),
            day_of_week=int(row["day_of_week"]),
            total_sales=float(row["total_sales"]),
            total_customers=int(row["total_customers"]),
            open_stores=int(row["open_stores"]),
            promo_stores=int(row["promo_stores"]),
            avg_sales_per_store=float(row["avg_sales_per_store"]),
        )
        daily_records.append(metric)

    db.bulk_save_objects(daily_records)
    db.commit()

    logger.info("Successfully seeded %d stores and %d daily metrics", len(store_records), len(daily_records))

    return {
        "stores_ingested": len(store_records),
        "daily_metrics_ingested": len(daily_records),
    }
