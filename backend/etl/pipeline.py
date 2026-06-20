"""
RetailWise AI — ETL Pipeline Orchestrator
Single entry point that chains Extract → Transform → Load for a given shop + entity.

Usage from code:
    from etl.pipeline import run_pipeline, run_shop_pipeline
    from database.db import SessionLocal

    db = SessionLocal()
    result = run_pipeline("shop_a", "products", db)
    db.close()
"""

import logging
import os
from pathlib import Path
from typing import List, Optional

import yaml

from etl.extractor import extract
from etl.loader import load
from etl.models import ETLResult, ShopETLSummary
from etl.transformer import transform

logger = logging.getLogger(__name__)

# ── Default paths (relative to backend/) ──────────────────────────────────────
SHOPS_DIR = os.environ.get("ETL_SHOPS_DIR", "shops")
DATA_DIR  = os.environ.get("ETL_DATA_DIR",  "data")

# Entity load order matters: products must be loaded before inventory/sales
ENTITY_ORDER = ["products", "suppliers", "inventory", "sales"]


def _load_shop_config(shop_id: str) -> dict:
    """Load and parse the YAML config for a given shop."""
    config_path = Path(SHOPS_DIR) / f"{shop_id}.yaml"
    if not config_path.exists():
        raise FileNotFoundError(
            f"No config found for shop '{shop_id}'. "
            f"Expected: {config_path.resolve()}"
        )
    with open(config_path, encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return config


def run_pipeline(
    shop_id: str,
    entity: str,
    db,
    on_conflict: str = "skip",
    config: Optional[dict] = None,
) -> ETLResult:
    """
    Run the full ETL pipeline for a single shop + entity.

    Args:
        shop_id:     Shop identifier (matches filename in shops/).
        entity:      "products" | "inventory" | "sales" | "suppliers"
        db:          SQLAlchemy session.
        on_conflict: "skip" | "update"
        config:      Pre-loaded config dict (optional — loaded from file if None).

    Returns:
        ETLResult with row counts, warnings, and errors.
    """
    from datetime import datetime
    start = datetime.utcnow()

    logger.info("=" * 60)
    logger.info("[pipeline] Starting ETL: shop=%s entity=%s", shop_id, entity)

    # Load shop config
    if config is None:
        config = _load_shop_config(shop_id)

    sources = config.get("sources", {})
    if entity not in sources:
        return ETLResult(
            shop_id=shop_id,
            entity=entity,
            rows_extracted=0,
            rows_transformed=0,
            rows_inserted=0,
            rows_updated=0,
            rows_skipped=0,
            rows_errored=0,
            errors=[f"No source configured for entity '{entity}' in shop config."],
            duration_seconds=0.0,
            success=False,
        )

    source_cfg = sources[entity]

    # ── EXTRACT ───────────────────────────────────────────────────────────────
    logger.info("[pipeline] EXTRACT: reading source file...")
    raw_df = extract(source_cfg, base_data_dir=DATA_DIR)
    rows_extracted = len(raw_df)

    # ── TRANSFORM ─────────────────────────────────────────────────────────────
    logger.info("[pipeline] TRANSFORM: applying mapping...")
    clean_df, warnings = transform(raw_df, entity, source_cfg, shop_id=shop_id)

    # ── LOAD ──────────────────────────────────────────────────────────────────
    logger.info("[pipeline] LOAD: writing to database...")
    conflict_strategy = source_cfg.get("on_conflict", on_conflict)
    result = load(clean_df, entity, db, shop_id=shop_id, on_conflict=conflict_strategy)

    # Merge validation warnings into result
    result.warnings = warnings
    result.rows_extracted = rows_extracted

    duration = (datetime.utcnow() - start).total_seconds()
    result.duration_seconds = round(duration, 3)

    logger.info("[pipeline] ✅ Done: %s", result.summary)
    return result


def run_shop_pipeline(
    shop_id: str,
    db,
    on_conflict: str = "skip",
    entities: Optional[List[str]] = None,
) -> ShopETLSummary:
    """
    Run the full ETL pipeline for ALL entities of a shop in dependency order.

    Args:
        shop_id:   Shop identifier.
        db:        SQLAlchemy session.
        on_conflict: Default conflict resolution ("skip" | "update").
        entities:  Specific entities to run (defaults to all configured entities).

    Returns:
        ShopETLSummary with results for each entity.
    """
    from datetime import datetime
    start = datetime.utcnow()

    config = _load_shop_config(shop_id)
    shop_name = config.get("shop_name", shop_id)
    configured_entities = list(config.get("sources", {}).keys())

    # Respect dependency order
    run_order = [e for e in ENTITY_ORDER if e in configured_entities]
    if entities:
        run_order = [e for e in run_order if e in entities]

    logger.info(
        "[pipeline] 🚀 Full ETL for shop='%s': entities=%s",
        shop_id, run_order
    )

    results = []
    for entity in run_order:
        result = run_pipeline(shop_id, entity, db, on_conflict=on_conflict, config=config)
        results.append(result)
        if not result.success:
            logger.warning(
                "[pipeline] ⚠️ Entity '%s' had %d errors — continuing.",
                entity, result.rows_errored
            )

    total_duration = (datetime.utcnow() - start).total_seconds()
    fully_ok = all(r.success for r in results)

    summary = ShopETLSummary(
        shop_id=shop_id,
        shop_name=shop_name,
        results=results,
        total_duration_seconds=round(total_duration, 3),
        fully_successful=fully_ok,
    )

    logger.info(
        "[pipeline] %s full ETL for shop='%s' in %.2fs",
        "✅ Completed" if fully_ok else "⚠️ Completed with errors",
        shop_id, total_duration,
    )
    return summary


def list_shops() -> List[dict]:
    """Return a list of all configured shops with basic info."""
    shops_path = Path(SHOPS_DIR)
    if not shops_path.exists():
        return []

    shops = []
    for yaml_file in sorted(shops_path.glob("*.yaml")):
        try:
            with open(yaml_file, encoding="utf-8") as f:
                cfg = yaml.safe_load(f)
            shops.append({
                "shop_id":   cfg.get("shop_id", yaml_file.stem),
                "shop_name": cfg.get("shop_name", "Unknown"),
                "location":  cfg.get("location", ""),
                "entities":  list(cfg.get("sources", {}).keys()),
            })
        except Exception as exc:
            logger.warning("Could not parse shop config %s: %s", yaml_file, exc)

    return shops
