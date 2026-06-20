"""
RetailWise AI — Supplier Intelligence Agent (Agent 5)
Section 7 — Agent 5 of full_flow.md

Scores all eligible suppliers for each drafted order.
Attaches best supplier + ranked comparison table to each order.
Stores full supplier_rankings in state["supplier_rankings"].

Composite score formula:
    score = (price_score × 0.50) + (reliability_score × 0.30) + (regional_score × 0.20)

Weights match the spec Section 7 Agent 5.
"""

import logging
from time import time

from sqlalchemy.orm import Session

from agents.state import RetailWiseState
from database.db import SessionLocal
from database.models import Product, Supplier, SupplierDelivery, SupplierPrice
from rag.rag_engine import query_rag

logger = logging.getLogger(__name__)

# Score weights — must sum to 1.0
_W_PRICE = 0.50
_W_RELIABILITY = 0.30
_W_REGIONAL = 0.20

# Store region (Thrissur) — used for regional scoring
_STORE_REGION = "Thrissur"

# Regional proximity map: how "close" a region is to Thrissur
_REGION_SCORE: dict[str, float] = {
    "Thrissur": 100.0,
    "Ernakulam": 80.0,
    "Kochi": 70.0,
    "Palakkad": 60.0,
    "Coimbatore": 50.0,
    "Malappuram": 65.0,
    "Kozhikode": 55.0,
    "Kottayam": 75.0,
    "Alappuzha": 70.0,
}
_DEFAULT_REGIONAL_SCORE = 40.0

# Penalty points deducted from regional_score when rain + remote supplier
_RAIN_PENALTY = 30.0
_RAIN_RISK_REGIONS = {"Palakkad", "Coimbatore"}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_latest_price(
    supplier_id: int,
    product_id: int,
    db: Session,
) -> float | None:
    """Return the most recent price per unit for this supplier-product pair."""
    row = (
        db.query(SupplierPrice)
        .filter(
            SupplierPrice.supplier_id == supplier_id,
            SupplierPrice.product_id == product_id,
        )
        .order_by(SupplierPrice.recorded_date.desc())
        .first()
    )
    return float(row.price_per_unit) if row else None


def _get_reliability(supplier_id: int, db: Session) -> tuple[float, float, int]:
    """
    Compute on-time delivery rate and average rating for a supplier
    based on the last 90 days of SupplierDelivery records.

    Returns (on_time_rate_pct, avg_rating, total_deliveries)
    """
    from datetime import date, timedelta
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
        return 75.0, 3.5, 0  # neutral defaults for new/unknown suppliers

    on_time_count = sum(1 for d in deliveries if d.on_time is True)
    on_time_rate = (on_time_count / total) * 100.0

    ratings = [d.rating for d in deliveries if d.rating is not None]
    avg_rating = sum(ratings) / len(ratings) if ratings else 3.5

    return round(on_time_rate, 1), round(avg_rating, 2), total


def _regional_score(region: str, rain_heavy: bool) -> float:
    """
    Score based on supplier region vs store location.
    Applies rain penalty for remote regions when heavy rain is forecast.
    """
    base = _REGION_SCORE.get(region, _DEFAULT_REGIONAL_SCORE)
    if rain_heavy and region in _RAIN_RISK_REGIONS:
        base = max(0.0, base - _RAIN_PENALTY)
    return base


