from agents.state import AgentState

def ceo_agent(state: AgentState) -> dict:
    """
    CEO Agent Supervisor. Performs supervisor orchestration logging.
    CEO does not perform business analysis; it only routes tasks.
    """
    print("--- CEO SUPERVISOR AGENT ---")
    history = state.get("history", [])
    history.append({"agent": "CEO_Supervisor", "output": {"decision": "Evaluating execution flags for routing..."}})
    return {"history": history}

def ceo_router(state: AgentState) -> str:
    """
    Supervisor routing logic:
    
    IF context_done == false -> Context Agent
    ELSE IF forecast_done == false -> Forecast Agent
    ELSE IF inventory_done == false -> Inventory Agent
    ELSE IF procurement_done == false -> Procurement Agent
    ELSE IF supplier_done == false -> Supplier Intelligence Agent
    ELSE -> Critic Agent
    
    If Critic Agent returns APPROVED -> Executive Decision Agent
    If Critic Agent returns REPLAN -> Route back to Forecast Agent (resets done flag)
    """
    context_done = state.get("context_done", False)
    forecast_done = state.get("forecast_done", False)
    inventory_done = state.get("inventory_done", False)
    procurement_done = state.get("procurement_done", False)
    supplier_done = state.get("supplier_done", False)
    
    critic_decision = state.get("critic_decision")
    executive_rec = state.get("executive_recommendation")
    
    print(f"CEO evaluating flags: context={context_done}, forecast={forecast_done}, inventory={inventory_done}, procurement={procurement_done}, supplier={supplier_done}, critic={critic_decision}")
    
    if not context_done:
        print("CEO Decision -> Route to: CONTEXT AGENT")
        return "context"
        
    if not forecast_done:
        print("CEO Decision -> Route to: FORECAST AGENT")
        return "forecast"
        
    if not inventory_done:
        print("CEO Decision -> Route to: INVENTORY AGENT")
        return "inventory"
        
    if not procurement_done:
        print("CEO Decision -> Route to: PROCUREMENT AGENT")
        return "procurement"
        
    if not supplier_done:
        print("CEO Decision -> Route to: SUPPLIER INTELLIGENCE AGENT")
        return "supplier"
        
    # All analysis agents completed -> run Critic Agent
    if not critic_decision:
        print("CEO Decision -> Route to: CRITIC AGENT")
        return "critic"
        
    if critic_decision == "REPLAN":
        # Loop limit logic to prevent infinite cycling
        replan_count = sum(1 for h in state.get("history", []) if h.get("agent") == "CriticAgent" and h.get("output", {}).get("critic_decision") == "REPLAN")
        if replan_count <= 1:
            print("CEO Decision (Critic REPLAN) -> Routing back to: FORECAST AGENT")
            return "forecast_replan"
            
        print("CEO Decision (Loop Limit Reached) -> Force Proceed to: EXECUTIVE AGENT")
        return "executive"
        
    if critic_decision == "APPROVED":
        if executive_rec is None:
            print("CEO Decision (Critic APPROVED) -> Route to: EXECUTIVE DECISION AGENT")
            return "executive"
            
    print("CEO Decision -> END workflow.")
    return "__end__"
