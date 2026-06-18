"""
RetailWise AI — Demand Forecasting Agent (Agent 3)
Section 7 — Agent 3 of full_flow.md

Runs Facebook Prophet per SKU on the last 90 days of sales data.
Applies scenario multipliers from the Scenario Engine for the 7-day adjusted forecast.

Prophet is CPU-bound: runs in a ThreadPoolExecutor so it does not block
the async FastAPI event loop.

On per-product Prophet failure: falls back to avg_daily_demand baseline.
"""

import asyncio
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
from statistics import mean
from time import time

import pandas as pd
from sqlalchemy.orm import Session

from agents.state import RetailWiseState
from database.db import SessionLocal
from database.models import Product, SalesRecord
from scenario_engine.rules import get_product_multiplier

logger = logging.getLogger(__name__)

# Thread pool for Prophet (CPU-bound work off the async loop)
_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="prophet")


# ── Prophet runner (runs inside thread pool) ──────────────────────────────────

def _run_prophet_for_product(
    product_id: int,
    product_sku: str,
    product_name: str,
    avg_daily_demand: float,
    category: str,
    active_scenarios: list[dict],
    db_session_factory,
) -> dict:
    """
    Synchronous function — safe to run in a thread pool.

    Loads sales records, fits Prophet, predicts next 14 days,
    applies scenario multipliers for the first 7 days.

    Returns the forecast dict for state["forecast"][product_id].
    """
    today = date.today()
    next_14 = [today + timedelta(days=i) for i in range(1, 15)]
    next_7 = next_14[:7]

    # ── Load sales records from DB ────────────────────────────────────────
    db: Session = db_session_factory()
    try:
        cutoff = today - timedelta(days=90)
        records = (
            db.query(SalesRecord)
            .filter(
                SalesRecord.product_id == product_id,
                SalesRecord.date >= cutoff,
                SalesRecord.date < today,
            )
            .order_by(SalesRecord.date)
            .all()
        )
    finally:
        db.close()

    # Need at least 2 data points for Prophet; fallback if insufficient
    if len(records) < 2:
        logger.warning(
            "[forecast] %s (%s): insufficient data (%d rows) — using avg_daily_demand fallback.",
            product_name,
            product_sku,
            len(records),
        )
        return _fallback_forecast(avg_daily_demand, category, active_scenarios)

    # ── Build DataFrame ───────────────────────────────────────────────────
    df = pd.DataFrame(
        {
            "ds": pd.to_datetime([r.date for r in records]),
            "y": [max(0.0, float(r.quantity_sold)) for r in records],
        }
    )

    # ── Fit Prophet ───────────────────────────────────────────────────────
    try:
        # Suppress Prophet/cmdstanpy stdout noise
        import logging as _logging
        _logging.getLogger("prophet").setLevel(_logging.WARNING)
        _logging.getLogger("cmdstanpy").setLevel(_logging.WARNING)

        from prophet import Prophet

        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False,
            interval_width=0.80,
        )
        model.add_country_holidays(country_name="IN")
        model.fit(df)

    except Exception as exc:
        logger.error(
            "[forecast] Prophet fit failed for %s (%s): %s — using fallback.",
            product_name,
            product_sku,
            exc,
        )
        return _fallback_forecast(avg_daily_demand, category, active_scenarios)

    # ── Predict next 14 days ──────────────────────────────────────────────
    try:
        future = model.make_future_dataframe(periods=14, freq="D")
        raw_forecast = model.predict(future)

        # Index forecast rows by date string for easy lookup
        forecast_by_date: dict[str, dict] = {}
        for _, row in raw_forecast.iterrows():
            ds = row["ds"].date()
            forecast_by_date[ds.isoformat()] = {
                "yhat": max(0.0, float(row["yhat"])),
                "yhat_lower": max(0.0, float(row["yhat_lower"])),
                "yhat_upper": max(0.0, float(row["yhat_upper"])),
            }

    except Exception as exc:
        logger.error(
            "[forecast] Prophet predict failed for %s (%s): %s — using fallback.",
            product_name,
            product_sku,
            exc,
        )
        return _fallback_forecast(avg_daily_demand, category, active_scenarios)

    # ── Apply scenario multipliers (next 7 days) ──────────────────────────
    multiplier, reasons = get_product_multiplier(category, active_scenarios)

    # ── Build per-day detail (14 days) ────────────────────────────────────
    daily_detail: list[dict] = []
    for day in next_14:
        day_str = day.isoformat()
        raw = forecast_by_date.get(day_str, {"yhat": avg_daily_demand, "yhat_lower": 0.0, "yhat_upper": avg_daily_demand * 1.5})
        base = raw["yhat"]
        # Apply multiplier only for next 7 days (near-term actionable window)
        adj = round(base * multiplier, 1) if day in next_7 else round(base, 1)
        daily_detail.append(
            {
                "date": day_str,
                "base": round(base, 1),
                "adjusted": adj,
                "lower": round(raw["yhat_lower"], 1),
                "upper": round(raw["yhat_upper"], 1),
            }
        )

    # ── Summary metrics ───────────────────────────────────────────────────
    next_7_bases = [d["base"] for d in daily_detail[:7]]
    next_7_adjs = [d["adjusted"] for d in daily_detail[:7]]
    next_14_bases = [d["base"] for d in daily_detail]

    baseline_daily = round(mean(next_7_bases), 2) if next_7_bases else avg_daily_demand
    adjusted_daily = round(mean(next_7_adjs), 2) if next_7_adjs else avg_daily_demand * multiplier
    seven_day_total = round(sum(next_7_adjs), 1)
    fourteen_day_total = round(sum(next_14_bases), 1)

    # ── Build Recharts-ready JSON for the frontend Analytics page ─────────
    recharts_data = [
        {
            "date": d["date"],
            "baseline": d["base"],
            "adjusted": d["adjusted"],
            "lower": d["lower"],
            "upper": d["upper"],
        }
        for d in daily_detail
    ]

    return {
        "product_id": product_id,
        "product_sku": product_sku,
        "product_name": product_name,
        "baseline_daily": baseline_daily,
        "scenario_adjusted_daily": adjusted_daily,
        "7day_total": seven_day_total,
        "14day_total": fourteen_day_total,
        "multiplier": round(multiplier, 3),
        "reasons": reasons,
        "daily_detail": daily_detail,       # per-day breakdown
        "recharts_data": recharts_data,     # ready for ForecastChart.tsx
        "data_source": "Prophet (90-day history)",
    }


