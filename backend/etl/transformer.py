"""
RetailWise AI — ETL Transformer
The core translation layer.

Takes a raw DataFrame (any column names) + the shop's mapping config
and outputs a clean DataFrame matching the Retail OS schema exactly.

Responsibilities:
  1. Column rename      — "MRP" → "selling_price"
  2. Type coercion      — strings → float/int/date/bool
  3. Value mapping      — "GRC" → "staples"  (per value_maps config)
  4. Default injection  — fill missing required fields with config defaults
  5. Category inference — guess category from product name if not present
  6. Validation         — drop rows with missing critical fields, collect warnings
"""

import logging
import re
from datetime import datetime, date
from typing import Any, Dict, List, Tuple

import pandas as pd

from etl.models import ValidationWarning

logger = logging.getLogger(__name__)

# ── Retail OS canonical schemas (required + optional fields per entity) ────────

SCHEMAS: Dict[str, Dict] = {
    "products": {
        "required": ["name", "sku", "category", "selling_price", "cost_price", "unit"],
        "optional": [
            "brand", "unit_size", "order_cycle", "order_day",
            "reorder_point_days", "lead_time_days", "shelf_life_days",
            "min_threshold", "demand_events", "avg_daily_demand", "is_active",
        ],
        "defaults": {
            "brand": None,
            "unit_size": 1.0,
            "order_cycle": "weekly",
            "order_day": None,
            "reorder_point_days": 3.0,
            "lead_time_days": 2,
            "shelf_life_days": 9999,
            "min_threshold": 0.0,
            "demand_events": "",
            "avg_daily_demand": 0.0,
            "is_active": True,
        },
        "types": {
            "selling_price": "float",
            "cost_price": "float",
            "unit_size": "float",
            "reorder_point_days": "float",
            "lead_time_days": "int",
            "shelf_life_days": "int",
            "min_threshold": "float",
            "avg_daily_demand": "float",
            "is_active": "bool",
        },
        "category_values": [
            "staples", "dairy", "snacks", "spices",
            "beverages", "cleaning", "personal_care",
        ],
    },
    "inventory": {
        "required": ["sku", "quantity", "purchase_price"],
        "optional": [
            "batch_number", "unit", "manufactured_date",
            "expiry_date", "status",
        ],
        "defaults": {
            "batch_number": None,       # auto-generated in loader if None
            "unit": None,               # copied from product in loader
            "manufactured_date": None,
            "expiry_date": None,
            "status": "active",
        },
        "types": {
            "quantity": "float",
            "purchase_price": "float",
            "manufactured_date": "date",
            "expiry_date": "date",
        },
    },
    "sales": {
        "required": ["sku", "date", "quantity_sold"],
        "optional": ["revenue", "event_tag"],
        "defaults": {
            "revenue": 0.0,
            "event_tag": "normal",
        },
        "types": {
            "quantity_sold": "float",
            "revenue": "float",
            "date": "date",
        },
    },
    "suppliers": {
        "required": ["name", "whatsapp_number", "region"],
        "optional": [
            "contact_name", "email", "supply_categories", "notes", "is_active",
        ],
        "defaults": {
            "contact_name": "Unknown",
            "email": None,
            "supply_categories": "staples",
            "notes": None,
            "is_active": True,
        },
        "types": {
            "is_active": "bool",
        },
    },
}

# ── Category keyword inference ────────────────────────────────────────────────

_CATEGORY_KEYWORDS = {
    "dairy":        ["milk", "curd", "butter", "ghee", "cheese", "paneer", "egg", "cream", "yogurt"],
    "staples":      ["rice", "wheat", "flour", "oil", "sugar", "salt", "dal", "lentil", "coconut"],
    "snacks":       ["chips", "biscuit", "namkeen", "mixture", "wafer", "cracker", "cookie", "cake", "chocolate"],
    "beverages":    ["tea", "coffee", "juice", "water", "soft drink", "cola", "soda", "energy drink", "noodle"],
    "spices":       ["chilli", "pepper", "turmeric", "masala", "cumin", "coriander", "cardamom", "garam"],
    "cleaning":     ["detergent", "soap", "surf", "vim", "phenyl", "floor cleaner", "dishwash", "bleach", "sanitizer"],
    "personal_care":["shampoo", "lotion", "cream", "toothpaste", "paste", "brush", "razor", "deo", "body wash"],
}


def _infer_category(product_name: str) -> str:
    """Guess Retail OS category from a product name using keyword matching."""
    name_lower = product_name.lower()
    for category, keywords in _CATEGORY_KEYWORDS.items():
        if any(kw in name_lower for kw in keywords):
            return category
    return "staples"  # safe default


# ── Type coercers ─────────────────────────────────────────────────────────────

def _to_float(val: Any) -> float:
    if pd.isna(val) or val == "" or val == "nan":
        return 0.0
    cleaned = re.sub(r"[₹$,\s]", "", str(val))
    try:
        return float(cleaned)
    except (ValueError, TypeError):
        return 0.0


def _to_int(val: Any) -> int:
    return int(_to_float(val))


def _to_bool(val: Any) -> bool:
    if isinstance(val, bool):
        return val
    s = str(val).strip().lower()
    return s in {"1", "true", "yes", "y", "active", "t"}


def _to_date(val: Any, fmt: str = None) -> date | None:
    if pd.isna(val) or str(val).strip() in {"", "nan", "None", "NaT"}:
        return None
    s = str(val).strip()
    if fmt:
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    # Try common formats
    for f in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%m/%d/%Y", "%d.%m.%Y", "%Y%m%d"):
        try:
            return datetime.strptime(s, f).date()
        except ValueError:
            continue
    return None


