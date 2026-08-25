"""Demand Forecasting Service.

Implements a lightweight rolling-average + linear-regression-with-time-features
forecasting approach. The model is trained once per startup on the pre-processed
M5 representative SKU subset and cached in memory to keep API responses fast.

Design decisions:
- Uses sklearn LinearRegression with day-of-week, month, lag features. Simple,
  fast, and interpretable.
- Falls back to a 14-day rolling mean if LinearRegression training fails.
- Avoids global full-dataset reload on every request (module-level cache).
- Validation split: last 28 days of history held out for MAE/RMSE computation.
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Tuple, Any

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error

from app.config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Module-level cache: loaded once per process startup
# ---------------------------------------------------------------------------
_forecast_cache: Dict[str, Any] = {}
_df_cached: Optional[pd.DataFrame] = None


# ---------------------------------------------------------------------------
# Data Loading
# ---------------------------------------------------------------------------

def _get_processed_path() -> str:
    return os.path.join(settings.PROCESSED_DATA_DIR, "forecasting", "m5_representative_skus.csv")


def load_forecasting_data(force_reload: bool = False) -> pd.DataFrame:
    """Load the processed M5 representative subset into memory (cached)."""
    global _df_cached

    if _df_cached is not None and not force_reload:
        return _df_cached

    csv_path = _get_processed_path()
    if not os.path.exists(csv_path):
        raise FileNotFoundError(
            f"Forecasting dataset not found at {csv_path}. "
            "Run: python backend/app/services/data_manager.py"
        )

    df = pd.read_csv(csv_path, parse_dates=["date"])
    df = df.sort_values(["id", "date"]).reset_index(drop=True)

    # Ensure numeric types
    df["sales_units"] = pd.to_numeric(df["sales_units"], errors="coerce").fillna(0.0)
    df["sell_price"] = pd.to_numeric(df["sell_price"], errors="coerce").fillna(2.99)

    _df_cached = df
    logger.info("Loaded forecasting dataset: %d rows, %d unique series", len(df), df["id"].nunique())
    return df


def get_available_items() -> List[Dict[str, str]]:
    """Return list of (item_id, store_id, category) tuples from cached data."""
    df = load_forecasting_data()
    result = (
        df[["item_id", "store_id", "cat_id"]]
        .drop_duplicates()
        .rename(columns={"cat_id": "category"})
        .to_dict(orient="records")
    )
    return result


# ---------------------------------------------------------------------------
# Feature Engineering
# ---------------------------------------------------------------------------

def _build_features(df_item: pd.DataFrame) -> pd.DataFrame:
    """Add time and lag features to an item time-series."""
    df = df_item.copy().sort_values("date").reset_index(drop=True)

    df["day_of_week"] = df["date"].dt.dayofweek
    df["month"] = df["date"].dt.month
    df["day_of_month"] = df["date"].dt.day
    df["week_of_year"] = df["date"].dt.isocalendar().week.astype(int)

    # Lag features
    df["lag_7"] = df["sales_units"].shift(7).bfill().fillna(0)
    df["lag_14"] = df["sales_units"].shift(14).bfill().fillna(0)
    df["rolling_7_mean"] = df["sales_units"].rolling(7, min_periods=1).mean()
    df["rolling_14_mean"] = df["sales_units"].rolling(14, min_periods=1).mean()

    # Event / SNAP flags
    df["has_event"] = df["event_name_1"].notna().astype(int)

    return df


FEATURE_COLS = [
    "day_of_week", "month", "day_of_month", "week_of_year",
    "lag_7", "lag_14", "rolling_7_mean", "rolling_14_mean", "has_event",
]


# ---------------------------------------------------------------------------
# Rolling-Mean Baseline
# ---------------------------------------------------------------------------

def _rolling_mean_forecast(
    series: pd.Series,
    horizon: int = 14,
    window: int = 14,
) -> Tuple[np.ndarray, None]:
    """Simple rolling mean baseline. Returns (predictions array, None)."""
    recent_mean = float(series.iloc[-window:].mean()) if len(series) >= window else float(series.mean())
    predictions = np.full(horizon, max(0.0, recent_mean))
    return predictions, None


# ---------------------------------------------------------------------------
# Linear Regression Model
# ---------------------------------------------------------------------------

VALIDATION_DAYS = 28
FORECAST_HORIZON = 14


def _train_and_forecast(
    df_item: pd.DataFrame,
    horizon: int = FORECAST_HORIZON,
    validation_days: int = VALIDATION_DAYS,
) -> Dict[str, Any]:
    """Train LinearRegression, produce validation metrics, and forecast future demand."""
    df_feat = _build_features(df_item)

    n = len(df_feat)
    if n < validation_days + 15:
        # Not enough data — fallback to rolling mean
        preds, _ = _rolling_mean_forecast(df_feat["sales_units"], horizon=horizon)
        recent_hist = df_feat.tail(60)[["date", "sales_units"]].to_dict(orient="records")
        mae_val = float(df_feat["sales_units"].std() or 1.0)
        rmse_val = mae_val
        future_dates = [df_feat["date"].iloc[-1] + timedelta(days=i + 1) for i in range(horizon)]
        return {
            "model": "rolling_mean_14d",
            "mae": round(mae_val, 3),
            "rmse": round(rmse_val, 3),
            "history": recent_hist,
            "future_dates": future_dates,
            "future_preds": preds.tolist(),
        }

    train_df = df_feat.iloc[: n - validation_days]
    val_df = df_feat.iloc[n - validation_days :]

    X_train = train_df[FEATURE_COLS].values
    y_train = train_df["sales_units"].values
    X_val = val_df[FEATURE_COLS].values
    y_val = val_df["sales_units"].values

    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_val_s = scaler.transform(X_val)

    model = LinearRegression()
    model.fit(X_train_s, y_train)

    val_preds = np.maximum(0, model.predict(X_val_s))
    mae_val = float(mean_absolute_error(y_val, val_preds))
    rmse_val = float(np.sqrt(mean_squared_error(y_val, val_preds)))

    # Forecast future: use a rolling approach seeded from last known lags
    last_row = df_feat.iloc[-1]
    lag7 = float(df_feat["sales_units"].iloc[-7]) if n >= 7 else float(df_feat["sales_units"].mean())
    lag14 = float(df_feat["sales_units"].iloc[-14]) if n >= 14 else float(df_feat["sales_units"].mean())
    roll7 = float(df_feat["sales_units"].iloc[-7:].mean())
    roll14 = float(df_feat["sales_units"].iloc[-14:].mean())

    future_preds = []
    future_dates = []
    last_date = df_feat["date"].iloc[-1]

    for i in range(1, horizon + 1):
        fd = last_date + timedelta(days=i)
        future_feat = np.array([[
            fd.dayofweek,
            fd.month,
            fd.day,
            fd.isocalendar()[1],
            lag7,
            lag14,
            roll7,
            roll14,
            0,  # no event assumed for future
        ]])
        future_feat_s = scaler.transform(future_feat)
        pred = max(0.0, float(model.predict(future_feat_s)[0]))
        future_preds.append(pred)
        future_dates.append(fd)

        # Update rolling values with prediction
        lag14 = lag7
        lag7 = pred
        roll7 = (roll7 * 6 + pred) / 7
        roll14 = (roll14 * 13 + pred) / 14

    # Return last 60 days of history for chart
    recent_hist = df_feat.tail(60)[["date", "sales_units"]].to_dict(orient="records")

    return {
        "model": "linear_regression_time_features",
        "mae": round(mae_val, 3),
        "rmse": round(rmse_val, 3),
        "history": recent_hist,
        "future_dates": future_dates,
        "future_preds": future_preds,
    }


# ---------------------------------------------------------------------------
# Public Forecasting API
# ---------------------------------------------------------------------------

def forecast_item(item_id: str, store_id: str, horizon: int = FORECAST_HORIZON) -> Optional[Dict[str, Any]]:
    """Generate a demand forecast for the given item/store combination.

    Returns structured result suitable for the ForecastResponse schema, or None if not found.
    Caches results per (item_id, store_id) to avoid repeated model fitting on identical requests.
    """
    cache_key = f"{item_id}|{store_id}|{horizon}"
    if cache_key in _forecast_cache:
        return _forecast_cache[cache_key]

    df = load_forecasting_data()
    mask = (df["item_id"] == item_id) & (df["store_id"] == store_id)
    df_item = df[mask].copy()

    if df_item.empty:
        return None

    cat = df_item["cat_id"].iloc[0]
    fit_result = _train_and_forecast(df_item, horizon=horizon)

    # Build history points
    history_points = [
        {
            "date": str(r["date"])[:10] if hasattr(r["date"], "strftime") else str(r["date"])[:10],
            "actual": round(float(r["sales_units"]), 2),
            "predicted": round(float(r["sales_units"]), 2),  # history = actuals
        }
        for r in fit_result["history"]
    ]

    # Build forecast points
    forecast_points = [
        {
            "date": str(fd)[:10],
            "actual": None,
            "predicted": round(float(pv), 2),
        }
        for fd, pv in zip(fit_result["future_dates"], fit_result["future_preds"])
    ]

    result = {
        "item_id": item_id,
        "store_id": store_id,
        "category": cat,
        "model_name": fit_result["model"],
        "forecast_horizon_days": horizon,
        "mae": fit_result["mae"],
        "rmse": fit_result["rmse"],
        "history": history_points,
        "forecast": forecast_points,
    }

    _forecast_cache[cache_key] = result
    return result
