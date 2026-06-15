import os
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional, Union
import json
from datetime import datetime

app = FastAPI(title="RetailOS AI Forecast Service")

class ForecastInput(BaseModel):
    sales_history: Union[float, List[float]]  # Can be a single recent sales value or list of past sales
    festival_multiplier: float
    weather_multiplier: float
    hartal_multiplier: float
    trend_multiplier: float
    trend_score: Optional[int] = 78

@app.post("/forecast")
def generate_forecast(data: ForecastInput):
    """
    Implements a statistical demand forecast model (simulating Facebook Prophet)
    by combining recent sales signals with weather, festival, trends, and hartal multipliers.
    """
    if isinstance(data.sales_history, list):
        recent_sales = data.sales_history[-1] if data.sales_history else 140.0
    else:
        recent_sales = float(data.sales_history)
        
    scaled_forecast = recent_sales * data.festival_multiplier * data.weather_multiplier * data.hartal_multiplier * data.trend_multiplier * 6.70
    forecast_value = int(round(scaled_forecast, -1))
    
    trend_score = data.trend_score if data.trend_score is not None else 78
    confidence_value = int(round(min(98, 80 + trend_score * 0.15)))
    
    return {
        "forecast": forecast_value,
        "confidence": confidence_value,
        "method": "Facebook Prophet Simulator"
    }

@app.post("/run-daily-brief")
def run_daily_brief():
    """
    Triggered daily by n8n or cron.
    Automatically queries the warehouse database, scans live external indicators,
    runs the LangGraph state machine, and archives today's Morning Brief.
    """
    # 1. Query mock PostgreSQL database for inventory and sales
    db_path = r"d:\Projects\Retail OS\database.json"
    if not os.path.exists(db_path):
        db = {"inventory": 420, "sales": 140}
    else:
        with open(db_path, "r") as f:
            db = json.load(f)
            
    inventory = db.get("inventory", 420)
    sales = db.get("sales", 140)
    
    # 2. Determine current festival calendar season (e.g. check current date or default to Onam)
    festival = "Onam"
    
    # 3. Setup initial state for automatic execution
    initial_state = {
        "inventory": inventory,
        "sales": sales,
        "festival": festival,
        "hartal": True,  # Will be evaluated by live news scan
        "weather": "Rain",  # Will be evaluated by live weather scan
        "temperature": 0.0,
        "trend_score": 0,
        "commodity_risk": "",
        "forecast": 0,
        "confidence": 0,
        "inventory_gap": 0,
        "inventory_status": "",
        "procurement_qty": 0,
        "supplier": "",
        "supplier_score": 0,
        "critic_decision": "",
        
        # Done flags
        "context_done": False,
        "forecast_done": False,
        "inventory_done": False,
        "procurement_done": False,
        "supplier_done": False,
        
        # Metadata
        "executive_recommendation": None,
        "history": [],
        "api_simulation": True,  # Uses simulated LLM for quota safety during background triggers
        "gemini_api_key": os.getenv("GEMINI_API_KEY"),
        "weather_multiplier": None,
        "festival_multiplier": None,
        "hartal_multiplier": None,
        "trend_multiplier": None
    }
    
    # Import graph locally to prevent circular import startup warnings
    from graph import create_workflow_graph
    
    # 4. Invoke multi-agent LangGraph workflow
    workflow = create_workflow_graph()
    final_state = workflow.invoke(initial_state)
    
    # 5. Archive report brief to local server directories
    brief = final_state.get("executive_recommendation", "")
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    briefs_dir = r"d:\Projects\Retail OS\briefs"
    os.makedirs(briefs_dir, exist_ok=True)
    brief_file_path = os.path.join(briefs_dir, f"morning_brief_{date_str}.txt")
    
    with open(brief_file_path, "w") as f:
        f.write(brief)
        
    return {
        "status": "success",
        "date": date_str,
        "archived_brief": brief_file_path,
        "data": {
            "forecast": final_state.get("forecast"),
            "inventory_gap": final_state.get("inventory_gap"),
            "procurement_qty": final_state.get("procurement_qty"),
            "supplier": final_state.get("supplier"),
            "critic_decision": final_state.get("critic_decision")
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
