"""
RetailWise AI — Scenario Engine Rules
Section 7 of full_flow.md (scenario_engine/rules.py)

ZERO LLM calls. Pure Python rule evaluation.
Fast, deterministic, and testable.

All triggers are lambda functions that receive the context dict.
Multiple active scenarios are multiplied together (never added).
"""

from __future__ import annotations

# ── Scenario Rules ────────────────────────────────────────────────────────────
# Each rule:
#   id                : unique string identifier
#   name              : human-readable display name
#   trigger           : lambda ctx -> bool  (pure, no side-effects)
#   urgency           : "CRITICAL" | "HIGH" | "MEDIUM" | "LOW" | "INFO"
#   category_impacts  : {category_or_"_all": {"multiplier": float, "reason": str}}
#   action            : one-line recommended action shown in UI
#   supply_warning    : optional supply-chain warning string

SCENARIO_RULES: list[dict] = [
    {
        "id": "hartal_pre_day",
        "name": "Hartal Tomorrow — Pre-Buy Rush",
        "trigger": lambda ctx: (
            ctx.get("hartal_tomorrow") or ctx.get("hartal_days_away") == 1
        ),
        "urgency": "CRITICAL",
        "category_impacts": {
            "dairy": {
                "multiplier": 1.80,
                "reason": (
                    "Milk and egg deliveries stop on hartal. "
                    "Customers stock up heavily today."
                ),
            },
            "staples": {
                "multiplier": 1.60,
                "reason": (
                    "Rice, oil, flour — families ensure full stocks before hartal."
                ),
            },
            "snacks": {
                "multiplier": 1.65,
                "reason": (
                    "Snacks and chips see peak pre-hartal demand — "
                    "people stay home all day."
                ),
            },
            "beverages": {
                "multiplier": 1.45,
                "reason": "Tea demand rises as people plan to be home.",
            },
            "spices": {
                "multiplier": 1.30,
                "reason": "Home cooking all day increases spice purchases.",
            },
            "cleaning": {
                "multiplier": 1.10,
                "reason": "Mild uplift — households do chores on hartal day.",
            },
            "personal_care": {
                "multiplier": 1.05,
                "reason": "Small uplift from stocking behaviour.",
            },
        },
        "action": (
            "Order maximum safe stock today without waiting for the normal cycle."
        ),
        "supply_warning": None,
    },
    {
        "id": "hartal_day",
        "name": "Hartal Today",
        "trigger": lambda ctx: ctx.get("hartal_today", False),
        "urgency": "INFO",
        "category_impacts": {
            "_all": {
                "multiplier": 0.08,
                "reason": "Store near-closed on hartal day.",
            },
        },
        "action": "No new orders needed today. Resume normal schedule tomorrow.",
        "supply_warning": None,
    },
    {
        "id": "hartal_two_days_away",
        "name": "Hartal in 2 Days — Early Stocking Begins",
        "trigger": lambda ctx: ctx.get("hartal_days_away") == 2,
        "urgency": "HIGH",
        "category_impacts": {
            "dairy": {
                "multiplier": 1.25,
                "reason": (
                    "Some households begin stocking up 2 days before hartal."
                ),
            },
            "staples": {
                "multiplier": 1.20,
                "reason": "Early pre-hartal demand beginning.",
            },
        },
        "action": (
            "Ensure full stock is ordered today so you are fully ready "
            "for tomorrow's rush."
        ),
        "supply_warning": None,
    },
    {
        "id": "onam_season",
        "name": "Onam Season",
        "trigger": lambda ctx: any(
            f["festival"] == "Onam" and f["days_away"] <= 10
            for f in ctx.get("upcoming_festivals", [])
        ),
        "urgency": "HIGH",
        "category_impacts": {
            "snacks": {
                "multiplier": 1.45,
                "reason": (
                    "Banana chips are the iconic Onam sadya item — "
                    "highest annual demand."
                ),
            },
            "staples": {
                "multiplier": 1.35,
                "reason": "Rice for sadya feast — highest consumption of the year.",
            },
            "dairy": {
                "multiplier": 1.25,
                "reason": (
                    "Payasam preparation requires large quantities of milk."
                ),
            },
            "beverages": {
                "multiplier": 1.20,
                "reason": "Festival home entertaining drives beverage demand.",
            },
            "cleaning": {
                "multiplier": 1.20,
                "reason": (
                    "Onam cleaning tradition — detergent and cleaning demand spikes."
                ),
            },
            "personal_care": {
                "multiplier": 1.15,
                "reason": "Personal grooming for festival visits.",
            },
        },
        "action": (
            "Place above-normal orders this week. Snacks and rice are the priority."
        ),
        "supply_warning": None,
    },
    {
        "id": "ramadan_month",
        "name": "Ramadan Month",
        "trigger": lambda ctx: any(
            f["festival"] == "Ramadan"
            for f in ctx.get("upcoming_festivals", [])
        ),
        "urgency": "MEDIUM",
        "category_impacts": {
            "spices": {
                "multiplier": 1.55,
                "reason": (
                    "Iftar and suhoor cooking requires significantly more spices."
                ),
            },
            "staples": {
                "multiplier": 1.30,
                "reason": (
                    "Rice and flour demand up with daily home cooking for iftar."
                ),
            },
            "dairy": {
                "multiplier": 1.20,
                "reason": "Milk demand rises for suhoor (pre-dawn meal).",
            },
            "beverages": {
                "multiplier": 1.15,
                "reason": "Dates and beverages consumed at iftar.",
            },
        },
        "action": (
            "Ensure spice stocks remain full throughout the month. "
            "Reorder more frequently."
        ),
        "supply_warning": None,
    },
    {
        "id": "eid_approaching",
        "name": "Eid — Final Rush",
        "trigger": lambda ctx: any(
            f["festival"] == "Eid" and f["days_away"] <= 3
            for f in ctx.get("upcoming_festivals", [])
        ),
        "urgency": "CRITICAL",
        "category_impacts": {
            "spices": {
                "multiplier": 1.85,
                "reason": (
                    "Eid biryani — highest single-day spike for red chilli "
                    "and garam masala all year."
                ),
            },
            "staples": {
                "multiplier": 1.50,
                "reason": "Rice demand peaks for biryani and special Eid meals.",
            },
            "snacks": {
                "multiplier": 1.55,
                "reason": "Snacks for Eid entertaining and gifting.",
            },
            "dairy": {
                "multiplier": 1.40,
                "reason": "Sweets, payasam, and dessert preparation.",
            },
        },
        "action": (
            "URGENT: Stock spices immediately. "
            "Red chilli and garam masala will sell out."
        ),
        "supply_warning": None,
    },
    {
        "id": "christmas_week",
        "name": "Christmas Season",
        "trigger": lambda ctx: any(
            f["festival"] == "Christmas" and f["days_away"] <= 7
            for f in ctx.get("upcoming_festivals", [])
        ),
        "urgency": "HIGH",
        "category_impacts": {
            "beverages": {
                "multiplier": 1.50,
                "reason": (
                    "Coffee and tea demand highest during Christmas "
                    "gifting and visiting."
                ),
            },
            "snacks": {
                "multiplier": 1.45,
                "reason": "Mixture and snacks for Christmas home visits.",
            },
            "dairy": {
                "multiplier": 1.35,
                "reason": "Cake and sweet preparation — extra eggs and milk.",
            },
            "staples": {
                "multiplier": 1.30,
                "reason": "Flour demand rises for Christmas baking.",
            },
            "personal_care": {
                "multiplier": 1.25,
                "reason": "Grooming products for family gatherings.",
            },
        },
        "action": "Stock coffee, eggs, and flour. These will move fast this week.",
        "supply_warning": None,
    },
    {
        "id": "vishu_day",
        "name": "Vishu Festival",
        "trigger": lambda ctx: any(
            f["festival"] == "Vishu" and f["days_away"] <= 3
            for f in ctx.get("upcoming_festivals", [])
        ),
        "urgency": "MEDIUM",
        "category_impacts": {
            "staples": {
                "multiplier": 1.30,
                "reason": "Rice and coconut oil for Vishu feast.",
            },
            "snacks": {
                "multiplier": 1.25,
                "reason": "Banana chips — traditional Vishu item.",
            },
            "personal_care": {
                "multiplier": 1.20,
                "reason": "New clothes and grooming for Vishu celebration.",
            },
        },
        "action": "Stock rice, coconut oil, and banana chips before Vishu.",
        "supply_warning": None,
    },
    {
        "id": "rainy_day",
        "name": "Heavy Rain Tomorrow",
        "trigger": lambda ctx: (
            ctx.get("weather", {})
            .get("tomorrow", {})
            .get("rain_heavy", False)
        ),
        "urgency": "MEDIUM",
        "category_impacts": {
            "beverages": {
                "multiplier": 1.30,
                "reason": (
                    "Hot drinks — tea and coffee demand rises sharply in heavy rain."
                ),
            },
            "snacks": {
                "multiplier": 1.25,
                "reason": "Snacking increases when people stay indoors.",
            },
            "dairy": {
                "multiplier": 1.10,
                "reason": "Mild uplift from home cooking.",
            },
            "_all": {
                "multiplier": 0.90,
                "reason": "Foot traffic reduces overall by ~10% on heavy rain days.",
            },
        },
        "action": (
            "Reduce perishable orders by 10%. "
            "Avoid ordering from Palakkad suppliers tomorrow."
        ),
        "supply_warning": (
            "Palakkad and Coimbatore suppliers may face road delays due to rain."
        ),
    },
    {
        "id": "weekend",
        "name": "Weekend Boost",
        "trigger": lambda ctx: ctx.get("weekday") in ["Saturday", "Sunday"],
        "urgency": "LOW",
        "category_impacts": {
            "_all": {
                "multiplier": 1.10,
                "reason": "Weekend family shopping — +10% across all categories.",
            },
        },
        "action": "Ensure shelves are well-stocked for weekend traffic.",
        "supply_warning": None,
    },
]


