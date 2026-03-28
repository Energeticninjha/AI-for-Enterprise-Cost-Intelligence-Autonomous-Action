from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from agents.state import GraphState
from agents.intake_agent import intake_node
from agents.sourcing_agent import sourcing_node
from agents.contract_agent import contract_node
from agents.approval_agent import approval_node
from agents.execution_agent import execution_node
from agents.exception_agent import exception_node
from agents.audit_agent import audit_node

def router(state: GraphState) -> str:
    if state.get("issues"):
        if state.get("error_count", 0) > 3:
            return "audit_agent"
        return "exception_agent"
    
    status = state.get("status")
    if status == "intake_done":
        return "sourcing_agent"
    elif status == "sourcing_done":
        return "contract_agent"
    elif status == "contract_done":
        return "approval_agent"
    elif status == "approval_pending":
        return END # Stalls for human in loop
    elif status == "approval_done":
        return "execution_agent"
    elif status == "execution_done":
        return "audit_agent"
    elif status == "exception_fixed":
        return "contract_agent"
    elif status == "completed" or status == "failed":
        return END
        
    return "audit_agent"

def build_graph():
    workflow = StateGraph(GraphState)
    
    workflow.add_node("intake_agent", intake_node)
    workflow.add_node("sourcing_agent", sourcing_node)
    workflow.add_node("contract_agent", contract_node)
    workflow.add_node("approval_agent", approval_node)
    workflow.add_node("execution_agent", execution_node)
    workflow.add_node("exception_agent", exception_node)
    workflow.add_node("audit_agent", audit_node)
    
    workflow.add_edge(START, "intake_agent")
    workflow.add_conditional_edges("intake_agent", router)
    workflow.add_conditional_edges("sourcing_agent", router)
    workflow.add_conditional_edges("contract_agent", router)
    workflow.add_conditional_edges("approval_agent", router)
    workflow.add_conditional_edges("execution_agent", router)
    workflow.add_conditional_edges("exception_agent", router)
    workflow.add_edge("audit_agent", END)
    
    memory = MemorySaver()
    return workflow.compile(checkpointer=memory)
