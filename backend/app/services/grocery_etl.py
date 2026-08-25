"""Grocery Dataset ETL Service.

Extracts, cleans, transforms, and ingests product catalog data from GroceryDataset.csv.
"""

import os
import re
import logging
from typing import Optional, List, Dict, Any
import pandas as pd
from sqlalchemy.orm import Session

from app.config import settings
from app.models.product import Product

logger = logging.getLogger(__name__)


def clean_price_value(val: Any) -> float:
    """Clean and parse price strings into floating-point numbers."""
    if pd.isna(val):
        return 0.0
    val_str = str(val).replace("$", "").replace(",", "").strip()
    match = re.search(r"(\d+\.?\d*)", val_str)
    return float(match.group(1)) if match else 0.0


def clean_rating_value(val: Any) -> Optional[float]:
    """Extract numeric star rating from descriptive rating string."""
    if pd.isna(val):
        return None
    match = re.search(r"Rated\s+(\d+\.?\d*)\s+out of", str(val))
    if match:
        return float(match.group(1))
    # Fallback to general float extraction if format varies
    match_fallback = re.search(r"(\d+\.?\d*)", str(val))
    return float(match_fallback.group(1)) if match_fallback else None


def clean_discount_value(val: Any) -> float:
    """Extract normalized discount percentage or amount."""
    if pd.isna(val) or "no discount" in str(val).lower():
        return 0.0
    match_pct = re.search(r"(\d+)\s*%", str(val))
    if match_pct:
        return float(match_pct.group(1))
    match_doll = re.search(r"\$\s*(\d+\.?\d*)", str(val))
    return float(match_doll.group(1)) if match_doll else 0.0


def clean_text_field(val: Any, default: str = "") -> str:
    """Clean multi-line text and whitespace."""
    if pd.isna(val):
        return default
    text = str(val).strip()
    # Normalize excessive internal whitespace
    return re.sub(r"\s+", " ", text)


def load_and_clean_grocery_data(data_root: Optional[str] = None) -> pd.DataFrame:
    """Load raw GroceryDataset.csv and return cleaned DataFrame."""
    root = data_root or settings.SMART_RETAIL_DATA_ROOT
    csv_path = os.path.join(root, "04_Grocery", "raw", "GroceryDataset.csv")

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"GroceryDataset.csv not found at {csv_path}")

    df = pd.read_csv(csv_path)

    # Perform cleaning transformations
    cleaned_df = pd.DataFrame()
    cleaned_df["sub_category"] = df["Sub Category"].apply(lambda x: clean_text_field(x, "General"))
    cleaned_df["title"] = df["Title"].apply(lambda x: clean_text_field(x, "Unknown Item"))
    cleaned_df["price"] = df["Price"].apply(clean_price_value)
    cleaned_df["discount"] = df["Discount"].apply(lambda x: clean_text_field(x, "No Discount"))
    cleaned_df["discount_pct"] = df["Discount"].apply(clean_discount_value)
    cleaned_df["rating"] = df["Rating"].apply(clean_rating_value)
    cleaned_df["currency"] = df["Currency"].apply(lambda x: clean_text_field(x, "$")[:16])
    cleaned_df["feature"] = df["Feature"].apply(lambda x: clean_text_field(x, "") if pd.notna(x) else None)
    cleaned_df["description"] = df["Product Description"].apply(
        lambda x: clean_text_field(x, "") if pd.notna(x) else None
    )

    # Filter invalid records where title is missing
    cleaned_df = cleaned_df[cleaned_df["title"].str.strip() != ""].reset_index(drop=True)

    # Save cleaned processed copy into repository processed data folder
    output_dir = os.path.join(settings.PROCESSED_DATA_DIR, "inventory")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "cleaned_products.csv")
    cleaned_df.to_csv(output_path, index=False)
    logger.info("Saved cleaned grocery catalog to %s (%d records)", output_path, len(cleaned_df))

    return cleaned_df


def ingest_grocery_catalog(
    db: Session,
    data_root: Optional[str] = None,
    limit: Optional[int] = None,
) -> int:
    """Ingest cleaned grocery products into SQLite/PostgreSQL products table."""
    df = load_and_clean_grocery_data(data_root=data_root)

    if limit and limit > 0:
        df = df.head(limit)

    # Clear existing products to ensure idempotency during re-ingestion
    db.query(Product).delete()
    db.commit()

    products_to_create = []
    for _, row in df.iterrows():
        product = Product(
            title=row["title"],
            sub_category=row["sub_category"],
            price=float(row["price"]),
            discount=row["discount"],
            discount_pct=float(row["discount_pct"]),
            rating=float(row["rating"]) if pd.notna(row["rating"]) else None,
            currency=row["currency"],
            feature=row["feature"],
            description=row["description"],
        )
        products_to_create.append(product)

    db.bulk_save_objects(products_to_create)
    db.commit()
    logger.info("Successfully ingested %d products into database", len(products_to_create))
    return len(products_to_create)
