"""
app/api/anpr_routes.py - ANPR Image Processing & OCR API Routes
================================================================
Smart ANPR Vehicle Verification System

Endpoints implemented:
- POST /api/anpr/upload
"""

import os
import uuid
from pathlib import Path
from flask import Blueprint, jsonify, request, send_from_directory

from app.core.config import Config
from app.services.anpr_detector import process_vehicle_image, validate_image_file
from app.services.ocr_service import read_plate_text
from app.services.vehicle_verifier import verify_vehicle_compliance
from app.services.document_verifier import parse_date

anpr_bp = Blueprint("anpr", __name__)


@anpr_bp.route("/anpr/upload", methods=["POST"])
def anpr_upload():
    """
    POST /api/anpr/upload
    Accepts a vehicle image, detects the license plate, crops it, extracts text
    via EasyOCR, cleans and validates the plate number, and optionally cross-references
    the database for full compliance verification.
    
    Form Data:
        image / file: The vehicle image file (multipart/form-data)
        verify: 'true' (default: true) to auto-verify against database
        reference_date: YYYY-MM-DD (optional, for verification inspection)
    """
    try:
        # 1. Check for file upload
        file_obj = request.files.get("image") or request.files.get("file")
        if not file_obj or file_obj.filename == "":
            return jsonify({
                "success": False,
                "processing_status": "MISSING_FILE",
                "error": "No image file provided. Please attach a vehicle image under 'image' or 'file' field."
            }), 400

        filename = file_obj.filename
        file_bytes = file_obj.read()

        # 2. Image validation
        is_valid, err_msg, image_bgr = validate_image_file(file_bytes, filename)
        if not is_valid:
            status_code = 413 if "size exceeds" in (err_msg or "") else 400
            return jsonify({
                "success": False,
                "processing_status": "INVALID_IMAGE",
                "error": err_msg
            }), status_code

        # 3. Save original uploaded vehicle image
        upload_dir = Path(Config.UPLOAD_DIR)
        upload_dir.mkdir(parents=True, exist_ok=True)

        ext = Path(filename).suffix.lower() or ".jpg"
        unique_upload_name = f"upload_{uuid.uuid4().hex[:12]}{ext}"
        upload_path = upload_dir / unique_upload_name
        with open(upload_path, "wb") as f:
            f.write(file_bytes)

        uploaded_url = f"/static/uploads/{unique_upload_name}"

        # 4. Plate Detection and Cropping
        detection_res = process_vehicle_image(image_bgr, save_crops=True)
        if not detection_res["plate_detected"]:
            return jsonify({
                "success": False,
                "processing_status": "NO_PLATE_DETECTED",
                "error": "No number plate detected in uploaded vehicle image.",
                "detection_method": detection_res["detection_method"],
                "weights_available": detection_res["weights_available"],
                "uploaded_image_url": uploaded_url
            }), 422

        primary_detection = detection_res["primary"]
        crop_image = primary_detection["crop_image"]
        crop_url = primary_detection["crop_url"]
        bounding_box = primary_detection["box"]
        detection_conf = primary_detection["confidence"]

        # 5. EasyOCR Character Extraction
        ocr_res = read_plate_text(crop_image, preprocess=True)
        raw_ocr_text = ocr_res.get("raw_text", "")
        ocr_confidence = ocr_res.get("ocr_confidence", 0.0)
        cleaned_info = ocr_res.get("cleaned", {})
        final_plate = cleaned_info.get("final_registration_number", "")

        # 6. Optional Vehicle Compliance Verification (Phase 3 Integration)
        auto_verify = request.form.get("verify", "true").lower() in ("true", "1", "yes")
        ref_date_str = request.form.get("reference_date")
        ref_date = parse_date(ref_date_str) if ref_date_str else None

        verification_data = None
        if auto_verify and final_plate:
            verification_data = verify_vehicle_compliance(final_plate, reference_date=ref_date)

        # Multi-plate detection note
        multiple_plates = detection_res["detections_count"] > 1

        # Auto-log into inspections table
        inspection_rec = None
        try:
            from app.models.database import insert_inspection
            import json, time
            v_status = "COMPLIANT"
            v_summary = "All documents valid"
            v_list = []
            if verification_data and verification_data.get("violations"):
                v_list = verification_data["violations"]
                v_status = "VIOLATION"
                v_summary = ", ".join([v.get("title", v.get("violation_code", "Violation")) for v in v_list])
            elif verification_data and not verification_data.get("is_registered"):
                v_status = "UNREGISTERED"
                v_summary = "Vehicle not found in national registry"

            lat = float(request.form.get("latitude") or 28.5355)
            lon = float(request.form.get("longitude") or 77.3910)
            loc = request.form.get("location_name") or "Sector 04 Expressway Checkpoint"
            off_name = request.form.get("officer_name") or "Insp. Vikram Sharma"

            code = f"INSP-2026-{int(time.time() * 1000) % 100000:05d}"
            insp_id = insert_inspection(
                inspection_code=code,
                registration_number=final_plate,
                detection_confidence=detection_conf,
                ocr_confidence=ocr_confidence,
                plate_image_url=crop_url,
                vehicle_image_url=uploaded_url,
                verification_status=v_status,
                violations_summary=v_summary,
                violations_json=json.dumps(v_list),
                officer_name=off_name,
                latitude=lat,
                longitude=lon,
                location_name=loc,
                notes="Live ANPR roadside capture",
            )
            inspection_rec = {"id": insp_id, "code": code, "status": v_status}
        except Exception:
            pass

        return jsonify({
            "success": True,
            "processing_status": "SUCCESS",
            "registration_number": final_plate,
            "plate_detected": True,
            "crop_url": crop_url,
            "bbox_confidence": detection_conf,
            "ocr_confidence": ocr_confidence,
            "inspection": inspection_rec,
            "detection": {
                "confidence": detection_conf,
                "method": detection_res["detection_method"],
                "weights_available": detection_res["weights_available"],
                "bounding_box": bounding_box,
                "multiple_plates_detected": multiple_plates,
                "total_plates_found": detection_res["detections_count"],
            },
            "ocr": {
                "raw_text": raw_ocr_text,
                "confidence": ocr_confidence,
                "is_valid_format": cleaned_info.get("is_valid_format", False),
                "format_type": cleaned_info.get("format_type"),
                "components": cleaned_info.get("components"),
                "low_confidence_warning": cleaned_info.get("low_confidence_warning", False),
                "manual_review_needed": cleaned_info.get("manual_review_needed", False),
                "status_message": cleaned_info.get("status_message"),
            },
            "media": {
                "uploaded_image_url": uploaded_url,
                "cropped_plate_url": crop_url,
            },
            "database_verification": verification_data,
            "auto_verification": verification_data
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "processing_status": "INTERNAL_ERROR",
            "error": f"ANPR pipeline processing encountered an unexpected error: {str(e)}"
        }), 500


@anpr_bp.route("/static/<path:subpath>", methods=["GET"])
def serve_static(subpath):
    """Serve uploaded vehicle images and cropped plate images."""
    static_root = Path(Config.STATIC_DIR)
    return send_from_directory(str(static_root), subpath)
