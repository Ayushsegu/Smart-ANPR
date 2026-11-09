"""
app/api/challan_routes.py - Digital Challan & QR-PDF Engine API Endpoints
========================================================================
Smart ANPR Vehicle Verification System

Endpoints implemented:
- POST /api/challans/generate            - Generate digital challan with itemized fines, PDF & QR
- GET  /api/challans/<challan_number>    - Retrieve full challan details & verification info
- GET  /api/challans/<challan_number>/pdf - Download/stream official PDF challan receipt
- GET  /api/challans/<challan_number>/qr  - Download/stream scannable verification QR barcode
- POST /api/challans/<challan_number>/pay - Process academic demonstration payment status update
"""

from pathlib import Path
from flask import Blueprint, jsonify, request, send_file

from app.core.config import Config
from app.services.challan_service import (
    generate_digital_challan,
    get_challan_details,
    process_demonstration_payment,
)
from app.services.pdf_generator import generate_challan_pdf
from app.services.qr_generator import generate_challan_qr

challan_bp = Blueprint("challan_bp", __name__)


# ============================================================================
# 1. GENERATE DIGITAL CHALLAN
# ============================================================================

@challan_bp.route("/challans/generate", methods=["POST"])
def api_generate_challan():
    """
    Generate an official digital traffic challan.

    Expected JSON Body:
    {
        "registration_number": "MH12DE5678",       (required)
        "violations": ["EXPIRED_PUC"],              (optional, auto-detects if omitted)
        "description": "Officer field note",        (optional)
        "custom_overrides": {"EXPIRED_PUC": 10000} (optional fine schedule override)
    }

    Returns:
        HTTP 201: Created challan details, itemized fine breakdown, PDF and QR URLs.
        HTTP 400: Missing or invalid request parameters.
        HTTP 404: Vehicle registration number not found.
        HTTP 422: Vehicle has no active violations.
    """
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({
                "success": False,
                "error": "Request body must be a valid JSON object."
            }), 400

        registration_number = data.get("registration_number")
        if not registration_number or not str(registration_number).strip():
            return jsonify({
                "success": False,
                "error": "Missing required field: 'registration_number'."
            }), 400

        violations = data.get("violations")
        description = data.get("description", "")
        custom_overrides = data.get("custom_overrides")

        # Determine server base URL from request host
        server_base = request.host_url.rstrip("/")

        result = generate_digital_challan(
            registration_number=registration_number,
            violations=violations,
            description=description,
            custom_overrides=custom_overrides,
            base_url=server_base,
        )

        return jsonify(result), 201

    except ValueError as ve:
        err_msg = str(ve)
        if "not registered" in err_msg.lower():
            return jsonify({"success": False, "error": err_msg}), 404
        if "no detected violations" in err_msg.lower():
            return jsonify({"success": False, "error": err_msg}), 422
        return jsonify({"success": False, "error": err_msg}), 400

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to generate digital challan: {str(e)}"
        }), 500


# ============================================================================
# 2. RETRIEVE CHALLAN DETAILS (VERIFICATION ENDPOINT)
# ============================================================================

@challan_bp.route("/challans/<challan_number>", methods=["GET"])
def api_get_challan(challan_number: str):
    """
    Retrieve full details for a citation by unique challan number.
    This also serves as the QR code verification target endpoint.

    Returns:
        HTTP 200: Full details, fine breakdown, payment status, and artifact URLs.
        HTTP 404: Challan not found.
    """
    try:
        clean_num = challan_number.strip().upper()
        server_base = request.host_url.rstrip("/")
        details = get_challan_details(clean_num, base_url=server_base)

        if not details:
            return jsonify({
                "success": False,
                "error": f"Challan citation '{clean_num}' not found in the enforcement database."
            }), 404

        return jsonify(details), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to retrieve challan citation: {str(e)}"
        }), 500


# ============================================================================
# 3. STREAM / DOWNLOAD PDF RECEIPT
# ============================================================================

