"""
RetailWise AI — Inventory Intelligence Agent (Agent 4)
Section 7 — Agent 4 of full_flow.md

Analyses current stock against forecasted demand.
Generates alert flags, expiry warnings, and drafts orders
according to each product's order cycle rules.
"""

import logging
from datetime import date, timedelta
from time import time

from sqlalchemy.orm import Session

from agents.state import RetailWiseState
from database.db import SessionLocal
from database.models import InventoryBatch, Product
from scenario_engine.rules import get_product_multiplier

logger = logging.getLogger(__name__)

# Days-to-expiry thresholds for batch alerts
_EXPIRY_CRITICAL_DAYS = 3
_EXPIRY_WARNING_DAYS = 10

# Excess threshold in days
_EXCESS_DAYS = 21

# Critical/out-of-stock threshold in days
_CRITICAL_DAYS = 2

# Safety buffer multiplier on daily order quantity
_SAFETY_BUFFER = 1.20

WEEKDAY_NAMES = [
    "Monday", "Tuesday", "Wednesday",
    "Thursday", "Friday", "Saturday", "Sunday",
]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _days_remaining(current_stock: float, adj_daily: float) -> float:
    """Days of stock left at the adjusted daily demand rate."""
    if adj_daily <= 0:
        return 9999.0
    return round(current_stock / adj_daily, 1)


def _alert_level(current_stock: float, days_rem: float, reorder_point_days: float) -> str:
    if current_stock == 0:
        return "out_of_stock"
    if days_rem < _CRITICAL_DAYS:
        return "critical"
    if days_rem < reorder_point_days:
        return "warning"
    if days_rem > _EXCESS_DAYS:
        return "excess"
    return "ok"


def _check_expiry(batches: list[InventoryBatch], today: date) -> list[dict]:
    """Return expiry alert dicts for any active batch expiring within the threshold."""
    alerts = []
    for batch in batches:
        if not batch.expiry_date or batch.quantity <= 0:
            continue
        days_to_expiry = (batch.expiry_date - today).days
        if days_to_expiry <= 0:
            severity = "expired"
            recommendation = "Remove from shelf immediately. Write off stock."
        elif days_to_expiry <= _EXPIRY_CRITICAL_DAYS:
            severity = "critical_expiry"
            recommendation = "Immediate discount — sell today."
        elif days_to_expiry <= _EXPIRY_WARNING_DAYS:
            severity = "expiring_soon"
            recommendation = (
                "Discount 15%. Bundle with popular item. "
                "Run promotions this week."
            )
        else:
            continue  # healthy, skip
        alerts.append(
            {
                "batch_number": batch.batch_number,
                "severity": severity,
                "days_to_expiry": days_to_expiry,
                "quantity": batch.quantity,
                "expiry_date": batch.expiry_date.isoformat(),
                "est_loss": round(batch.quantity * batch.purchase_price, 2),
                "recommendation": recommendation,
            }
        )
    return alerts


def _should_order(
    product: Product,
    alert: str,
    today_weekday: str,
    today_day_of_month: int,
) -> tuple[bool, str]:
    """
    Determine whether to draft an order for this product today.
    Returns (should_order: bool, order_cycle_label: str).
    """
    is_critical = alert in ("out_of_stock", "critical")

    if is_critical:
        return True, "emergency"

    if product.order_cycle == "daily":
        return True, "daily"

    if product.order_cycle == "weekly":
        if today_weekday == product.order_day:
            return True, "weekly"
        return False, ""

    if product.order_cycle == "monthly":
        try:
            if today_day_of_month == int(product.order_day or "0"):
                return True, "monthly"
        except (ValueError, TypeError):
            pass
        return False, ""

    return False, ""


