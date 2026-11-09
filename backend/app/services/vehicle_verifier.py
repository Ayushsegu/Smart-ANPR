"""
app/services/vehicle_verifier.py - Vehicle Compliance & Violation Verification Engine
=====================================================================================
Smart ANPR Vehicle Verification System

This service coordinates:
1. Vehicle lookup by registration number (case-insensitive).
2. Comprehensive multi-document compliance evaluation (RC, INSURANCE, PUC, ROAD_TAX).
3. Automated violation detection (Expired documents, Missing mandatory records).
4. Summary counting (expired count, expiring count, valid count, missing count).
5. Overall verification verdict ('COMPLIANT', 'ATTENTION_REQUIRED', 'NON_COMPLIANT').
6. Fine calculation integration with itemized breakdown.
"""

from datetime import date, datetime
from typing import Any, Dict, List, Optional
from pathlib import Path

from app.core.fines_config import (
    MANDATORY_DOCUMENTS,
    get_rule_for_document,
)
from app.services.document_verifier import (
    STATUS_EXPIRED,
    STATUS_EXPIRING_SOON,
    STATUS_MISSING,
    STATUS_VALID,
    verify_single_document,
)
from app.services.fine_calculator import calculate_fine_breakdown
from app.models.database import (
    get_documents_by_vehicle_id,
    get_vehicle_by_plate,
    get_challans_by_vehicle_id,
)

# Overall compliance classification outcomes
VERDICT_COMPLIANT = "COMPLIANT"
VERDICT_ATTENTION_REQUIRED = "ATTENTION_REQUIRED"
VERDICT_NON_COMPLIANT = "NON_COMPLIANT"


