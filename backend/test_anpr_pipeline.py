"""
test_anpr_pipeline.py - Phase 4 ANPR & OCR Processing Pipeline Test Suite
==========================================================================
Smart ANPR Vehicle Verification System

Tests all Phase 4 requirements:
1. YOLOv8 model loading & configuration inspection.
2. Plate detection on vehicle image.
3. Bounding box extraction & image cropping.
4. EasyOCR text extraction.
5. Registration number cleaning & Indian format validation.
6. Common OCR character misread correction.
7. Handling image validation & invalid image formats.
8. Handling images with missing / no number plates.
9. Flask REST API endpoint POST /api/anpr/upload:
   - Success with auto-verification against live database
   - 422 Unprocessable Entity when no plate is detected
   - 400 Bad Request on invalid file formats
   - 400 Bad Request on missing file payload
10. Regression check for existing Phase 1, 2, and 3 APIs.
"""

import io
import sys
import unittest
from pathlib import Path

# Add backend directory to path
BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import cv2
import numpy as np

from app import create_app
from app.core.config import Config
from app.services.plate_cleaner import (
    clean_and_validate_plate,
    clean_raw_text,
    correct_ocr_ambiguities,
    validate_plate_format,
)
from app.services.ocr_service import get_easyocr_reader, read_plate_text
from app.services.anpr_detector import (
    LicensePlateDetector,
    crop_plate,
    get_detector,
    process_vehicle_image,
    validate_image_file,
)


