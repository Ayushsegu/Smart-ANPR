"""
app/api/inspection_routes.py - Vehicle Detection History & GPS Inspection APIs
=============================================================================
Smart ANPR Vehicle Verification System

Endpoints:
- GET  /api/inspections      - Retrieve inspection records with search, filter, and pagination
- GET  /api/inspections/<id> - Retrieve single inspection detail
- POST /api/inspections      - Record a new vehicle inspection with GPS coordinates
"""

import time
import json
from flask import Blueprint, jsonify, request
from app.core.auth import auth_required
from app.models.database import (
    get_all_inspections,
    get_inspection_by_id,
    insert_inspection,
)

inspection_bp = Blueprint("inspections", __name__)


@inspection_bp.route("/inspections", methods=["GET"])
def list_inspections():
    """
    GET /api/inspections
    Query parameters:
    - search: license plate, inspection code, or checkpoint name
    - status: ALL, COMPLIANT, VIOLATION, UNREGISTERED
    - limit: maximum records (default: 50)
    - offset: pagination offset (default: 0)
    """
    search = request.args.get("search", "").strip() or None
    status = request.args.get("status", "ALL").strip() or None
    limit = min(int(request.args.get("limit", 50)), 200)
    offset = max(int(request.args.get("offset", 0)), 0)

    records = get_all_inspections(search=search, status=status, limit=limit, offset=offset)

    # Parse violations_json if string
    for rec in records:
        if rec.get("violations_json") and isinstance(rec["violations_json"], str):
            try:
                rec["violations"] = json.loads(rec["violations_json"])
            except Exception:
                rec["violations"] = []
        else:
            rec["violations"] = []

    return jsonify({
        "success": True,
        "count": len(records),
        "inspections": records,
    }), 200


@inspection_bp.route("/inspections/<int:inspection_id>", methods=["GET"])
def get_inspection(inspection_id: int):
    """
    GET /api/inspections/<id>
    Retrieve detailed telemetry for a single inspection.
    """
    rec = get_inspection_by_id(inspection_id)
    if not rec:
        return jsonify({
            "success": False,
            "error": f"Inspection record with ID {inspection_id} not found."
        }), 404

    if rec.get("violations_json") and isinstance(rec["violations_json"], str):
        try:
            rec["violations"] = json.loads(rec["violations_json"])
        except Exception:
            rec["violations"] = []
    else:
        rec["violations"] = []

    return jsonify({
        "success": True,
        "inspection": rec,
    }), 200


@inspection_bp.route("/inspections", methods=["POST"])
def record_inspection():
    """
    POST /api/inspections
    Payload:
    - registration_number: Vehicle plate (required)
    - detection_confidence: float (default: 0.95)
    - ocr_confidence: float (default: 0.90)
    - verification_status: COMPLIANT | VIOLATION | UNREGISTERED (default: COMPLIANT)
    - violations_summary: str
    - violations: list of violation objects
    - latitude: float (GPS)
    - longitude: float (GPS)
    - location_name: str
    - officer_name: str
    - notes: str
    """
    data = request.get_json(silent=True) or {}
    reg = (data.get("registration_number") or data.get("plate_number") or "").strip().upper()
    if not reg:
        return jsonify({
            "success": False,
            "error": "Field 'registration_number' (or 'plate_number') is required."
        }), 400

    code = f"INSP-2026-{int(time.time() * 1000) % 100000:05d}"
    violations = data.get("violations", [])
    violations_json = json.dumps(violations) if isinstance(violations, list) else None

    new_id = insert_inspection(
        inspection_code=code,
        registration_number=reg,
        detection_confidence=float(data.get("detection_confidence", 0.95)),
        ocr_confidence=float(data.get("ocr_confidence", 0.90)),
        plate_image_url=data.get("plate_image_url"),
        vehicle_image_url=data.get("vehicle_image_url"),
        verification_status=data.get("verification_status", "COMPLIANT").upper(),
        violations_summary=data.get("violations_summary", ""),
        violations_json=violations_json,
        officer_id=data.get("officer_id"),
        officer_name=data.get("officer_name", "Duty Officer"),
        latitude=float(data.get("latitude", 28.5355)),
        longitude=float(data.get("longitude", 77.3910)),
        location_name=data.get("location_name", "Roadside Surveillance Node"),
        notes=data.get("notes", "Real-time ANPR scan log"),
    )

    created = get_inspection_by_id(new_id)
    return jsonify({
        "success": True,
        "message": f"Inspection {code} logged successfully.",
        "inspection": created,
    }), 201
