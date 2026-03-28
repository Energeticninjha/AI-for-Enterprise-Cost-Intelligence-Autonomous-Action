import pdfplumber
import re

def parse_pr_pdf(pdf_path: str) -> dict:
    """Parse a Purchase Request PDF and extract key fields."""
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    
    # Simple regex extraction for demo purposes
    data = {
        "pr_number": "",
        "vendor_name": "",
        "gstin": "",
        "pan": "",
        "amount": 0.0,
        "items": []
    }
    
    pr_match = re.search(r'PR\sNumber:[ \t]*([^\n]+)', text)
    if pr_match:
        data["pr_number"] = pr_match.group(1).strip()
        
    vendor_match = re.search(r'Vendor:[ \t]*([^\n]+)', text)
    if vendor_match:
        data["vendor_name"] = vendor_match.group(1).strip()
        
    gstin_match = re.search(r'GSTIN:[ \t]*([^\n]+)', text)
    if gstin_match:
        data["gstin"] = gstin_match.group(1).strip()
        
    pan_match = re.search(r'PAN:[ \t]*([^\n]+)', text)
    if pan_match:
        val = pan_match.group(1).strip()
        if val and not val.startswith(('Total', 'Items')):
            data["pan"] = val
        
    amount_match = re.search(r'Total\s+Amount:[ \t]*([\d\.]+)', text)
    if amount_match:
        data["amount"] = float(amount_match.group(1))
        
    if data["amount"] > 0:
        data["items"] = ["Extracted Item 1"]
        
    return data
