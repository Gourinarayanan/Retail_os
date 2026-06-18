"""
RetailWise AI — Scenario Engine Runner
Wraps evaluate_scenarios() into a LangGraph-compatible node function.

ZERO LLM calls. ZERO external calls. Pure Python only.
"""

from time import time

from agents.state import RetailWiseState
from scenario_engine.rules import evaluate_scenarios


def run_scenario_engine(state: RetailWiseState) -> RetailWiseState:
    """
    LangGraph node: Scenario Engine.

    Reads state["context"], evaluates all scenario rules, and stores
    the list of active scenarios in state["active_scenarios"].

    Each active scenario dict contains:
        id, name, urgency, category_impacts, action, supply_warning

    Returns the updated state.
    """
    # ── Log: started ──────────────────────────────────────────────────────
    state["agent_log"].append(
        {
            "agent": "scenario",
            "status": "started",
            "summary": "Evaluating scenario rules against context...",
            "ts": time(),
        }
    )

    # ── Core evaluation — pure Python, no LLM ────────────────────────────
    context = state.get("context", {})
    active_scenarios = evaluate_scenarios(context)

    state["active_scenarios"] = active_scenarios

    # ── Build summary line for SSE stream ─────────────────────────────────
    if active_scenarios:
        names = ", ".join(s["name"] for s in active_scenarios)
        critical = [s for s in active_scenarios if s["urgency"] == "CRITICAL"]
        summary = (
            f"{len(active_scenarios)} active scenario(s): {names}."
            + (
                f" ⚠️ {len(critical)} CRITICAL."
                if critical
                else ""
            )
        )
    else:
        summary = "No active demand scenarios today — normal operating conditions."

    # ── Log: complete ──────────────────────────────────────────────────────
    state["agent_log"].append(
        {
            "agent": "scenario",
            "status": "complete",
            "summary": summary,
            "ts": time(),
        }
    )

    return state
