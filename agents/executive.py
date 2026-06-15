from google import genai
from agents.state import AgentState
import os

def executive_agent(state: AgentState) -> dict:
    """
    Executive Decision Agent: Generates the RetailOS Executive Morning Brief.
    Combines outputs from Context, Forecast, Inventory, Procurement, Supplier, and Critic.
    """
    print("--- EXECUTIVE DECISION AGENT ---")
    festival = state.get("festival", "Onam")
    weather = state.get("weather", "Rain")
    hartal_status = "Tomorrow" if state.get("hartal", True) else "None"
    
    forecast = state.get("forecast", 2900)
    confidence = state.get("confidence", 92)
    inventory = state.get("inventory", 420)
    inventory_gap = state.get("inventory_gap", 2480)
    procurement_qty = state.get("procurement_qty", 2480)
    supplier = state.get("supplier", "Supplier C").replace("_", " ")
    
    risk_level = "Medium"
    
    festival_clause = f"due to the upcoming {festival} festival" if festival != "None" else "due to seasonal demand"
    weather_clause = f", {weather.lower()} weather conditions" if weather != "Normal" else ""
    hartal_clause = ", and pre-hartal panic buying" if state.get("hartal", True) else ""
    
    rec_text = (
        f"Demand is expected to rise {festival_clause}{weather_clause}{hartal_clause}.\n"
        "Current inventory is insufficient to cover this period.\n"
        "Immediate procurement is recommended.\n"
        f"{supplier} has been selected due to superior reliability-adjusted cost performance."
    )
    
    # Construct exact blueprint layout:
    # RetailOS Executive Morning Brief
    #
    # Festival:
    # Onam
    #
    # Weather:
    # Rain
    #
    # Hartal:
    # Tomorrow
    #
    # Forecast:
    # 2900 Units
    #
    # Confidence:
    # 92%
    #
    # Inventory:
    # 420 Units
    #
    # Inventory Gap:
    # 2480 Units
    #
    # Recommended Procurement:
    # 2480 Units
    #
    # Selected Supplier:
    # Supplier C
    #
    # Business Risk:
    # Medium
    #
    # Executive Recommendation:
    # Demand is expected to surge due to Onam, rainfall conditions, and pre-hartal purchasing behavior.
    # Current inventory is insufficient.
    # Immediate procurement is recommended.
    # Supplier C has been selected due to superior reliability-adjusted cost performance.
    
    report_template = (
        "RetailOS Executive Morning Brief\n\n"
        f"Festival:\n{festival}\n\n"
        f"Weather:\n{weather}\n\n"
        f"Hartal:\n{hartal_status}\n\n"
        f"Forecast:\n{forecast} Units\n\n"
        f"Confidence:\n{confidence}%\n\n"
        f"Inventory:\n{inventory} Units\n\n"
        f"Inventory Gap:\n{inventory_gap} Units\n\n"
        f"Recommended Procurement:\n{procurement_qty} Units\n\n"
        f"Selected Supplier:\n{supplier}\n\n"
        f"Business Risk:\n{risk_level}\n\n"
        f"Executive Recommendation:\n{rec_text}"
    )

    api_key = state.get("gemini_api_key") or os.getenv("GEMINI_API_KEY")
    use_simulation = state.get("api_simulation", True) or not api_key

    if not use_simulation and api_key:
        try:
            client = genai.Client(api_key=api_key)
            prompt = f"""
            You are the Executive Decision Agent of RetailOS.
            Compile the following data into the "RetailOS Executive Morning Brief":
            - Festival: {festival}
            - Weather: {weather}
            - Hartal Status: {hartal_status}
            - Forecast: {forecast} Units
            - Confidence: {confidence}%
            - Inventory: {inventory} Units
            - Inventory Gap: {inventory_gap} Units
            - Procurement Qty: {procurement_qty} Units
            - Selected Supplier: {supplier}
            - Business Risk: {risk_level}
            
            Follow this exact layout structure:
            
            RetailOS Executive Morning Brief
            
            Festival:
            [Festival]
            
            Weather:
            [Weather]
            
            Hartal:
            [Hartal]
            
            Forecast:
            [Forecast Value] Units
            
            Confidence:
            [Confidence Value]%
            
            Inventory:
            [Inventory Value] Units
            
            Inventory Gap:
            [Inventory Gap Value] Units
            
            Recommended Procurement:
            [Procurement Value] Units
            
            Selected Supplier:
            [Supplier Name]
            
            Business Risk:
            [Risk Level]
            
            Executive Recommendation:
            [Recommendation text details, including Onam surge, weather, and supplier reliability explanation]
            """
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
            )
            report_text = response.text.strip()
            return {
                "executive_recommendation": report_text,
                "history": state.get("history", []) + [{"agent": "ExecutiveAgent", "output": {"recommendation": report_text}}]
            }
        except Exception as e:
            print(f"Gemini API error in Executive Agent: {e}. Falling back to simulation.")
            
    return {
        "executive_recommendation": report_template,
        "history": state.get("history", []) + [{"agent": "ExecutiveAgent", "output": {"recommendation": report_template}}]
    }
