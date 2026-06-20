"""
RetailWise AI — ETL Loader
Takes a clean, Retail OS-schema DataFrame and bulk-inserts/upserts records
into the central SQLite database using SQLAlchemy.

Conflict resolution strategies:
  skip   — if a record already exists (matched by natural key), leave it alone
  update — overwrite the existing record with the new data
"""

import logging
from datetime import datetime, date
from typing import Dict, Any

import pandas as pd
from sqlalchemy.orm import Session

from database.models import (
    InventoryBatch,
    Product,
    SalesRecord,
    Supplier,
    SupplierPrice,
)
from etl.models import ETLResult

logger = logging.getLogger(__name__)

# ── Natural key per entity (used for duplicate detection) ─────────────────────
NATURAL_KEYS: Dict[str, str] = {
    "products":  "sku",
    "inventory": "batch_number",
    "sales":     None,           # sales are always inserted (date+sku unique check optional)
    "suppliers": "whatsapp_number",
}


def load(
    df: pd.DataFrame,
    entity: str,
    db: Session,
    shop_id: str = "unknown",
    on_conflict: str = "skip",
) -> ETLResult:
    """
    Load a transformed DataFrame into the Retail OS database.

    Args:
        df:           Clean DataFrame matching the Retail OS schema for this entity.
        entity:       "products" | "inventory" | "sales" | "suppliers"
        db:           SQLAlchemy session.
        shop_id:      Shop identifier (for logging and result tagging).
        on_conflict:  "skip" | "update"

    Returns:
        ETLResult with row counts.
    """
    start = datetime.utcnow()
    inserted = updated = skipped = errored = 0
    errors = []

    rows = df.to_dict(orient="records")

    for i, row in enumerate(rows):
        try:
            row = _clean_row(row)  # remove NaNs, convert dates
            if entity == "products":
                inserted_n, updated_n, skipped_n = _upsert_product(row, db, on_conflict)
            elif entity == "inventory":
                inserted_n, updated_n, skipped_n = _upsert_inventory(row, db, on_conflict)
            elif entity == "sales":
                inserted_n, updated_n, skipped_n = _insert_sale(row, db)
            elif entity == "suppliers":
                inserted_n, updated_n, skipped_n = _upsert_supplier(row, db, on_conflict)
            else:
                raise ValueError(f"Unknown entity: {entity}")

            inserted += inserted_n
            updated  += updated_n
            skipped  += skipped_n

        except Exception as exc:
            errored += 1
            msg = f"Row {i}: {exc}"
            errors.append(msg)
            logger.warning("[load][%s/%s] %s", shop_id, entity, msg)
            db.rollback()

    try:
        db.commit()
    except Exception as exc:
        db.rollback()
        errors.append(f"Commit failed: {exc}")
        logger.error("[load][%s/%s] Commit failed: %s", shop_id, entity, exc)

    duration = (datetime.utcnow() - start).total_seconds()

    result = ETLResult(
        shop_id=shop_id,
        entity=entity,
        rows_extracted=len(rows),
        rows_transformed=len(rows),
        rows_inserted=inserted,
        rows_updated=updated,
        rows_skipped=skipped,
        rows_errored=errored,
        errors=errors,
        duration_seconds=round(duration, 3),
        success=errored == 0,
    )

    logger.info("[load] %s", result.summary)
    return result


# ── Entity-specific upsert logic ──────────────────────────────────────────────

def _upsert_product(row: dict, db: Session, on_conflict: str):
    existing = db.query(Product).filter_by(sku=row["sku"]).first()
    if existing:
        if on_conflict == "update":
            for k, v in row.items():
                if hasattr(existing, k):
                    setattr(existing, k, v)
            return 0, 1, 0
        else:
            return 0, 0, 1
    db.add(Product(**{k: v for k, v in row.items() if hasattr(Product, k)}))
    return 1, 0, 0


def _upsert_inventory(row: dict, db: Session, on_conflict: str):
    # Look up product_id via SKU
    sku = row.pop("sku", None)
    product = db.query(Product).filter_by(sku=sku).first() if sku else None
    if not product:
        raise ValueError(f"Product with SKU '{sku}' not found in database. Load products first.")

    row["product_id"] = product.id

    # Inherit unit from product if not provided
    if not row.get("unit"):
        row["unit"] = product.unit

    existing = db.query(InventoryBatch).filter_by(batch_number=row["batch_number"]).first()
    if existing:
        if on_conflict == "update":
            for k, v in row.items():
                if hasattr(existing, k):
                    setattr(existing, k, v)
            return 0, 1, 0
        else:
            return 0, 0, 1

    # Compute expiry status
    row.setdefault("status", _compute_status(row.get("expiry_date")))
    db.add(InventoryBatch(**{k: v for k, v in row.items() if hasattr(InventoryBatch, k)}))
    return 1, 0, 0


def _insert_sale(row: dict, db: Session):
    sku = row.pop("sku", None)
    product = db.query(Product).filter_by(sku=sku).first() if sku else None
    if not product:
        raise ValueError(f"Product with SKU '{sku}' not found. Load products first.")

    row["product_id"] = product.id

    # Compute revenue from selling_price if not provided
    if not row.get("revenue") or row["revenue"] == 0.0:
        row["revenue"] = round(product.selling_price * float(row.get("quantity_sold", 0)), 2)

    db.add(SalesRecord(**{k: v for k, v in row.items() if hasattr(SalesRecord, k)}))
    return 1, 0, 0


def _upsert_supplier(row: dict, db: Session, on_conflict: str):
    existing = db.query(Supplier).filter_by(whatsapp_number=row["whatsapp_number"]).first()
    if existing:
        if on_conflict == "update":
            for k, v in row.items():
                if hasattr(existing, k):
                    setattr(existing, k, v)
            return 0, 1, 0
        else:
            return 0, 0, 1
    db.add(Supplier(**{k: v for k, v in row.items() if hasattr(Supplier, k)}))
    return 1, 0, 0


# ── Utilities ─────────────────────────────────────────────────────────────────

def _clean_row(row: dict) -> dict:
    """Remove NaN values and ensure Python native types for SQLAlchemy."""
    cleaned = {}
    for k, v in row.items():
        if isinstance(v, float) and pd.isna(v):
            cleaned[k] = None
        elif v == "nan" or v == "None":
            cleaned[k] = None
        else:
            cleaned[k] = v
    return cleaned


def _compute_status(expiry_date) -> str:
    """Compute inventory batch status based on expiry date."""
    if expiry_date is None:
        return "active"
    today = date.today()
    if isinstance(expiry_date, str):
        try:
            expiry_date = date.fromisoformat(expiry_date)
        except ValueError:
            return "active"
    if expiry_date < today:
        return "expired"
    days_to_expiry = (expiry_date - today).days
    if days_to_expiry <= 7:
        return "expiring_soon"
    return "active"