def verify_vehicle_compliance(
    registration_number: str,
    reference_date: Optional[date] = None,
    db_path: Optional[str | Path] = None
) -> Optional[Dict[str, Any]]:
    """
    Perform a complete compliance inspection for a vehicle.

    Args:
        registration_number: License plate string (e.g. 'DL01AB1234')
        reference_date: Optional datetime.date for comparison (defaults to today)
        db_path: Optional path to SQLite anpr.db

    Returns:
        Structured verification dictionary, or None if vehicle is not found.
    """
    clean_plate = registration_number.strip().upper()

    # 1. Look up vehicle in database
    vehicle = get_vehicle_by_plate(clean_plate, db_path=db_path)
    if not vehicle:
        return None

    # 2. Retrieve existing documents for vehicle
    doc_records = get_documents_by_vehicle_id(vehicle["id"], db_path=db_path)
    records_by_type = {d["document_type"].upper(): d for d in doc_records}

    # 3. Evaluate all 4 mandatory document types
    evaluated_documents: Dict[str, Dict[str, Any]] = {}
    expired_count = 0
    expiring_count = 0
    valid_count = 0
    missing_count = 0

    detected_violations: List[Dict[str, Any]] = []

    for doc_type in MANDATORY_DOCUMENTS:
        raw_doc = records_by_type.get(doc_type)
        eval_result = verify_single_document(raw_doc, doc_type, reference_date=reference_date)
        if raw_doc and raw_doc.get("provider"):
            eval_result["provider"] = raw_doc["provider"]
        else:
            eval_result["provider"] = "Govt. Transport & Statutory Authority"
        evaluated_documents[doc_type] = eval_result

        status = eval_result["status"]
        if status == STATUS_EXPIRED:
            expired_count += 1
            rule = get_rule_for_document(doc_type, "EXPIRED")
            if rule:
                detected_violations.append({
                    "code": rule["code"],
                    "violation_code": rule["code"],
                    "document_type": doc_type,
                    "condition": "EXPIRED",
                    "title": rule["title"],
                    "statute": rule["statute"],
                    "fine_amount": rule["fine_amount"],
                    "severity": rule["severity"],
                    "description": eval_result["message"],
                })
        elif status == STATUS_EXPIRING_SOON:
            expiring_count += 1
        elif status == STATUS_VALID:
            valid_count += 1
        elif status == STATUS_MISSING:
            missing_count += 1
            rule = get_rule_for_document(doc_type, "MISSING")
            if rule:
                detected_violations.append({
                    "code": rule["code"],
                    "violation_code": rule["code"],
                    "document_type": doc_type,
                    "condition": "MISSING",
                    "title": rule["title"],
                    "statute": rule["statute"],
                    "fine_amount": rule["fine_amount"],
                    "severity": rule["severity"],
                    "description": eval_result["message"],
                })

    # 4. Determine overall compliance verdict
    has_violations = len(detected_violations) > 0
    if expired_count > 0 or missing_count > 0:
        verdict = VERDICT_NON_COMPLIANT
        recommendation = "Action Required: Vehicle is in violation of traffic regulations. Issue Digital Challan."
        verdict_badge = "red"
    elif expiring_count > 0:
        verdict = VERDICT_ATTENTION_REQUIRED
        recommendation = "Advisory: One or more documents are expiring soon. Issue renewal notice to owner."
        verdict_badge = "yellow"
    else:
        verdict = VERDICT_COMPLIANT
        recommendation = "Clear: All mandatory documents are fully valid and up to date."
        verdict_badge = "green"

    # 5. Calculate fine breakdown for any detected violations
    fine_summary = calculate_fine_breakdown(detected_violations)

    # 6. Fetch previous demo challans for this vehicle
    previous_challans = get_challans_by_vehicle_id(vehicle["id"], db_path=db_path)

    ref_date_used = (reference_date or datetime.now().date()).isoformat()

    return {
        "success": True,
        "is_demo": bool(vehicle.get("is_demo", 1)),
        "demo_notice": "DEMO RECORD – NOT VERIFIED AGAINST GOVERNMENT DATABASES",
        "registration_number": clean_plate,
        "vehicle": {
            "id": vehicle["id"],
            "registration_number": vehicle["registration_number"],
            "demo_id": vehicle.get("demo_id") or f"DEMO-{vehicle['id']:02d}",
            "is_demo": bool(vehicle.get("is_demo", 1)),
            "state": vehicle.get("state") or "Delhi",
            "rto_code": vehicle.get("rto_code") or "DL-01",
            "registration_status": vehicle.get("registration_status") or "ACTIVE",
            "owner_name": vehicle["owner_name"],
            "owner_phone": vehicle.get("owner_phone") or "+91-98765-43210",
            "owner_address": vehicle.get("owner_address") or "124, Vikas Marg, New Delhi",
            "manufacturer": vehicle.get("manufacturer") or "Maruti Suzuki",
            "vehicle_type": vehicle["vehicle_type"],
            "vehicle_class": vehicle.get("vehicle_class") or vehicle["vehicle_type"],
            "vehicle_model": vehicle["vehicle_model"],
            "vehicle_color": vehicle.get("vehicle_color") or "White",
            "fuel_type": vehicle.get("fuel_type") or "Petrol",
            "manufacturing_year": vehicle.get("manufacturing_year") or 2022,
            "chassis_number": vehicle.get("chassis_number") or f"SYN-CHAS-{clean_plate}",
            "engine_number": vehicle.get("engine_number") or f"SYN-ENG-{clean_plate}",
            "registration_date": vehicle["registration_date"],
            "driver_name": vehicle.get("driver_name") or vehicle["owner_name"],
            "driver_license_number": vehicle.get("driver_license_number") or f"DL-{clean_plate[:4]}2020",
            "driver_license_class": vehicle.get("driver_license_class") or "LMV",
            "driver_license_expiry": vehicle.get("driver_license_expiry") or "2032-12-31",
            "driver_license_status": vehicle.get("driver_license_status") or "VALID",
            "created_at": vehicle.get("created_at"),
        },
        "documents": evaluated_documents,
        "challans": previous_challans,
        "summary": {
            "total_documents_checked": len(MANDATORY_DOCUMENTS),
            "valid_count": valid_count,
            "expiring_count": expiring_count,
            "expired_count": expired_count,
            "missing_count": missing_count,
            "has_violations": has_violations,
            "overall_status": verdict,
            "verdict_badge": verdict_badge,
            "recommendation": recommendation,
        },
        "violations": detected_violations,
        "fines": fine_summary,
        "metadata": {
            "reference_date": ref_date_used,
            "verification_timestamp": datetime.now().isoformat(),
        }
    }
