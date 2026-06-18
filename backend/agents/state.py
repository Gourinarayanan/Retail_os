"""
RetailWise AI — Shared LangGraph State
Section 7 of full_flow.md — RetailWiseState TypedDict

This is the single shared state object passed between all 7 agents.
No changes from the spec.
"""

from typing import Dict, List, Optional, TypedDict


class RetailWiseState(TypedDict):
    date: str                        # ISO date string: "2024-10-15"
    weekday: str                     # "Monday" | "Tuesday" | ... | "Sunday"
    business_name: str               # From BUSINESS_NAME env var
    run_id: str                      # UUID — used for SSE stream identification

    # Per-agent outputs
    context: Dict                    # weather, hartal flags, upcoming festivals
    active_scenarios: List[Dict]     # Evaluated scenario rules with demand impacts
    forecast: Dict                   # Prophet per-SKU 7+14 day forecast
    inventory_status: Dict           # Per-SKU: stock, days_remaining, alerts
    orders_draft: List[Dict]         # Drafted orders pending owner approval
    supplier_rankings: Dict          # Per category: ranked + scored suppliers
    opportunities: List[Dict]        # Profit opportunity cards
    daily_brief: str                 # Gemini-generated morning brief (markdown)
    sources: List[str]               # All data sources cited this run
    agent_log: List[Dict]            # {"agent", "status", "summary", "ts"} — feeds SSE