class ANPRPipelineTestSuite(unittest.TestCase):
    """Automated unit and integration test suite for ANPR & OCR modules."""

    @classmethod
    def setUpClass(cls):
        """Set up Flask test client and verify sample images exist."""
        cls.samples_dir = Path(Config.SAMPLES_DIR)
        if not (cls.samples_dir / "sample_car_DL01AB1234.jpg").exists():
            from generate_sample_images import generate_all_samples
            generate_all_samples()

        cls.app = create_app(Config)
        cls.client = cls.app.test_client()

    # ------------------------------------------------------------------------
    # 1. Text Cleaner & Positional Disambiguation Tests
    # ------------------------------------------------------------------------
    def test_01_clean_raw_text(self):
        """Verify removal of spaces, hyphens, and HSRP 'IND' prefix."""
        # Spaces and hyphens
        self.assertEqual(clean_raw_text("DL 01 AB 1234"), "DL01AB1234")
        self.assertEqual(clean_raw_text("MH-12-DE-5678"), "MH12DE5678")
        self.assertEqual(clean_raw_text("  ka . 03 / mj : 9012 "), "KA03MJ9012")

        # HSRP 'IND' prefix
        self.assertEqual(clean_raw_text("IND DL01AB1234"), "DL01AB1234")
        self.assertEqual(clean_raw_text("INDMH12DE5678"), "MH12DE5678")

    def test_02_correct_ocr_ambiguities(self):
        """Verify positional optical character confusion fixes (0 vs O, 1 vs I, etc.)."""
        # Digit '0' in state code letters -> converted to 'O'
        # Letter 'O' in numeric RTO / last 4 digits -> converted to '0'
        # Example: 'DL O1 AB 1234' with letter O in RTO
        corrected = correct_ocr_ambiguities("DLO1AB1234")
        self.assertEqual(corrected, "DL01AB1234")

        # Letter 'O' instead of digit '0' in last 4 digits: 'DL01AB12O4'
        corrected_num = correct_ocr_ambiguities("DL01AB12O4")
        self.assertEqual(corrected_num, "DL01AB1204")

        # Letter 'I' in last digits: 'DL01AB12I4' -> 'DL01AB1214'
        corrected_one = correct_ocr_ambiguities("DL01AB12I4")
        self.assertEqual(corrected_one, "DL01AB1214")

    def test_03_validate_plate_format(self):
        """Verify regex validation for Indian standard and Bharat series plates."""
        # Valid standard Indian plates
        valid, fmt, comps = validate_plate_format("DL01AB1234")
        self.assertTrue(valid)
        self.assertEqual(fmt, "STANDARD_INDIAN")
        self.assertEqual(comps["state_code"], "DL")
        self.assertEqual(comps["rto_code"], "01")
        self.assertEqual(comps["number"], "1234")

        # Commercial format
        valid_comm, fmt_comm, _ = validate_plate_format("DL1LAA9988")
        self.assertTrue(valid_comm)

        # Bharat series
        valid_bh, fmt_bh, comps_bh = validate_plate_format("22BH1234AA")
        self.assertTrue(valid_bh)
        self.assertEqual(fmt_bh, "BHARAT_SERIES")

        # Invalid formats
        invalid, _, _ = validate_plate_format("INVALID_PLATE")
        self.assertFalse(invalid)
        invalid2, _, _ = validate_plate_format("1234567")
        self.assertFalse(invalid2)

    def test_04_clean_and_validate_plate_pipeline(self):
        """Full plate cleaning pipeline test with confidence flags."""
        res = clean_and_validate_plate("IND DL 01 AB 1234", ocr_confidence=0.88)
        self.assertTrue(res["is_valid_format"])
        self.assertEqual(res["final_registration_number"], "DL01AB1234")
        self.assertFalse(res["low_confidence_warning"])
        self.assertFalse(res["manual_review_needed"])

        # Low confidence triggers warning
        res_low = clean_and_validate_plate("DL 01 AB 1234", ocr_confidence=0.35)
        self.assertTrue(res_low["is_valid_format"])
        self.assertTrue(res_low["low_confidence_warning"])
        self.assertTrue(res_low["manual_review_needed"])

    # ------------------------------------------------------------------------
    # 2. Image Validation Tests
    # ------------------------------------------------------------------------
    def test_05_image_validation_valid(self):
        """Verify image validation succeeds on valid JPEG bytes."""
        car_img_path = self.samples_dir / "sample_car_DL01AB1234.jpg"
        with open(car_img_path, "rb") as f:
            bytes_data = f.read()

        is_valid, err, img = validate_image_file(bytes_data, "car.jpg")
        self.assertTrue(is_valid)
        self.assertIsNone(err)
        self.assertIsNotNone(img)
        self.assertGreater(img.shape[0], 0)

    def test_06_image_validation_invalid_format(self):
        """Verify image validation rejects disallowed file extensions (.txt, .pdf)."""
        txt_path = self.samples_dir / "sample_invalid.txt"
        with open(txt_path, "rb") as f:
            bytes_data = f.read()

        is_valid, err, img = validate_image_file(bytes_data, "document.txt")
        self.assertFalse(is_valid)
        self.assertIn("Unsupported file extension", err)
        self.assertIsNone(img)

    def test_07_image_validation_corrupted_data(self):
        """Verify image validation rejects fake corrupted image bytes."""
        corrupted = b"NOT_A_REAL_IMAGE_BYTES_CORRUPTED"
        is_valid, err, img = validate_image_file(corrupted, "corrupt.jpg")
        self.assertFalse(is_valid)
        self.assertIn("Failed to decode image", err)

    # ------------------------------------------------------------------------
    # 3. Plate Detection & Cropping Tests
    # ------------------------------------------------------------------------
    def test_08_detector_instance_and_weights_mode(self):
        """Verify detector loads and correctly reports weights availability state."""
        detector = get_detector()
        self.assertIsInstance(detector, LicensePlateDetector)
        # Weights status is cleanly reported (True if .pt exists, False if fallback mode)
        self.assertIn(detector.weights_available, (True, False))

    def test_09_plate_detection_positive(self):
        """Verify plate detection succeeds on sample vehicle image with license plate."""
        car_img_path = self.samples_dir / "sample_car_DL01AB1234.jpg"
        img = cv2.imread(str(car_img_path))
        self.assertIsNotNone(img)

        result = process_vehicle_image(img, save_crops=True)
        self.assertTrue(result["plate_detected"])
        self.assertGreater(result["detections_count"], 0)
        self.assertGreater(result["primary"]["confidence"], 0.50)

        box = result["primary"]["box"]
        self.assertEqual(len(box), 4)
        # Check coordinates validity: x2 > x1 and y2 > y1
        self.assertGreater(box[2], box[0])
        self.assertGreater(box[3], box[1])

        # Check crop image exists and has valid shape
        crop = result["primary"]["crop_image"]
        self.assertGreater(crop.shape[0], 20)
        self.assertGreater(crop.shape[1], 50)

    def test_10_plate_detection_negative_no_plate(self):
        """Verify detection returns plate_detected=False on image with no vehicle plate."""
        road_img_path = self.samples_dir / "sample_road_no_plate.jpg"
        img = cv2.imread(str(road_img_path))
        self.assertIsNotNone(img)

        result = process_vehicle_image(img, save_crops=False)
        self.assertFalse(result["plate_detected"])
        self.assertEqual(result["detections_count"], 0)

    def test_11_crop_plate_padding_safety(self):
        """Verify crop_plate respects image boundary limits with padding."""
        dummy_img = np.zeros((400, 600, 3), dtype=np.uint8)
        # Box very close to image top-left edge
        box = [5, 5, 100, 50]
        crop, padded_box = crop_plate(dummy_img, box, padding_pct=0.10)

        self.assertEqual(padded_box[0], 0)  # Clamped to left edge 0
        self.assertEqual(padded_box[1], 0)  # Clamped to top edge 0
        self.assertGreater(padded_box[2], 100)
        self.assertGreater(padded_box[3], 50)
        self.assertGreater(crop.shape[0], 0)

    # ------------------------------------------------------------------------
    # 4. EasyOCR Reading Tests
    # ------------------------------------------------------------------------
    def test_12_easyocr_model_reader(self):
        """Verify EasyOCR reader initializes with local offline models."""
        reader = get_easyocr_reader()
        self.assertIsNotNone(reader)

    def test_13_easyocr_extract_plate_text(self):
        """Verify EasyOCR extracts characters from standalone plate crop."""
        crop_path = self.samples_dir / "sample_cropped_plate_DL01AB1234.jpg"
        ocr_res = read_plate_text(str(crop_path), preprocess=True)

        self.assertTrue(ocr_res["success"])
        self.assertTrue(ocr_res["text_found"])
        self.assertGreater(ocr_res["ocr_confidence"], 0.60)
        # Verify recognized cleaned plate is DL01AB1234
        self.assertEqual(ocr_res["cleaned"]["final_registration_number"], "DL01AB1234")
        self.assertTrue(ocr_res["cleaned"]["is_valid_format"])

    # ------------------------------------------------------------------------
    # 5. Flask REST API Integration: POST /api/anpr/upload
    # ------------------------------------------------------------------------
    def test_14_api_upload_success_and_verify(self):
        """POST /api/anpr/upload with DL01AB1234 vehicle image returns 200 with full verification."""
        car_img_path = self.samples_dir / "sample_car_DL01AB1234.jpg"
        with open(car_img_path, "rb") as f:
            data = {
                "image": (f, "vehicle_car.jpg"),
                "verify": "true"
            }
            res = self.client.post(
                "/api/anpr/upload",
                data=data,
                content_type="multipart/form-data"
            )

        self.assertEqual(res.status_code, 200)
        json_data = res.get_json()
        self.assertTrue(json_data["success"])
        self.assertEqual(json_data["processing_status"], "SUCCESS")
        self.assertEqual(json_data["registration_number"], "DL01AB1234")
        self.assertTrue(json_data["plate_detected"])
        self.assertGreater(json_data["detection"]["confidence"], 0.50)
        self.assertIn("cropped_plate_url", json_data["media"])

        # Check integrated Phase 3 database verification
        db_verif = json_data["database_verification"]
        self.assertIsNotNone(db_verif)
        self.assertEqual(db_verif["vehicle"]["owner_name"], "Aarav Sharma")
        self.assertEqual(db_verif["summary"]["overall_status"], "COMPLIANT")
        self.assertEqual(db_verif["summary"]["valid_count"], 4)

    def test_15_api_upload_commercial_vehicle_violation(self):
        """POST /api/anpr/upload with MH12DE5678 identifies vehicle and flags expired PUC."""
        car_img_path = self.samples_dir / "sample_commercial_MH12DE5678.jpg"
        with open(car_img_path, "rb") as f:
            data = {
                "image": (f, "commercial_truck.jpg"),
                "verify": "true"
            }
            res = self.client.post(
                "/api/anpr/upload",
                data=data,
                content_type="multipart/form-data"
            )

        self.assertEqual(res.status_code, 200)
        json_data = res.get_json()
        self.assertTrue(json_data["success"])
        self.assertEqual(json_data["registration_number"], "MH12DE5678")

        # Database check verifies Expired PUC detected
        db_verif = json_data["database_verification"]
        self.assertIsNotNone(db_verif)
        self.assertEqual(db_verif["summary"]["overall_status"], "NON_COMPLIANT")
        self.assertEqual(db_verif["summary"]["expired_count"], 1)
        self.assertEqual(db_verif["violations"][0]["violation_code"], "EXPIRED_PUC")

    def test_16_api_upload_negative_no_plate(self):
        """POST /api/anpr/upload with no-plate image returns 422 Unprocessable Entity."""
        road_img_path = self.samples_dir / "sample_road_no_plate.jpg"
        with open(road_img_path, "rb") as f:
            data = {"image": (f, "empty_road.jpg")}
            res = self.client.post(
                "/api/anpr/upload",
                data=data,
                content_type="multipart/form-data"
            )

        self.assertEqual(res.status_code, 422)
        json_data = res.get_json()
        self.assertFalse(json_data["success"])
        self.assertEqual(json_data["processing_status"], "NO_PLATE_DETECTED")
        self.assertIn("No number plate detected", json_data["error"])

    def test_17_api_upload_invalid_file_format(self):
        """POST /api/anpr/upload with non-image file (.txt) returns 400 Bad Request."""
        data = {
            "image": (io.BytesIO(b"Plain text content"), "test_file.txt")
        }
        res = self.client.post(
            "/api/anpr/upload",
            data=data,
            content_type="multipart/form-data"
        )
        self.assertEqual(res.status_code, 400)
        json_data = res.get_json()
        self.assertFalse(json_data["success"])
        self.assertEqual(json_data["processing_status"], "INVALID_IMAGE")

    def test_18_api_upload_missing_file_payload(self):
        """POST /api/anpr/upload with empty body returns 400 Bad Request."""
        res = self.client.post("/api/anpr/upload", data={})
        self.assertEqual(res.status_code, 400)
        json_data = res.get_json()
        self.assertFalse(json_data["success"])
        self.assertEqual(json_data["processing_status"], "MISSING_FILE")

    # ------------------------------------------------------------------------
    # 6. Regression Check: Existing APIs
    # ------------------------------------------------------------------------
    def test_19_regression_previous_phases(self):
        """Verify /api/health and Phase 2 & 3 verification endpoints remain operational."""
        # 1. Health endpoint
        res_h = self.client.get("/api/health")
        self.assertEqual(res_h.status_code, 200)
        self.assertEqual(res_h.get_json()["status"], "healthy")

        # 2. Vehicle verify endpoint
        res_v = self.client.get("/api/vehicles/DL01AB1234/verify")
        self.assertEqual(res_v.status_code, 200)
        self.assertTrue(res_v.get_json()["success"])

        # 3. Challans calculate endpoint
        res_c = self.client.post("/api/challans/calculate", json={
            "violations": ["EXPIRED_INSURANCE"]
        })
        self.assertEqual(res_c.status_code, 200)
        self.assertEqual(res_c.get_json()["calculation"]["total_fine"], 2000.0)


def run_tests():
    """Run all Phase 4 tests with verbose runner."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(ANPRPipelineTestSuite)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
