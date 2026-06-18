"""Scenario Engine package — pure Python, zero LLM calls."""

from scenario_engine.rules import evaluate_scenarios, get_product_multiplier, SCENARIO_RULES

__all__ = ["evaluate_scenarios", "get_product_multiplier", "SCENARIO_RULES"]