# ── All known product categories ──────────────────────────────────────────────
ALL_CATEGORIES = (
    "dairy",
    "staples",
    "snacks",
    "spices",
    "beverages",
    "cleaning",
    "personal_care",
)


def evaluate_scenarios(context: dict) -> list[dict]:
    """
    Evaluate all SCENARIO_RULES against the provided context dict.
    Returns a list of active scenario dicts (only rules whose trigger fired).

    Each returned dict contains:
        id, name, urgency, category_impacts, action, supply_warning
    """
    active: list[dict] = []
    for rule in SCENARIO_RULES:
        try:
            if rule["trigger"](context):
                active.append(
                    {
                        "id": rule["id"],
                        "name": rule["name"],
                        "urgency": rule["urgency"],
                        "category_impacts": rule["category_impacts"],
                        "action": rule["action"],
                        "supply_warning": rule.get("supply_warning"),
                    }
                )
        except Exception:
            # Never let a bad trigger crash the pipeline
            pass
    return active


def get_product_multiplier(
    category: str,
    active_scenarios: list[dict],
) -> tuple[float, list[str]]:
    """
    Compute the combined demand multiplier for a given product category
    across all active scenarios.

    Rules:
    - Category-specific impact takes precedence over _all.
    - For rainy_day: category uplift and _all reduction are BOTH applied
      (they are multiplied together already in each rule's impact dict).
    - Multiple active scenarios: their multipliers are MULTIPLIED (not added).

    Returns:
        (combined_multiplier, reason_strings)

    reason_strings are shown verbatim in the UI ReasoningPanel.
    """
    combined_multiplier: float = 1.0
    reasons: list[str] = []

    for scenario in active_scenarios:
        impacts: dict = scenario["category_impacts"]

        # Resolve category-specific impact, fall back to _all
        cat_impact = impacts.get(category)
        all_impact = impacts.get("_all")

        if cat_impact and all_impact:
            # Both present (e.g. rainy_day): multiply them together
            effective_multiplier = cat_impact["multiplier"] * all_impact["multiplier"]
            reason_text = (
                f"{cat_impact['reason']} "
                f"(×{cat_impact['multiplier']}) — "
                f"{all_impact['reason']} "
                f"(×{all_impact['multiplier']})"
            )
        elif cat_impact:
            effective_multiplier = cat_impact["multiplier"]
            reason_text = (
                f"{cat_impact['reason']} (×{cat_impact['multiplier']})"
            )
        elif all_impact:
            effective_multiplier = all_impact["multiplier"]
            reason_text = (
                f"{all_impact['reason']} (×{all_impact['multiplier']})"
            )
        else:
            # This scenario does not affect this category at all
            continue

        combined_multiplier *= effective_multiplier
        reasons.append(f"[{scenario['name']}] {reason_text}")

    return round(combined_multiplier, 3), reasons
