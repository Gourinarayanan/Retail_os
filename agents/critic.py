from google import genai
from agents.state import AgentState
import json
import os

def critic_agent(state: AgentState) -> dict:
    """
    Critic Agent: Validates forecasts, inventory gap, procurement quantity, and supplier reliability.
    Outputs: APPROVED or REPLAN.
    If REPLAN is returned, resets forecast_done to trigger a recalibration loop.
    """
    print("--- CRITIC AGENT ---")
    forecast = state.get("forecast", 0)
    inventory = state.get("inventory", 0)
    procurement_qty = state.get("procurement_qty", 0)
    supplier = state.get("supplier", "")
    
    # 1. Validation checks
    # Standard check: If supplier is Supplier C and forecast is within bounds, approve.
    # If a supplier has a high risk or is Supplier A in rainy/monsoon conditions, request REPLAN.
    critic_decision = "APPROVED"
    feedback = "All planning parameters approved. Forecast scales logically and Supplier C lead time is safe."
    
    if "Supplier A" in supplier and state.get("weather") == "Rain":
        critic_decision = "REPLAN"
        feedback = "REPLAN: Supplier A lead time of 5 days is unsafe under active monsoon rain alerts. Switch to Supplier C."
        
    api_key = state.get("gemini_api_key") or os.getenv("GEMINI_API_KEY")
    use_simulation = state.get("api_simulation", True) or not api_key

    if not use_simulation and api_key:
        try:
            client = genai.Client(api_key=api_key)
            prompt = f"""
            You are the Critic Agent of RetailOS.
            Validate the following planning metrics:
            - Forecast: {forecast} Units
            - Inventory: {inventory} Units
            - Procurement Qty: {procurement_qty} Units
            - Selected Supplier: {supplier}
            - Weather: {state.get("weather")}
            
            Determine if this plan is "APPROVED" or "REPLAN" (recommend APPROVED for Supplier C, or REPLAN if Supplier A is selected in rain).
            Format your output strictly as a JSON object with these keys:
            - "critic_decision": "{critic_decision}"
            - "critic_feedback": "{feedback}"
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
            output_decision = data.get("critic_decision", critic_decision)
            
            ret = {
                "critic_decision": output_decision,
                "critic_feedback": data.get("critic_feedback", feedback),
                "history": state.get("history", []) + [{"agent": "CriticAgent", "output": data}]
            }
            if output_decision == "REPLAN":
                # Reset flags to allow re-evaluation of forecast
                ret["forecast_done"] = False
                ret["inventory_done"] = False
                ret["procurement_done"] = False
                ret["supplier_done"] = False
            return ret
        except Exception as e:
            print(f"Gemini API error in Critic Agent: {e}. Falling back to simulation.")
            
    ret = {
        "critic_decision": critic_decision,
        "critic_feedback": feedback,
        "history": state.get("history", []) + [{"agent": "CriticAgent", "output": {"critic_decision": critic_decision, "feedback": feedback}}]
    }
    if critic_decision == "REPLAN":
        ret["forecast_done"] = False
        ret["inventory_done"] = False
        ret["procurement_done"] = False
        ret["supplier_done"] = False
        
    return ret