@challan_bp.route("/challans/<challan_number>/pdf", methods=["GET"])
def api_get_challan_pdf(challan_number: str):
    """
    Stream or download the official PDF receipt for a traffic challan.
    If the PDF file has not yet been compiled on disk, it is dynamically generated on-the-fly.

    Returns:
        application/pdf binary file stream, or HTTP 404 if challan not found.
    """
    try:
        clean_num = challan_number.strip().upper()
        details = get_challan_details(clean_num)
        if not details:
            return jsonify({
                "success": False,
                "error": f"Challan citation '{clean_num}' does not exist."
            }), 404

        pdf_path = Path(Config.PDF_OUTPUT_DIR) / f"{clean_num}.pdf"

        # Dynamically compile PDF if missing
        if not pdf_path.is_file():
            qr_path = Path(Config.QR_OUTPUT_DIR) / f"{clean_num}.png"
            if not qr_path.is_file():
                generate_challan_qr(clean_num)

            pdf_payload = {
                "challan_number": clean_num,
                "registration_number": details["vehicle"]["registration_number"],
                "owner_name": details["vehicle"]["owner_name"],
                "vehicle_type": details["vehicle"]["vehicle_type"],
                "vehicle_model": details["vehicle"]["vehicle_model"],
                "violation_type": details["violation_type"],
                "fine_amount": details["fine_amount"],
                "challan_date": details["challan_date"],
                "payment_status": details["payment_status"],
                "challan_status": details.get("challan_status", "ISSUED"),
                "description": details.get("description", ""),
                "fine_breakdown": details.get("fine_breakdown"),
            }
            generate_challan_pdf(pdf_payload, qr_image_path=str(qr_path))

        return send_file(
            str(pdf_path),
            mimetype="application/pdf",
            as_attachment=False,
            download_name=f"{clean_num}.pdf"
        )

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to retrieve PDF receipt: {str(e)}"
        }), 500


# ============================================================================
# 4. STREAM / VIEW QR CODE IMAGE
# ============================================================================

@challan_bp.route("/challans/<challan_number>/qr", methods=["GET"])
def api_get_challan_qr(challan_number: str):
    """
    Stream the PNG verification QR code image for a citation.
    If the image is not found on disk, it is dynamically generated.

    Returns:
        image/png binary file stream, or HTTP 404 if challan not found.
    """
    try:
        clean_num = challan_number.strip().upper()
        details = get_challan_details(clean_num)
        if not details:
            return jsonify({
                "success": False,
                "error": f"Challan citation '{clean_num}' does not exist."
            }), 404

        qr_path = Path(Config.QR_OUTPUT_DIR) / f"{clean_num}.png"
        if not qr_path.is_file():
            server_base = request.host_url.rstrip("/")
            generate_challan_qr(clean_num, base_url=server_base)

        return send_file(
            str(qr_path),
            mimetype="image/png",
            as_attachment=False,
            download_name=f"{clean_num}.png"
        )

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to retrieve QR code image: {str(e)}"
        }), 500


# ============================================================================
# 5. DEMONSTRATION PAYMENT SIMULATION
# ============================================================================

@challan_bp.route("/challans/<challan_number>/pay", methods=["POST"])
def api_pay_challan(challan_number: str):
    """
    Process an academic demonstration payment simulation for a challan citation.
    Updates the payment status ('PAID', 'FAILED', 'PENDING') and updates the PDF.

    Request Body (optional):
        {"action": "PAY"}  (options: 'PAY', 'FAIL', 'RESET')

    Returns:
        HTTP 200: Updated challan details and demonstration confirmation.
        HTTP 404: Challan not found.
    """
    try:
        clean_num = challan_number.strip().upper()
        data = request.get_json(silent=True) or {}
        action = data.get("action", "PAY")

        result = process_demonstration_payment(clean_num, action=action)
        if not result:
            return jsonify({
                "success": False,
                "error": f"Challan citation '{clean_num}' not found."
            }), 404

        return jsonify(result), 200

    except ValueError as ve:
        return jsonify({"success": False, "error": str(ve)}), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to process demonstration payment: {str(e)}"
        }), 500
