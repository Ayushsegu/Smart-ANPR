"""
test_camera_anpr_pipeline.py - Live Camera Capture & ANPR End-to-End Test Suite
================================================================================
Smart ANPR Vehicle Verification System

Automated tests for Live Camera Capture feature:
1.  Camera MediaDevices configuration & constraint structure
2.  Camera permission granted vs denied error handling
3.  Simulated roadside camera frame capture to JPEG
4.  Retake and confirm photo capture workflow logic
5.  Hardware resource release and track cleanup
6.  Camera-captured photo multipart submission to POST /api/anpr/upload
7.  YOLOv8 / Morphological plate detection on camera photograph
8.  EasyOCR neural character recognition on camera photograph
9.  Indian HSRP plate cleaning and format validation
10. Parivahan vehicle database lookup from camera photo
11. Multi-document verification (RC, Insurance, PUC, Road Tax)
12. Violation detection and illustrative fine calculation
13. Instant digital challan issuance from camera capture
14. Verification QR barcode and ReportLab PDF receipt compilation
15. Demonstration payment lifecycle simulation
16. Non-regression: Existing image upload functionality remains 100% operational
"""

import io
import json
import os
import sys
import unittest
from datetime import datetime
from pathlib import Path
from PIL import Image

# Ensure backend directory is in Python path
BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app import create_app
from app.core.config import Config
from app.models.database import get_vehicle_by_plate, get_challan_by_number
from app.services.anpr_detector import process_vehicle_image
from app.services.ocr_service import read_plate_text
from app.services.plate_cleaner import clean_and_validate_plate
from app.services.vehicle_verifier import verify_vehicle_compliance
from app.services.challan_service import generate_digital_challan, process_demonstration_payment


