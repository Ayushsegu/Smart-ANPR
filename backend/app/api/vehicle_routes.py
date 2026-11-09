"""
app/api/vehicle_routes.py - Vehicle, Document, Verification & Challan API Routes
================================================================================
Smart ANPR Vehicle Verification System

Endpoints implemented:
- GET  /api/vehicles
- GET  /api/vehicles/<registration_number>
- GET  /api/vehicles/<registration_number>/documents
- GET  /api/challans
- GET  /api/vehicles/<registration_number>/verify    (Phase 3)
- POST /api/vehicles/verify                          (Phase 3)
- POST /api/challans/calculate                       (Phase 3)
"""

from flask import Blueprint, jsonify, request
from app.models.database import (
    get_all_vehicles,
    get_vehicle_by_plate,
    get_documents_by_plate,
    get_all_challans,
    get_challans_by_vehicle_id,
    insert_demo_vehicle,
    get_demo_fleet_metrics,
)
from app.services.vehicle_verifier import verify_vehicle_compliance
from app.services.fine_calculator import calculate_fine_breakdown
from app.services.document_verifier import parse_date

vehicle_bp = Blueprint("vehicles", __name__)


# ============================================================================
# Phase 2 Endpoints (Preserved & Reused)
# ============================================================================

@vehicle_bp.route("/vehicles/metrics", methods=["GET"])
def get_fleet_metrics():
    """Retrieve dynamic fleet compliance metrics calculated from real SQLite records."""
    try:
        metrics = get_demo_fleet_metrics()
        return jsonify({
            "success": True,
            "metrics": metrics
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to compute fleet metrics: {str(e)}"
        }), 500


@vehicle_bp.route("/vehicles", methods=["GET"])
def list_vehicles():
    """
    Retrieve registered vehicles in the database with optional search and filters.
    Query parameters:
    - search: registration number, owner name, model, demo_id
    - vehicle_type: Car, Motorcycle, Scooter, SUV, Commercial, Transport
    - state: Delhi, Haryana, Maharashtra, Karnataka, etc.
    - is_demo: 1 (demo only) or 0
    """
    try:
        vehicles = get_all_vehicles()
        search = request.args.get("search", "").strip().lower()
        v_type = request.args.get("vehicle_type", "").strip().lower()
        state = request.args.get("state", "").strip().lower()
        is_demo_param = request.args.get("is_demo")

        filtered = vehicles
        if search:
            filtered = [
                v for v in filtered
                if search in (v.get("registration_number") or "").lower()
                or search in (v.get("owner_name") or "").lower()
                or search in (v.get("vehicle_model") or "").lower()
                or search in (v.get("demo_id") or "").lower()
                or search in (v.get("manufacturer") or "").lower()
            ]

        if v_type and v_type != "all":
            filtered = [
                v for v in filtered
                if (v.get("vehicle_type") or "").lower() == v_type
                or (v.get("vehicle_class") or "").lower() == v_type
            ]

        if state and state != "all":
            filtered = [
                v for v in filtered
                if state in (v.get("state") or "").lower()
            ]

        if is_demo_param is not None:
            val = 1 if is_demo_param.lower() in ("1", "true") else 0
            filtered = [v for v in filtered if v.get("is_demo", 1) == val]

        return jsonify({
            "success": True,
            "count": len(filtered),
            "total_unfiltered": len(vehicles),
            "vehicles": filtered
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to retrieve vehicles: {str(e)}"
        }), 500


