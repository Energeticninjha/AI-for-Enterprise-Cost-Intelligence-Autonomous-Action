import re

def validate_pan(pan: str) -> bool:
    """Validate Indian PAN card format (5 letters, 4 numbers, 1 letter)."""
    return bool(re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$', pan.upper()))

def validate_gstin(gstin: str) -> bool:
    """Validate GSTIN format (15 characters)."""
    # 2 digits state code, 10 chars PAN, 1 entity num, Z default, 1 checksum
    return bool(re.match(r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$', gstin.upper()))

def validate_tds_rate(vendor_category: str, provided_rate: float, amount: float = 0.0, is_individual: bool = False) -> bool:
    """Validate TDS rates based on category (FY 2025-26 / 2026-27)."""
    if vendor_category == "contractor": # 194C
        expected = 1.0 if is_individual else 2.0
        return provided_rate == expected
    elif vendor_category == "professional_services": # 194J
        return provided_rate == 10.0
    elif vendor_category == "technical_services": # 194J
        return provided_rate == 2.0
    elif vendor_category == "goods": # 194Q
        expected = 0.1 if amount > 5000000 else 0.0
        return provided_rate == expected
    return provided_rate == 0.0

def detect_common_sme_issues(vendor_data: dict) -> list[str]:
    """Detect common errors in SME vendor setup (e.g., missing PAN, GST vs PAN mismatch)."""
    issues = []
    pan = vendor_data.get('pan', '')
    gstin = vendor_data.get('gstin', '')
    
    if not pan:
        issues.append("Missing PAN: SME Vendor must provide a valid 10-character PAN card number.")
    elif not validate_pan(pan):
        issues.append(f"Invalid PAN format '{pan}': Must be uppercase 5 letters, 4 numbers, 1 letter.")
        
    if gstin:
        if not validate_gstin(gstin):
            issues.append(f"Invalid GSTIN format '{gstin}': Must be exactly 15 chars (e.g., 27ABCDE1234F2Z5).")
        elif pan and gstin[2:12].upper() != pan.upper():
            issues.append(f"GSTIN and PAN mismatch: Vendor registered PAN {pan} does not match inline GSTIN PAN {gstin[2:12]}.")
            
    return issues