def _score_supplier(
    supplier: Supplier,
    product_id: int,
    order_qty: float,
    all_prices: list[float],
    rain_heavy: bool,
    db: Session,
) -> dict | None:
    """
    Score a single supplier for a specific product order.

    Returns scored dict or None if supplier doesn't carry this product.
    """
    price = _get_latest_price(supplier.id, product_id, db)
    if price is None:
        return None  # supplier doesn't carry this product

    # ── Price score ───────────────────────────────────────────────────────
    min_price = min(all_prices)
    max_price = max(all_prices)
    price_range = max(max_price - min_price, 0.01)
    # Higher score for lower price (inverted normalisation)
    price_score = ((max_price - price) / price_range) * 100.0

    # ── Reliability score ──────────────────────────────────────────────────
    on_time_pct, avg_rating, total_deliveries = _get_reliability(supplier.id, db)
    reliability_score = on_time_pct  # already 0–100

    # ── Regional score ─────────────────────────────────────────────────────
    reg_score = _regional_score(supplier.region, rain_heavy)

    # ── Composite score ────────────────────────────────────────────────────
    composite = (
        price_score * _W_PRICE
        + reliability_score * _W_RELIABILITY
        + reg_score * _W_REGIONAL
    )

    # ── Savings vs costliest supplier ─────────────────────────────────────
    saving_vs_costliest = round((max_price - price) * order_qty, 2)

    # Rain risk flag
    region_risk = rain_heavy and supplier.region in _RAIN_RISK_REGIONS

    return {
        "supplier_id": supplier.id,
        "name": supplier.name,
        "contact_name": supplier.contact_name,
        "whatsapp_number": supplier.whatsapp_number,
        "region": supplier.region,
        "price_per_unit": round(price, 2),
        "on_time_rate_pct": on_time_pct,
        "avg_rating": avg_rating,
        "total_deliveries_90d": total_deliveries,
        "region_risk": region_risk,
        "price_score": round(price_score, 1),
        "reliability_score": round(reliability_score, 1),
        "regional_score": round(reg_score, 1),
        "composite_score": round(composite, 2),
        "saving_vs_costliest": saving_vs_costliest,
        "notes": supplier.notes or "",
    }


# ── LangGraph node ────────────────────────────────────────────────────────────

