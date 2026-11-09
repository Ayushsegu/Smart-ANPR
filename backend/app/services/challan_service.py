"""
app/services/challan_service.py - Digital Challan Business Logic & Service Engine
================================================================================
Smart ANPR Vehicle Verification System

This service coordinates:
1. Unique citation number generation and collision prevention (e.g. CH-2026-XXXXX).
2. Integration with Phase 3 Fine Calculation Engine (fine_calculator.py).
3. Automated compliance inspection fallback (detects expired/missing documents).
4. Synchronized PDF receipt creation (pdf_generator.py) and QR barcode generation (qr_generator.py).
5. Relational persistence into SQLite `challans` table.
6. Demonstration payment status transition (PENDING -> PAID / FAILED) with automatic
   PDF badge re-rendering.
7. Clear academic demonstration notices on all issued artifacts.
"""

import json
import secrets
import string
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from app.core.config import Config
from app.core.fines_config import STATUTORY_DISCLAIMER
from app.models.database import (
    get_challan_by_number,
    get_vehicle_by_plate,
    insert_challan,
    update_challan_artifacts,
    update_challan_payment_status,
)
from app.services.fine_calculator import calculate_fine_breakdown
from app.services.pdf_generator import generate_challan_pdf
from app.services.qr_generator import generate_challan_qr
from app.services.vehicle_verifier import verify_vehicle_compliance


def generate_unique_challan_number(db_path: Optional[str | Path] = None) -> str:
    """
    Generate a collision-resistant unique challan citation number.
    Format: CH-{YEAR}-{5_ALPHANUMERIC_CHARS} (e.g. 'CH-2026-9A82F')

    Args:
        db_path: Optional path to SQLite database.

    Returns:
        A unique, verified non-colliding challan number.
    """
    current_year = datetime.now().year
    alphabet = string.ascii_uppercase + string.digits
    # Exclude confusing characters O, 0, I, 1 for legibility
    clean_alphabet = "".join([c for c in alphabet if c not in "OI01"])

    for _ in range(50):
        random_suffix = "".join(secrets.choice(clean_alphabet) for _ in range(5))
        candidate = f"CH-{current_year}-{random_suffix}"
        existing = get_challan_by_number(candidate, db_path=db_path)
        if not existing:
            return candidate

    # Fallback timestamp-based suffix if loop exhausts
    ts_suffix = datetime.now().strftime("%f")[:5]
    return f"CH-{current_year}-{ts_suffix}"


