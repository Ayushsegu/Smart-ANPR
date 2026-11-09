"""
app/api/helmet_routes.py - Two-Wheeler Helmet Detection & Rider Safety APIs
===========================================================================
Smart ANPR Vehicle Verification System

Endpoints:
- POST /api/helmet/detect - Analyzes vehicle image for rider helmet compliance
"""

from flask import Blueprint, jsonify, request
from app.services.helmet_detector import HelmetDetector

helmet_bp = Blueprint("helmet", __name__)
detector = HelmetDetector()


@helmet_bp.route("/helmet/detect", methods=["POST"])
def detect_helmet():
    """
    POST /api/helmet/detect
    Accepts image file under 'image' or 'file' (multipart/form-data).
    """
    file_obj = request.files.get("image") or request.files.get("file")
    if not file_obj or file_obj.filename == "":
        return jsonify({
            "success": False,
            "error": "No image file provided. Please attach an image under 'image' or 'file'."
        }), 400

    try:
        image_bytes = file_obj.read()
        result = detector.detect_helmet(image_bytes)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to execute helmet detection: {str(e)}"
        }), 500


@helmet_bp.route("/helmet/status", methods=["GET"])
def helmet_status():
    """
    GET /api/helmet/status
    Returns detector model state and whether dedicated weights are loaded.
    """
    return jsonify({
        "success": True,
        "is_dedicated_model": detector.is_dedicated_model,
        "weights_status": detector.weights_status,
        "model_loaded": detector.model is not None,
    }), 200
