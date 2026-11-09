from datetime import datetime, timezone
from flask import Blueprint, jsonify

health_bp = Blueprint("health", __name__)

@health_bp.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "Smart ANPR Traffic Enforcement API",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "phase": "Phase 6 - Professional Frontend Dashboard Integration"
    }), 200