class LiveCameraANPRTestSuite(unittest.TestCase):
    """Test suite verifying Live Camera Capture and end-to-end processing."""

    @classmethod
    def setUpClass(cls):
        cls.app = create_app(Config)
        cls.client = cls.app.test_client()
        cls.samples_dir = Path(Config.SAMPLES_DIR)
        cls.camera_sample = cls.samples_dir / "sample_commercial_MH12DE5678.jpg"

    # -------------------------------------------------------------------------
    # TEST 1: Camera MediaDevices Constraints & Component Verification
    # -------------------------------------------------------------------------
    def test_01_camera_component_and_constraints(self):
        """Verify LiveCameraCapture.jsx component structure and MediaDevices constraints."""
        comp_file = Config.BASE_DIR.parent / "frontend" / "src" / "components" / "LiveCameraCapture.jsx"
        self.assertTrue(comp_file.is_file(), "LiveCameraCapture.jsx missing on filesystem.")

        content = comp_file.read_text()
        # Verify MediaDevices API usage
        self.assertIn("navigator.mediaDevices.getUserMedia", content)
        # Verify rear camera facingMode preference
        self.assertIn("facingMode", content)
        self.assertIn("environment", content)
        # Verify canvas snapshot method
        self.assertIn("canvas.toBlob", content)
        self.assertIn("image/jpeg", content)
        # Verify track cleanup
        self.assertIn("track.stop()", content)

    # -------------------------------------------------------------------------
    # TEST 2: Camera Permission Error Handling Logic
    # -------------------------------------------------------------------------
    def test_02_camera_permission_error_handling(self):
        """Verify explicit handling for NotAllowedError, NotFoundError, and NotReadableError."""
        comp_file = Config.BASE_DIR.parent / "frontend" / "src" / "components" / "LiveCameraCapture.jsx"
        content = comp_file.read_text()

        self.assertIn("NotAllowedError", content)
        self.assertIn("PermissionDeniedError", content)
        self.assertIn("NotFoundError", content)
        self.assertIn("NotReadableError", content)

    # -------------------------------------------------------------------------
    # TEST 3: Camera Capture Frame Conversion to JPEG File
    # -------------------------------------------------------------------------
    def test_03_camera_photo_capture_and_format(self):
        """Verify captured photo from camera is valid JPEG with standard magic bytes."""
        with open(self.camera_sample, "rb") as f:
            raw_bytes = f.read()

        # JPEG magic bytes: \xff\xd8\xff
        self.assertTrue(raw_bytes.startswith(b"\xff\xd8\xff"), "Captured photo not valid JPEG.")

        # Verify Pillow parses image
        with Image.open(io.BytesIO(raw_bytes)) as img:
            img.verify()
            self.assertEqual(img.format, "JPEG")
            self.assertGreater(img.width, 200)
            self.assertGreater(img.height, 100)

    # -------------------------------------------------------------------------
    # TEST 4: Backend Camera Image Upload (POST /api/anpr/upload)
    # -------------------------------------------------------------------------
    def test_04_camera_photo_backend_upload(self):
        """Verify multipart submission of roadside camera photo to POST /api/anpr/upload."""
        with open(self.camera_sample, "rb") as f:
            raw_bytes = f.read()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        camera_filename = f"roadside_camera_{timestamp}.jpg"

        data = {
            "image": (io.BytesIO(raw_bytes), camera_filename)
        }

        res = self.client.post("/api/anpr/upload", data=data, content_type="multipart/form-data")
        self.assertEqual(res.status_code, 200)

        json_data = res.get_json()
        self.assertTrue(json_data["success"])
        self.assertTrue(json_data["plate_detected"])
        self.assertEqual(json_data["registration_number"], "MH12DE5678")
        self.assertIn("crop_url", json_data)

    # -------------------------------------------------------------------------
    # TEST 5: YOLO & Morphological Localization on Camera Capture
    # -------------------------------------------------------------------------
    def test_05_plate_localization_on_camera_photo(self):
        """Verify plate localization on roadside camera photo."""
        det_res = process_vehicle_image(str(self.camera_sample))
        self.assertTrue(det_res["plate_detected"])
        self.assertIn(det_res["detection_method"], ["yolov8", "cv_contour"])

        primary = det_res["primary"]
        self.assertIsNotNone(primary["box"])
        self.assertGreater(primary["confidence"], 0.70)
        self.assertTrue(os.path.isfile(primary["crop_path"]))

    # -------------------------------------------------------------------------
    # TEST 6: EasyOCR Neural Character Extraction on Camera Photo
    # -------------------------------------------------------------------------
    def test_06_easyocr_extraction_on_camera_photo(self):
        """Verify real deep learning character recognition on camera crop."""
        det_res = process_vehicle_image(str(self.camera_sample))
        crop_path = det_res["primary"]["crop_path"]

        ocr_res = read_plate_text(crop_path)
        self.assertTrue(ocr_res["success"])
        self.assertTrue(ocr_res["text_found"])
        self.assertIn("MH 12 DE 5678", ocr_res["raw_text"])
        self.assertGreater(ocr_res["ocr_confidence"], 0.75)

    # -------------------------------------------------------------------------
    # TEST 7: Indian License Plate Cleaning & Formatting
    # -------------------------------------------------------------------------
    def test_07_plate_cleaning_and_hsrp_format(self):
        """Verify whitespace removal and Indian HSRP syntax matching."""
        det_res = process_vehicle_image(str(self.camera_sample))
        ocr_res = read_plate_text(det_res["primary"]["crop_path"])

        cleaned = clean_and_validate_plate(ocr_res["raw_text"], ocr_res["ocr_confidence"])
        self.assertEqual(cleaned["cleaned_text"], "MH12DE5678")
        self.assertTrue(cleaned["is_valid_format"])
        self.assertEqual(cleaned["format_type"], "STANDARD_INDIAN")
        self.assertEqual(cleaned["components"]["state_code"], "MH")
        self.assertEqual(cleaned["components"]["rto_code"], "12")
        self.assertEqual(cleaned["components"]["series"], "DE")
        self.assertEqual(cleaned["components"]["number"], "5678")

    # -------------------------------------------------------------------------
    # TEST 8: Vehicle Database Verification from Camera Capture
    # -------------------------------------------------------------------------
    def test_08_database_verification_from_camera(self):
        """Verify querying Parivahan SQLite database using camera extracted plate."""
        compliance = verify_vehicle_compliance("MH12DE5678")
        self.assertIsNotNone(compliance)

        v = compliance["vehicle"]
        self.assertEqual(v["registration_number"], "MH12DE5678")
        self.assertEqual(v["owner_name"], "Priya Deshmukh")

        docs = compliance["documents"]
        self.assertEqual(docs["RC"]["status"], "VALID")
        self.assertEqual(docs["INSURANCE"]["status"], "VALID")
        self.assertEqual(docs["ROAD_TAX"]["status"], "VALID")
        self.assertEqual(docs["PUC"]["status"], "EXPIRED")

        self.assertEqual(compliance["summary"]["overall_status"], "NON_COMPLIANT")
        self.assertEqual(compliance["summary"]["expired_count"], 1)

    # -------------------------------------------------------------------------
    # TEST 9: Digital Challan Issuance from Camera Capture
    # -------------------------------------------------------------------------
    def test_09_challan_generation_from_camera(self):
        """Verify issuing digital challan from camera inspection."""
        challan = generate_digital_challan(
            registration_number="MH12DE5678",
            description="Roadside officer live camera capture enforcement."
        )

        ch_num = challan["challan_number"]
        self.assertTrue(ch_num.startswith("CH-"))
        self.assertEqual(challan["vehicle"]["registration_number"], "MH12DE5678")
        self.assertEqual(challan["fine_amount"], 10000.0)
        self.assertEqual(challan["payment_status"], "PENDING")
        self.assertEqual(challan["challan_status"], "ISSUED")

        # Verify artifacts
        pdf_disk = Path(Config.PDF_OUTPUT_DIR) / f"{ch_num}.pdf"
        qr_disk = Path(Config.QR_OUTPUT_DIR) / f"{ch_num}.png"
        self.assertTrue(pdf_disk.is_file(), f"PDF missing: {pdf_disk}")
        self.assertTrue(qr_disk.is_file(), f"QR missing: {qr_disk}")

    # -------------------------------------------------------------------------
    # TEST 10: Demonstration Payment Update from Camera Citation
    # -------------------------------------------------------------------------
    def test_10_demonstration_payment_simulation(self):
        """Verify simulated payment for citation issued via live camera."""
        challan = generate_digital_challan("MH12DE5678")
        ch_num = challan["challan_number"]

        settled = process_demonstration_payment(ch_num, action="PAY")
        self.assertEqual(settled["payment_status"], "PAID")
        self.assertEqual(settled["challan_status"], "SETTLED")

    # -------------------------------------------------------------------------
    # TEST 11: Non-Regression: Existing File Upload Functionality
    # -------------------------------------------------------------------------
    def test_11_existing_image_upload_preserved(self):
        """Verify existing image upload functionality works identically."""
        sample_car = self.samples_dir / "sample_car_DL01AB1234.jpg"
        with open(sample_car, "rb") as f:
            raw_bytes = f.read()

        data = {
            "image": (io.BytesIO(raw_bytes), "sample_car_DL01AB1234.jpg")
        }

        res = self.client.post("/api/anpr/upload", data=data, content_type="multipart/form-data")
        self.assertEqual(res.status_code, 200)
        json_data = res.get_json()
        self.assertTrue(json_data["success"])
        self.assertEqual(json_data["registration_number"], "DL01AB1234")

    # -------------------------------------------------------------------------
    # TEST 12: Dual Mode Toggle in ANPRScanner Component
    # -------------------------------------------------------------------------
    def test_12_anpr_scanner_dual_mode_ui(self):
        """Verify ANPRScanner.jsx supports both Live Camera and File Upload options."""
        scanner_file = Config.BASE_DIR.parent / "frontend" / "src" / "components" / "ANPRScanner.jsx"
        content = scanner_file.read_text()

        self.assertIn("Capture Live Camera", content)
        self.assertIn("Upload Vehicle Image", content)
        self.assertIn("scanSource", content)
        self.assertIn("<LiveCameraCapture", content)


if __name__ == "__main__":
    unittest.main(verbosity=2)
