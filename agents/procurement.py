from google import genai
from services.commodity import get_commodity_prices
from agents.state import AgentState
import json
import os

def procurement_agent(state: AgentState) -> dict:
    """
    Procurement Agent: Determine required procurement.
    Formulas:
        required_stock = forecast + (forecast * 0.20)
        procurement_qty = required_stock - inventory
        
    Timing Optimization:
        If commodity_risk is HIGH, we optimize procurement timing by purchasing 
        only the immediate inventory gap (skipping safety stock) to avoid buying at peak commodity prices.
        Hence, procurement_qty = inventory_gap.
    Updates state and sets procurement_done = True.
    """
    print("--- PROCUREMENT AGENT ---")
    inventory = state.get("inventory", 420)
    forecast = state.get("forecast", 2900)
    inventory_gap = state.get("inventory_gap", 2480)
    commodity_risk = state.get("commodity_risk", "HIGH")
    
    # 1. Standard safety stock calculation
    safety_stock = int(forecast * 0.20)
    required_stock = forecast + safety_stock
    
    # 2. Timing Optimization: If commodity risk is HIGH, bypass safety stock to avoid price peak
    if commodity_risk == "HIGH":
        print("Commodity Risk is HIGH. Optimizing timing: skipping safety stock to avoid peak prices.")
        procurement_qty = max(0, inventory_gap)
    else:
        procurement_qty = max(0, required_stock - inventory)
        
    urgency = "HIGH" if commodity_risk == "HIGH" or inventory_gap > 1000 else "MEDIUM"
    
    api_key = state.get("gemini_api_key") or os.getenv("GEMINI_API_KEY")
    use_simulation = state.get("api_simulation", True) or not api_key

    if not use_simulation and api_key:
        try:
            client = genai.Client(api_key=api_key)
            prompt = f"""
            You are the Procurement Agent of RetailOS.
            Inputs:
            - Forecast: {forecast}
            - Current Stock: {inventory}
            - Inventory Gap: {inventory_gap}
            - Commodity Risk: {commodity_risk}
            
            Decide the procurement quantity (target: {procurement_qty} due to timing optimization) and urgency ("HIGH" or "MEDIUM").
            Format your output strictly as a JSON object with these keys:
            - "procurement_qty": {procurement_qty}
            - "urgency": "{urgency}"
            """
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
            )
            text_resp = response.text.strip()
            if "```json" in text_resp:
                text_resp = text_resp.split("```json")[1].split("```")[0].strip()
            elif "```" in text_resp:
                text_resp = text_resp.split("```")[1].split("```")[0].strip()
                
            data = json.loads(text_resp)
            return {
                "procurement_qty": int(data.get("procurement_qty", procurement_qty)),
                "procurement_done": True,
                "history": state.get("history", []) + [{"agent": "ProcurementAgent", "output": data}]
            }
        except Exception as e:
            print(f"Gemini API error in Procurement Agent: {e}. Falling back to simulation.")
            
    output_data = {
        "procurement_qty": procurement_qty,
        "urgency": urgency
    }
    
    return {
        "procurement_qty": output_data["procurement_qty"],
        "procurement_done": True,
        "history": state.get("history", []) + [{"agent": "ProcurementAgent", "output": output_data}]
    }