_TYPE_COERCERS = {
    "float": _to_float,
    "int":   _to_int,
    "bool":  _to_bool,
    "date":  _to_date,
}


# ── Main transform function ───────────────────────────────────────────────────

def transform(
    df: pd.DataFrame,
    entity: str,
    source_cfg: dict,
    shop_id: str = "unknown",
) -> Tuple[pd.DataFrame, List[ValidationWarning]]:
    """
    Transform a raw DataFrame into a Retail OS-compliant DataFrame for the given entity.

    Args:
        df:          Raw DataFrame from extractor (string columns, shop-specific names).
        entity:      One of: "products", "inventory", "sales", "suppliers".
        source_cfg:  The entity's source block from shop YAML config.
        shop_id:     Used for logging only.

    Returns:
        (clean_df, warnings) where clean_df has Retail OS column names and correct types.
    """
    if entity not in SCHEMAS:
        raise ValueError(f"Unknown entity '{entity}'. Supported: {list(SCHEMAS.keys())}")

    schema = SCHEMAS[entity]
    mapping: Dict[str, str] = source_cfg.get("mapping", {})
    value_maps: Dict[str, Dict] = source_cfg.get("value_maps", {})
    date_formats: Dict[str, str] = source_cfg.get("date_formats", {})
    config_defaults: Dict[str, Any] = source_cfg.get("defaults", {})
    warnings: List[ValidationWarning] = []

    # ── Step 1: Rename columns per mapping ────────────────────────────────────
    # mapping = { retail_os_field: raw_column_name }
    reverse_map = {v: k for k, v in mapping.items()}  # raw_col → retail_os_field
    df = df.rename(columns=reverse_map)

    logger.info(
        "[transform][%s/%s] After rename: columns = %s",
        shop_id, entity, list(df.columns)
    )

    # ── Step 2: Apply value maps (e.g. "GRC" → "staples") ────────────────────
    for field, vmap in value_maps.items():
        if field in df.columns:
            df[field] = df[field].map(lambda v: vmap.get(str(v).strip(), v))

    # ── Step 3: Inject defaults for missing columns ───────────────────────────
    # Priority: config_defaults > schema defaults
    merged_defaults = {**schema["defaults"], **config_defaults}
    for field, default_val in merged_defaults.items():
        if field not in df.columns:
            df[field] = default_val

    # ── Step 4: Category inference (products only) ────────────────────────────
    if entity == "products" and "category" in df.columns:
        valid_cats = schema.get("category_values", [])
        def _fix_category(row):
            cat = str(row.get("category", "")).strip().lower()
            if cat in valid_cats:
                return cat
            # Try inference from product name
            return _infer_category(str(row.get("name", "")))
        df["category"] = df.apply(_fix_category, axis=1)

    # ── Step 5: Type coercion ─────────────────────────────────────────────────
    for field, type_name in schema.get("types", {}).items():
        if field not in df.columns:
            continue
        coercer = _TYPE_COERCERS.get(type_name)
        if coercer is None:
            continue
        if type_name == "date":
            date_fmt = date_formats.get(field)
            df[field] = df[field].apply(lambda v: coercer(v, date_fmt))
        else:
            df[field] = df[field].apply(coercer)

    # ── Step 6: Normalize phone numbers for suppliers ─────────────────────────
    if entity == "suppliers" and "whatsapp_number" in df.columns:
        df["whatsapp_number"] = df["whatsapp_number"].apply(_normalize_phone)

    # ── Step 7: Auto-generate batch_number for inventory ─────────────────────
    if entity == "inventory" and "batch_number" in df.columns:
        today_str = datetime.now().strftime("%Y%m%d")
        df["batch_number"] = df.apply(
            lambda row: (
                row["batch_number"]
                if pd.notna(row["batch_number"]) and str(row["batch_number"]) not in {"", "nan", "None"}
                else f"BATCH-{shop_id.upper()}-{today_str}-{row.name + 1:04d}"
            ),
            axis=1,
        )

    # ── Step 8: Validate required fields ──────────────────────────────────────
    required = schema["required"]
    missing_cols = [f for f in required if f not in df.columns]
    if missing_cols:
        raise ValueError(
            f"[{shop_id}/{entity}] Required fields missing after mapping: {missing_cols}. "
            f"Check the 'mapping' section in the shop config YAML."
        )

    # Drop rows where any required field is null/empty
    valid_rows = []
    for idx, row in df.iterrows():
        row_ok = True
        for field in required:
            val = row[field]
            if val is None or (isinstance(val, float) and pd.isna(val)) or str(val).strip() == "":
                warnings.append(ValidationWarning(
                    row_index=int(idx),
                    field=field,
                    issue=f"Required field '{field}' is empty — row dropped",
                    raw_value=str(val),
                ))
                row_ok = False
                break
        if row_ok:
            valid_rows.append(idx)

    dropped = len(df) - len(valid_rows)
    if dropped:
        logger.warning("[transform][%s/%s] Dropped %d rows with missing required fields", shop_id, entity, dropped)

    df = df.loc[valid_rows].reset_index(drop=True)

    # ── Step 9: Keep only Retail OS fields (required + optional) ─────────────
    all_fields = required + schema["optional"]
    df = df[[f for f in all_fields if f in df.columns]]

    logger.info(
        "[transform][%s/%s] ✅ Transformed %d rows → %d columns",
        shop_id, entity, len(df), len(df.columns)
    )

    return df, warnings


def _normalize_phone(val: Any) -> str:
    """Normalize phone numbers to +91XXXXXXXXXX format."""
    s = re.sub(r"[^\d+]", "", str(val))
    if not s.startswith("+"):
        if s.startswith("91") and len(s) == 12:
            s = "+" + s
        elif len(s) == 10:
            s = "+91" + s
    return s