async def run_supplier_agent(state: RetailWiseState) -> RetailWiseState:
    """
    LangGraph node: Supplier Intelligence Agent.

    For each order in state["orders_draft"]:
      1. Find all suppliers carrying that product's category
      2. Score each using price + reliability + regional composite
      3. Rank them and attach to the order dict
      4. Select the best supplier and fill in price/cost on the order

    Stores full supplier_rankings in state["supplier_rankings"].
    """
    # ── Log: started ──────────────────────────────────────────────────────
    state["agent_log"].append(
        {
            "agent": "supplier",
            "status": "started",
            "summary": "Scoring suppliers for each drafted order...",
            "ts": time(),
        }
    )

    orders_draft: list[dict] = state.get("orders_draft", [])
    context: dict = state.get("context", {})

    # Check if heavy rain is active (reduces remote supplier scores)
    rain_heavy: bool = (
        context.get("weather", {})
        .get("tomorrow", {})
        .get("rain_heavy", False)
    )

    # Also check active scenarios for explicit rain scenario
    active_scenarios = state.get("active_scenarios", [])
    rain_scenario_active = any(s["id"] == "rainy_day" for s in active_scenarios)
    rain_heavy = rain_heavy or rain_scenario_active

    db: Session = SessionLocal()
    try:
        all_suppliers = (
            db.query(Supplier).filter(Supplier.is_active == True).all()
        )

        supplier_rankings: dict = {}
        total_savings = 0.0
        
        # Cache RAG supplier strategies to avoid repeated queries for the same supplier
        supplier_strategies_cache: dict[int, str] = {}

        for order in orders_draft:
            product_id: int = order["product_id"]
            category: str = order["category"]
            order_qty: float = order.get("ai_recommended_qty", 1.0)

            # Filter suppliers that carry this category
            eligible_suppliers = [
                s for s in all_suppliers
                if category in [c.strip() for c in s.supply_categories.split(",")]
            ]

            if not eligible_suppliers:
                logger.warning(
                    "[supplier] No eligible suppliers for category '%s' (product_id=%d).",
                    category,
                    product_id,
                )
                continue

            # Get all valid prices for this product (to normalise price score)
            all_prices: list[float] = []
            for s in eligible_suppliers:
                p = _get_latest_price(s.id, product_id, db)
                if p is not None:
                    all_prices.append(p)

            if not all_prices:
                logger.warning(
                    "[supplier] No price data found for product_id=%d. Skipping.",
                    product_id,
                )
                continue

            # Score each eligible supplier
            scored: list[dict] = []
            for supplier in eligible_suppliers:
                result = _score_supplier(
                    supplier=supplier,
                    product_id=product_id,
                    order_qty=order_qty,
                    all_prices=all_prices,
                    rain_heavy=rain_heavy,
                    db=db,
                )
                if result is not None:
                    scored.append(result)

            if not scored:
                continue

            # Sort by composite score descending
            scored.sort(key=lambda x: x["composite_score"], reverse=True)

            # Best supplier is the top-ranked
            best = scored[0]

            # Attach supplier + pricing info to the order
            total_cost = round(best["price_per_unit"] * order_qty, 2)
            order["supplier_id"] = best["supplier_id"]
            order["supplier_name"] = best["name"]
            order["supplier_contact"] = best["contact_name"]
            order["supplier_whatsapp"] = best["whatsapp_number"]
            order["price_per_unit"] = best["price_per_unit"]
            order["total_cost"] = total_cost
            order["supplier_rankings"] = scored   # full table for UI comparison
            order["saving_vs_second"] = (
                round(
                    (scored[1]["price_per_unit"] - best["price_per_unit"]) * order_qty, 2
                )
                if len(scored) > 1 else 0.0
            )
            
            # ── RAG Playbook Injection ────────────────────────────────────────
            # Query the RAG for the best supplier's negotiation/playbook strategy
            best_id = best["supplier_id"]
            if best_id not in supplier_strategies_cache:
                rag_q = f"What is the specific ordering, credit terms, and negotiation playbook for supplier {best['name']}?"
                rag_ans = query_rag(rag_q).get("answer", "")
                
                if rag_ans:
                    # Summarize the RAG context with Gemini to keep it short for the UI
                    from services.gemini_service import generate
                    summary_prompt = f"Summarize this supplier rule into 1 short sentence starting with 'Playbook: ': {rag_ans[:500]}"
                    try:
                        strategy_line = generate(summary_prompt)
                    except Exception as e:
                        logger.warning("[supplier] RAG summary failed: %s", e)
                        strategy_line = f"Playbook: Preferred supplier for {category}."
                else:
                    strategy_line = f"Playbook: Standard ordering terms apply for {best['name']}."
                
                supplier_strategies_cache[best_id] = strategy_line
            
            # Append the RAG playbook strategy to the AI reasoning
            order["ai_reasoning"] += f"\n\n{supplier_strategies_cache[best_id]}"

            total_savings += max(0.0, order.get("saving_vs_second", 0.0))

            # Store rankings keyed by category for the Suppliers page
            supplier_rankings[category] = scored

        state["orders_draft"] = orders_draft
        state["supplier_rankings"] = supplier_rankings

    finally:
        db.close()

    # ── Build SSE summary ─────────────────────────────────────────────────
    assigned = [o for o in orders_draft if o.get("supplier_name")]
    summary_parts: list[str] = []

    if assigned:
        # Find the supplier used most
        from collections import Counter
        name_counts = Counter(o["supplier_name"] for o in assigned if o.get("supplier_name"))
        top_supplier = name_counts.most_common(1)[0][0] if name_counts else "N/A"
        summary_parts.append(
            f"Best supplier assigned for {len(assigned)} order(s). "
            f"Most used: {top_supplier}."
        )

    if rain_heavy:
        summary_parts.append(
            "⚠️ Rain penalty applied — Palakkad/remote suppliers scored down."
        )

    if total_savings > 0:
        summary_parts.append(
            f"Estimated savings vs second-best: ₹{round(total_savings):,} across all orders."
        )

    if not summary_parts:
        summary_parts.append("Supplier scoring complete. No eligible suppliers found for some categories.")

    # ── Log: complete ──────────────────────────────────────────────────────
    state["agent_log"].append(
        {
            "agent": "supplier",
            "status": "complete",
            "summary": " ".join(summary_parts),
            "ts": time(),
        }
    )

    return state
