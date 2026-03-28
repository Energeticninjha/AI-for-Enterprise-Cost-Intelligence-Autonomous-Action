import asyncio
import httpx
import requests

ERP_BASE_URL = "http://localhost:8000"

async def _post(endpoint: str, data: dict) -> dict:
    def sync_post():
        resp = requests.post(f"{ERP_BASE_URL}{endpoint}", json=data)
        resp.raise_for_status()
        return resp.json()
    return await asyncio.to_thread(sync_post)

async def create_pr(items: list, amount: float) -> dict:
    return await _post("/pr", {"items": items, "amount": amount})

async def create_po(pr_id: str, vendor_id: str, amount: float) -> dict:
    return await _post("/po", {"pr_id": pr_id, "vendor_id": vendor_id, "amount": amount})

async def process_invoice(po_id: str, vendor_id: str, amount: float) -> dict:
    return await _post("/invoice", {"po_id": po_id, "vendor_id": vendor_id, "invoice_amount": amount})
