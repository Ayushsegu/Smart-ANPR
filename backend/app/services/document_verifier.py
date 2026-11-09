"""
app/services/document_verifier.py - Modular Document Verification Engine
========================================================================
Smart ANPR Vehicle Verification System

This service implements the 4 document compliance evaluation rules:
1. VALID: Expiry date is more than 30 days away.
2. EXPIRING_SOON: Expiry date is within the next 30 days (0 to 30 days inclusive).
3. EXPIRED: Expiry date is before the reference date (negative days remaining).
4. MISSING: Required document record is absent from the database.

Rules utilize Python's `datetime` module without hardcoded dates.
"""

from datetime import date, datetime
from typing import Any, Dict, Optional

# Constants for document statuses
STATUS_VALID = "VALID"
STATUS_EXPIRING_SOON = "EXPIRING_SOON"
STATUS_EXPIRED = "EXPIRED"
STATUS_MISSING = "MISSING"

# UI visual badge mappings for frontend consumption
BADGE_COLORS = {
    STATUS_VALID: "green",
    STATUS_EXPIRING_SOON: "yellow",
    STATUS_EXPIRED: "red",
    STATUS_MISSING: "gray",
}


def parse_date(date_val: Any) -> Optional[date]:
    """
    Safely parse various date representations (str, datetime, date) into a date object.
    Supports YYYY-MM-DD format commonly used across SQLite and ISO standards.
    """
    if date_val is None:
        return None
    if isinstance(date_val, datetime):
        return date_val.date()
    if isinstance(date_val, date):
        return date_val
    if isinstance(date_val, str):
        # Support both 'YYYY-MM-DD' and 'YYYY-MM-DD HH:MM:SS'
        clean_str = date_val.strip()
        for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y/%m/%d", "%d-%m-%Y"):
            try:
                return datetime.strptime(clean_str, fmt).date()
            except ValueError:
                continue
    return None


def evaluate_document_status(
    expiry_date_val: Any,
    reference_date: Optional[date] = None
) -> Dict[str, Any]:
    """
    Core business logic rule evaluator for a single document's expiry date.

    Args:
        expiry_date_val: String (YYYY-MM-DD), date, or datetime of document expiry.
        reference_date: Optional comparison date. Defaults to datetime.now().date().

    Returns:
        Dict containing:
            - status: VALID | EXPIRING_SOON | EXPIRED
            - days_until_expiry: int
            - badge_color: green | yellow | red
            - message: human-readable status description
    """
    ref_date = reference_date if reference_date is not None else datetime.now().date()
    exp_date = parse_date(expiry_date_val)

    if exp_date is None:
        return {
            "status": STATUS_MISSING,
            "days_until_expiry": None,
            "badge_color": BADGE_COLORS[STATUS_MISSING],
            "message": "Invalid or missing expiry date on record.",
            "is_valid": False,
            "is_expiring_soon": False,
            "is_expired": False,
            "is_missing": True,
        }

    # Calculate delta in days
    days_until_expiry = (exp_date - ref_date).days

    if days_until_expiry < 0:
        days_ago = abs(days_until_expiry)
        msg = f"Expired {days_ago} day{'s' if days_ago != 1 else ''} ago (on {exp_date.isoformat()})."
        status = STATUS_EXPIRED
    elif days_until_expiry <= 30:
        msg = f"Expires in {days_until_expiry} day{'s' if days_until_expiry != 1 else ''} (on {exp_date.isoformat()})."
        status = STATUS_EXPIRING_SOON
    else:
        msg = f"Valid for {days_until_expiry} more days (expires {exp_date.isoformat()})."
        status = STATUS_VALID

    return {
        "status": status,
        "days_until_expiry": days_until_expiry,
        "expiry_date": exp_date.isoformat(),
        "badge_color": BADGE_COLORS[status],
        "message": msg,
        "is_valid": status == STATUS_VALID,
        "is_expiring_soon": status == STATUS_EXPIRING_SOON,
        "is_expired": status == STATUS_EXPIRED,
        "is_missing": False,
    }


def verify_single_document(
    document_record: Optional[Dict[str, Any]],
    document_type: str,
    reference_date: Optional[date] = None
) -> Dict[str, Any]:
    """
    Verifies a document database record or generates a missing document entry.

    Args:
        document_record: Dict row from SQLite or None if document is absent.
        document_type: The required type (RC, INSURANCE, PUC, ROAD_TAX).
        reference_date: Optional evaluation date.

    Returns:
        Structured dictionary with full document status and metadata.
    """
    clean_type = document_type.strip().upper()

    # Rule 4: MISSING document record does not exist
    if not document_record:
        return {
            "document_type": clean_type,
            "document_number": None,
            "issue_date": None,
            "expiry_date": None,
            "status": STATUS_MISSING,
            "days_until_expiry": None,
            "badge_color": BADGE_COLORS[STATUS_MISSING],
            "message": f"Mandatory document '{clean_type}' is missing from vehicle registry.",
            "is_valid": False,
            "is_expiring_soon": False,
            "is_expired": False,
            "is_missing": True,
        }

    # Evaluate expiry using core rules
    expiry_eval = evaluate_document_status(
        expiry_date_val=document_record.get("expiry_date"),
        reference_date=reference_date
    )

    issue_date_parsed = parse_date(document_record.get("issue_date"))

    return {
        "id": document_record.get("id"),
        "vehicle_id": document_record.get("vehicle_id"),
        "document_type": clean_type,
        "document_number": document_record.get("document_number"),
        "issue_date": issue_date_parsed.isoformat() if issue_date_parsed else document_record.get("issue_date"),
        "expiry_date": expiry_eval.get("expiry_date", document_record.get("expiry_date")),
        "status": expiry_eval["status"],
        "days_until_expiry": expiry_eval["days_until_expiry"],
        "badge_color": expiry_eval["badge_color"],
        "message": expiry_eval["message"],
        "is_valid": expiry_eval["is_valid"],
        "is_expiring_soon": expiry_eval["is_expiring_soon"],
        "is_expired": expiry_eval["is_expired"],
        "is_missing": False,
    }
