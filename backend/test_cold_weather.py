import sys
import os

# Ensure we can import from backend modules
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from scenario_engine.rules import evaluate_scenarios

# Mock Context representing 15 Celsius tomorrow
mock_context = {
    "weather": {
        "tomorrow": {
            "temp": 15.0,
            "rain_heavy": False
        }
    },
    "upcoming_festivals": [],
    "weekday": "Monday",
    "hartal_tomorrow": False,
    "hartal_today": False
}

print("\n--- RUNNING SCENARIO ENGINE WITH 15°C WEATHER ---")
active_scenarios = evaluate_scenarios(mock_context)

for scenario in active_scenarios:
    print(f"\n[TRIGGERED] {scenario['name']} (Urgency: {scenario['urgency']})")
    print(f"Action Required: {scenario['action']}")
    print("Impacts on Store:")
    for category, impact in scenario["category_impacts"].items():
        print(f"  - {category.upper()}: Multiply demand by {impact['multiplier']}x ({impact['reason']})")

print("\n-------------------------------------------------")
