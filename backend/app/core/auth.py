"""
app/core/auth.py - Authentication & Role-Based Access Control
============================================================
Smart ANPR Vehicle Verification System

Implements:
1. Cryptographic token generation & validation using itsdangerous URLSafeTimedSerializer.
2. Officer authentication decorator (@auth_required).
3. Role-based access control decorator (@role_required(['ADMIN', 'OFFICER'])).
"""

from functools import wraps
from typing import Any, Callable, Dict, List, Optional
from flask import jsonify, request, g
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature

from app.core.config import Config
from app.models.database import get_officer_by_id

# Serializer instance for stateless auth tokens
_SERIALIZER = URLSafeTimedSerializer(Config.SECRET_KEY, salt="officer-auth-v1")
TOKEN_MAX_AGE_SECONDS = 86400 * 7  # 7 days validity


def generate_auth_token(officer: Dict[str, Any]) -> str:
    """Generate a signed cryptographic token for an authenticated officer."""
    payload = {
        "user_id": officer["id"],
        "username": officer["username"],
        "role": officer["role"],
        "badge_number": officer["badge_number"],
    }
    return _SERIALIZER.dumps(payload)


def verify_auth_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify and unpack a cryptographic token. Returns payload or None."""
    try:
        data = _SERIALIZER.loads(token, max_age=TOKEN_MAX_AGE_SECONDS)
        return data
    except (SignatureExpired, BadSignature, Exception):
        return None


def get_token_from_header() -> Optional[str]:
    """Extract Bearer token from the incoming request Authorization header."""
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header[7:].strip()
    return None


def auth_required(f: Callable) -> Callable:
    """Decorator requiring a valid officer token on protected API endpoints."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_from_header()
        if not token:
            return jsonify({
                "success": False,
                "error": "Authentication required. Please provide a valid Bearer token in Authorization header."
            }), 401

        payload = verify_auth_token(token)
        if not payload:
            return jsonify({
                "success": False,
                "error": "Invalid or expired session token. Please log in again."
            }), 401

        # Look up active officer in database
        officer = get_officer_by_id(payload["user_id"])
        if not officer or not officer.get("is_active"):
            return jsonify({
                "success": False,
                "error": "Officer account is inactive or not found."
            }), 401

        # Store authenticated officer in Flask g
        g.current_officer = officer
        return f(*args, **kwargs)

    return decorated


def role_required(allowed_roles: List[str]) -> Callable:
    """Decorator ensuring current officer has one of the allowed roles."""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        @auth_required
        def decorated(*args, **kwargs):
            current_role = g.current_officer.get("role", "OFFICER")
            if current_role not in allowed_roles:
                return jsonify({
                    "success": False,
                    "error": f"Permission denied. Required role(s): {', '.join(allowed_roles)}. Your role: {current_role}."
                }), 403
            return f(*args, **kwargs)

        return decorated

    return decorator
