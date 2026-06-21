"""
RetailWise AI — CEO Agent (Orchestrator) — Agent 1
Section 7 — Agent 1 of full_flow.md

Responsibilities:
  1. run_briefing_agent()       — Gemini morning brief generation + DB save
  2. run_pipeline_streaming()   — agents run sequentially; each agent_log entry
                                  is put into an asyncio.Queue as it fires.
                                  Used by the SSE router for real-time streaming.
  3. run_full_pipeline()        — non-streaming version for APScheduler / tests.

LangGraph graph (verbatim from spec):
    context → scenario → forecast → inventory → supplier → opportunity → briefing
"""

import json
import logging
import os
import uuid
from datetime import date
from time import time

from dotenv import load_dotenv
from sqlalchemy.orm import Session

from agents.context_agent import run_context_agent
from agents.forecast_agent import run_forecast_agent
from agents.inventory_agent import run_inventory_agent
from agents.opportunity_agent import run_opportunity_agent
from agents.state import RetailWiseState
from agents.supplier_agent import run_supplier_agent
from database.db import SessionLocal
from database.models import DailyBriefing, Order
from scenario_engine.engine import run_scenario_engine
from services import gemini_service

load_dotenv()

logger = logging.getLogger(__name__)

_BUSINESS_NAME: str = os.environ.get("BUSINESS_NAME", "RetailWise Store")
_BUSINESS_LOCATION: str = os.environ.get("BUSINESS_LOCATION", "Kerala")

WEEKDAY_NAMES = [
    "Monday", "Tuesday", "Wednesday",
    "Thursday", "Friday", "Saturday", "Sunday",
]

# ── Briefing Agent ────────────────────────────────────────────────────────────

async def run_briefing_agent(state: RetailWiseState) -> RetailWiseState:
    """
    LangGraph node: Briefing Agent.

    Calls gemini_service.generate_morning_brief(state) to produce
    the final markdown morning brief.

    Persists a DailyBriefing row to the database.
    Saves all pending orders from state["orders_draft"] to the Order table.
    """
    # ── Log: started ──────────────────────────────────────────────────────
    state["agent_log"].append(
        {
            "agent": "briefing",
            "status": "started",
            "summary": "Generating morning brief with Gemini Flash...",
            "ts": time(),
        }
    )

    # ── Generate brief ────────────────────────────────────────────────────
    try:
        brief_text = gemini_service.generate_morning_brief(state)
    except Exception as exc:
        logger.error("[briefing] Gemini morning brief failed: %s", exc)
        brief_text = (
            f"Good morning. RetailWise AI briefing for {state.get('date', 'today')} "
            "could not be generated — Gemini API unavailable. "
            "Please check your inventory and pending orders manually."
        )

    state["daily_brief"] = brief_text

    # ── Persist DailyBriefing to DB ───────────────────────────────────────
    today_date = date.today()
    db: Session = SessionLocal()
    try:
        # Upsert: replace today's briefing if one already exists
        existing = (
            db.query(DailyBriefing)
            .filter(DailyBriefing.date == today_date)
            .first()
        )

        briefing_row = existing or DailyBriefing()
        briefing_row.date = today_date
        briefing_row.brief_text = brief_text
        briefing_row.context_json = json.dumps(state.get("context", {}), default=str)
        briefing_row.scenarios_json = json.dumps(state.get("active_scenarios", []), default=str)
        briefing_row.inventory_alerts_json = json.dumps(
            [
                v for v in state.get("inventory_status", {}).values()
                if v.get("alert") not in ("ok", "excess")
                or v.get("expiry_alerts")
            ],
            default=str,
        )
        briefing_row.orders_json = json.dumps(state.get("orders_draft", []), default=str)
        briefing_row.forecast_json = json.dumps(state.get("forecast", {}), default=str)
        briefing_row.opportunities_json = json.dumps(state.get("opportunities", []), default=str)

        if not existing:
            db.add(briefing_row)

        # ── Persist drafted orders to the Order table ─────────────────────
        # Wipe old unmodified pending orders so we don't duplicate them on re-runs
        db.query(Order).filter(Order.status == "pending_approval", Order.owner_modified == False).delete()
        db.commit()

        for draft in state.get("orders_draft", []):
            if not draft.get("supplier_id") or not draft.get("price_per_unit"):
                logger.warning(
                    "[briefing] Skipping order for %s — no supplier assigned.",
                    draft.get("product_name"),
                )
                continue

            order_row = Order(
                supplier_id=draft["supplier_id"],
                product_id=draft["product_id"],
                order_cycle=draft["order_cycle"],
                ai_recommended_qty=draft["ai_recommended_qty"],
                ai_reasoning=draft["ai_reasoning"],
                final_qty=draft["ai_recommended_qty"],   # starts equal to AI rec
                owner_modified=False,
                owner_note=None,
                unit=draft["unit"],
                price_per_unit=draft["price_per_unit"],
                total_cost=draft.get("total_cost", draft["price_per_unit"] * draft["ai_recommended_qty"]),
                status="pending_approval",
                whatsapp_message=_build_whatsapp_message(draft),
            )
            db.add(order_row)

        db.commit()
        logger.info("[briefing] DailyBriefing and %d order(s) saved to DB.", len(state.get("orders_draft", [])))

    except Exception as exc:
        logger.error("[briefing] DB save failed: %s", exc)
        db.rollback()
    finally:
        db.close()

    # ── Log: complete ──────────────────────────────────────────────────────
    state["agent_log"].append(
        {
            "agent": "briefing",
            "status": "complete",
            "summary": "Morning brief ready.",
            "ts": time(),
        }
    )

    return state


