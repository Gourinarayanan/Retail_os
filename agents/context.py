from google import genai
from services.weather import get_weather_data
from services.news import get_news_data
from services.trends import get_trends_data
from services.commodity import get_commodity_prices
from rag.vector_store import festival_rag, hartal_rag
from agents.state import AgentState
import json
import os

def context_agent(state: AgentState) -> dict:
    """
    Context Agent: Understands the external business environment.
    Queries Weather, News, Google Trends, Festival RAG, and Hartal RAG.
    Updates state and sets context_done = True.
    """
    print("--- CONTEXT AGENT ---")
    festival_input = state.get("festival", "Onam")
    weather_input = state.get("weather", "Rain")
    hartal_input = state.get("hartal", True)
    
    # 1. Weather API Integration
    weather_results = get_weather_data(weather_input)
    temp = weather_results.get("temperature", 31.0)
    weather_mult = weather_results.get("weather_multiplier", 1.10)
    
    # 2. News API Integration
    news_results = get_news_data(news_query="Kerala Hartal", hartal_input=hartal_input)
    hartal_active = news_results.get("hartal", True)
    
    # 3. Google Trends Integration
    trends_results = get_trends_data(festival=festival_input)
    trend_score = trends_results.get("trend_score", 78)
    trend_mult = trends_results.get("trend_multiplier", 1.20)
    
    # 4. Festival RAG Retrieval
    fest_matches = festival_rag.search(festival_input, top_k=1)
    festival_multiplier = 1.00
    if fest_matches:
        festival_multiplier = fest_matches[0].get("metadata", {}).get("multiplier", 1.00)
        
    # 5. Hartal RAG Retrieval
    # If hartal is tomorrow/active, retrieve "Before Hartal" multiplier
    hartal_query = "Before Hartal" if hartal_active else "During Hartal"
    hartal_matches = hartal_rag.search(hartal_query, top_k=1)
    hartal_multiplier = 1.00
    if hartal_matches:
        hartal_multiplier = hartal_matches[0].get("metadata", {}).get("multiplier", 1.00)
        
    # 6. Commodity Prices Risk Integration
    commodity_data = get_commodity_prices()
    commodity_risk = commodity_data.get("commodity_risk", "HIGH")
    
    # Dynamic context dict to output
    output_data = {
        "festival": festival_input,
        "weather": weather_results.get("weather", weather_input),
        "temperature": temp,
        "hartal": hartal_active,
        "festival_multiplier": festival_multiplier,
        "hartal_multiplier": hartal_multiplier,
        "trend_score": trend_score,
        "trend_multiplier": trend_mult,
        "weather_multiplier": weather_mult,
        "commodity_risk": commodity_risk
    }
    
    api_key = state.get("gemini_api_key") or os.getenv("GEMINI_API_KEY")
    use_simulation = state.get("api_simulation", True) or not api_key

    if not use_simulation and api_key:
        try:
            client = genai.Client(api_key=api_key)
            prompt = f"""
            You are the Context Agent of RetailOS.
            Process these raw metrics:
            - Weather Results: {weather_results}
            - News Results: {news_results}
            - Trends Results: {trends_results}
            - Festival RAG multiplier for {festival_input}: {festival_multiplier}
            - Hartal RAG multiplier: {hartal_multiplier}
            
            Format your decision strictly as a JSON object with these keys:
            - "festival": "{festival_input}"
            - "weather": "{weather_results.get('weather')}"
            - "temperature": {temp}
            - "hartal": {str(hartal_active).lower()}
            - "festival_multiplier": {festival_multiplier}
            - "hartal_multiplier": {hartal_multiplier}
            - "trend_score": {trend_score}
            - "trend_multiplier": {trend_mult}
            - "weather_multiplier": {weather_mult}
            - "commodity_risk": "{commodity_risk}"
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
            data["context_done"] = True
            data["history"] = state.get("history", []) + [{"agent": "ContextAgent", "output": data}]
            return data
        except Exception as e:
            print(f"Gemini API error in Context Agent: {e}. Falling back to simulation.")
            
    # Simulation fallback
    return {
        "festival": output_data["festival"],
        "weather": output_data["weather"],
        "temperature": output_data["temperature"],
        "hartal": output_data["hartal"],
        "festival_multiplier": output_data["festival_multiplier"],
        "hartal_multiplier": output_data["hartal_multiplier"],
        "trend_score": output_data["trend_score"],
        "trend_multiplier": output_data["trend_multiplier"],
        "weather_multiplier": output_data["weather_multiplier"],
        "commodity_risk": output_data["commodity_risk"],
        "context_done": True,
        "history": state.get("history", []) + [{"agent": "ContextAgent", "output": output_data}]
    }
