"""
app/core/fines_config.py - Configurable Fine Schedule & Violation Rules
========================================================================
Smart ANPR Vehicle Verification System

This module defines the configurable traffic violation rules and illustrative
fine schedule under the Indian Motor Vehicles Act (e.g. 1988/2019 amendments).

DISCLAIMER:
All fine amounts, violation categories, and statutory references in this schedule
are strictly illustrative for academic demonstration and simulation. Actual statutory
penalties are governed by competent state and central transport authorities.
"""

from typing import Any, Dict, Optional

# Illustrative statutory disclaimer
STATUTORY_DISCLAIMER = (
    "Illustrative demonstration schedule pursuant to the Indian Motor Vehicles "
    "(Amendment) Act framework. Actual penalties vary by state jurisdiction, vehicle "
    "class, and judicial discretion."
)

# Standard mandatory document types that every motor vehicle must possess
MANDATORY_DOCUMENTS = ["RC", "INSURANCE", "PUC", "ROAD_TAX"]

# Configurable illustrative violation rules catalog
DEFAULT_VIOLATION_RULES: Dict[str, Dict[str, Any]] = {
    "EXPIRED_INSURANCE": {
        "code": "EXPIRED_INSURANCE",
        "title": "Driving Without Valid Insurance",
        "document_type": "INSURANCE",
        "condition": "EXPIRED",
        "statute": "Section 196, Motor Vehicles Act 1988",
        "fine_amount": 2000.0,
        "severity": "HIGH",
        "description": "Operating a motor vehicle without an active third-party insurance policy.",
    },
    "MISSING_INSURANCE": {
        "code": "MISSING_INSURANCE",
        "title": "Missing Motor Insurance Policy Record",
        "document_type": "INSURANCE",
        "condition": "MISSING",
        "statute": "Section 196, Motor Vehicles Act 1988",
        "fine_amount": 2000.0,
        "severity": "HIGH",
        "description": "No insurance policy registered or produced for the vehicle.",
    },
    "EXPIRED_PUC": {
        "code": "EXPIRED_PUC",
        "title": "Pollution Under Control (PUC) Violation",
        "document_type": "PUC",
        "condition": "EXPIRED",
        "statute": "Section 190(2), Motor Vehicles Act 1988",
        "fine_amount": 10000.0,
        "severity": "HIGH",
        "description": "Vehicle operating with expired or invalid vehicular emission certificate.",
    },
    "MISSING_PUC": {
        "code": "MISSING_PUC",
        "title": "Missing PUC Certificate Record",
        "document_type": "PUC",
        "condition": "MISSING",
        "statute": "Section 190(2), Motor Vehicles Act 1988",
        "fine_amount": 10000.0,
        "severity": "HIGH",
        "description": "No valid pollution compliance certificate found in vehicle registry.",
    },
    "EXPIRED_ROAD_TAX": {
        "code": "EXPIRED_ROAD_TAX",
        "title": "Default in Road Tax Payment",
        "document_type": "ROAD_TAX",
        "condition": "EXPIRED",
        "statute": "State Motor Vehicles Taxation Act",
        "fine_amount": 5000.0,
        "severity": "MEDIUM",
        "description": "Failure to pay statutory road tax beyond the prescribed grace period.",
    },
    "MISSING_ROAD_TAX": {
        "code": "MISSING_ROAD_TAX",
        "title": "Missing Road Tax Payment Record",
        "document_type": "ROAD_TAX",
        "condition": "MISSING",
        "statute": "State Motor Vehicles Taxation Act",
        "fine_amount": 5000.0,
        "severity": "MEDIUM",
        "description": "No road tax record found for the vehicle in the transport database.",
    },
    "EXPIRED_RC": {
        "code": "EXPIRED_RC",
        "title": "Driving an Unregistered / Expired RC Vehicle",
        "document_type": "RC",
        "condition": "EXPIRED",
        "statute": "Section 192, Motor Vehicles Act 1988",
        "fine_amount": 5000.0,
        "severity": "CRITICAL",
        "description": "Registration certificate fitness has lapsed; vehicle is not certified roadworthy.",
    },
    "MISSING_RC": {
        "code": "MISSING_RC",
        "title": "Missing Registration Certificate (RC)",
        "document_type": "RC",
        "condition": "MISSING",
        "statute": "Section 192, Motor Vehicles Act 1988",
        "fine_amount": 5000.0,
        "severity": "CRITICAL",
        "description": "Vehicle lacks a foundational registration certificate in the state registry.",
    },
    # General Road Safety Violations for challan calculation
    "OVER_SPEEDING": {
        "code": "OVER_SPEEDING",
        "title": "Over Speeding (Radar Camera Detected)",
        "document_type": None,
        "condition": None,
        "statute": "Section 183, Motor Vehicles Act 1988",
        "fine_amount": 2000.0,
        "severity": "MEDIUM",
        "description": "Exceeding designated urban or expressway statutory speed limits.",
    },
    "SIGNAL_JUMP": {
        "code": "SIGNAL_JUMP",
        "title": "Jumping Traffic Red Light",
        "document_type": None,
        "condition": None,
        "statute": "Section 184, Motor Vehicles Act 1988",
        "fine_amount": 1000.0,
        "severity": "MEDIUM",
        "description": "Failure to stop at a red signal at a regulated intersection.",
    },
    "NO_HELMET": {
        "code": "NO_HELMET",
        "title": "Riding Two-Wheeler Without Helmet",
        "document_type": None,
        "condition": None,
        "statute": "Section 194D, Motor Vehicles Act 1988",
        "fine_amount": 1000.0,
        "severity": "LOW",
        "description": "Operating or riding as pillion without authorized ISI/BIS protective headgear.",
    },
    "DANGEROUS_DRIVING": {
        "code": "DANGEROUS_DRIVING",
        "title": "Dangerous and Reckless Driving",
        "document_type": None,
        "condition": None,
        "statute": "Section 184, Motor Vehicles Act 1988",
        "fine_amount": 5000.0,
        "severity": "HIGH",
        "description": "Driving in a manner dangerous to the public, erratic lane weaving.",
    },
    "OVERLOADING": {
        "code": "OVERLOADING",
        "title": "Commercial Vehicle Overloading",
        "document_type": None,
        "condition": None,
        "statute": "Section 194, Motor Vehicles Act 1988",
        "fine_amount": 20000.0,
        "severity": "CRITICAL",
        "description": "Carrying load in excess of registered gross vehicle weight (GVW).",
    }
}


def get_violation_rule(code: str) -> Optional[Dict[str, Any]]:
    """Retrieve violation rule definition by violation code (case-insensitive)."""
    normalized_code = code.strip().upper()
    return DEFAULT_VIOLATION_RULES.get(normalized_code)


def get_rule_for_document(document_type: str, condition: str) -> Optional[Dict[str, Any]]:
    """
    Look up the violation rule that corresponds to a document type and its condition.
    Example: ('INSURANCE', 'EXPIRED') -> EXPIRED_INSURANCE rule.
    """
    doc_clean = document_type.strip().upper()
    cond_clean = condition.strip().upper()
    key = f"{cond_clean}_{doc_clean}"
    return DEFAULT_VIOLATION_RULES.get(key)


def get_all_violation_rules() -> Dict[str, Dict[str, Any]]:
    """Return a copy of all configured violation rules."""
    return {k: v.copy() for k, v in DEFAULT_VIOLATION_RULES.items()}
