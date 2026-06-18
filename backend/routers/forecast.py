"""
RetailWise AI — Forecast Router
GET /api/forecast/{sku}    — Prophet 14-day forecast (Recharts JSON)
GET /api/forecast/all      — all SKUs summary
GET /api/context/today     — active scenarios + weather + hartal
"""

import json
import logging
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.db import get_db
from database.models import DailyBriefing, Product

router = APIRouter(tags=["forecast"])
logger = logging.getLogger(__name__)


@router.get("/api/forecast/all")
def get_all_forecasts(db: Session = Depends(get_db)):
    """Summary forecast for all active SKUs from the latest briefing."""
    briefing = (
        db.query(DailyBriefing)
        .filter(DailyBriefing.date == date.today())
        .first()
    )
    if not briefing:
        raise HTTPException(
            status_code=404,
            detail="No briefing for today. Run the morning briefing first.",
        )

    try:
        orders = json.loads(briefing.orders_json or "[]")
    except Exception:
        orders = []

    products = db.query(Product).filter(Product.is_active == True).all()
    product_map = {p.id: p for p in products}

    results = []
    for p in products:
        results.append({
            "product_id": p.id,
            "sku": p.sku,
            "name": p.name,
            "category": p.category,
            "avg_daily_demand": p.avg_daily_demand,
        })
    return results


@router.get("/api/forecast/{sku}")
def get_sku_forecast(sku: str, db: Session = Depends(get_db)):
    """
    14-day Prophet forecast for a single SKU.
    Returns Recharts-ready JSON from the latest daily briefing's orders JSON.
    Falls back to avg_daily_demand if no briefing available.
    """
    product = db.query(Product).filter(Product.sku == sku).first()
    if not product:
        raise HTTPException(status_code=404, detail=f"Product SKU '{sku}' not found.")

    briefing = (
        db.query(DailyBriefing)
        .filter(DailyBriefing.date == date.today())
        .first()
    )

    if briefing:
        try:
            orders = json.loads(briefing.orders_json or "[]")
            for order in orders:
                if order.get("product_sku") == sku and order.get("recharts_data"):
                    return {
                        "product_id": product.id,
                        "sku": product.sku,
                        "name": product.name,
                        "recharts_data": order["recharts_data"],
                        "baseline_daily": order.get("baseline_daily", product.avg_daily_demand),
                        "scenario_adjusted_daily": order.get("scenario_adjusted_daily", product.avg_daily_demand),
                        "multiplier": order.get("multiplier", 1.0),
                        "reasons": order.get("reasons", []),
                        "data_source": "Prophet (latest briefing)",
                    }
        except Exception:
            pass

    # Fallback: flat forecast from avg_daily_demand
    from datetime import timedelta
    today = date.today()
    recharts_data = [
        {
            "date": (today + timedelta(days=i)).isoformat(),
            "baseline": product.avg_daily_demand,
            "adjusted": product.avg_daily_demand,
            "lower": round(product.avg_daily_demand * 0.85, 1),
            "upper": round(product.avg_daily_demand * 1.15, 1),
        }
        for i in range(1, 15)
    ]
    return {
        "product_id": product.id,
        "sku": product.sku,
        "name": product.name,
        "recharts_data": recharts_data,
        "baseline_daily": product.avg_daily_demand,
        "scenario_adjusted_daily": product.avg_daily_demand,
        "multiplier": 1.0,
        "reasons": [],
        "data_source": "Fallback (avg_daily_demand — run morning briefing for Prophet forecast)",
    }


@router.get("/api/context/today")
def get_today_context(db: Session = Depends(get_db)):
    """Active scenarios + weather + hartal flags from today's briefing."""
    briefing = (
        db.query(DailyBriefing)
        .filter(DailyBriefing.date == date.today())
        .first()
    )
    if not briefing:
        return {
            "date": date.today().isoformat(),
            "context": {},
            "active_scenarios": [],
            "message": "No briefing for today yet. Run the morning briefing.",
        }

    def _safe(raw, default):
        try:
            return json.loads(raw) if raw else default
        except Exception:
            return default

    return {
        "date": date.today().isoformat(),
        "context": _safe(briefing.context_json, {}),
        "active_scenarios": _safe(briefing.scenarios_json, []),
    }
