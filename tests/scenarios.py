import os
from pathlib import Path
from fpdf import FPDF

SCENARIOS_DIR = Path(__file__).parent / "data"

def ensure_dir():
    SCENARIOS_DIR.mkdir(parents=True, exist_ok=True)

def create_pdf(filename: str, vendor_name: str, gstin: str, pan: str, amount: float, pr_number: str):
    ensure_dir()
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Purchase Request", ln=True, align='C')
    pdf.cell(200, 10, txt=f"PR Number: {pr_number}", ln=True)
    pdf.cell(200, 10, txt=f"Vendor: {vendor_name}", ln=True)
    pdf.cell(200, 10, txt=f"GSTIN: {gstin}", ln=True)
    pdf.cell(200, 10, txt=f"PAN: {pan}", ln=True)
    pdf.cell(200, 10, txt=f"Total Amount: {amount}", ln=True)
    pdf.cell(200, 10, txt="Items: 1x Enterprise Software License", ln=True)
    pdf.output(str(SCENARIOS_DIR / filename))

def generate_scenarios():
    ensure_dir()
    # 1. Normal clean PR
    scenario_1 = {
        "name": "Normal clean PR",
        "description": "All details correct",
        "pdf_path": str(SCENARIOS_DIR / "scenario_1_pr.pdf"),
        "vendor_id": "V-1001",
        "category": "professional_services"
    }
    create_pdf("scenario_1_pr.pdf", "TechCorp India", "27AAAAA0000A1Z5", "AAAAA0000A", 150000.0, "PR-1001")

    # 2. Messy PR with missing PAN + GST mismatch
    scenario_2 = {
        "name": "Messy PR with issues",
        "description": "Missing PAN, Invalid GST format (self-healing demo)",
        "pdf_path": str(SCENARIOS_DIR / "scenario_2_pr.pdf"),
        "vendor_id": "V-1002",
        "category": "contractor"
    }
    # Notice wrong GSTIN, missing PAN
    create_pdf("scenario_2_pr.pdf", "SME Builders", "INVALID_GST", "", 50000.0, "PR-1002")

    # 3. Approval stall
    scenario_3 = {
        "name": "Approval stall",
        "description": "Amount exceeds threshold, stalls at Approval Agent",
        "pdf_path": str(SCENARIOS_DIR / "scenario_3_pr.pdf"),
        "vendor_id": "V-1003",
        "category": "rent"
    }
    # Amount very high to trigger approval fail
    create_pdf("scenario_3_pr.pdf", "MegaCorp Leasing", "29BBBBB1111B1Z5", "BBBBB1111B", 5000000.0, "PR-1003")

    return [scenario_1, scenario_2, scenario_3]

if __name__ == "__main__":
    generate_scenarios()
    print("Scenarios generated.")
