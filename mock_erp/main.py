from fastapi import FastAPI, HTTPException
import uuid

app = FastAPI(title="Mock ERP API for AvataarFlow")

@app.get("/")
def read_root():
    return {"message": "AvataarFlow Mock ERP is running", "endpoints": ["/pr", "/po", "/invoice"]}

@app.post("/pr")
async def create_purchase_request(pr_data: dict):
    """Mock endpoint to create a Purchase Request."""
    if "items" not in pr_data or not pr_data["items"]:
        raise HTTPException(status_code=400, detail="Items are required in PR")
    pr_id = f"PR-{uuid.uuid4().hex[:8].upper()}"
    return {"status": "success", "pr_id": pr_id, "message": "Purchase Request created successfully."}

@app.post("/po")
async def create_purchase_order(po_data: dict):
    """Mock endpoint to create a Purchase Order."""
    if "pr_id" not in po_data or "vendor_id" not in po_data:
        raise HTTPException(status_code=400, detail="pr_id and vendor_id are required")
    po_id = f"PO-{uuid.uuid4().hex[:8].upper()}"
    return {"status": "success", "po_id": po_id, "amount": po_data.get("amount", 0)}

@app.post("/invoice")
async def process_invoice(invoice_data: dict):
    """Mock endpoint to process an Invoice and trigger 3-way match."""
    required = ["po_id", "invoice_amount", "vendor_id"]
    if not all(k in invoice_data for k in required):
        raise HTTPException(status_code=400, detail="Missing required invoice matching fields")
    
    # Simulate a basic 3-way match logic
    if invoice_data.get("invoice_amount") <= 0:
        return {"status": "failed", "reason": "Invalid amount"}
        
    invoice_id = f"INV-{uuid.uuid4().hex[:8].upper()}"
    return {"status": "success", "invoice_id": invoice_id, "match_status": "matched", "payment_status": "initiated"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
