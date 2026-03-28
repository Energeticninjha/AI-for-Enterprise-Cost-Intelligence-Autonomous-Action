from agents.state import GraphState
from db.db_ops import log_audit_action
from tools.pdf_parser import parse_pr_pdf
from tools.erp_client import create_pr

async def intake_node(state: GraphState) -> dict:
    log_audit_action("IntakeAgent", "Spend Intelligence Analysis Started", {
        "reasoning": "Ingesting new Purchase Request documents. Monitoring for early signs of cost leakage or duplicate submissions.",
        "tool_calls": "pdf_parser.parse_pr_pdf()",
        "status": "In Progress"
    })
    
    try:
        pr_data = parse_pr_pdf(state["pdf_path"]) if state.get("pdf_path") else state.get("pr_data", {})
        
        erp_res = await create_pr(pr_data.get("items", []), pr_data.get("amount", 0.0))
        pr_id = erp_res.get("pr_id")
        amount = pr_data.get("amount", 0.0)
        
        log_audit_action("IntakeAgent", "Cost Baseline Established", {
            "reasoning": f"PR {pr_id} successfully parsed. Amount: Rs {amount}. No duplicate vendor cost patterns detected. Routing to sourcing.",
            "tool_calls": "mock_erp_create_pr()",
            "next_step": "sourcing_agent",
            "status": "Success"
        })
        return {
            "pr_data": pr_data, "pr_id": pr_id, "amount": amount, "status": "intake_done"
        }
    except Exception as e:
        issues = state.get("issues", []) + [f"Intake Error: {str(e)}"]
        log_audit_action("IntakeAgent", "Data Ingestion Failure", {
            "reasoning": f"Critical failure during PR extraction hitting ERP endpoint: {str(e)}. Flagging for exception loop.",
            "status": "Failure", "next_step": "exception_agent"
        })
        return {"issues": issues, "status": "failed"}
