"""
RetailWise AI — ETL Router
REST API endpoints for triggering ETL pipelines.

Endpoints:
  GET  /api/etl/shops                         — List all configured shops
  POST /api/etl/run/{shop_id}                 — Run full ETL for a shop (all entities)
  POST /api/etl/run/{shop_id}/{entity}        — Run ETL for one entity of a shop
  GET  /api/etl/preview/{shop_id}/{entity}    — Dry-run: extract + transform only
"""

import logging
from typing import List, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database.db import get_db
from etl.models import ETLResult, ShopETLSummary
from etl.pipeline import list_shops, run_pipeline, run_shop_pipeline

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/etl", tags=["etl"])

EntityType = Literal["products", "inventory", "sales", "suppliers"]
ConflictStrategy = Literal["skip", "update"]


# ── GET /api/etl/shops ────────────────────────────────────────────────────────

@router.get(
    "/shops",
    summary="List all configured shops",
    response_model=List[dict],
)
def get_shops():
    """
    Returns a list of all shops that have a YAML config file in the shops/ directory.
    Each entry includes shop_id, shop_name, location, and configured entities.
    """
    try:
        shops = list_shops()
        return shops
    except Exception as exc:
        logger.error("[etl] Failed to list shops: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


# ── POST /api/etl/run/{shop_id} ───────────────────────────────────────────────

@router.post(
    "/run/{shop_id}",
    summary="Run full ETL for a shop",
    response_model=ShopETLSummary,
)
def run_full_etl(
    shop_id: str,
    on_conflict: ConflictStrategy = Query(
        default="skip",
        description="How to handle duplicate records: skip (keep existing) or update (overwrite)",
    ),
    entities: Optional[str] = Query(
        default=None,
        description="Comma-separated list of entities to load (default: all). "
                    "E.g. 'products,inventory'",
    ),
    db: Session = Depends(get_db),
):
    """
    Run the complete ETL pipeline for a shop — all entities in dependency order:
    products → suppliers → inventory → sales.

    This is the primary endpoint for onboarding a new shop's data.
    """
    entity_list = [e.strip() for e in entities.split(",")] if entities else None

    try:
        summary = run_shop_pipeline(
            shop_id=shop_id,
            db=db,
            on_conflict=on_conflict,
            entities=entity_list,
        )
        return summary
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        logger.exception("[etl] Unexpected error running ETL for shop '%s'", shop_id)
        raise HTTPException(status_code=500, detail=str(exc))


# ── POST /api/etl/run/{shop_id}/{entity} ──────────────────────────────────────

@router.post(
    "/run/{shop_id}/{entity}",
    summary="Run ETL for one entity of a shop",
    response_model=ETLResult,
)
def run_entity_etl(
    shop_id: str,
    entity: EntityType,
    on_conflict: ConflictStrategy = Query(default="skip"),
    db: Session = Depends(get_db),
):
    """
    Run ETL for a single entity (e.g. just 'products' or just 'sales') of a shop.

    Note: inventory and sales depend on products being loaded first.
    """
    try:
        result = run_pipeline(
            shop_id=shop_id,
            entity=entity,
            db=db,
            on_conflict=on_conflict,
        )
        return result
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        logger.exception(
            "[etl] Unexpected error running ETL for %s/%s", shop_id, entity
        )
        raise HTTPException(status_code=500, detail=str(exc))


# ── GET /api/etl/preview/{shop_id}/{entity} ───────────────────────────────────

@router.get(
    "/preview/{shop_id}/{entity}",
    summary="Preview ETL output without loading to database",
    response_model=dict,
)
def preview_etl(
    shop_id: str,
    entity: EntityType,
    rows: int = Query(default=5, ge=1, le=50, description="Number of rows to return in preview"),
    db: Session = Depends(get_db),
):
    """
    Dry-run: Extracts and transforms data without writing to the database.
    Returns a sample of the clean transformed rows so you can validate the mapping
    before committing.
    """
    import yaml
    from pathlib import Path
    from etl.extractor import extract
    from etl.transformer import transform
    from etl.pipeline import SHOPS_DIR, DATA_DIR

    config_path = Path(SHOPS_DIR) / f"{shop_id}.yaml"
    if not config_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"No config found for shop '{shop_id}'",
        )

    try:
        with open(config_path, encoding="utf-8") as f:
            config = yaml.safe_load(f)

        source_cfg = config.get("sources", {}).get(entity)
        if not source_cfg:
            raise HTTPException(
                status_code=404,
                detail=f"No source configured for entity '{entity}' in shop '{shop_id}'",
            )

        raw_df = extract(source_cfg, base_data_dir=DATA_DIR)
        clean_df, warnings = transform(raw_df, entity, source_cfg, shop_id=shop_id)

        # Convert dates to ISO strings for JSON serialization
        clean_df = clean_df.copy()
        for col in clean_df.select_dtypes(include=["object"]).columns:
            pass  # already strings
        clean_df = clean_df.astype(str).replace("None", None).replace("nan", None)

        return {
            "shop_id": shop_id,
            "entity": entity,
            "total_rows": len(clean_df),
            "columns": list(clean_df.columns),
            "sample": clean_df.head(rows).to_dict(orient="records"),
            "validation_warnings": [w.model_dump() for w in warnings[:20]],
        }

    except HTTPException:
        raise
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        logger.exception("[etl] Preview failed for %s/%s", shop_id, entity)
        raise HTTPException(status_code=500, detail=str(exc))
