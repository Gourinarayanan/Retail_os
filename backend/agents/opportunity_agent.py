"""
RetailWise AI — Business Opportunity Agent (Agent 6)
Section 7 — Agent 6 of full_flow.md

Identifies profit opportunities from upcoming festivals within 14 days.
Uses scenario multipliers (from rules.py) to estimate extra units and profit.
Calls Gemini to write a 2-sentence actionable advice narrative for each opportunity.

Threshold: only surfaces opportunities where extra_profit > ₹500.
"""

import logging
from time import time

from sqlalchemy.orm import Session

from agents.state import RetailWiseState
from database.db import SessionLocal
from database.models import Product
from scenario_engine.rules import SCENARIO_RULES
from services import gemini_service

logger = logging.getLogger(__name__)

# Only surface opportunities with estimated extra profit above this threshold
_MIN_PROFIT_THRESHOLD = 500.0

# Only look at festivals within this many days
_FESTIVAL_LOOKAHEAD_DAYS = 14

# Map festival names to their scenario rule IDs (for multiplier lookup)
_FESTIVAL_TO_SCENARIO: dict[str, str] = {
    "Onam": "onam_season",
    "Eid": "eid_approaching",
    "Ramadan": "ramadan_month",
    "Christmas": "christmas_week",
    "Vishu": "vishu_day",
    "Diwali": "onam_season",   # treat Diwali similarly to Onam for now
    "Easter": "christmas_week",
    "Milad": "ramadan_month",
}


def _get_scenario_multiplier(scenario_id: str, category: str) -> float:
    """
    Look up the category multiplier from the SCENARIO_RULES list
    for a given scenario ID. Returns 1.0 if not found.
    """
    for rule in SCENARIO_RULES:
        if rule["id"] != scenario_id:
            continue
        impacts = rule.get("category_impacts", {})
        cat_impact = impacts.get(category) or impacts.get("_all")
        if cat_impact:
            return float(cat_impact["multiplier"])
    return 1.0


