from typing import TypedDict, Optional, List, Any

class GraphState(TypedDict):
    pr_id: Optional[str]
    vendor_id: Optional[str]
    pdf_path: Optional[str]
    pr_data: dict
    issues: List[str]
    vendor_category: Optional[str]
    po_id: Optional[str]
    invoice_id: Optional[str]
    amount: float
    approval_status: str
    status: str
    error_count: int