def _build_whatsapp_message(draft: dict) -> str:
    """Build the WhatsApp order message string stored in the Order row."""
    urgency = "🚨 URGENT — " if draft.get("order_cycle") == "emergency" else ""
    cycle_label = draft.get("order_cycle", "order").replace("_", " ").title()
    today_str = date.today().strftime("%d %b %Y")
    delivery = draft.get("delivery_date", today_str)

    return (
        f"{urgency}🛒 *RetailWise AI — {cycle_label} Order*\n\n"
        f"Namaskaram {draft.get('supplier_contact', 'Sir/Madam')},\n\n"
        f"Please supply the following:\n"
        f"• *Item:* {draft.get('product_name', 'N/A')}\n"
        f"• *Quantity:* {round(draft.get('ai_recommended_qty', 0))} {draft.get('unit', 'units')}s\n"
        f"• *Delivery by:* {delivery} (morning preferred)\n"
        f"• *Agreed price:* ₹{draft.get('price_per_unit', 0)}/{draft.get('unit', 'unit')}\n"
        f"• *Total:* ₹{round(draft.get('total_cost', 0)):,}\n\n"
        f"*From:* {_BUSINESS_NAME}, {_BUSINESS_LOCATION}\n"
        f"*Order Ref:* {draft.get('order_ref', 'N/A')}\n\n"
        f"Kindly confirm receipt of this order. 🙏\n\n"
        f"— Sent via RetailWise AI (automated)"
    ).strip()


# ── LangGraph graph — exact spec Section 7 Agent 1 ────────────────────────────

def _build_graph():
    """
    Build and compile the LangGraph StateGraph.
    Graph definition verbatim from spec Section 7 Agent 1.

    Handles langgraph 0.0.55 API (set_entry_point instead of START constant).
    """
    try:
        from langgraph.graph import END, StateGraph

        graph = StateGraph(RetailWiseState)

        # LangGraph 0.0.55 forbids using a TypedDict state key as a node name.
        # RetailWiseState keys: context, forecast, inventory_status, orders_draft,
        # supplier_rankings, opportunities, daily_brief, sources, agent_log, etc.
        # All node names use the _node suffix to avoid every possible collision.
        graph.add_node("ctx_node",         run_context_agent)
        graph.add_node("scenario_node",    run_scenario_engine)
        graph.add_node("forecast_node",    run_forecast_agent)
        graph.add_node("inventory_node",   run_inventory_agent)
        graph.add_node("supplier_node",    run_supplier_agent)
        graph.add_node("opportunity_node", run_opportunity_agent)
        graph.add_node("briefing_node",    run_briefing_agent)

        # Entry point
        graph.set_entry_point("ctx_node")

        # Linear pipeline edges
        graph.add_edge("ctx_node",         "scenario_node")
        graph.add_edge("scenario_node",    "forecast_node")
        graph.add_edge("forecast_node",    "inventory_node")
        graph.add_edge("inventory_node",   "supplier_node")
        graph.add_edge("supplier_node",    "opportunity_node")
        graph.add_edge("opportunity_node", "briefing_node")
        graph.add_edge("briefing_node",    END)

        return graph.compile()

    except Exception as exc:
        logger.error("[ceo] Failed to compile LangGraph: %s", exc)
        raise