def _fallback_forecast(
    avg_daily_demand: float,
    category: str,
    active_scenarios: list[dict],
) -> dict:
    """
    Fallback when Prophet fails or has insufficient data.
    Uses avg_daily_demand × scenario multiplier.
    """
    today = date.today()
    multiplier, reasons = get_product_multiplier(category, active_scenarios)
    adjusted = avg_daily_demand * multiplier

    daily_detail = []
    for i in range(1, 15):
        day = today + timedelta(days=i)
        daily_detail.append(
            {
                "date": day.isoformat(),
                "base": round(avg_daily_demand, 1),
                "adjusted": round(adjusted, 1) if i <= 7 else round(avg_daily_demand, 1),
                "lower": round(avg_daily_demand * 0.85, 1),
                "upper": round(avg_daily_demand * 1.15, 1),
            }
        )

    return {
        "baseline_daily": round(avg_daily_demand, 2),
        "scenario_adjusted_daily": round(adjusted, 2),
        "7day_total": round(adjusted * 7, 1),
        "14day_total": round(avg_daily_demand * 14, 1),
        "multiplier": round(multiplier, 3),
        "reasons": reasons,
        "daily_detail": daily_detail,
        "recharts_data": [
            {
                "date": d["date"],
                "baseline": d["base"],
                "adjusted": d["adjusted"],
                "lower": d["lower"],
                "upper": d["upper"],
            }
            for d in daily_detail
        ],
        "data_source": "Fallback (avg_daily_demand)",
    }


# ── LangGraph node ────────────────────────────────────────────────────────────

async def run_forecast_agent(state: RetailWiseState) -> RetailWiseState:
    """
    LangGraph node: Demand Forecasting Agent.

    Runs Prophet for each active product in a ThreadPoolExecutor
    (Prophet is CPU-bound and not async-safe).

    Stores per-product forecast in state["forecast"] keyed by product_id (str).
    """
    # ── Log: started ──────────────────────────────────────────────────────
    state["agent_log"].append(
        {
            "agent": "forecast",
            "status": "started",
            "summary": "Fitting Prophet models for all products...",
            "ts": time(),
        }
    )

    active_scenarios = state.get("active_scenarios", [])
    loop = asyncio.get_event_loop()

    # ── Load products list ────────────────────────────────────────────────
    db: Session = SessionLocal()
    try:
        products = db.query(Product).filter(Product.is_active == True).all()
        product_list = [
            {
                "id": p.id,
                "sku": p.sku,
                "name": p.name,
                "category": p.category,
                "avg_daily_demand": p.avg_daily_demand,
            }
            for p in products
        ]
    finally:
        db.close()

    if not product_list:
        logger.warning("[forecast] No active products found in DB.")
        state["agent_log"].append(
            {
                "agent": "forecast",
                "status": "complete",
                "summary": "No active products — nothing to forecast.",
                "ts": time(),
            }
        )
        return state

    # ── Run Prophet for each product in thread pool ───────────────────────
    forecast: dict = {}
    tasks = []

    for p in product_list:
        task = loop.run_in_executor(
            _executor,
            _run_prophet_for_product,
            p["id"],
            p["sku"],
            p["name"],
            p["avg_daily_demand"],
            p["category"],
            active_scenarios,
            SessionLocal,          # pass factory, not session (thread-safe)
        )
        tasks.append((str(p["id"]), p["sku"], task))

    # Gather results
    for product_id_str, sku, task in tasks:
        try:
            result = await task
            forecast[product_id_str] = result
        except Exception as exc:
            logger.error(
                "[forecast] Unhandled error for product_id=%s sku=%s: %s",
                product_id_str,
                sku,
                exc,
            )

    state["forecast"] = forecast

    # ── Build SSE summary ─────────────────────────────────────────────────
    n = len(forecast)
    multiplied = [v for v in forecast.values() if v.get("multiplier", 1.0) != 1.0]
    peak_product = max(
        forecast.values(),
        key=lambda v: v.get("scenario_adjusted_daily", 0),
        default=None,
    )

    summary_parts = [f"Prophet models fitted for {n} products."]
    if multiplied:
        summary_parts.append(
            f"{len(multiplied)} product(s) have scenario multipliers applied."
        )
    if peak_product:
        summary_parts.append(
            f"Highest adjusted demand: {peak_product.get('product_name', '?')} "
            f"({peak_product.get('scenario_adjusted_daily', 0):.1f}/day, "
            f"×{peak_product.get('multiplier', 1.0)})."
        )

    # ── Log: complete ──────────────────────────────────────────────────────
    state["agent_log"].append(
        {
            "agent": "forecast",
            "status": "complete",
            "summary": " ".join(summary_parts),
            "ts": time(),
        }
    )

    if "Prophet" not in state.get("sources", []):
        state.setdefault("sources", []).append("Prophet")

    return state