def generate_digital_challan(
    registration_number: str,
    violations: Optional[List[Union[str, Dict[str, Any]]]] = None,
    description: str = "",
    custom_overrides: Optional[Dict[str, float]] = None,
    base_url: Optional[str] = None,
    db_path: Optional[str | Path] = None,
) -> Dict[str, Any]:
    """
    Create a complete digital traffic challan for a registered vehicle.

    Steps:
    1. Validate vehicle existence in the SQLite database.
    2. If violations are not provided, run vehicle_verifier to detect all active non-compliances.
    3. Calculate itemized fine schedule using fine_calculator.
    4. Generate unique challan citation number.
    5. Generate scannable QR code PNG.
    6. Record challan in SQLite database.
    7. Generate ReportLab PDF receipt with embedded QR code.
    8. Update database record with artifact paths and return complete payload.

    Args:
        registration_number: Vehicle license plate string.
        violations: Optional list of violation codes or violation dicts.
        description: Optional notes/officer description.
        custom_overrides: Optional dict mapping violation codes to custom fine amounts.
        base_url: Optional base server URL for QR code verification link.
        db_path: Optional path to SQLite database.

    Returns:
        Structured challan dictionary.

    Raises:
        ValueError: If vehicle not found, or if no violations detected.
    """
    clean_plate = registration_number.strip().upper()
    server_base = (base_url or Config.BASE_URL).rstrip("/")

    # 1. Lookup vehicle in database
    vehicle = get_vehicle_by_plate(clean_plate, db_path=db_path)
    if not vehicle:
        raise ValueError(f"Vehicle '{clean_plate}' is not registered in the database.")

    # 2. Determine violations
    active_violations = violations or []
    if not active_violations:
        compliance_check = verify_vehicle_compliance(clean_plate, db_path=db_path)
        if compliance_check and compliance_check.get("violations"):
            active_violations = compliance_check["violations"]

    if not active_violations:
        raise ValueError(
            f"Vehicle '{clean_plate}' has no detected violations. Challan cannot be issued."
        )

    # 3. Calculate fine breakdown
    fine_summary = calculate_fine_breakdown(active_violations, custom_overrides=custom_overrides)
    if fine_summary["violations_count"] == 0:
        raise ValueError("No valid violation charges could be resolved.")

    total_fine = float(fine_summary["total_fine"])
    breakdown_items = fine_summary["items"]

    # Generate composite violation_type string
    violation_codes = [item["violation_code"] for item in breakdown_items]
    violation_type_str = ", ".join(violation_codes)

    # Generate composite description if not provided
    if not description:
        item_titles = [f"{item['title']} ({item['statute']})" for item in breakdown_items]
        challan_description = "; ".join(item_titles)
    else:
        challan_description = description.strip()

    # 4. Generate unique challan citation number
    challan_number = generate_unique_challan_number(db_path=db_path)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 5. Generate QR Code
    qr_abs_path, qr_web_url = generate_challan_qr(
        challan_number=challan_number,
        base_url=server_base,
    )

    # 6. Insert record into database
    breakdown_json_str = json.dumps(fine_summary, ensure_ascii=False)
    challan_id = insert_challan(
        challan_number=challan_number,
        vehicle_id=vehicle["id"],
        violation_type=violation_type_str,
        fine_amount=total_fine,
        challan_date=now_str,
        payment_status="PENDING",
        description=challan_description,
        challan_status="ISSUED",
        fine_breakdown_json=breakdown_json_str,
        pdf_path=None,  # Will be populated right after PDF compilation
        qr_path=qr_web_url,
        db_path=db_path,
    )

    # 7. Generate PDF document with embedded QR image
    pdf_payload = {
        "challan_number": challan_number,
        "registration_number": clean_plate,
        "owner_name": vehicle["owner_name"],
        "vehicle_type": vehicle["vehicle_type"],
        "vehicle_model": vehicle["vehicle_model"],
        "violation_type": violation_type_str,
        "fine_amount": total_fine,
        "challan_date": now_str,
        "payment_status": "PENDING",
        "challan_status": "ISSUED",
        "description": challan_description,
        "fine_breakdown": breakdown_items,
    }

    pdf_abs_path, pdf_web_url = generate_challan_pdf(
        challan_data=pdf_payload,
        qr_image_path=qr_abs_path,
    )

    # 8. Update database with PDF artifact path
    update_challan_artifacts(
        challan_number=challan_number,
        pdf_path=pdf_web_url,
        qr_path=qr_web_url,
        db_path=db_path,
    )

    return {
        "success": True,
        "challan_id": challan_id,
        "challan_number": challan_number,
        "vehicle": {
            "id": vehicle["id"],
            "registration_number": vehicle["registration_number"],
            "owner_name": vehicle["owner_name"],
            "vehicle_type": vehicle["vehicle_type"],
            "vehicle_model": vehicle["vehicle_model"],
        },
        "violation_type": violation_type_str,
        "description": challan_description,
        "fine_amount": total_fine,
        "fine_amount_formatted": f"₹{total_fine:,.2f}",
        "challan_date": now_str,
        "payment_status": "PENDING",
        "challan_status": "ISSUED",
        "fine_breakdown": fine_summary,
        "artifacts": {
            "pdf_url": pdf_web_url,
            "qr_url": qr_web_url,
            "verification_url": f"{server_base}/api/challans/{challan_number}",
        },
        "disclaimer": STATUTORY_DISCLAIMER,
    }