@vehicle_bp.route("/vehicles", methods=["POST"])
def register_demo_vehicle():
    """
    POST /api/vehicles
    Register a new demo vehicle into the local database (Admin/Officer capability).
    """
    try:
        data = request.get_json(silent=True) or {}
        reg_num = data.get("registration_number", "").strip().upper()
        owner = data.get("owner_name", "").strip()
        v_type = data.get("vehicle_type", "Car").strip()
        v_model = data.get("vehicle_model", "").strip()

        if not reg_num or not owner or not v_model:
            return jsonify({
                "success": False,
                "error": "Fields 'registration_number', 'owner_name', and 'vehicle_model' are required."
            }), 400

        from datetime import datetime
        reg_date = data.get("registration_date") or datetime.now().date().isoformat()

        veh_id = insert_demo_vehicle(
            registration_number=reg_num,
            owner_name=owner,
            vehicle_type=v_type,
            vehicle_model=v_model,
            registration_date=reg_date,
            demo_id=data.get("demo_id") or f"DEMO-{reg_num[-4:]}",
            is_demo=1,
            state=data.get("state", "Delhi"),
            rto_code=data.get("rto_code", "DL-01"),
            registration_status=data.get("registration_status", "ACTIVE"),
            owner_phone=data.get("owner_phone", "+91-98765-00000"),
            owner_address=data.get("owner_address", "New Delhi, India"),
            manufacturer=data.get("manufacturer", "Maruti Suzuki"),
            vehicle_class=data.get("vehicle_class", v_type),
            vehicle_color=data.get("vehicle_color", "White"),
            fuel_type=data.get("fuel_type", "Petrol"),
            manufacturing_year=int(data.get("manufacturing_year", 2022)),
            chassis_number=data.get("chassis_number") or f"SYN-CHAS-{reg_num}",
            engine_number=data.get("engine_number") or f"SYN-ENG-{reg_num}",
            driver_name=data.get("driver_name", owner),
            driver_license_number=data.get("driver_license_number") or f"DL-{reg_num[:4]}2020",
            driver_license_class=data.get("driver_license_class", "LMV"),
            driver_license_expiry=data.get("driver_license_expiry", "2032-12-31"),
            driver_license_status=data.get("driver_license_status", "VALID"),
        )

        created = get_vehicle_by_plate(reg_num)
        return jsonify({
            "success": True,
            "message": f"Demo vehicle {reg_num} successfully registered.",
            "vehicle": created
        }), 201
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to register demo vehicle: {str(e)}"
        }), 500


@vehicle_bp.route("/vehicles/<registration_number>", methods=["GET"])
def get_vehicle(registration_number: str):
    """Look up a single vehicle by its registration number (case-insensitive)."""
    try:
        clean_plate = registration_number.strip().upper()
        vehicle = get_vehicle_by_plate(clean_plate)
        if not vehicle:
            return jsonify({
                "success": False,
                "error": f"Vehicle with registration number '{clean_plate}' not found."
            }), 404

        return jsonify({
            "success": True,
            "vehicle": vehicle
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Database lookup failed: {str(e)}"
        }), 500


@vehicle_bp.route("/vehicles/<registration_number>/documents", methods=["GET"])
def get_vehicle_documents(registration_number: str):
    """Retrieve all 4 compliance documents for a specific vehicle by license plate."""
    try:
        clean_plate = registration_number.strip().upper()
        result = get_documents_by_plate(clean_plate)
        if not result:
            return jsonify({
                "success": False,
                "error": f"Vehicle with registration number '{clean_plate}' not found."
            }), 404

        return jsonify({
            "success": True,
            "registration_number": clean_plate,
            "vehicle": result["vehicle"],
            "documents_count": len(result["documents"]),
            "documents": result["documents"]
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to fetch documents: {str(e)}"
        }), 500


@vehicle_bp.route("/challans", methods=["GET"])
def list_challans():
    """
    Retrieve all traffic challan citations.
    Supports optional query filter: ?registration_number=DL01AB1234
    """
    try:
        reg_num = request.args.get("registration_number")
        all_challans = get_all_challans()

        if reg_num:
            clean_plate = reg_num.strip().upper()
            filtered = [
                c for c in all_challans
                if c.get("registration_number", "").upper() == clean_plate
            ]
            return jsonify({
                "success": True,
                "registration_number_filter": clean_plate,
                "count": len(filtered),
                "challans": filtered
            }), 200

        return jsonify({
            "success": True,
            "count": len(all_challans),
            "challans": all_challans
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to retrieve challans: {str(e)}"
        }), 500


# ============================================================================
# Phase 3 Endpoints: Verification & Fine Calculation Engine
# ============================================================================