def _calculate_order_qty(
    product: Product,
    current_stock: float,
    adj_daily: float,
    order_cycle_label: str,
    forecast_state: dict,
) -> float:
    """
    Compute recommended order quantity per spec Section 7 Agent 7.

    daily   : tomorrow_forecast × 1.20 safety
    weekly  : 7-day forecast total + 2-day safety stock − current_stock
    monthly : 30-day avg demand + 5-day safety buffer − current_stock
    emergency: days_until_next_order × adj_daily × 1.15
    """
    today = date.today()
    product_forecast = forecast_state.get(str(product.id), {})
    daily_detail: list[dict] = product_forecast.get("daily_detail", [])

    def forecast_for_day(target: date) -> float:
        target_str = target.isoformat()
        for row in daily_detail:
            if row.get("date") == target_str:
                return row.get("adjusted", adj_daily)
        return adj_daily

    def sum_forecast_next_n(n: int) -> float:
        total = 0.0
        for i in range(1, n + 1):
            total += forecast_for_day(today + timedelta(days=i))
        return total

    if order_cycle_label == "daily":
        tomorrow_forecast = forecast_for_day(today + timedelta(days=1))
        qty = tomorrow_forecast * _SAFETY_BUFFER

    elif order_cycle_label == "weekly":
        week_total = sum_forecast_next_n(7)
        safety_stock = adj_daily * 2
        qty = max(0.0, week_total + safety_stock - current_stock)

    elif order_cycle_label == "monthly":
        monthly_demand = product.avg_daily_demand * 30
        safety_stock = product.avg_daily_demand * 5
        qty = max(0.0, monthly_demand + safety_stock - current_stock)

    elif order_cycle_label == "emergency":
        # Cover the gap until next scheduled order day + 1 buffer day
        days_to_cover = _days_until_next_cycle(product, today) + 1
        qty = adj_daily * days_to_cover * 1.15

    else:
        qty = adj_daily * (product.lead_time_days + 7)

    return max(0.0, round(qty, 1))


def _days_until_next_cycle(product: Product, today: date) -> int:
    """Estimate days until the product's next scheduled order date."""
    if product.order_cycle == "daily":
        return 1
    if product.order_cycle == "weekly" and product.order_day:
        today_idx = today.weekday()  # Monday=0
        try:
            target_idx = WEEKDAY_NAMES.index(product.order_day)
        except ValueError:
            return 3
        days = (target_idx - today_idx) % 7
        return days if days > 0 else 7
    if product.order_cycle == "monthly":
        try:
            target_day = int(product.order_day or "1")
        except (ValueError, TypeError):
            return 14
        if today.day < target_day:
            return target_day - today.day
        # Next month
        next_month = (today.replace(day=1) + timedelta(days=32)).replace(day=target_day)
        return (next_month - today).days
    return 3


def _build_ai_reasoning(
    product: Product,
    qty: float,
    order_cycle_label: str,
    adj_daily: float,
    baseline_daily: float,
    multiplier: float,
    reasons: list[str],
    current_stock: float,
    days_remaining: float,
    expiry_alerts: list[dict],
    today_weekday: str,
    playbook_rule: str = "",
) -> str:
    """
    Build the full AI reasoning string shown verbatim in the UI ReasoningPanel.
    Implements spec Section 7 Agent 7 — AI Reasoning Builder.
    Numbers are ONLY from the actual computed values — never hardcoded.
    """
    lines: list[str] = []

    # 1. Base forecast line
    lines.append(
        f"Holt-Winters model forecasts an average of {round(baseline_daily, 1)} "
        f"{product.unit}s/day over the next 7 days (based on 90 days of your sales data)."
    )

    # 2. Active scenario impacts
    if reasons:
        for reason in reasons:
            lines.append(f"• {reason}")
    else:
        lines.append("• No active demand scenarios today — baseline demand applies.")

    if playbook_rule:
        lines.append(f"\n{playbook_rule}")

    # 3. Order cycle explanation
    if order_cycle_label == "daily":
        lines.append(
            f"This is a daily-order item. "
            f"Tomorrow's adjusted forecast is {round(adj_daily, 1)} {product.unit}s "
            f"+ {int((_SAFETY_BUFFER - 1) * 100)}% safety buffer = {round(qty)} {product.unit}s recommended."
        )
    elif order_cycle_label == "weekly":
        lines.append(
            f"Today ({today_weekday}) is your scheduled weekly order day for {product.name}. "
            f"7-day forecast total + 2-day safety stock − current stock "
            f"({round(current_stock)}) = {round(qty)} to order."
        )
    elif order_cycle_label == "monthly":
        lines.append(
            f"Today is your monthly order day for {product.name}. "
            f"30-day forecast + 5-day safety buffer − current stock "
            f"({round(current_stock)}) = {round(qty)} to order."
        )
    elif order_cycle_label == "emergency":
        lines.append(
            f"⚠️ EMERGENCY ORDER: Stock will run out in {days_remaining} days, "
            f"before the next scheduled {product.order_cycle} order. "
            f"Ordering {round(qty)} {product.unit}s to cover the gap."
        )

    # 4. Expiry note
    if expiry_alerts:
        lines.append(
            f"Note: {len(expiry_alerts)} batch(es) are expiring soon. "
            f"Sell older stock first (FIFO) to reduce waste."
        )

    return "\n".join(lines)


