"""
app/services/fine_calculator.py - Fine Calculation & Penalty Schedule Engine
=============================================================================
Smart ANPR Vehicle Verification System

This module calculates traffic violation fines and produces an itemized
financial breakdown.

Key Features:
- Supports multiple violations simultaneously.
- Automatic deduplication (prevents compounding identical violations twice).
- Configurable fine schedule with custom runtime overrides.
- Distinct statutory references per violation type (illustrative).
- Clear academic disclaimer regarding demonstration penalties.
"""

from typing import Any, Dict, List, Optional, Set, Union
from app.core.fines_config import (
    DEFAULT_VIOLATION_RULES,
    STATUTORY_DISCLAIMER,
    get_violation_rule,
)


def calculate_fine_breakdown(
    violations: List[Union[str, Dict[str, Any]]],
    custom_overrides: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """
    Calculate an itemized fine breakdown for a list of violation codes or objects.

    Args:
        violations: List of violation codes (e.g., ["EXPIRED_INSURANCE", "EXPIRED_PUC"])
                    or dictionaries containing at least a 'code' or 'violation_type' key.
        custom_overrides: Optional dict mapping violation_code -> custom float amount.

    Returns:
        Structured dictionary containing:
            - items: List of individual itemized violation charges
            - total_fine: Total aggregated monetary fine (float)
            - total_fine_formatted: String formatted with currency symbol
            - violations_count: Number of unique violations penalized
            - duplicate_violations_ignored: Number of duplicates filtered out
            - severity_summary: Count of violations by severity level
            - currency: "INR"
            - disclaimer: Statutory illustrative notice
    """
    overrides = custom_overrides or {}
    items: List[Dict[str, Any]] = []
    seen_codes: Set[str] = set()
    duplicates_count = 0

    severity_counts = {
        "CRITICAL": 0,
        "HIGH": 0,
        "MEDIUM": 0,
        "LOW": 0
    }

    for violation in violations:
        # Extract code regardless of whether violation is a str or dict
        if isinstance(violation, str):
            code = violation.strip().upper()
        elif isinstance(violation, dict):
            code = (
                violation.get("code")
                or violation.get("violation_code")
                or violation.get("violation_type")
                or ""
            ).strip().upper()
        else:
            continue

        if not code:
            continue

        # Prevent duplicate penalties for the exact same violation type
        if code in seen_codes:
            duplicates_count += 1
            continue

        seen_codes.add(code)

        # Lookup rule in configuration
        rule = get_violation_rule(code)
        if rule:
            # Check for custom override
            fine_amount = float(overrides.get(code, rule["fine_amount"]))
            title = rule["title"]
            statute = rule["statute"]
            severity = rule.get("severity", "MEDIUM")
            desc = rule.get("description", "")
        else:
            # Fallback for unrecognized custom violation code
            fine_amount = float(overrides.get(code, 1000.0))
            title = code.replace("_", " ").title()
            statute = "Motor Vehicles Act 1988 (General Violation)"
            severity = "MEDIUM"
            desc = "Violation detected during enforcement check."

        severity_counts[severity] = severity_counts.get(severity, 0) + 1

        items.append({
            "violation_code": code,
            "title": title,
            "statute": statute,
            "fine_amount": fine_amount,
            "fine_amount_formatted": f"₹{fine_amount:,.2f}",
            "severity": severity,
            "description": desc,
        })

    total_fine = sum(item["fine_amount"] for item in items)

    return {
        "items": items,
        "total_fine": total_fine,
        "total_fine_formatted": f"₹{total_fine:,.2f}",
        "violations_count": len(items),
        "duplicate_violations_ignored": duplicates_count,
        "severity_summary": severity_counts,
        "currency": "INR",
        "currency_symbol": "₹",
        "disclaimer": STATUTORY_DISCLAIMER,
    }
