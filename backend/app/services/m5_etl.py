"""M5 Forecasting Dataset ETL Service.

Prepares a lightweight, high-velocity representative subset of the M5 dataset for
predictive restocking and time-series demand forecasting without loading the full 59M rows into memory.
"""

import os
import logging
from typing import Optional, Dict, Any, List
import pandas as pd

from app.config import settings

logger = logging.getLogger(__name__)


def prepare_m5_forecasting_subset(
    data_root: Optional[str] = None,
    top_n_skus: int = 50,
    max_days: int = 365,
) -> Dict[str, Any]:
    """Extract and transform a representative forecasting subset from M5 raw files.

    Selection Logic:
    1. Reads `sales_train_validation.csv` item headers and historical sales columns.
    2. Identifies the top N highest-velocity items per category (FOODS, HOBBIES, HOUSEHOLD).
    3. Melts the recent time-window (e.g. last 365 days) into clean longitudinal format.
    4. Merges calendar event flags and pricing signals for demand modeling.
    5. Saves output to data/processed/forecasting/.
    """
    root = data_root or settings.SMART_RETAIL_DATA_ROOT
    sales_path = os.path.join(root, "02_M5", "raw", "sales_train_validation.csv")
    cal_path = os.path.join(root, "02_M5", "raw", "calendar.csv")
    prices_path = os.path.join(root, "02_M5", "raw", "sell_prices.csv")

    if not os.path.exists(sales_path) or not os.path.exists(cal_path):
        raise FileNotFoundError(f"M5 dataset files not found in {os.path.join(root, '02_M5', 'raw')}")

    # 1. Load Calendar
    df_cal = pd.read_csv(cal_path)

    # 2. Load Sales Data
    # Identify d_ columns
    df_sales = pd.read_csv(sales_path)
    d_cols = [c for c in df_sales.columns if c.startswith("d_")]

    # Calculate overall total unit sales per item to rank velocity
    df_sales["total_units"] = df_sales[d_cols].sum(axis=1)

    # Stratified selection: top items from each category
    selected_rows: List[pd.DataFrame] = []
    items_per_cat = max(5, top_n_skus // 3)
    for cat in df_sales["cat_id"].unique():
        cat_df = df_sales[df_sales["cat_id"] == cat].nlargest(items_per_cat, "total_units")
        selected_rows.append(cat_df)

    subset_sales = pd.concat(selected_rows).drop_duplicates(subset=["id"])

    # Restrict days to recent window for faster modeling
    recent_d_cols = d_cols[-max_days:] if len(d_cols) > max_days else d_cols
    id_vars = ["id", "item_id", "dept_id", "cat_id", "store_id", "state_id"]

    # Melt from wide to long format
    df_long = pd.melt(
        subset_sales[id_vars + recent_d_cols],
        id_vars=id_vars,
        value_vars=recent_d_cols,
        var_name="d",
        value_name="sales_units",
    )

    # Merge with calendar to get exact dates and event flags
    df_merged = pd.merge(
        df_long,
        df_cal[["d", "date", "wm_yr_wk", "weekday", "month", "year", "event_name_1", "event_type_1", "snap_CA", "snap_TX", "snap_WI"]],
        on="d",
        how="left",
    )

    # Optionally merge prices if sell_prices.csv is available
    if os.path.exists(prices_path):
        df_prices = pd.read_csv(prices_path)
        df_merged = pd.merge(
            df_merged,
            df_prices[["store_id", "item_id", "wm_yr_wk", "sell_price"]],
            on=["store_id", "item_id", "wm_yr_wk"],
            how="left",
        )
        df_merged["sell_price"] = df_merged["sell_price"].ffill().bfill().fillna(2.99)

    # Save to processed forecasting directory
    forecast_out_dir = os.path.join(settings.PROCESSED_DATA_DIR, "forecasting")
    os.makedirs(forecast_out_dir, exist_ok=True)

    out_csv = os.path.join(forecast_out_dir, "m5_representative_skus.csv")
    df_merged.to_csv(out_csv, index=False)
    logger.info("Saved M5 representative subset (%d rows) to %s", len(df_merged), out_csv)

    return {
        "items_count": len(subset_sales),
        "total_records": len(df_merged),
        "categories": list(df_sales["cat_id"].unique()),
        "output_path": out_csv,
    }
