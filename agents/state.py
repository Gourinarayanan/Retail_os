from typing import TypedDict, List, Dict, Any, Optional

class AgentState(TypedDict):
    # Standard Shared State parameters matching Version 1.0 Blueprint:
    inventory: int
    sales: int
    festival: str
    hartal: bool
    weather: str
    temperature: float
    trend_score: int
    commodity_risk: str
    
    forecast: int
    confidence: int  # percentage (e.g. 92)
    
    inventory_gap: int
    inventory_status: str  # Critical, Warning, Safe
    
    procurement_qty: int
    
    supplier: str
    supplier_score: int
    
    critic_decision: str  # APPROVED, REPLAN
    
    # Process completion flags for strict routing sequence:
    context_done: bool
    forecast_done: bool
    inventory_done: bool
    procurement_done: bool
    supplier_done: bool
    
    # Metadata for execution and simulation
    executive_recommendation: Optional[str]  # The Morning Brief report
    history: List[Dict[str, Any]]
    api_simulation: bool
    gemini_api_key: Optional[str]
    weather_multiplier: Optional[float]
    festival_multiplier: Optional[float]
    hartal_multiplier: Optional[float]
    trend_multiplier: Optional[float]
