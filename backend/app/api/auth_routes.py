"""
app/api/auth_routes.py - Officer Authentication & Role Management API
=====================================================================
Smart ANPR Vehicle Verification System

Endpoints:
- POST /api/auth/login       - Verify officer credentials and return signed token
- GET  /api/auth/me          - Retrieve current authenticated officer session details
- GET  /api/auth/officers    - List all registered officers (ADMIN only)
- POST /api/auth/officers    - Register new officer (ADMIN only)
"""

from flask import Blueprint, jsonify, request, g
from werkzeug.security import check_password_hash, generate_password_hash

from app.core.auth import generate_auth_token, auth_required, role_required
from app.models.database import (
    get_officer_by_username,
    get_officer_by_id,
    get_all_officers,
    insert_officer,
    update_officer,
    get_officer_preferences,
    update_officer_preferences,
)

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/auth/login", methods=["POST"])
def login():
    """
    POST /api/auth/login
    Authenticates an officer or administrator using real hashed credentials.

    Expected JSON body:
    {
        "username": "officer" | "admin",
        "password": "Officer@123" | "Admin@123"
    }
    """
    data = request.get_json(silent=True) or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({
            "success": False,
            "error": "Both username (or Officer ID) and password are required."
        }), 400

    # Look up officer by username in database
    officer = get_officer_by_username(username)
    if not officer:
        return jsonify({
            "success": False,
            "error": "Invalid officer credentials. Check Officer ID or username."
        }), 401

    if not officer.get("is_active"):
        return jsonify({
            "success": False,
            "error": "This officer account has been deactivated. Please contact an administrator."
        }), 403

    # Verify password hash
    password_hash = officer.get("password_hash", "")
    if not check_password_hash(password_hash, password):
        return jsonify({
            "success": False,
            "error": "Invalid password provided. Please verify your credentials."
        }), 401

    # Issue token
    token = generate_auth_token(officer)

    # Retrieve stored customization preferences
    prefs = get_officer_preferences(officer["id"])

    # Return safe officer dictionary (excluding password_hash)
    safe_officer = {
        "id": officer["id"],
        "username": officer["username"],
        "full_name": officer["full_name"],
        "badge_number": officer["badge_number"],
        "role": officer["role"],
        "station_id": officer["station_id"],
        "preferences": prefs,
        "created_at": officer.get("created_at"),
    }

    return jsonify({
        "success": True,
        "message": f"Welcome, {safe_officer['full_name']} ({safe_officer['role']}). Authentication successful.",
        "token": token,
        "officer": safe_officer,
    }), 200


@auth_bp.route("/auth/me", methods=["GET"])
@auth_required
def get_me():
    """
    GET /api/auth/me
    Retrieves the currently authenticated officer's profile and preferences.
    """
    officer = g.current_officer
    prefs = get_officer_preferences(officer["id"])
    return jsonify({
        "success": True,
        "officer": {
            "id": officer["id"],
            "username": officer["username"],
            "full_name": officer["full_name"],
            "badge_number": officer["badge_number"],
            "role": officer["role"],
            "station_id": officer["station_id"],
            "preferences": prefs,
            "created_at": officer.get("created_at"),
        }
    }), 200


@auth_bp.route("/auth/preferences", methods=["GET"])
@auth_required
def get_preferences():
    """
    GET /api/auth/preferences
    Retrieve customization preferences for current duty officer.
    """
    officer_id = g.current_officer["id"]
    prefs = get_officer_preferences(officer_id)
    return jsonify({
        "success": True,
        "preferences": prefs
    }), 200


@auth_bp.route("/auth/preferences", methods=["PUT"])
@auth_required
def save_preferences():
    """
    PUT /api/auth/preferences
    Save customization preferences (theme, language, date/time format) per user account.
    """
    officer_id = g.current_officer["id"]
    data = request.get_json(silent=True) or {}
    update_officer_preferences(officer_id, data)
    updated = get_officer_preferences(officer_id)
    return jsonify({
        "success": True,
        "message": "User customization preferences updated successfully.",
        "preferences": updated
    }), 200


@auth_bp.route("/auth/officers", methods=["GET"])
@role_required(["ADMIN"])
def list_officers():
    """
    GET /api/auth/officers
    Retrieve all officer accounts (Admin only).
    """
    officers = get_all_officers()
    return jsonify({
        "success": True,
        "count": len(officers),
        "officers": officers,
    }), 200


@auth_bp.route("/auth/officers", methods=["POST"])
@role_required(["ADMIN"])
def create_officer():
    """
    POST /api/auth/officers
    Create a new officer account (Admin only).
    """
    data = request.get_json(silent=True) or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")
    full_name = data.get("full_name", "").strip()
    badge_number = data.get("badge_number", "").strip()
    role = data.get("role", "OFFICER").strip().upper()
    station_id = data.get("station_id", "SEC-04-EXPRESSWAY").strip()

    if not username or not password or not full_name or not badge_number:
        return jsonify({
            "success": False,
            "error": "Fields username, password, full_name, and badge_number are required."
        }), 400

    if role not in ("ADMIN", "OFFICER"):
        return jsonify({
            "success": False,
            "error": "Invalid role specified. Role must be 'ADMIN' or 'OFFICER'."
        }), 400

    existing = get_officer_by_username(username)
    if existing:
        return jsonify({
            "success": False,
            "error": f"An officer with username '{username}' already exists."
        }), 409

    password_hash = generate_password_hash(password)
    try:
        new_id = insert_officer(
            username=username,
            password_hash=password_hash,
            full_name=full_name,
            badge_number=badge_number,
            role=role,
            station_id=station_id,
        )

        new_officer = get_officer_by_id(new_id)
        return jsonify({
            "success": True,
            "message": f"Officer '{full_name}' ({badge_number}) created successfully.",
            "officer_id": new_id,
            "officer": {
                "id": new_officer["id"],
                "username": new_officer["username"],
                "full_name": new_officer["full_name"],
                "badge_number": new_officer["badge_number"],
                "role": new_officer["role"],
                "station_id": new_officer["station_id"],
                "created_at": new_officer.get("created_at"),
            } if new_officer else None,
        }), 201
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to register officer: {str(e)}"
        }), 500


@auth_bp.route("/auth/officers/<int:officer_id>", methods=["PUT"])
@role_required(["ADMIN"])
def modify_officer(officer_id: int):
    """
    PUT /api/auth/officers/<id>
    Update officer details or toggle active status (Admin only).
    """
    data = request.get_json(silent=True) or {}
    full_name = data.get("full_name")
    role = data.get("role")
    station_id = data.get("station_id")
    is_active = data.get("is_active")

    existing = get_officer_by_id(officer_id)
    if not existing:
        return jsonify({
            "success": False,
            "error": f"Officer with ID {officer_id} not found."
        }), 404

    success = update_officer(
        officer_id=officer_id,
        full_name=full_name,
        role=role,
        station_id=station_id,
        is_active=is_active,
    )

    updated = get_officer_by_id(officer_id)
    return jsonify({
        "success": True,
        "message": f"Officer #{officer_id} updated successfully.",
        "officer": updated,
    }), 200

