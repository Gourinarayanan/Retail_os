"""
RetailWise AI — Suppliers Router
GET /api/suppliers                         — all suppliers with scores
GET /api/suppliers/{id}                    — single supplier + delivery history
GET /api/suppliers/compare/{product_id}    — side-by-side comparison for a product
"""

import logging
from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.db import get_db
from database.models import Supplier, SupplierDelivery, SupplierPrice

router = APIRouter(prefix="/api/suppliers", tags=["suppliers"])
logger = logging.getLogger(__name__)


def _get_reliability(supplier_id: int, db: Session) -> tuple[float, float, int]:
    cutoff = date.today() - timedelta(days=90)
    deliveries = (
        db.query(SupplierDelivery)
        .filter(
            SupplierDelivery.supplier_id == supplier_id,
            SupplierDelivery.order_date >= cutoff,
        )
        .all()
    )
    total = len(deliveries)
    if total == 0:
        return 75.0, 3.5, 0
    on_time = sum(1 for d in deliveries if d.on_time is True)
    ratings = [d.rating for d in deliveries if d.rating is not None]
    avg_rating = sum(ratings) / len(ratings) if ratings else 3.5
    return round((on_time / total) * 100, 1), round(avg_rating, 2), total


def _supplier_summary(s: Supplier, db: Session) -> dict:
    on_time_pct, avg_rating, total_deliveries = _get_reliability(s.id, db)
    return {
        "id": s.id,
        "name": s.name,
        "contact_name": s.contact_name,
        "whatsapp_number": s.whatsapp_number,
        "email": s.email,
        "region": s.region,
        "supply_categories": s.supply_categories.split(","),
        "notes": s.notes,
        "is_active": s.is_active,
        "on_time_rate_pct": on_time_pct,
        "avg_rating": avg_rating,
        "total_deliveries_90d": total_deliveries,
    }


@router.get("")
def get_all_suppliers(db: Session = Depends(get_db)):
    """All active suppliers with 90-day reliability stats."""
    suppliers = db.query(Supplier).filter(Supplier.is_active == True).all()
    return [_supplier_summary(s, db) for s in suppliers]


@router.get("/compare/{product_id}")
def compare_suppliers_for_product(product_id: int, db: Session = Depends(get_db)):
    """
    Side-by-side supplier comparison for a specific product.
    Returns all suppliers that have a price for this product, ranked by composite score.
    """
    prices = (
        db.query(SupplierPrice)
        .filter(SupplierPrice.product_id == product_id)
        .order_by(SupplierPrice.recorded_date.desc())
        .all()
    )
    if not prices:
        raise HTTPException(
            status_code=404,
            detail=f"No supplier prices found for product {product_id}.",
        )

    all_price_values = [p.price_per_unit for p in prices]
    min_price = min(all_price_values)
    max_price = max(all_price_values)
    price_range = max(max_price - min_price, 0.01)

    results = []
    for price_row in prices:
        supplier = db.query(Supplier).filter(Supplier.id == price_row.supplier_id).first()
        if not supplier:
            continue
        on_time_pct, avg_rating, total_del = _get_reliability(supplier.id, db)
        price_score = ((max_price - price_row.price_per_unit) / price_range) * 100
        composite = price_score * 0.50 + on_time_pct * 0.30 + 70 * 0.20
        results.append({
            "supplier_id": supplier.id,
            "name": supplier.name,
            "region": supplier.region,
            "contact_name": supplier.contact_name,
            "whatsapp_number": supplier.whatsapp_number,
            "price_per_unit": round(price_row.price_per_unit, 2),
            "min_order_qty": price_row.min_order_qty,
            "bulk_discount_qty": price_row.bulk_discount_qty,
            "bulk_discount_price": price_row.bulk_discount_price,
            "on_time_rate_pct": on_time_pct,
            "avg_rating": avg_rating,
            "total_deliveries_90d": total_del,
            "price_score": round(price_score, 1),
            "composite_score": round(composite, 2),
            "saving_vs_costliest": round((max_price - price_row.price_per_unit), 2),
            "recorded_date": price_row.recorded_date.isoformat(),
        })

    results.sort(key=lambda x: x["composite_score"], reverse=True)
    return results


@router.get("/{supplier_id}")
def get_supplier_detail(supplier_id: int, db: Session = Depends(get_db)):
    """Single supplier with last 20 deliveries and recent prices."""
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail=f"Supplier {supplier_id} not found.")

    deliveries = (
        db.query(SupplierDelivery)
        .filter(SupplierDelivery.supplier_id == supplier_id)
        .order_by(SupplierDelivery.order_date.desc())
        .limit(20)
        .all()
    )
    prices = (
        db.query(SupplierPrice)
        .filter(SupplierPrice.supplier_id == supplier_id)
        .order_by(SupplierPrice.recorded_date.desc())
        .all()
    )

    summary = _supplier_summary(supplier, db)
    summary["delivery_history"] = [
        {
            "id": d.id,
            "product_id": d.product_id,
            "order_date": d.order_date.isoformat(),
            "expected_delivery_date": d.expected_delivery_date.isoformat(),
            "actual_delivery_date": d.actual_delivery_date.isoformat() if d.actual_delivery_date else None,
            "on_time": d.on_time,
            "quantity_ordered": d.quantity_ordered,
            "quantity_received": d.quantity_received,
            "complaint": d.complaint,
            "rating": d.rating,
        }
        for d in deliveries
    ]
    summary["prices"] = [
        {
            "product_id": p.product_id,
            "price_per_unit": p.price_per_unit,
            "min_order_qty": p.min_order_qty,
            "bulk_discount_qty": p.bulk_discount_qty,
            "bulk_discount_price": p.bulk_discount_price,
            "recorded_date": p.recorded_date.isoformat(),
        }
        for p in prices
    ]
    return summary
