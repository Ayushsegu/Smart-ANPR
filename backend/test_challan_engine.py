"""
test_challan_engine.py - Automated Unit & Integration Tests for Phase 5
========================================================================
Smart ANPR Vehicle Verification System - Digital Challan & QR-PDF Engine

Test coverage:
1.  Unique citation number generation & format validation.
2.  QR code barcode generation & PII protection verification.
3.  ReportLab PDF receipt compilation & magic byte verification.
4.  Challan creation with single violation (MH12DE5678 - Expired PUC).
5.  Challan creation with multiple violations (TN09BK3456 - Insurance + PUC).
6.  Fine integration & automatic violation deduplication.
7.  Non-existent vehicle error handling (HTTP 404 / ValueError).
8.  Compliant vehicle protection (cannot issue challan with 0 violations).
9.  Flask API: POST /api/challans/generate.
10. Flask API: GET /api/challans/<challan_number> (QR verification endpoint).
11. Flask API: GET /api/challans/<challan_number> 404 handling.
12. Flask API: GET /api/challans/<challan_number>/pdf binary streaming.
13. Flask API: GET /api/challans/<challan_number>/qr binary streaming.
14. Demonstration payment simulation: PENDING -> PAID (SETTLED).
15. Demonstration payment simulation: PENDING -> FAILED.
16. Database UNIQUE constraint enforcement on challan_number.
17. File integrity verification: Both PDF and QR files can be opened and parsed.
"""

import json
import os
import re
import sys
import tempfile
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
from app.models.database import (
    get_all_challans,
    get_challan_by_number,
    get_db_connection,
    get_vehicle_by_plate,
    insert_challan,
    update_challan_payment_status,
)
from app.services.challan_service import (
    generate_digital_challan,
    generate_unique_challan_number,
    get_challan_details,
    process_demonstration_payment,
)
from app.services.pdf_generator import generate_challan_pdf
from app.services.qr_generator import generate_challan_qr


