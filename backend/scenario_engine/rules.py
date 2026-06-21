"""
RetailWise AI — Scenario Engine Rules
Section 7 of full_flow.md (scenario_engine/rules.py)

ZERO LLM calls. Pure Python rule evaluation.
Fast, deterministic, and testable.

All triggers are lambda functions that receive the context dict.
Multiple active scenarios are multiplied together (never added).
"""

from __future__ import annotations

SCENARIO_RULES: list[dict] = [
    # 🏮 FESTIVAL SCENARIOS
    {
        "id": "onam_15_days",
        "name": "Onam Season — Early Planning",
        "trigger": lambda ctx: any(f["festival"] == "Onam" and 7 < f["days_away"] <= 15 for f in ctx.get("upcoming_festivals", [])),
        "urgency": "LOW",
        "category_impacts": {
            "snacks": {"multiplier": 1.30, "reason": "Advance orders for Banana Chips begin."},
            "staples": {"multiplier": 1.20, "reason": "Rice and Jaggery early procurement."},
            "dairy": {"multiplier": 1.15, "reason": "Ghee and dairy pre-orders."},
        },
        "action": "Increase forecast by 30%. Start procurement immediately to avoid shortages.",
        "supply_warning": "Banana chips manufacturers getting overloaded.",
    },
    {
        "id": "onam_7_days",
        "name": "Onam Season — Peak Buying",
        "trigger": lambda ctx: any(f["festival"] == "Onam" and 2 < f["days_away"] <= 7 for f in ctx.get("upcoming_festivals", [])),
        "urgency": "HIGH",
        "category_impacts": {
            "snacks": {"multiplier": 1.60, "reason": "Banana Chips demand explodes."},
            "dairy": {"multiplier": 1.40, "reason": "Payasam ingredients spike."},
            "cleaning": {"multiplier": 1.30, "reason": "Cleaning products rise for home prep."},
            "staples": {"multiplier": 1.40, "reason": "Rice and sugar moving fast."},
        },
        "action": "Emergency stock build-up. Ensure all Onam staples are fully stocked.",
        "supply_warning": None,
    },
    {
        "id": "onam_2_days",
        "name": "Onam Season — Panic Buying",
        "trigger": lambda ctx: any(f["festival"] == "Onam" and f["days_away"] <= 2 for f in ctx.get("upcoming_festivals", [])),
        "urgency": "CRITICAL",
        "category_impacts": {
            "snacks": {"multiplier": 2.00, "reason": "Last-minute sadya panic buying."},
            "dairy": {"multiplier": 1.80, "reason": "Milk and ghee selling out."},
            "staples": {"multiplier": 1.50, "reason": "Final rice purchases."},
        },
        "action": "Maximum stock alert. Reorder immediately if stocks dip below 30%.",
        "supply_warning": None,
    },
    {
        "id": "ramadan_month",
        "name": "Ramadan Month",
        "trigger": lambda ctx: any(f["festival"] == "Ramadan" for f in ctx.get("upcoming_festivals", [])),
        "urgency": "MEDIUM",
        "category_impacts": {
            "staples": {"multiplier": 1.30, "reason": "Rice and flour demand up for daily iftar."},
            "dairy": {"multiplier": 1.25, "reason": "Milk demand rises for suhoor."},
            "beverages": {"multiplier": 1.40, "reason": "Dates, juices, and beverages for evening break-fast."},
            "spices": {"multiplier": 1.50, "reason": "Heavy evening cooking demand."},
        },
        "action": "Shift inventory prep to accommodate heavy evening demand spikes.",
        "supply_warning": None,
    },
    {
        "id": "eid_5_days",
        "name": "Eid — Final Rush",
        "trigger": lambda ctx: any(f["festival"] == "Eid" and f["days_away"] <= 5 for f in ctx.get("upcoming_festivals", [])),
        "urgency": "CRITICAL",
        "category_impacts": {
            "staples": {"multiplier": 1.80, "reason": "Biryani rice demand peaks massively."},
            "spices": {"multiplier": 1.90, "reason": "Spices for biryani selling out fast."},
            "beverages": {"multiplier": 1.50, "reason": "Soft drinks for entertaining."},
            "dairy": {"multiplier": 1.40, "reason": "Dessert prep ingredients."},
        },
        "action": "Large procurement order needed immediately for Biryani items.",
        "supply_warning": None,
    },
    {
        "id": "christmas_2_weeks",
        "name": "Christmas Season",
        "trigger": lambda ctx: any(f["festival"] == "Christmas" and f["days_away"] <= 14 for f in ctx.get("upcoming_festivals", [])),
        "urgency": "HIGH",
        "category_impacts": {
            "staples": {"multiplier": 1.50, "reason": "Flour and sugar for baking."},
            "dairy": {"multiplier": 1.45, "reason": "Eggs and butter for cakes."},
            "snacks": {"multiplier": 1.40, "reason": "Dry fruits and plum cake ingredients."},
        },
        "action": "Increase bakery inventory massively.",
        "supply_warning": None,
    },
    {
        "id": "vishu_day",
        "name": "Vishu Festival",
        "trigger": lambda ctx: any(f["festival"] == "Vishu" and f["days_away"] <= 5 for f in ctx.get("upcoming_festivals", [])),
        "urgency": "MEDIUM",
        "category_impacts": {
            "staples": {"multiplier": 1.35, "reason": "Rice and coconut oil for feast."},
            "snacks": {"multiplier": 1.30, "reason": "Traditional snacks demand."},
        },
        "action": "Stock up on coconut oil and snacks.",
        "supply_warning": None,
    },
    {
        "id": "diwali_season",
        "name": "Diwali Festival",
        "trigger": lambda ctx: any(f["festival"] == "Diwali" and f["days_away"] <= 7 for f in ctx.get("upcoming_festivals", [])),
        "urgency": "HIGH",
        "category_impacts": {
            "snacks": {"multiplier": 1.80, "reason": "Sweets and dry fruit gift packs moving fast."},
            "beverages": {"multiplier": 1.40, "reason": "Soft drinks for parties."},
            "dairy": {"multiplier": 1.50, "reason": "Ghee for sweet preparation."},
        },
        "action": "Ensure massive stock of sweets and gift packs.",
        "supply_warning": None,
    },

    # 🛑 HARTAL SCENARIOS
    {
        "id": "hartal_3_days",
        "name": "Hartal Announced — 3 Days Before",
        "trigger": lambda ctx: ctx.get("hartal_days_away") == 3,
        "urgency": "HIGH",
        "category_impacts": {
            "staples": {"multiplier": 1.30, "reason": "People begin storing essentials."},
            "dairy": {"multiplier": 1.25, "reason": "Milk and bread stocking starts."},
            "snacks": {"multiplier": 1.20, "reason": "Early snack stocking."},
        },
        "action": "Begin increasing daily orders to prepare for tomorrow's panic buy.",
        "supply_warning": None,
    },
    {
        "id": "hartal_tomorrow",
        "name": "Hartal Tomorrow — Massive Panic Buying",
        "trigger": lambda ctx: ctx.get("hartal_tomorrow") or ctx.get("hartal_days_away") in [1, 2],
        "urgency": "CRITICAL",
        "category_impacts": {
            "dairy": {"multiplier": 2.20, "reason": "Milk and bread demand explodes."},
            "staples": {"multiplier": 1.80, "reason": "Instant noodles and rice moving fast."},
            "snacks": {"multiplier": 1.70, "reason": "Snacks for home stay."},
        },
        "action": "Emergency procurement mode. Order maximum safe limits.",
        "supply_warning": None,
    },
    {
        "id": "hartal_today",
        "name": "Hartal Today",
        "trigger": lambda ctx: ctx.get("hartal_today", False),
        "urgency": "INFO",
        "category_impacts": {
            "_all": {"multiplier": 0.05, "reason": "Store traffic down 95%. Deliveries stopped."},
        },
        "action": "Pause procurement. Delay deliveries until tomorrow.",
        "supply_warning": "No deliveries possible today.",
    },

    # 🌧️ WEATHER SCENARIOS
    {
        "id": "heavy_rain",
        "name": "Heavy Rain",
        "trigger": lambda ctx: ctx.get("weather", {}).get("tomorrow", {}).get("rain_heavy", False),
        "urgency": "MEDIUM",
        "category_impacts": {
            "beverages": {"multiplier": 1.40, "reason": "Tea and coffee demand spikes."},
            "snacks": {"multiplier": 1.30, "reason": "Hot snacks and biscuits."},
            "dairy": {"multiplier": 0.80, "reason": "Ice cream demand falls."},
        },
        "action": "Focus on tea, coffee, and indoor snacks.",
        "supply_warning": None,
    },
    {
        "id": "continuous_rain",
        "name": "Continuous Rain (5+ Days)",
        "trigger": lambda ctx: ctx.get("continuous_rain", False),
        "urgency": "HIGH",
        "category_impacts": {
            "staples": {"multiplier": 1.50, "reason": "Instant food and packaged items favored."},
            "snacks": {"multiplier": 1.30, "reason": "Packaged food storage increases."},
        },
        "action": "Increase instant food stock.",
        "supply_warning": "High risk of delivery delays.",
    },
    {
        "id": "flood_warning",
        "name": "Flood Warning",
        "trigger": lambda ctx: ctx.get("flood_warning", False),
        "urgency": "CRITICAL",
        "category_impacts": {
            "beverages": {"multiplier": 3.00, "reason": "Drinking water panic buying."},
            "staples": {"multiplier": 2.00, "reason": "Packaged food and instant noodles."},
            "cleaning": {"multiplier": 2.00, "reason": "Candles and emergency supplies (mapped)."},
        },
        "action": "Build emergency stock of water and instant food immediately.",
        "supply_warning": "Supplier routes may be cut off soon.",
    },
    {
        "id": "flood_active",
        "name": "Flood Active",
        "trigger": lambda ctx: ctx.get("flood_active", False),
        "urgency": "CRITICAL",
        "category_impacts": {
            "_all": {"multiplier": 0.10, "reason": "Store visits collapsed due to flooding."},
        },
        "action": "Stop normal forecasting. Operate in emergency mode.",
        "supply_warning": "Logistics paralyzed.",
    },

    # 🔥 HEATWAVE SCENARIOS
    {
        "id": "heatwave",
        "name": "Heatwave (>35°C)",
        "trigger": lambda ctx: ctx.get("weather", {}).get("tomorrow", {}).get("temp", 0) > 35.0,
        "urgency": "HIGH",
        "category_impacts": {
            "beverages": {"multiplier": 1.80, "reason": "Soft drinks and water spiking."},
            "dairy": {"multiplier": 1.60, "reason": "Ice cream sales surging."},
            "spices": {"multiplier": 0.90, "reason": "Heavy cooking reduced."},
        },
        "action": "Ensure chillers are full of water and cold drinks.",
        "supply_warning": None,
    },
    {
        "id": "extreme_heat",
        "name": "Extreme Heat (>40°C)",
        "trigger": lambda ctx: ctx.get("weather", {}).get("tomorrow", {}).get("temp", 0) > 40.0,
        "urgency": "CRITICAL",
        "category_impacts": {
            "beverages": {"multiplier": 2.50, "reason": "ORS, electrolytes, and juices in critical demand."},
            "dairy": {"multiplier": 1.80, "reason": "Maximum ice cream demand."},
            "staples": {"multiplier": 0.80, "reason": "People avoiding heavy cooking."},
        },
        "action": "Prioritize electrolyte drinks and bottled water.",
        "supply_warning": None,
    },

    # ❄️ COLD WEATHER
    {
        "id": "cold_weather",
        "name": "Cold Weather",
        "trigger": lambda ctx: ctx.get("weather", {}).get("tomorrow", {}).get("temp", 99) < 20.0,
        "urgency": "MEDIUM",
        "category_impacts": {
            "beverages": {"multiplier": 1.50, "reason": "Tea, coffee, and soup demand rises."},
        },
        "action": "Stock up on hot beverage ingredients.",
        "supply_warning": None,
    },

    # 🏫 SCHOOL SCENARIOS
    {
        "id": "school_reopening",
        "name": "School Reopening",
        "trigger": lambda ctx: ctx.get("school_reopening", False),
        "urgency": "HIGH",
        "category_impacts": {
            "staples": {"multiplier": 1.30, "reason": "Stationery (mapped) and lunchbox items."},
            "snacks": {"multiplier": 1.40, "reason": "Kids snacks and biscuits."},
        },
        "action": "Increase kid-friendly snacks and lunch supplies.",
        "supply_warning": None,
    },
    {
        "id": "exam_season",
        "name": "Exam Season",
        "trigger": lambda ctx: ctx.get("exam_season", False),
        "urgency": "MEDIUM",
        "category_impacts": {
            "beverages": {"multiplier": 1.40, "reason": "Coffee, tea, and energy drinks."},
            "snacks": {"multiplier": 1.20, "reason": "Late-night studying snacks."},
        },
        "action": "Stock energy drinks and coffee.",
        "supply_warning": None,
    },

    # 💰 SALARY CYCLE
    {
        "id": "salary_week_first",
        "name": "First Week of Month (Salary)",
        "trigger": lambda ctx: ctx.get("salary_cycle") == "first_week",
        "urgency": "LOW",
        "category_impacts": {
            "personal_care": {"multiplier": 1.25, "reason": "Premium brands selling faster."},
            "snacks": {"multiplier": 1.15, "reason": "Customers spend more freely."},
        },
        "action": "Push premium brands to front shelves.",
        "supply_warning": None,
    },
    {
        "id": "salary_week_last",
        "name": "Last Week of Month",
        "trigger": lambda ctx: ctx.get("salary_cycle") == "last_week",
        "urgency": "LOW",
        "category_impacts": {
            "staples": {"multiplier": 1.10, "reason": "Customers become price sensitive; budget brands move."},
            "personal_care": {"multiplier": 0.85, "reason": "Premium brands slowdown."},
        },
        "action": "Ensure budget staples are well-stocked.",
        "supply_warning": None,
    },

    # 🏏 SPORTS SCENARIOS
    {
        "id": "ipl_match",
        "name": "IPL Match Day",
        "trigger": lambda ctx: ctx.get("sports_event") == "ipl_match",
        "urgency": "MEDIUM",
        "category_impacts": {
            "snacks": {"multiplier": 1.50, "reason": "Chips and finger foods."},
            "beverages": {"multiplier": 1.40, "reason": "Soft drinks demand."},
        },
        "action": "Ensure snacks and cold drinks are ready for evening.",
        "supply_warning": None,
    },
    {
        "id": "ipl_final",
        "name": "IPL Final / India World Cup",
        "trigger": lambda ctx: ctx.get("sports_event") in ["ipl_final", "world_cup"],
        "urgency": "HIGH",
        "category_impacts": {
            "snacks": {"multiplier": 2.20, "reason": "Massive party product demand."},
            "beverages": {"multiplier": 2.00, "reason": "Cold drinks selling out."},
        },
        "action": "Huge spike in party items. Order maximum chips and drinks.",
        "supply_warning": None,
    },

    # 🚍 LOGISTICS & HARVEST
    {
        "id": "transport_strike_announced",
        "name": "Transport Strike Announced",
        "trigger": lambda ctx: ctx.get("transport_strike_status") == "announced",
        "urgency": "HIGH",
        "category_impacts": {
            "_all": {"multiplier": 1.20, "reason": "Increase safety stock anticipating delays."},
        },
        "action": "Increase safety stock for all essentials immediately.",
        "supply_warning": "Supplier delays imminent.",
    },
    {
        "id": "transport_strike_active",
        "name": "Transport Strike Active",
        "trigger": lambda ctx: ctx.get("transport_strike_status") == "active",
        "urgency": "CRITICAL",
        "category_impacts": {
            "_all": {"multiplier": 0.50, "reason": "Freeze non-essential orders due to no replenishment."},
        },
        "action": "Freeze non-essential orders.",
        "supply_warning": "No replenishment arriving.",
    },
    {
        "id": "fuel_hike",
        "name": "Fuel Price Hike",
        "trigger": lambda ctx: ctx.get("fuel_price_hike", False),
        "urgency": "MEDIUM",
        "category_impacts": {
            "_all": {"multiplier": 1.10, "reason": "Increase reorder quantity to reduce delivery frequency."},
        },
        "action": "Order in bulk to save on rising logistics costs.",
        "supply_warning": "Logistics costs increasing.",
    },
    {
        "id": "coconut_harvest",
        "name": "Coconut Harvest Season",
        "trigger": lambda ctx: ctx.get("harvest_season") == "coconut",
        "urgency": "INFO",
        "category_impacts": {
            "staples": {"multiplier": 1.30, "reason": "Coconut oil prices down, increase procurement."},
        },
        "action": "Increase procurement of coconut oil while prices are low.",
        "supply_warning": None,
    },

    # 👰 EVENTS & LIFE
    {
        "id": "wedding_season",
        "name": "Wedding Season",
        "trigger": lambda ctx: ctx.get("wedding_season", False),
        "urgency": "HIGH",
        "category_impacts": {
            "staples": {"multiplier": 1.80, "reason": "Bulk rice and ghee purchases."},
            "spices": {"multiplier": 1.70, "reason": "Bulk spices for catering."},
            "beverages": {"multiplier": 1.50, "reason": "Soft drinks for functions."},
        },
        "action": "Ensure bulk items are fully stocked for catering orders.",
        "supply_warning": None,
    },
    {
        "id": "tourist_season",
        "name": "Tourist Season",
        "trigger": lambda ctx: ctx.get("tourist_season", False),
        "urgency": "MEDIUM",
        "category_impacts": {
            "beverages": {"multiplier": 1.50, "reason": "Water and juice demand from travelers."},
            "snacks": {"multiplier": 1.40, "reason": "On-the-go snacks."},
        },
        "action": "Stock up on travel-friendly beverages and snacks.",
        "supply_warning": None,
    },
    
    # 📉 ECONOMICS & TRENDS
    {
        "id": "competitor_discount",
        "name": "Competitor Discount Active",
        "trigger": lambda ctx: ctx.get("competitor_discount", False),
        "urgency": "HIGH",
        "category_impacts": {
            "_all": {"multiplier": 0.80, "reason": "Sales dropping to competitor (e.g. Lulu 20% off)."},
        },
        "action": "Suggest counter-promotions immediately.",
        "supply_warning": None,
    },
    {
        "id": "viral_product",
        "name": "Viral Product Trend",
        "trigger": lambda ctx: ctx.get("viral_trend", False),
        "urgency": "CRITICAL",
        "category_impacts": {
            "snacks": {"multiplier": 1.50, "reason": "Demand increase due to social media trend."},
        },
        "action": "Procurement mode! Secure stock before suppliers run out.",
        "supply_warning": "High risk of regional stockouts.",
    },
    {
        "id": "weekend_boost",
        "name": "Weekend Boost",
        "trigger": lambda ctx: ctx.get("weekday") in ["Saturday", "Sunday"],
        "urgency": "LOW",
        "category_impacts": {
            "_all": {"multiplier": 1.10, "reason": "Weekend family shopping traffic."},
        },
        "action": "Ensure shelves are full.",
        "supply_warning": None,
    }
]

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
            pass
    return active

def get_product_multiplier(
    category: str,
    active_scenarios: list[dict],
) -> tuple[float, list[str]]:
    combined_multiplier: float = 1.0
    reasons: list[str] = []

    for scenario in active_scenarios:
        impacts: dict = scenario["category_impacts"]

        cat_impact = impacts.get(category)
        all_impact = impacts.get("_all")

        if cat_impact and all_impact:
            effective_multiplier = cat_impact["multiplier"] * all_impact["multiplier"]
            reason_text = (
                f"{cat_impact['reason']} (×{cat_impact['multiplier']}) — "
                f"{all_impact['reason']} (×{all_impact['multiplier']})"
            )
        elif cat_impact:
            effective_multiplier = cat_impact["multiplier"]
            reason_text = f"{cat_impact['reason']} (×{cat_impact['multiplier']})"
        elif all_impact:
            effective_multiplier = all_impact["multiplier"]
            reason_text = f"{all_impact['reason']} (×{all_impact['multiplier']})"
        else:
            continue

        combined_multiplier *= effective_multiplier
        reasons.append(f"[{scenario['name']}] {reason_text}")

    return round(combined_multiplier, 3), reasons
