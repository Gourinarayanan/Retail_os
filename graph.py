from langgraph.graph import StateGraph, END
from agents.state import AgentState
from agents.ceo import ceo_agent, ceo_router
from agents.context import context_agent
from agents.forecast import forecast_agent
from agents.inventory import inventory_agent
from agents.procurement import procurement_agent
from agents.supplier import supplier_agent
from agents.critic import critic_agent
from agents.executive import executive_agent

def create_workflow_graph():
    """
    Creates and compiles the StateGraph for the RetailOS AI multi-agent system.
    """
    # Initialize the StateGraph with our custom shared state schema
    workflow = StateGraph(AgentState)
    
    # 1. Add all agent nodes to the graph
    workflow.add_node("ceo", ceo_agent)
    workflow.add_node("context", context_agent)
    workflow.add_node("forecast", forecast_agent)
    workflow.add_node("inventory", inventory_agent)
    workflow.add_node("procurement", procurement_agent)
    workflow.add_node("supplier", supplier_agent)
    workflow.add_node("critic", critic_agent)
    workflow.add_node("executive", executive_agent)
    
    # 2. Set the entry point of the agent graph
    workflow.set_entry_point("ceo")
    
    # 3. Add edges from agent nodes back to the CEO Supervisor
    workflow.add_edge("context", "ceo")
    workflow.add_edge("forecast", "ceo")
    workflow.add_edge("inventory", "ceo")
    workflow.add_edge("procurement", "ceo")
    workflow.add_edge("supplier", "ceo")
    workflow.add_edge("critic", "ceo")
    workflow.add_edge("executive", "ceo")
    
    # 4. Configure conditional edges for the CEO Supervisor
    # The CEO reads the current state and routes to the appropriate node dynamically.
    workflow.add_conditional_edges(
        "ceo",
        ceo_router,
        {
            "context": "context",
            "forecast": "forecast",
            "inventory": "inventory",
            "procurement": "procurement",
            "supplier": "supplier",
            "critic": "critic",
            "executive": "executive",
            "forecast_replan": "forecast",  # Critic REPLAN flow triggers Forecast Agent again
            "__end__": END
        }
    )
    
    # Compile the graph
    return workflow.compile()