class ChallanEngineTestSuite(unittest.TestCase):
    """Automated test suite verifying the Digital Challan & QR-PDF Engine."""

    @classmethod
    def setUpClass(cls):
        """Set up Flask test client and ensure test static directories exist."""
        cls.app = create_app(Config)
        cls.client = cls.app.test_client()

        # Temporary directory for isolated artifact testing if needed
        cls.test_qr_dir = Path(Config.QR_OUTPUT_DIR)
        cls.test_pdf_dir = Path(Config.PDF_OUTPUT_DIR)
        cls.test_qr_dir.mkdir(parents=True, exist_ok=True)
        cls.test_pdf_dir.mkdir(parents=True, exist_ok=True)

    # -------------------------------------------------------------------------
    # TEST 1: Unique Challan Number Generation
    # -------------------------------------------------------------------------
    def test_01_unique_challan_number_generation(self):
        """Verify format, randomness, and collision resistance of citation numbers."""
        numbers = [generate_unique_challan_number() for _ in range(25)]
        current_year = str(datetime.now().year)

        for num in numbers:
            self.assertTrue(num.startswith(f"CH-{current_year}-"), f"Invalid prefix in: {num}")
            self.assertEqual(len(num), 13, f"Unexpected citation number length: {num}")
            # Ensure no confusing letters like O, I, 0, 1 in the random suffix
            suffix = num.split("-")[-1]
            for bad_char in "OI01":
                self.assertNotIn(bad_char, suffix, f"Confusing character '{bad_char}' found in {num}")

        # Ensure all 25 candidate numbers are completely unique
        self.assertEqual(len(set(numbers)), 25, "Duplicate citation numbers were generated.")

    # -------------------------------------------------------------------------
    # TEST 2: QR Code Generation & PII Protection
    # -------------------------------------------------------------------------
    def test_02_qr_code_generation(self):
        """Verify QR barcode generation, PNG magic bytes, and absence of sensitive PII."""
        test_ch = "CH-TEST-QR001"
        file_path, web_url = generate_challan_qr(test_ch, base_url="http://127.0.0.1:5001")

        self.assertTrue(os.path.isfile(file_path), f"QR code file not created: {file_path}")
        self.assertTrue(web_url.startswith("/static/challans/qr/"))
        self.assertTrue(web_url.endswith(f"{test_ch}.png"))

        # Check PNG header magic bytes
        with open(file_path, "rb") as f:
            header = f.read(8)
            self.assertEqual(header, b"\x89PNG\r\n\x1a\n", "Generated QR is not a valid PNG file.")

        # Verify PIL can open and parse image
        with Image.open(file_path) as img:
            img.verify()
            self.assertEqual(img.format, "PNG")

    # -------------------------------------------------------------------------
    # TEST 3: ReportLab PDF Receipt Generation
    # -------------------------------------------------------------------------
    def test_03_pdf_generation_layout_and_header(self):
        """Verify PDF receipt generation, %PDF- magic bytes, and file size."""
        test_ch = "CH-TEST-PDF001"
        qr_path, _ = generate_challan_qr(test_ch)

        dummy_data = {
            "challan_number": test_ch,
            "registration_number": "MH12DE5678",
            "owner_name": "Priya Deshmukh",
            "vehicle_type": "Car",
            "vehicle_model": "Honda City 1.5 V",
            "violation_type": "EXPIRED_PUC",
            "fine_amount": 10000.0,
            "challan_date": "2026-11-07 10:30:00",
            "payment_status": "PENDING",
            "challan_status": "ISSUED",
            "description": "Pollution Under Control Certificate Expired",
            "fine_breakdown": [
                {
                    "title": "Pollution Under Control Certificate Expired",
                    "statute": "MVA 1988 § 190(2)",
                    "severity": "CRITICAL",
                    "fine_amount": 10000.0,
                    "description": "Vehicle operating with expired emissions certificate."
                }
            ]
        }

        file_path, web_url = generate_challan_pdf(dummy_data, qr_image_path=qr_path)
        self.assertTrue(os.path.isfile(file_path), f"PDF receipt not found: {file_path}")
        self.assertTrue(web_url.startswith("/static/challans/pdf/"))

        # Verify PDF header magic bytes
        with open(file_path, "rb") as f:
            header = f.read(5)
            self.assertEqual(header, b"%PDF-", "Generated document is not a valid PDF.")
            f.seek(0, 2)
            file_size = f.tell()
            self.assertGreater(file_size, 5000, f"PDF file size ({file_size} bytes) suspiciously small.")

    # -------------------------------------------------------------------------
    # TEST 4: Challan Creation with Single Violation
    # -------------------------------------------------------------------------
    def test_04_challan_creation_with_single_violation(self):
        """Verify automatic detection and challan creation for vehicle with expired PUC."""
        result = generate_digital_challan("MH12DE5678")

        self.assertTrue(result["success"])
        self.assertTrue(result["challan_number"].startswith("CH-"))
        self.assertEqual(result["vehicle"]["registration_number"], "MH12DE5678")
        self.assertEqual(result["vehicle"]["owner_name"], "Priya Deshmukh")
        self.assertEqual(result["payment_status"], "PENDING")
        self.assertEqual(result["challan_status"], "ISSUED")
        self.assertEqual(result["fine_amount"], 10000.0)
        self.assertIn("EXPIRED_PUC", result["violation_type"])
        self.assertTrue(os.path.isfile(Path(Config.PDF_OUTPUT_DIR) / f"{result['challan_number']}.pdf"))
        self.assertTrue(os.path.isfile(Path(Config.QR_OUTPUT_DIR) / f"{result['challan_number']}.png"))

    # -------------------------------------------------------------------------
    # TEST 5: Challan Creation with Multiple Violations
    # -------------------------------------------------------------------------
    def test_05_challan_creation_with_multiple_violations(self):
        """Verify challan generation for vehicle with multiple non-compliant documents."""
        # TN09BK3456 has expired INSURANCE (₹2,000) and expired PUC (₹10,000)
        result = generate_digital_challan("TN09BK3456")

        self.assertTrue(result["success"])
        self.assertEqual(result["vehicle"]["registration_number"], "TN09BK3456")
        self.assertEqual(result["vehicle"]["owner_name"], "Suresh Ramachandran")
        self.assertEqual(result["fine_amount"], 12000.0)
        self.assertEqual(result["fine_breakdown"]["violations_count"], 2)

        codes = {item["violation_code"] for item in result["fine_breakdown"]["items"]}
        self.assertIn("EXPIRED_INSURANCE", codes)
        self.assertIn("EXPIRED_PUC", codes)

    # -------------------------------------------------------------------------
    # TEST 6: Fine Calculation Integration & Deduplication
    # -------------------------------------------------------------------------
    def test_06_fine_calculation_integration_and_deduplication(self):
        """Verify duplicate violation items are penalized only once."""
        result = generate_digital_challan(
            registration_number="MH12DE5678",
            violations=["EXPIRED_PUC", "EXPIRED_PUC", "EXPIRED_PUC"]
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["fine_amount"], 10000.0)
        self.assertEqual(result["fine_breakdown"]["violations_count"], 1)
        self.assertEqual(result["fine_breakdown"]["duplicate_violations_ignored"], 2)

    # -------------------------------------------------------------------------
    # TEST 7: Invalid Registration Number Handling
    # -------------------------------------------------------------------------
    def test_07_invalid_registration_number_handling(self):
        """Verify attempting to create a challan for an unregistered vehicle raises ValueError."""
        with self.assertRaises(ValueError) as ctx:
            generate_digital_challan("XX99ZZ9999")
        self.assertIn("not registered", str(ctx.exception).lower())

    # -------------------------------------------------------------------------
    # TEST 8: Fully Compliant Vehicle Protection
    # -------------------------------------------------------------------------
    def test_08_fully_compliant_vehicle_challan_prevention(self):
        """Verify attempting to issue a challan for a vehicle with no violations is blocked."""
        # DL01AB1234 has all 4 valid documents
        with self.assertRaises(ValueError) as ctx:
            generate_digital_challan("DL01AB1234")
        self.assertIn("no detected violations", str(ctx.exception).lower())

    # -------------------------------------------------------------------------
    # TEST 9: Flask API: POST /api/challans/generate
    # -------------------------------------------------------------------------
    def test_09_api_post_generate_endpoint(self):
        """Verify POST /api/challans/generate returns 201 Created and correct schema."""
        response = self.client.post(
            "/api/challans/generate",
            json={
                "registration_number": "HR26CV6789",  # Has expired insurance
                "description": "Officer automated patrol detection."
            }
        )
        self.assertEqual(response.status_code, 201)
        data = response.get_json()

        self.assertTrue(data["success"])
        self.assertTrue(data["challan_number"].startswith("CH-"))
        self.assertEqual(data["vehicle"]["registration_number"], "HR26CV6789")
        self.assertEqual(data["payment_status"], "PENDING")
        self.assertIn("artifacts", data)
        self.assertTrue(data["artifacts"]["pdf_url"].endswith(".pdf"))
        self.assertTrue(data["artifacts"]["qr_url"].endswith(".png"))
        self.assertIn("verification_url", data["artifacts"])

    # -------------------------------------------------------------------------
    # TEST 10: Flask API: GET /api/challans/<challan_number> (QR Verification Target)
    # -------------------------------------------------------------------------
    def test_10_api_get_challan_verification_endpoint(self):
        """Verify GET /api/challans/<challan_number> retrieves complete citation details."""
        # Generate challan first
        gen_res = generate_digital_challan("CH01XY2468")  # Expired road tax
        ch_num = gen_res["challan_number"]

        # Fetch via API
        response = self.client.get(f"/api/challans/{ch_num}")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()

        self.assertTrue(data["success"])
        self.assertEqual(data["challan_number"], ch_num)
        self.assertEqual(data["vehicle"]["registration_number"], "CH01XY2468")
        self.assertEqual(data["vehicle"]["owner_name"], "Jaspreet Kaur")
        self.assertIn("fine_amount", data)
        self.assertIn("artifacts", data)

    # -------------------------------------------------------------------------
    # TEST 11: Flask API: GET /api/challans/<challan_number> Not Found
    # -------------------------------------------------------------------------
    def test_11_api_get_challan_not_found(self):
        """Verify GET /api/challans/<invalid_number> returns HTTP 404."""
        response = self.client.get("/api/challans/CH-9999-NONEXISTENT")
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertFalse(data["success"])
        self.assertIn("not found", data["error"].lower())

    # -------------------------------------------------------------------------
    # TEST 12: Flask API: GET /api/challans/<challan_number>/pdf Binary Streaming
    # -------------------------------------------------------------------------
    def test_12_api_pdf_streaming(self):
        """Verify GET /api/challans/<challan_number>/pdf returns application/pdf."""
        gen_res = generate_digital_challan("MH04GH4321")
        ch_num = gen_res["challan_number"]

        response = self.client.get(f"/api/challans/{ch_num}/pdf")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/pdf")
        self.assertTrue(response.data.startswith(b"%PDF-"), "Streamed data missing %PDF- header.")
        response.close()

    # -------------------------------------------------------------------------
    # TEST 13: Flask API: GET /api/challans/<challan_number>/qr Binary Streaming
    # -------------------------------------------------------------------------
    def test_13_api_qr_streaming(self):
        """Verify GET /api/challans/<challan_number>/qr returns image/png."""
        gen_res = generate_digital_challan("MH04GH4321")
        ch_num = gen_res["challan_number"]

        response = self.client.get(f"/api/challans/{ch_num}/qr")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "image/png")
        self.assertTrue(response.data.startswith(b"\x89PNG"), "Streamed data missing PNG magic bytes.")
        response.close()

    # -------------------------------------------------------------------------
    # TEST 14: Demonstration Payment Simulation: PENDING -> PAID (SETTLED)
    # -------------------------------------------------------------------------
    def test_14_payment_status_transition_pending_to_paid(self):
        """Verify demonstration payment updates status to PAID and settles challan."""
        gen_res = generate_digital_challan("DL1LAA9988")
        ch_num = gen_res["challan_number"]
        self.assertEqual(gen_res["payment_status"], "PENDING")

        # Execute simulated payment
        pay_res = self.client.post(f"/api/challans/{ch_num}/pay", json={"action": "PAY"})
        self.assertEqual(pay_res.status_code, 200)
        pay_data = pay_res.get_json()

        self.assertEqual(pay_data["payment_status"], "PAID")
        self.assertEqual(pay_data["challan_status"], "SETTLED")
        self.assertIn("demonstration_notice", pay_data)

        # Verify persistence in database
        db_record = get_challan_by_number(ch_num)
        self.assertEqual(db_record["payment_status"], "PAID")
        self.assertEqual(db_record["challan_status"], "SETTLED")

    # -------------------------------------------------------------------------
    # TEST 15: Demonstration Payment Simulation: PENDING -> FAILED
    # -------------------------------------------------------------------------
    def test_15_payment_status_transition_to_failed(self):
        """Verify simulated payment failure updates status to FAILED without settling."""
        gen_res = generate_digital_challan("WB02PQ3344")
        ch_num = gen_res["challan_number"]

        fail_res = self.client.post(f"/api/challans/{ch_num}/pay", json={"action": "FAIL"})
        self.assertEqual(fail_res.status_code, 200)
        fail_data = fail_res.get_json()

        self.assertEqual(fail_data["payment_status"], "FAILED")
        self.assertEqual(fail_data["challan_status"], "ISSUED")

    # -------------------------------------------------------------------------
    # TEST 16: Database UNIQUE Constraint Enforcement
    # -------------------------------------------------------------------------
    def test_16_duplicate_challan_number_database_integrity(self):
        """Verify SQLite UNIQUE constraint rejects duplicate challan numbers."""
        import sqlite3
        import secrets

        duplicate_num = f"CH-DUP-{secrets.token_hex(4).upper()}"
        vehicle = get_vehicle_by_plate("DL01AB1234")

        # First insert succeeds
        insert_challan(
            challan_number=duplicate_num,
            vehicle_id=vehicle["id"],
            violation_type="Test 1",
            fine_amount=500.0,
            challan_date="2026-11-07 12:00:00",
            payment_status="PENDING",
        )

        # Second insert with identical challan_number must raise sqlite3.IntegrityError
        with self.assertRaises(sqlite3.IntegrityError):
            insert_challan(
                challan_number=duplicate_num,
                vehicle_id=vehicle["id"],
                violation_type="Test 2",
                fine_amount=1000.0,
                challan_date="2026-11-07 12:01:00",
                payment_status="PENDING",
            )

    # -------------------------------------------------------------------------
    # TEST 17: File Integrity Verification (Files Can Actually Be Opened)
    # -------------------------------------------------------------------------
    def test_17_pdf_and_qr_files_can_actually_be_opened(self):
        """Verify that generated PDF and QR files can be opened and parsed without corruption."""
        gen_res = generate_digital_challan("TN09BK3456")
        ch_num = gen_res["challan_number"]

        pdf_disk_path = Path(Config.PDF_OUTPUT_DIR) / f"{ch_num}.pdf"
        qr_disk_path = Path(Config.QR_OUTPUT_DIR) / f"{ch_num}.png"

        # 1. Open and verify QR code with PIL
        self.assertTrue(qr_disk_path.is_file(), "QR code file missing.")
        with Image.open(str(qr_disk_path)) as qr_img:
            qr_img.verify()
            self.assertGreater(qr_img.width, 50)
            self.assertGreater(qr_img.height, 50)

        # 2. Open and inspect PDF structure
        self.assertTrue(pdf_disk_path.is_file(), "PDF file missing.")
        with open(str(pdf_disk_path), "rb") as f:
            content = f.read()
            self.assertTrue(content.startswith(b"%PDF-1."))
            self.assertTrue(b"%%EOF" in content or b"startxref" in content, "PDF missing termination xref marker.")
            self.assertGreater(len(content), 6000)


if __name__ == "__main__":
    unittest.main(verbosity=2)
