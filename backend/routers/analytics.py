"""
RetailWise AI — Analytics Router
GET /api/analytics/sales-trend          — 30-day revenue trend per category
GET /api/analytics/top-products         — best and worst performing products
GET /api/analytics/supplier-performance — reliability + pricing over time
GET /api/analytics/inventory-health     — stock status over time
"""

import logging
from collections import defaultdict
from datetime import date, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database.db import get_db
from database.models import Product, SalesRecord, Supplier, SupplierDelivery, SupplierPrice

router = APIRouter(prefix="/api/analytics", tags=["analytics"])
logger = logging.getLogger(__name__)


@router.get("/sales-trend")
def get_sales_trend(
    days: int = Query(30, ge=7, le=365),
    db: Session = Depends(get_db),
):
    """
    Daily revenue grouped by category for the last N days.
    Returns Recharts-ready BarChart data.
    """
    cutoff = date.today() - timedelta(days=days)
    records = (
        db.query(SalesRecord)
        .filter(SalesRecord.date >= cutoff)
        .order_by(SalesRecord.date)
        .all()
    )
    products = {p.id: p for p in db.query(Product).all()}

    # Aggregate: date → category → total revenue
    daily: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    categories: set[str] = set()
    for r in records:
        p = products.get(r.product_id)
        if not p:
            continue
        day_str = r.date.isoformat()
        daily[day_str][p.category] += r.revenue
        categories.add(p.category)

    # Build sorted list of day dicts for Recharts
    result = []
    current = cutoff
    while current <= date.today():
        day_str = current.isoformat()
        entry = {"date": day_str}
        for cat in sorted(categories):
            entry[cat] = round(daily.get(day_str, {}).get(cat, 0.0), 2)
        result.append(entry)
        current += timedelta(days=1)

    return {"data": result, "categories": sorted(categories), "days": days}


@router.get("/top-products")
def get_top_products(
    days: int = Query(30, ge=7, le=365),
    limit: int = Query(5, ge=1, le=15),
    db: Session = Depends(get_db),
):
    """Best and worst performing products by total revenue over the last N days."""
    cutoff = date.today() - timedelta(days=days)
    records = (
        db.query(SalesRecord)
        .filter(SalesRecord.date >= cutoff)
        .all()
    )
    products = {p.id: p for p in db.query(Product).all()}

    totals: dict[int, dict] = defaultdict(lambda: {"revenue": 0.0, "qty": 0.0})
    for r in records:
        totals[r.product_id]["revenue"] += r.revenue
        totals[r.product_id]["qty"] += r.quantity_sold

    ranked = []
    for pid, agg in totals.items():
        p = products.get(pid)
        if not p:
            continue
        ranked.append({
            "product_id": pid,
            "name": p.name,
            "sku": p.sku,
            "category": p.category,
            "total_revenue": round(agg["revenue"], 2),
            "total_qty_sold": round(agg["qty"], 1),
        })

    ranked.sort(key=lambda x: x["total_revenue"], reverse=True)
    return {
        "best": ranked[:limit],
        "worst": ranked[-limit:] if len(ranked) >= limit else ranked[::-1][:limit],
        "days": days,
    }


@router.get("/supplier-performance")
def get_supplier_performance(db: Session = Depends(get_db)):
    """On-time delivery rate per supplier over the last 180 days."""
    cutoff = date.today() - timedelta(days=180)
    suppliers = db.query(Supplier).filter(Supplier.is_active == True).all()
    deliveries = (
        db.query(SupplierDelivery)
        .filter(SupplierDelivery.order_date >= cutoff)
        .all()
    )

    # Group by supplier
    by_supplier: dict[int, list] = defaultdict(list)
    for d in deliveries:
        by_supplier[d.supplier_id].append(d)

    results = []
    for s in suppliers:
        s_deliveries = by_supplier.get(s.id, [])
        total = len(s_deliveries)
        on_time = sum(1 for d in s_deliveries if d.on_time is True)
        ratings = [d.rating for d in s_deliveries if d.rating is not None]
        avg_rating = round(sum(ratings) / len(ratings), 2) if ratings else 3.5

        results.append({
            "supplier_id": s.id,
            "name": s.name,
            "region": s.region,
            "total_deliveries": total,
            "on_time_count": on_time,
            "on_time_rate_pct": round((on_time / total * 100) if total > 0 else 75.0, 1),
            "avg_rating": avg_rating,
            "categories": s.supply_categories.split(","),
        })

    results.sort(key=lambda x: x["on_time_rate_pct"], reverse=True)
    return results


@router.get("/inventory-health")
def get_inventory_health(db: Session = Depends(get_db)):
    """Current stock status snapshot for all products (for dashboard health chart)."""
    products = db.query(Product).filter(Product.is_active == True).all()
    from database.models import InventoryBatch

    all_batches = db.query(InventoryBatch).all()
    batches_by_product: dict[int, list] = defaultdict(list)
    for b in all_batches:
        batches_by_product[b.product_id].append(b)

    result = []
    for p in products:
        batches = batches_by_product.get(p.id, [])
        active = [b for b in batches if b.status not in ("depleted", "expired")]
        current_stock = sum(b.quantity for b in active)
        avg = p.avg_daily_demand or 1.0
        days_remaining = round(current_stock / avg, 1) if avg > 0 else 9999.0

        if current_stock == 0:
            status = "out_of_stock"
        elif days_remaining < 2:
            status = "critical"
        elif days_remaining < p.reorder_point_days:
            status = "warning"
        elif days_remaining > 21:
            status = "excess"
        else:
            status = "ok"

        result.append({
            "product_id": p.id,
            "name": p.name,
            "sku": p.sku,
            "category": p.category,
            "current_stock": round(current_stock, 1),
            "days_remaining": days_remaining,
            "status": status,
            "min_threshold": p.min_threshold,
        })

    result.sort(key=lambda x: x["days_remaining"])
    return result
