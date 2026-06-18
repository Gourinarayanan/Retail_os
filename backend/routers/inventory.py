"""
RetailWise AI — Inventory Router
GET   /api/inventory                      — all products with stock + alerts
GET   /api/inventory/alerts               — only items with status ≠ ok
GET   /api/inventory/{product_id}         — single product full detail
PATCH /api/inventory/{batch_id}/quantity  — manual stock adjustment
"""

import logging
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database.db import get_db
from database.models import InventoryBatch, Product

router = APIRouter(prefix="/api/inventory", tags=["inventory"])
logger = logging.getLogger(__name__)


# ── Pydantic schemas ──────────────────────────────────────────────────────────

class QuantityAdjustment(BaseModel):
    quantity: float = Field(..., ge=0, description="New quantity (must be ≥ 0)")
    note: str | None = Field(None, max_length=300)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _batch_to_dict(b: InventoryBatch) -> dict:
    today = date.today()
    days_to_expiry = None
    if b.expiry_date:
        days_to_expiry = (b.expiry_date - today).days
    return {
        "id": b.id,
        "batch_number": b.batch_number,
        "quantity": b.quantity,
        "unit": b.unit,
        "purchase_price": b.purchase_price,
        "manufactured_date": b.manufactured_date.isoformat() if b.manufactured_date else None,
        "expiry_date": b.expiry_date.isoformat() if b.expiry_date else None,
        "days_to_expiry": days_to_expiry,
        "status": b.status,
        "created_at": b.created_at.isoformat(),
    }


def _product_stock_status(product: Product, batches: list[InventoryBatch]) -> dict:
    today = date.today()
    active_batches = [b for b in batches if b.status not in ("depleted", "expired")]
    current_stock = sum(b.quantity for b in active_batches)
    avg = product.avg_daily_demand or 1.0
    days_remaining = round(current_stock / avg, 1) if avg > 0 else 9999.0

    if current_stock == 0:
        stock_status = "out_of_stock"
    elif days_remaining < 2:
        stock_status = "critical"
    elif days_remaining < product.reorder_point_days:
        stock_status = "warning"
    elif days_remaining > 21:
        stock_status = "excess"
    else:
        stock_status = "ok"

    # Expiry alerts
    expiry_alerts = []
    for b in active_batches:
        if not b.expiry_date:
            continue
        days = (b.expiry_date - today).days
        if days <= 10:
            expiry_alerts.append({
                "batch_number": b.batch_number,
                "days_to_expiry": days,
                "quantity": b.quantity,
                "severity": "expired" if days <= 0 else ("critical_expiry" if days <= 3 else "expiring_soon"),
            })

    return {
        "product_id": product.id,
        "name": product.name,
        "sku": product.sku,
        "category": product.category,
        "brand": product.brand,
        "unit": product.unit,
        "selling_price": product.selling_price,
        "cost_price": product.cost_price,
        "avg_daily_demand": product.avg_daily_demand,
        "min_threshold": product.min_threshold,
        "reorder_point_days": product.reorder_point_days,
        "lead_time_days": product.lead_time_days,
        "order_cycle": product.order_cycle,
        "order_day": product.order_day,
        "current_stock": round(current_stock, 1),
        "days_remaining": days_remaining,
        "stock_status": stock_status,
        "expiry_alerts": expiry_alerts,
        "batches": [_batch_to_dict(b) for b in batches],
    }


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("")
def get_all_inventory(db: Session = Depends(get_db)):
    """All active products with current stock levels, batch details, and alerts."""
    products = db.query(Product).filter(Product.is_active == True).all()
    all_batches = db.query(InventoryBatch).all()

    batches_by_product: dict[int, list] = {}
    for b in all_batches:
        batches_by_product.setdefault(b.product_id, []).append(b)

    return [
        _product_stock_status(p, batches_by_product.get(p.id, []))
        for p in products
    ]


@router.get("/alerts")
def get_inventory_alerts(db: Session = Depends(get_db)):
    """Only products with status ≠ ok (out_of_stock, critical, warning, excess)."""
    products = db.query(Product).filter(Product.is_active == True).all()
    all_batches = db.query(InventoryBatch).all()

    batches_by_product: dict[int, list] = {}
    for b in all_batches:
        batches_by_product.setdefault(b.product_id, []).append(b)

    results = []
    for p in products:
        item = _product_stock_status(p, batches_by_product.get(p.id, []))
        if item["stock_status"] != "ok" or item["expiry_alerts"]:
            results.append(item)

    return results


@router.get("/{product_id}")
def get_product_inventory(product_id: int, db: Session = Depends(get_db)):
    """Single product with full batch details."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found.")

    batches = (
        db.query(InventoryBatch)
        .filter(InventoryBatch.product_id == product_id)
        .order_by(InventoryBatch.created_at)
        .all()
    )
    return _product_stock_status(product, batches)


@router.patch("/{batch_id}/quantity")
def adjust_batch_quantity(
    batch_id: int,
    body: QuantityAdjustment,
    db: Session = Depends(get_db),
):
    """
    Manual stock adjustment for a specific batch.
    Used when stock is received outside the order system.
    """
    batch = db.query(InventoryBatch).filter(InventoryBatch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail=f"Batch {batch_id} not found.")

    old_qty = batch.quantity
    batch.quantity = body.quantity

    # Update status based on new quantity
    if body.quantity == 0:
        batch.status = "depleted"
    elif batch.expiry_date:
        today = date.today()
        days = (batch.expiry_date - today).days
        if days <= 0:
            batch.status = "expired"
        elif days <= 7:
            batch.status = "expiring_soon"
        else:
            batch.status = "active"
    else:
        batch.status = "active"

    db.commit()
    db.refresh(batch)

    logger.info(
        "[inventory] Batch %s quantity adjusted: %.1f → %.1f. Note: %s",
        batch.batch_number, old_qty, body.quantity, body.note,
    )

    return {
        "message": f"Batch {batch.batch_number} updated.",
        "old_quantity": old_qty,
        "new_quantity": batch.quantity,
        "status": batch.status,
    }