# ── LangGraph node ────────────────────────────────────────────────────────────

async def run_inventory_agent(state: RetailWiseState) -> RetailWiseState:
    """
    LangGraph node: Inventory Intelligence Agent.

    Reads DB stock levels, computes days_remaining using forecast data,
    sets alert levels, checks expiry, and drafts orders into state["orders_draft"].
    """
    # ── Log: started ──────────────────────────────────────────────────────
    state["agent_log"].append(
        {
            "agent": "inventory",
            "status": "started",
            "summary": "Analysing stock levels, expiry dates, and drafting orders...",
            "ts": time(),
        }
    )

    today = date.today()
    today_weekday = WEEKDAY_NAMES[today.weekday()]
    today_day_of_month = today.day
    forecast_state: dict = state.get("forecast", {})
    active_scenarios = state.get("active_scenarios", [])

    # ── Load products + inventory batches from DB ─────────────────────────
    db: Session = SessionLocal()
    try:
        products = db.query(Product).filter(Product.is_active == True).all()
        # Load all active batches at once
        all_batches = (
            db.query(InventoryBatch)
            .filter(InventoryBatch.status.in_(["active", "expiring_soon"]))
            .all()
        )
    finally:
        db.close()

    # Group batches by product_id
    batches_by_product: dict[int, list[InventoryBatch]] = {}
    for batch in all_batches:
        batches_by_product.setdefault(batch.product_id, []).append(batch)

    inventory_status: dict = {}
    orders_draft: list[dict] = []

    for product in products:
        product_batches = batches_by_product.get(product.id, [])
        current_stock = sum(b.quantity for b in product_batches)

        # Get scenario-adjusted daily demand from forecast agent output
        product_forecast = forecast_state.get(str(product.id), {})
        baseline_daily: float = product_forecast.get(
            "baseline_daily", product.avg_daily_demand
        )
        adj_daily: float = product_forecast.get(
            "scenario_adjusted_daily", product.avg_daily_demand
        )
        multiplier: float = product_forecast.get("multiplier", 1.0)
        reasons: list[str] = product_forecast.get("reasons", [])

        days_rem = _days_remaining(current_stock, adj_daily)
        alert = _alert_level(current_stock, days_rem, product.reorder_point_days)
        expiry_alerts = _check_expiry(product_batches, today)

        # ── Inventory status entry ────────────────────────────────────────
        inventory_status[str(product.id)] = {
            "product_id": product.id,
            "product_name": product.name,
            "sku": product.sku,
            "category": product.category,
            "unit": product.unit,
            "current_stock": round(current_stock, 1),
            "min_threshold": product.min_threshold,
            "days_remaining": days_rem,
            "alert": alert,
            "baseline_daily": round(baseline_daily, 2),
            "adj_daily": round(adj_daily, 2),
            "scenario_multiplier": round(multiplier, 3),
            "expiry_alerts": expiry_alerts,
            "batches": [
                {
                    "batch_number": b.batch_number,
                    "quantity": b.quantity,
                    "expiry_date": b.expiry_date.isoformat() if b.expiry_date else None,
                    "status": b.status,
                    "purchase_price": b.purchase_price,
                }
                for b in product_batches
            ],
        }

        # ── Order drafting ────────────────────────────────────────────────
        should, cycle_label = _should_order(
            product, alert, today_weekday, today_day_of_month
        )

        # Skip if excess (and not out_of_stock)
        if alert == "excess" and cycle_label != "emergency":
            should = False

        if not should or not cycle_label:
            continue

        qty = _calculate_order_qty(
            product, current_stock, adj_daily, cycle_label, forecast_state
        )

        if qty <= 0:
            continue

        # ── RAG Playbook Injection for Emergencies ────────────────────────
        playbook_rule = ""
        if cycle_label == "emergency" or alert == "out_of_stock":
            try:
                from rag.rag_engine import query_rag
                rag_q = f"What is the store policy on dealing with Stockouts and Emergency Orders for {product.category}?"
                rag_ans = query_rag(rag_q).get("answer", "")
                if rag_ans:
                    from services.gemini_service import generate
                    summary_prompt = f"Summarize this inventory rule into 1 short sentence starting with 'Emergency Policy: ': {rag_ans[:500]}"
                    playbook_rule = generate(summary_prompt)
            except Exception as e:
                logger.warning("[inventory] RAG query failed: %s", e)

        reasoning = _build_ai_reasoning(
            product=product,
            qty=qty,
            order_cycle_label=cycle_label,
            adj_daily=adj_daily,
            baseline_daily=baseline_daily,
            multiplier=multiplier,
            reasons=reasons,
            current_stock=current_stock,
            days_remaining=days_rem,
            expiry_alerts=expiry_alerts,
            today_weekday=today_weekday,
            playbook_rule=playbook_rule,
        )

        delivery_date = today + timedelta(days=product.lead_time_days)

        orders_draft.append(
            {
                "product_id": product.id,
                "product_name": product.name,
                "product_sku": product.sku,
                "category": product.category,
                "unit": product.unit,
                "order_cycle": cycle_label,
                "ai_recommended_qty": qty,
                "final_qty": qty,          # Owner can edit this later
                "ai_reasoning": reasoning,
                "delivery_date": delivery_date.isoformat(),
                "order_ref": f"PO-{today.strftime('%Y%m%d')}-{product.sku}",
                "alert": alert,
                # Supplier and price filled in by supplier agent
                "supplier_id": None,
                "supplier_name": None,
                "price_per_unit": None,
                "total_cost": None,
            }
        )

    state["inventory_status"] = inventory_status
    state["orders_draft"] = orders_draft

    # ── Build SSE summary ─────────────────────────────────────────────────
    out_of_stock = [v for v in inventory_status.values() if v["alert"] == "out_of_stock"]
    critical = [v for v in inventory_status.values() if v["alert"] == "critical"]
    expiring = [v for v in inventory_status.values() if v["expiry_alerts"]]

    summary_parts: list[str] = []
    if out_of_stock:
        names = ", ".join(v["product_name"] for v in out_of_stock)
        summary_parts.append(f"🚫 OUT OF STOCK: {names}.")
    if critical:
        names = ", ".join(
            f"{v['product_name']} ({v['days_remaining']}d)" for v in critical
        )
        summary_parts.append(f"🔴 Critical: {names}.")
    if expiring:
        summary_parts.append(f"⚠️ {len(expiring)} product(s) with expiry alerts.")
    summary_parts.append(f"{len(orders_draft)} order(s) drafted for approval.")

    # ── Log: complete ──────────────────────────────────────────────────────
    state["agent_log"].append(
        {
            "agent": "inventory",
            "status": "complete",
            "summary": " ".join(summary_parts),
            "ts": time(),
        }
    )

    return state