async def run_opportunity_agent(state: RetailWiseState) -> RetailWiseState:
    """
    LangGraph node: Business Opportunity Agent.

    For each upcoming festival (≤ 14 days away) in state["context"]:
      For each product matching that festival's demand_events:
        Compute extra units and profit from the scenario multiplier.
        If profit > ₹500: ask Gemini for a 2-sentence advice card.
        Append to state["opportunities"].

    Sorts opportunities by extra_profit descending.
    """
    # ── Log: started ──────────────────────────────────────────────────────
    state["agent_log"].append(
        {
            "agent": "opportunity",
            "status": "started",
            "summary": "Scanning upcoming festivals for profit opportunities...",
            "ts": time(),
        }
    )

    context: dict = state.get("context", {})
    upcoming_festivals: list[dict] = context.get("upcoming_festivals", [])

    # Filter to festivals within the lookahead window
    near_festivals = [
        f for f in upcoming_festivals
        if f.get("days_away", 999) <= _FESTIVAL_LOOKAHEAD_DAYS
    ]

    if not near_festivals:
        logger.info("[opportunity] No upcoming festivals within %d days.", _FESTIVAL_LOOKAHEAD_DAYS)
        state["opportunities"] = []
        state["agent_log"].append(
            {
                "agent": "opportunity",
                "status": "complete",
                "summary": f"No festivals within {_FESTIVAL_LOOKAHEAD_DAYS} days — no opportunities to surface.",
                "ts": time(),
            }
        )
        return state

    # ── Load all active products from DB ──────────────────────────────────
    db: Session = SessionLocal()
    try:
        products = db.query(Product).filter(Product.is_active == True).all()
    finally:
        db.close()

    opportunities: list[dict] = []

    for festival in near_festivals:
        festival_name: str = festival.get("festival", "")
        days_away: int = festival.get("days_away", 0)
        duration_days: int = festival.get("duration_days", 1)

        scenario_id = _FESTIVAL_TO_SCENARIO.get(festival_name)
        if not scenario_id:
            logger.debug("[opportunity] No scenario mapping for festival '%s'.", festival_name)
            continue

        # Normalise festival name to match demand_events field
        festival_key = festival_name.lower()

        for product in products:
            # Check if this product responds to this festival event
            demand_events = [
                e.strip().lower()
                for e in (product.demand_events or "").split(",")
                if e.strip()
            ]

            # Match on festival name OR its scenario event tag
            event_match = (
                festival_key in demand_events
                or scenario_id.replace("_season", "").replace("_month", "")
                   .replace("_week", "").replace("_day", "").replace("_approaching", "")
                in demand_events
            )

            if not event_match:
                continue

            multiplier = _get_scenario_multiplier(scenario_id, product.category)
            if multiplier <= 1.0:
                continue  # no uplift for this category

            # ── Calculate opportunity ─────────────────────────────────────
            extra_units = (multiplier - 1.0) * product.avg_daily_demand * duration_days
            extra_revenue = extra_units * product.selling_price
            extra_profit = extra_units * (product.selling_price - product.cost_price)

            if extra_profit < _MIN_PROFIT_THRESHOLD:
                continue

            # ── Gemini: 2-sentence advice card ────────────────────────────
            try:
                narrative = gemini_service.generate_opportunity_narrative(
                    festival=festival_name,
                    days_away=days_away,
                    duration_days=duration_days,
                    product_name=product.name,
                    demand_uplift_pct=round((multiplier - 1.0) * 100),
                    extra_revenue_est=round(extra_revenue),
                    extra_profit_est=round(extra_profit),
                )
            except Exception as exc:
                logger.warning(
                    "[opportunity] Gemini narrative failed for %s / %s: %s",
                    product.name,
                    festival_name,
                    exc,
                )
                # Fallback narrative — uses computed numbers, no invention
                narrative = (
                    f"Stock up {product.name} before {festival_name} — "
                    f"demand rises {round((multiplier - 1.0) * 100)}% for {duration_days} days. "
                    f"Estimated extra profit: ₹{round(extra_profit):,}."
                )

            opportunities.append(
                {
                    "festival": festival_name,
                    "days_away": days_away,
                    "duration_days": duration_days,
                    "product_id": product.id,
                    "product_sku": product.sku,
                    "product_name": product.name,
                    "category": product.category,
                    "demand_uplift_pct": round((multiplier - 1.0) * 100),
                    "extra_units": round(extra_units, 1),
                    "extra_revenue_est": round(extra_revenue, 2),
                    "extra_profit_est": round(extra_profit, 2),
                    "narrative": narrative,
                    "action": (
                        f"Stock {round(extra_units)} extra {product.unit}s of "
                        f"{product.name} before {festival_name}"
                    ),
                    "scenario_id": scenario_id,
                    "multiplier": round(multiplier, 3),
                }
            )

    # Sort by extra_profit descending — highest opportunity first
    opportunities.sort(key=lambda x: x["extra_profit_est"], reverse=True)

    state["opportunities"] = opportunities

    # ── Build SSE summary ─────────────────────────────────────────────────
    total_potential = sum(o["extra_profit_est"] for o in opportunities)
    top = opportunities[0] if opportunities else None

    if top:
        summary = (
            f"{len(opportunities)} profit opportunity(ies) found. "
            f"Top: {top['product_name']} for {top['festival']} "
            f"(+{top['demand_uplift_pct']}%, ₹{round(top['extra_profit_est']):,} extra profit). "
            f"Total potential: ₹{round(total_potential):,}."
        )
    else:
        summary = "No opportunities above the profit threshold found for upcoming festivals."

    # ── Log: complete ──────────────────────────────────────────────────────
    state["agent_log"].append(
        {
            "agent": "opportunity",
            "status": "complete",
            "summary": summary,
            "ts": time(),
        }
    )

    return state
