"""
verify_endpoints.py - Quick script to verify and print API responses
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

print("=" * 65)
print("1. GET /api/health")
print("=" * 65)
r1 = client.get("/api/health")
print(f"HTTP Status: {r1.status_code}")
print(json.dumps(r1.get_json(), indent=2))

print("\n" + "=" * 65)
print("2. GET /api/vehicles (Summary & Sample Vehicle)")
print("=" * 65)
r2 = client.get("/api/vehicles")
d2 = r2.get_json()
print(f"HTTP Status: {r2.status_code} | Total Count: {d2['count']}")
print(json.dumps(d2['vehicles'][0], indent=2))

print("\n" + "=" * 65)
print("3. GET /api/vehicles/DL01AB1234 (Search by Plate)")
print("=" * 65)
r3 = client.get("/api/vehicles/DL01AB1234")
print(f"HTTP Status: {r3.status_code}")
print(json.dumps(r3.get_json(), indent=2))

print("\n" + "=" * 65)
print("4. GET /api/vehicles/MH12DE5678/documents (Documents by Plate)")
print("=" * 65)
r4 = client.get("/api/vehicles/MH12DE5678/documents")
print(f"HTTP Status: {r4.status_code}")
print(json.dumps(r4.get_json(), indent=2))

print("\n" + "=" * 65)
print("5. GET /api/challans (Summary & First 2 Citations)")
print("=" * 65)
r5 = client.get("/api/challans")
d5 = r5.get_json()
print(f"HTTP Status: {r5.status_code} | Total Citations: {d5['count']}")
print(json.dumps(d5['challans'][:2], indent=2))

print("\n" + "=" * 65)
print("6. GET /api/vehicles/NONEXISTENT (404 Error Handling)")
print("=" * 65)
r6 = client.get("/api/vehicles/NONEXISTENT")
print(f"HTTP Status: {r6.status_code}")
print(json.dumps(r6.get_json(), indent=2))
