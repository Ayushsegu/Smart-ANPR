"""
demo_anpr_pipeline.py - Live ANPR & OCR Processing Demonstration
=================================================================
Smart ANPR Vehicle Verification System

Demonstrates actual API responses for Phase 4 endpoint:
- POST /api/anpr/upload
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
samples_dir = Path(Config.SAMPLES_DIR)

print("=" * 75)
print("1. POST /api/anpr/upload - Car with DL01AB1234 (Compliant Vehicle)")
print("=" * 75)
car_path = samples_dir / "sample_car_DL01AB1234.jpg"
with open(car_path, "rb") as f:
    r1 = client.post(
        "/api/anpr/upload",
        data={"image": (f, "sample_car_DL01AB1234.jpg"), "verify": "true"},
        content_type="multipart/form-data"
    )
print(f"HTTP Status: {r1.status_code}")
print(json.dumps(r1.get_json(), indent=2))

print("\n" + "=" * 75)
print("2. POST /api/anpr/upload - Commercial Vehicle with MH12DE5678 (Expired PUC)")
print("=" * 75)
comm_path = samples_dir / "sample_commercial_MH12DE5678.jpg"
with open(comm_path, "rb") as f:
    r2 = client.post(
        "/api/anpr/upload",
        data={"image": (f, "sample_commercial_MH12DE5678.jpg"), "verify": "true"},
        content_type="multipart/form-data"
    )
print(f"HTTP Status: {r2.status_code}")
print(json.dumps(r2.get_json(), indent=2))

print("\n" + "=" * 75)
print("3. POST /api/anpr/upload - Negative Test: Image with No Plate")
print("=" * 75)
no_plate_path = samples_dir / "sample_road_no_plate.jpg"
with open(no_plate_path, "rb") as f:
    r3 = client.post(
        "/api/anpr/upload",
        data={"image": (f, "sample_road_no_plate.jpg")},
        content_type="multipart/form-data"
    )
print(f"HTTP Status: {r3.status_code}")
print(json.dumps(r3.get_json(), indent=2))

print("\n" + "=" * 75)
print("4. POST /api/anpr/upload - Invalid Format Test: Non-image file (.txt)")
print("=" * 75)
txt_path = samples_dir / "sample_invalid.txt"
with open(txt_path, "rb") as f:
    r4 = client.post(
        "/api/anpr/upload",
        data={"image": (f, "sample_invalid.txt")},
        content_type="multipart/form-data"
    )
print(f"HTTP Status: {r4.status_code}")
print(json.dumps(r4.get_json(), indent=2))