def get_challan_details(
    challan_number: str,
    base_url: Optional[str] = None,
    db_path: Optional[str | Path] = None,
) -> Optional[Dict[str, Any]]:
    """
    Retrieve full details for a challan by its unique citation number.

    Args:
        challan_number: Unique citation number (e.g. 'CH-2026-9A82F').
        base_url: Base server URL for building artifact links.
        db_path: Optional path to SQLite database.

    Returns:
        Dictionary with challan details, vehicle info, fine items, and URLs,
        or None if not found.
    """
    record = get_challan_by_number(challan_number, db_path=db_path)
    if not record:
        return None

    server_base = (base_url or Config.BASE_URL).rstrip("/")
    clean_num = record["challan_number"]

    # Parse fine breakdown JSON if present
    breakdown_data: Optional[Dict[str, Any]] = None
    if record.get("fine_breakdown_json"):
        try:
            breakdown_data = json.loads(record["fine_breakdown_json"])
        except Exception:
            breakdown_data = None

    # Derive artifact URLs if not explicitly stored in older records
    pdf_url = record.get("pdf_path") or f"/static/challans/pdf/{clean_num}.pdf"
    qr_url = record.get("qr_path") or f"/static/challans/qr/{clean_num}.png"

    return {
        "success": True,
        "challan_id": record["id"],
        "challan_number": clean_num,
        "vehicle": {
            "id": record["vehicle_id"],
            "registration_number": record["registration_number"],
            "owner_name": record["owner_name"],
            "vehicle_type": record["vehicle_type"],
            "vehicle_model": record["vehicle_model"],
            "registration_date": record.get("registration_date"),
        },
        "violation_type": record["violation_type"],
        "fine_amount": record["fine_amount"],
        "fine_amount_formatted": f"₹{float(record['fine_amount']):,.2f}",
        "challan_date": record["challan_date"],
        "payment_status": record["payment_status"],
        "challan_status": record.get("challan_status", "ISSUED"),
        "description": record.get("description", ""),
        "fine_breakdown": breakdown_data,
        "artifacts": {
            "pdf_url": pdf_url,
            "qr_url": qr_url,
            "verification_url": f"{server_base}/api/challans/{clean_num}",
        },
        "disclaimer": STATUTORY_DISCLAIMER,
    }


def process_demonstration_payment(
    challan_number: str,
    action: str = "PAY",
    db_path: Optional[str | Path] = None,
) -> Optional[Dict[str, Any]]:
    """
    Process an academic demonstration payment status update for a challan.

    Supported action states:
    - 'PAY' -> sets payment_status='PAID', challan_status='SETTLED'
    - 'FAIL' -> sets payment_status='FAILED', challan_status='ISSUED'
    - 'RESET' -> sets payment_status='PENDING', challan_status='ISSUED'

    Regenerates the PDF receipt with the updated status badge!

    Args:
        challan_number: Unique citation number.
        action: 'PAY', 'FAIL', or 'RESET'.
        db_path: Optional path to SQLite database.

    Returns:
        Updated challan dictionary, or None if challan not found.
    """
    record = get_challan_by_number(challan_number, db_path=db_path)
    if not record:
        return None

    act_upper = action.strip().upper()
    if act_upper in ("PAY", "PAID"):
        new_payment_status = "PAID"
    elif act_upper in ("FAIL", "FAILED"):
        new_payment_status = "FAILED"
    elif act_upper in ("RESET", "PENDING"):
        new_payment_status = "PENDING"
    else:
        raise ValueError(f"Invalid payment action '{action}'. Must be 'PAY', 'FAIL', or 'RESET'.")

    # Update database
    updated = update_challan_payment_status(
        challan_number=challan_number,
        payment_status=new_payment_status,
        db_path=db_path,
    )
    if not updated:
        return None

    # Fetch updated details
    updated_record = get_challan_by_number(challan_number, db_path=db_path)
    if not updated_record:
        return None

    # Regenerate QR code if not present
    clean_num = updated_record["challan_number"]
    qr_file = Path(Config.QR_OUTPUT_DIR) / f"{clean_num}.png"
    if not qr_file.is_file():
        generate_challan_qr(clean_num)

    # Regenerate PDF with updated status badge
    pdf_payload = {
        "challan_number": clean_num,
        "registration_number": updated_record["registration_number"],
        "owner_name": updated_record["owner_name"],
        "vehicle_type": updated_record["vehicle_type"],
        "vehicle_model": updated_record["vehicle_model"],
        "violation_type": updated_record["violation_type"],
        "fine_amount": updated_record["fine_amount"],
        "challan_date": updated_record["challan_date"],
        "payment_status": updated_record["payment_status"],
        "challan_status": updated_record.get("challan_status", "ISSUED"),
        "description": updated_record.get("description", ""),
        "fine_breakdown_json": updated_record.get("fine_breakdown_json"),
    }
    generate_challan_pdf(pdf_payload, qr_image_path=str(qr_file))

    details = get_challan_details(clean_num, db_path=db_path)
    if details:
        details["demonstration_notice"] = (
            "Demonstration payment status update simulated successfully. "
            "No actual monetary transfer or payment gateway processing occurred."
        )
    return details
