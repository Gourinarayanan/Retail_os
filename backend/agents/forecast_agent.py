"""
RetailWise AI — Demand Forecasting Agent (Agent 3)
Section 7 — Agent 3 of full_flow.md

Runs Holt-Winters Exponential Smoothing per SKU on the last 90 days of sales data.
Replaces Facebook Prophet (which required a C++ Stan backend incompatible with Windows).

Holt-Winters (Triple Exponential Smoothing) is ideal for retail forecasting:
  - Handles weekly seasonality (seasonal_periods=7) natively
  - Captures linear trends in demand
  - Pure Python via statsmodels — no compiler required
  - Fits extremely fast (< 1ms per product)

Applies scenario multipliers from the Scenario Engine for the 7-day adjusted forecast.

Holt-Winters runs synchronously and is fast enough to NOT need a ThreadPoolExecutor,
but we keep the executor pattern for consistency and to keep the async loop unblocked.

On per-product fit failure: falls back to avg_daily_demand baseline.
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

# Thread pool (keeps the async event loop unblocked)
_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="holtwinters")

# Minimum data points required for Holt-Winters with weekly seasonality (2 full weeks)
_MIN_ROWS_FOR_HW = 14


# ── Holt-Winters runner (runs inside thread pool) ─────────────────────────────

def _run_hw_for_product(
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

    Loads 90 days of sales records, fits Holt-Winters Exponential Smoothing,
    predicts next 14 days, applies scenario multipliers for the first 7 days.

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

    # ── Aggregate by Date ─────────────────────────────────────────────────
    from collections import defaultdict
    daily_sales = defaultdict(float)
    for r in records:
        # SalesRecord.date is a DateTime, so we extract the date part
        d = r.date.date() if hasattr(r.date, "date") else r.date
        daily_sales[d] += max(0.0, float(r.quantity_sold))
        
    # Need at least 2 distinct days of data
    if len(daily_sales) < 2:
        logger.warning(
            "[forecast] %s (%s): insufficient data (%d days) — using avg_daily_demand fallback.",
            product_name,
            product_sku,
            len(daily_sales),
        )
        return _fallback_forecast(avg_daily_demand, category, active_scenarios)

    # ── Build Continuous Series ───────────────────────────────────────────
    # We must fill in missing days with 0.0 to keep the 7-day seasonality intact!
    min_date = min(daily_sales.keys())
    # Max date is yesterday
    max_date = today - timedelta(days=1)
    
    current_date = min_date
    series = []
    while current_date <= max_date:
        series.append(daily_sales.get(current_date, 0.0))
        current_date += timedelta(days=1)

    # ── Fit Holt-Winters (Advanced Grid Search) ─────────────────────────────
    try:
        from statsmodels.tsa.holtwinters import ExponentialSmoothing

        # "mul" models strictly require data > 0
        can_use_mul = all(x > 0 for x in series)
        
        trend_opts = ["add", "mul", None] if can_use_mul else ["add", None]
        seasonal_opts = ["add", "mul", None] if can_use_mul else ["add", None]
        
        best_aic = float("inf")
        best_model_fit = None
        best_params = {}

        if len(series) >= _MIN_ROWS_FOR_HW:
            # Test all combinations of trend and weekly seasonality
            for t in trend_opts:
                for s in seasonal_opts:
                    try:
                        model = ExponentialSmoothing(
                            series,
                            trend=t,
                            seasonal=s,
                            seasonal_periods=7 if s is not None else None,
                            initialization_method="estimated",
                        )
                        fit = model.fit(optimized=True, remove_bias=True)
                        if fit.aic < best_aic:
                            best_aic = fit.aic
                            best_model_fit = fit
                            best_params = {"trend": t, "seasonal": s}
                    except Exception:
                        continue
        else:
            # Not enough data for seasonal model — test trend combinations only
            logger.info(
                "[forecast] %s (%s): only %d rows — using trend-only grid search.",
                product_name,
                product_sku,
                len(series),
            )
            for t in trend_opts:
                try:
                    model = ExponentialSmoothing(
                        series,
                        trend=t,
                        seasonal=None,
                        initialization_method="estimated",
                    )
                    fit = model.fit(optimized=True, remove_bias=True)
                    if fit.aic < best_aic:
                        best_aic = fit.aic
                        best_model_fit = fit
                        best_params = {"trend": t, "seasonal": None}
                except Exception:
                    continue

        if best_model_fit is None:
            raise ValueError("All Holt-Winters configurations failed to converge.")

        logger.debug(
            "[forecast] %s grid search selected %s (AIC: %.2f)", 
            product_sku, best_params, best_aic
        )

        fitted = best_model_fit

        # Predict next 14 days
        raw_forecast = fitted.forecast(14)
        # Clamp negatives to 0
        predictions = [max(0.0, float(v)) for v in raw_forecast]

    except Exception as exc:
        logger.error(
            "[forecast] Holt-Winters fit failed for %s (%s): %s — using fallback.",
            product_name,
            product_sku,
            exc,
        )
        return _fallback_forecast(avg_daily_demand, category, active_scenarios)

    # ── Compute prediction intervals (±15% approximation) ─────────────────
    # statsmodels HW simulate() can give exact intervals but is slow.
    # A ±15% band is a practical approximation for retail planning.
    interval_frac = 0.15

    # ── Apply scenario multipliers (next 7 days only) ─────────────────────
    multiplier, reasons = get_product_multiplier(category, active_scenarios)

    # ── Build per-day detail (14 days) ────────────────────────────────────
    daily_detail: list[dict] = []
    for i, day in enumerate(next_14):
        base = predictions[i]
        adj = round(base * multiplier, 1) if day in next_7 else round(base, 1)
        daily_detail.append(
            {
                "date": day.isoformat(),
                "base": round(base, 1),
                "adjusted": adj,
                "lower": round(max(0.0, base * (1 - interval_frac)), 1),
                "upper": round(base * (1 + interval_frac), 1),
            }
        )

    # ── Summary metrics ───────────────────────────────────────────────────
    next_7_bases = [d["base"] for d in daily_detail[:7]]
    next_7_adjs = [d["adjusted"] for d in daily_detail[:7]]

    baseline_daily = round(mean(next_7_bases), 2) if next_7_bases else avg_daily_demand
    adjusted_daily = round(mean(next_7_adjs), 2) if next_7_adjs else avg_daily_demand * multiplier
    seven_day_total = round(sum(next_7_adjs), 1)
    fourteen_day_total = round(sum(d["base"] for d in daily_detail), 1)

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
        "daily_detail": daily_detail,
        "recharts_data": recharts_data,
        "data_source": "Holt-Winters Exponential Smoothing (90-day history)",
    }


def _fallback_forecast(
    avg_daily_demand: float,
    category: str,
    active_scenarios: list[dict],
) -> dict:
    """
    Fallback when Holt-Winters fails or has insufficient data.
    Uses avg_daily_demand × scenario multiplier.
    """
    today = date.today()
    multiplier, reasons = get_product_multiplier(category, active_scenarios)
    adjusted = avg_daily_demand * multiplier
    interval_frac = 0.15

    daily_detail = []
    for i in range(1, 15):
        day = today + timedelta(days=i)
        base = avg_daily_demand
        adj = round(adjusted, 1) if i <= 7 else round(base, 1)
        daily_detail.append(
            {
                "date": day.isoformat(),
                "base": round(base, 1),
                "adjusted": adj,
                "lower": round(max(0.0, base * (1 - interval_frac)), 1),
                "upper": round(base * (1 + interval_frac), 1),
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

    Runs Holt-Winters for each active product in a ThreadPoolExecutor
    (keeps the async event loop unblocked).

    Stores per-product forecast in state["forecast"] keyed by product_id (str).
    """
    # ── Log: started ──────────────────────────────────────────────────────
    state["agent_log"].append(
        {
            "agent": "forecast",
            "status": "started",
            "summary": "Fitting Holt-Winters models for all products...",
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

    # ── Run Holt-Winters for each product in thread pool ──────────────────
    forecast: dict = {}
    tasks = []

    for p in product_list:
        task = loop.run_in_executor(
            _executor,
            _run_hw_for_product,
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

    summary_parts = [f"Holt-Winters models fitted for {n} products."]
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

    if "Holt-Winters" not in state.get("sources", []):
        state.setdefault("sources", []).append("Holt-Winters")

    return state
