import pytest
import os
import sys

# Ensure package context
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tools.india_validators import validate_pan, validate_gstin, detect_common_sme_issues
from tools.pdf_parser import parse_pr_pdf
from tests.scenarios import generate_scenarios

@pytest.fixture(scope="module")
def scenarios_data():
    return generate_scenarios()

def test_validate_pan():
    assert validate_pan("ABCDE1234F") is True
    assert validate_pan("abcde1234f") is True
    assert validate_pan("12345ABCDE") is False
    assert validate_pan("ABCD1234F") is False
    assert validate_pan("ABCDE1234") is False

def test_validate_gstin():
    assert validate_gstin("27ABCDE1234F1Z5") is True
    assert validate_gstin("27abcde1234f1z5") is True
    assert validate_gstin("27ABCDE12341Z5") is False
    assert validate_gstin("XYZ") is False

def test_detect_sme_issues():
    # Valid
    issues = detect_common_sme_issues({"pan": "ABCDE1234F", "gstin": "27ABCDE1234F1Z5"})
    assert len(issues) == 0

    # Missing PAN
    issues = detect_common_sme_issues({"gstin": "27ABCDE1234F1Z5"})
    assert any("Missing PAN" in i for i in issues)

    # GSTIN format invalid
    issues = detect_common_sme_issues({"pan": "ABCDE1234F", "gstin": "27ABCDE"})
    assert any("Invalid GSTIN format" in i for i in issues)

    # Mismatch
    issues = detect_common_sme_issues({"pan": "ABCDE1234F", "gstin": "27ZZZZZ9999Z1Z5"})
    assert any("GSTIN and PAN mismatch" in i for i in issues)

def test_pdf_parsing(scenarios_data):
    # Test Scenario 1 (Clean)
    data_1 = parse_pr_pdf(scenarios_data[0]["pdf_path"])
    assert data_1["pan"] == "AAAAA0000A"
    assert data_1["gstin"] == "27AAAAA0000A1Z5"
    assert data_1["amount"] == 150000.0
    assert data_1["pr_number"] == "PR-1001"
    
    # Test Scenario 2 (Messy)
    data_2 = parse_pr_pdf(scenarios_data[1]["pdf_path"])
    assert data_2["pan"] == ""
    assert data_2["gstin"] == "INVALID_GST"
    assert data_2["amount"] == 50000.0
