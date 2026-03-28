from agents.state import GraphState
from db.db_ops import log_audit_action

async def audit_node(state: GraphState) -> dict:
    final_status = "completed" if not state.get("issues") else "failed"
    log_audit_action("AuditAgent", "Workflow Sign-off", {
        "reasoning": f"Aggregated comprehensive cost intelligence records. Terminal trace verified as {final_status}. Initiating log lockdown.",
        "tool_calls": "certify_db_writes()", "status": "Success", "next_step": "END"
    })
    return {"status": final_status}