# Compile once at module load time
_pipeline = _build_graph()


# ── Streaming pipeline (queue-based, for SSE) ─────────────────────────────────

def _make_initial_state(run_id: str) -> RetailWiseState:
    today = date.today()
    return {
        "date": today.isoformat(),
        "weekday": WEEKDAY_NAMES[today.weekday()],
        "business_name": _BUSINESS_NAME,
        "run_id": run_id,
        "context": {},
        "active_scenarios": [],
        "forecast": {},
        "inventory_status": {},
        "orders_draft": [],
        "supplier_rankings": {},
        "opportunities": [],
        "daily_brief": "",
        "sources": [],
        "agent_log": [],
    }


async def run_pipeline_streaming(queue: "asyncio.Queue") -> RetailWiseState:
    """
    Run each agent node manually in sequence.
    After every agent_log append, the new entry is immediately put into
    the asyncio.Queue so the SSE endpoint can stream it without waiting
    for the full pipeline to complete.

    A sentinel value of None is put into the queue when the pipeline is done.

    Args:
        queue: asyncio.Queue that the SSE generator reads from.

    Returns:
        Final RetailWiseState.
    """
    import asyncio

    run_id = str(uuid.uuid4())
    state = _make_initial_state(run_id)

    async def _run_node(node_fn, node_name: str):
        """Run one agent, then flush all new agent_log entries to the queue."""
        prev_len = len(state["agent_log"])
        try:
            updated = await node_fn(state)
            # Merge returned state back (LangGraph nodes return new state)
            state.update(updated)
        except Exception as exc:
            logger.error("[ceo] Node '%s' failed: %s", node_name, exc)
            state["agent_log"].append({
                "agent": node_name,
                "status": "error",
                "summary": f"{node_name} failed: {exc}",
                "ts": time(),
            })

        # Flush any new log entries to queue
        new_entries = state["agent_log"][prev_len:]
        for entry in new_entries:
            await queue.put(entry)

    logger.info("[ceo] Starting streaming pipeline run_id=%s", run_id)

    # Emit pipeline-started event
    started_entry = {
        "agent": "ceo",
        "status": "started",
        "summary": "Initialising RetailWise AI pipeline...",
        "ts": time(),
    }
    state["agent_log"].append(started_entry)
    await queue.put(started_entry)

    # Run all agents in exact spec order
    nodes = [
        (run_context_agent,     "context"),
        (run_scenario_engine,   "scenario"),
        (run_forecast_agent,    "forecast"),
        (run_inventory_agent,   "inventory"),
        (run_supplier_agent,    "supplier"),
        (run_opportunity_agent, "opportunity"),
        (run_briefing_agent,    "briefing"),
    ]

    for node_fn, node_name in nodes:
        await _run_node(node_fn, node_name)

    logger.info(
        "[ceo] Streaming pipeline complete. run_id=%s orders=%d opportunities=%d",
        run_id,
        len(state.get("orders_draft", [])),
        len(state.get("opportunities", [])),
    )

    # Sentinel: signals SSE generator to close the stream
    await queue.put(None)
    return state


# ── Non-streaming pipeline (APScheduler / tests) ──────────────────────────────

async def run_full_pipeline() -> RetailWiseState:
    """
    Non-streaming version of the pipeline — used by APScheduler morning job.
    Runs via LangGraph compiled graph; returns final state when all agents done.
    """
    import asyncio

    # Reuse streaming pipeline internally; discard the queue
    q: asyncio.Queue = asyncio.Queue()
    state = await run_pipeline_streaming(q)
    return state
