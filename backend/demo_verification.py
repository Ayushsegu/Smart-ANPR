"""
demo_verification.py - Live Verification Engine Demonstration Script
=====================================================================
Smart ANPR Vehicle Verification System

Demonstrates actual API responses for Phase 3 endpoints:
- GET  /api/vehicles/<registration_number>/verify
- POST /api/vehicles/verify
- POST /api/challans/calculate
"""

import json
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app import create_app
from app.core.config import Config

app = create_app(Config)
client = app.test_client()

print("=" * 70)
print("1. GET /api/vehicles/DL01AB1234/verify (Clean / Fully Compliant Vehicle)")
print("=" * 70)
r1 = client.get("/api/vehicles/DL01AB1234/verify?reference_date=2026-11-07")
print(f"Status: {r1.status_code}")
print(json.dumps(r1.get_json(), indent=2))

print("\n" + "=" * 70)
print("2. GET /api/vehicles/MH12DE5678/verify (Single Violation: Expired PUC)")
print("=" * 70)
r2 = client.get("/api/vehicles/MH12DE5678/verify?reference_date=2026-11-07")
print(f"Status: {r2.status_code}")
print(json.dumps(r2.get_json(), indent=2))

print("\n" + "=" * 70)
print("3. POST /api/vehicles/verify (Multiple Violations: TN09BK3456)")
print("=" * 70)
r3 = client.post("/api/vehicles/verify", json={
    "registration_number": "TN09BK3456",
    "reference_date": "2026-11-07"
})
print(f"Status: {r3.status_code}")
print(json.dumps(r3.get_json(), indent=2))

print("\n" + "=" * 70)
print("4. POST /api/challans/calculate (Fine Breakdown for Direct Violations)")
print("=" * 70)
r4 = client.post("/api/challans/calculate", json={
    "violations": ["EXPIRED_INSURANCE", "EXPIRED_PUC", "SIGNAL_JUMP"]
})
print(f"Status: {r4.status_code}")
print(json.dumps(r4.get_json(), indent=2))

print("\n" + "=" * 70)
print("5. POST /api/challans/calculate (Fine Breakdown by Vehicle Plate + Speeding)")
print("=" * 70)
r5 = client.post("/api/challans/calculate", json={
    "registration_number": "MH12DE5678",
    "reference_date": "2026-11-07",
    "additional_violations": ["OVER_SPEEDING"]
})
print(f"Status: {r5.status_code}")
print(json.dumps(r5.get_json(), indent=2))
