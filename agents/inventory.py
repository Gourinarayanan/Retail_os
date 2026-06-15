from google import genai
from agents.state import AgentState
import json
import os

def inventory_agent(state: AgentState) -> dict:
    """
    Inventory Agent: Analyzes inventory health.
    Formulas:
        inventory_gap = forecast - inventory
        days_of_inventory = inventory / (forecast / 15)
        Critical: < 3 days of inventory
        Warning: 3-7 days of inventory
        Safe: > 7 days of inventory
    Updates state and sets inventory_done = True.
    """
    print("--- INVENTORY AGENT ---")
    inventory = state.get("inventory", 420)
    forecast = state.get("forecast", 2900)
    
    # Calculate gap
    inventory_gap = forecast - inventory
    
    # Calculate days of inventory (15-day scaling horizon)
    daily_demand = forecast / 15.0 if forecast > 0 else 1.0
    days_of_inventory = inventory / daily_demand
    
    # Classify status
    if days_of_inventory < 3.0:
        inventory_status = "CRITICAL"
    elif days_of_inventory <= 7.0:
        inventory_status = "WARNING"
    else:
        inventory_status = "SAFE"
        
    api_key = state.get("gemini_api_key") or os.getenv("GEMINI_API_KEY")
    use_simulation = state.get("api_simulation", True) or not api_key

    if not use_simulation and api_key:
        try:
            client = genai.Client(api_key=api_key)
            prompt = f"""
            You are the Inventory Agent of RetailOS.
            Inputs:
            - Current Stock: {inventory}
            - Forecast: {forecast}
            - Calculated Gap: {inventory_gap}
            - Days of Inventory: {days_of_inventory:.2f} days
            
            Confirm the inventory gap and status ("CRITICAL" if days < 3, "WARNING" if 3-7, "SAFE" if > 7).
            Format your output strictly as a JSON object with these keys:
            - "inventory_gap": {inventory_gap}
            - "inventory_status": "{inventory_status}"
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
                "inventory_gap": int(data.get("inventory_gap", inventory_gap)),
                "inventory_status": data.get("inventory_status", inventory_status),
                "inventory_done": True,
                "history": state.get("history", []) + [{"agent": "InventoryAgent", "output": data}]
            }
        except Exception as e:
            print(f"Gemini API error in Inventory Agent: {e}. Falling back to simulation.")
            
    output_data = {
        "inventory_gap": inventory_gap,
        "inventory_status": inventory_status
    }
    
    return {
        "inventory_gap": output_data["inventory_gap"],
        "inventory_status": output_data["inventory_status"],
        "inventory_done": True,
        "history": state.get("history", []) + [{"agent": "InventoryAgent", "output": output_data}]
    }