@vehicle_bp.route("/vehicles/<registration_number>/verify", methods=["GET"])
def verify_vehicle_endpoint(registration_number: str):
    """
    GET /api/vehicles/<registration_number>/verify
    Inspect compliance for all 4 mandatory documents (RC, Insurance, PUC, Road Tax),
    detect violations, count expired/expiring documents, and compute fine breakdown.
    
    Optional query parameter:
        ?reference_date=YYYY-MM-DD  (allows evaluating as of a specific date)
    """
    try:
        clean_plate = registration_number.strip().upper()
        ref_date_str = request.args.get("reference_date")
        ref_date = parse_date(ref_date_str) if ref_date_str else None

        result = verify_vehicle_compliance(clean_plate, reference_date=ref_date)
        if not result:
            return jsonify({
                "success": False,
                "error": f"Vehicle with registration number '{clean_plate}' not found in registry."
            }), 404

        return jsonify(result), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Verification inspection failed: {str(e)}"
        }), 500


@vehicle_bp.route("/vehicles/verify", methods=["POST"])
def verify_vehicle_post():
    """
    POST /api/vehicles/verify
    Accepts JSON body:
        {
            "registration_number": "DL01AB1234",
            "reference_date": "YYYY-MM-DD"  // optional
        }
    """
    try:
        data = request.get_json(silent=True) or {}
        registration_number = data.get("registration_number")

        if not registration_number or not str(registration_number).strip():
            return jsonify({
                "success": False,
                "error": "Missing required field: 'registration_number' is required in request body."
            }), 400

        clean_plate = str(registration_number).strip().upper()
        ref_date_str = data.get("reference_date")
        ref_date = parse_date(ref_date_str) if ref_date_str else None

        result = verify_vehicle_compliance(clean_plate, reference_date=ref_date)
        if not result:
            return jsonify({
                "success": False,
                "error": f"Vehicle with registration number '{clean_plate}' not found in registry."
            }), 404

        return jsonify(result), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Verification processing failed: {str(e)}"
        }), 500


@vehicle_bp.route("/challans/calculate", methods=["POST"])
def calculate_challan_fine():
    """
    POST /api/challans/calculate
    Calculates itemized fines for a list of violations or for a vehicle.

    Supported JSON payloads:
    1. By list of violation codes:
        {
            "violations": ["EXPIRED_INSURANCE", "EXPIRED_PUC"],
            "custom_overrides": {"EXPIRED_INSURANCE": 2500.0} // optional
        }
    2. By vehicle registration number:
        {
            "registration_number": "MH12DE5678",
            "additional_violations": ["SIGNAL_JUMP"] // optional
        }
    """
    try:
        data = request.get_json(silent=True) or {}
        violations_input = data.get("violations")
        reg_number = data.get("registration_number")
        custom_overrides = data.get("custom_overrides")

        if not violations_input and not reg_number:
            return jsonify({
                "success": False,
                "error": "Request body must contain either 'violations' (list of violation codes) or 'registration_number'."
            }), 400

        collected_violations = []

        # If registration_number is provided, retrieve its detected document violations
        if reg_number:
            clean_plate = str(reg_number).strip().upper()
            ref_date_str = data.get("reference_date")
            ref_date = parse_date(ref_date_str) if ref_date_str else None

            verification = verify_vehicle_compliance(clean_plate, reference_date=ref_date)
            if not verification:
                return jsonify({
                    "success": False,
                    "error": f"Vehicle '{clean_plate}' not found for fine calculation."
                }), 404

            collected_violations.extend(verification.get("violations", []))

            # Include any additional manual violations (e.g. Speeding, Signal jump)
            additional = data.get("additional_violations", [])
            if isinstance(additional, list):
                collected_violations.extend(additional)

        # If direct violations list is provided
        if violations_input:
            if not isinstance(violations_input, list):
                return jsonify({
                    "success": False,
                    "error": "'violations' field must be a JSON array of violation codes."
                }), 400
            collected_violations.extend(violations_input)

        # Calculate fine breakdown
        breakdown = calculate_fine_breakdown(
            violations=collected_violations,
            custom_overrides=custom_overrides
        )

        return jsonify({
            "success": True,
            "registration_number": reg_number.strip().upper() if reg_number else None,
            "calculation": breakdown
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Fine calculation failed: {str(e)}"
        }), 500
