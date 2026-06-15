from google import genai
from agents.state import AgentState
import requests
import json
import os

def forecast_agent(state: AgentState) -> dict:
    """
    Forecast Agent: Generates demand forecasts.
    Inputs: sales_history, festival_multiplier, weather_multiplier, hartal_multiplier, trend_multiplier.
    Sends HTTP POST request to FastAPI endpoint /forecast.
    Updates state and sets forecast_done = True.
    """
    print("--- FORECAST AGENT ---")
    sales = state.get("sales", 140)
    fest_mult = state.get("festival_multiplier", 1.42)
    weather_mult = state.get("weather_multiplier", 1.10)
    hartal_mult = state.get("hartal_multiplier", 1.65)
    trend_mult = state.get("trend_multiplier", 1.20)
    trend_score = state.get("trend_score", 78)
    
    # 1. Prepare request payload for FastAPI local forecast microservice
    payload = {
        "sales_history": float(sales),
        "festival_multiplier": float(fest_mult),
        "weather_multiplier": float(weather_mult),
        "hartal_multiplier": float(hartal_mult),
        "trend_multiplier": float(trend_mult),
        "trend_score": int(trend_score)
    }
    
    forecast_value = 2900
    confidence_value = 92
    
    # Call local microservice endpoint
    try:
        url = "http://127.0.0.1:8000/forecast"
        response = requests.post(url, json=payload, timeout=5)
        if response.status_code == 200:
            data = response.json()
            forecast_value = data.get("forecast", forecast_value)
            confidence_value = data.get("confidence", confidence_value)
            print(f"Forecast service returned: Forecast={forecast_value}, Confidence={confidence_value}")
    except Exception as e:
        print(f"Error calling local forecast service: {e}. Falling back to default calculation.")
        # Re-verify local math logic
        scaled = sales * fest_mult * weather_mult * hartal_mult * trend_mult * 6.70
        forecast_value = int(round(scaled, -1))
        confidence_value = int(min(98, 80 + trend_score * 0.15))
        
    api_key = state.get("gemini_api_key") or os.getenv("GEMINI_API_KEY")
    use_simulation = state.get("api_simulation", True) or not api_key

    if not use_simulation and api_key:
        try:
            client = genai.Client(api_key=api_key)
            prompt = f"""
            You are the Forecast Agent of RetailOS.
            Our Facebook Prophet endpoint returned: Forecast={forecast_value}, Confidence={confidence_value}%.
            Review the sales history of {sales} units and multipliers (Festival: {fest_mult}, Weather: {weather_mult}, Hartal: {hartal_mult}, Trends: {trend_mult}).
            
            Confirm the values and format your output strictly as a JSON object with these keys:
            - "forecast": {forecast_value}
            - "confidence": {confidence_value}
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
                "forecast": int(data.get("forecast", forecast_value)),
                "confidence": int(data.get("confidence", confidence_value)),
                "forecast_done": True,
                "history": state.get("history", []) + [{"agent": "ForecastAgent", "output": data}]
            }
        except Exception as e:
            print(f"Gemini API error in Forecast Agent: {e}. Falling back to simulation.")
            
    output_data = {
        "forecast": forecast_value,
        "confidence": confidence_value
    }
    
    return {
        "forecast": output_data["forecast"],
        "confidence": output_data["confidence"],
        "forecast_done": True,
        "history": state.get("history", []) + [{"agent": "ForecastAgent", "output": output_data}]
    }
