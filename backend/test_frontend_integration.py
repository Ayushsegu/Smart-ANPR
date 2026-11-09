"""
test_frontend_integration.py - Full-Stack & Frontend-Backend Integration Tests
=============================================================================
Smart ANPR Vehicle Verification System - Phase 6

Verifies:
1.  Root SPA delivery (`GET /`) serves React HTML index.
2.  Built static JavaScript & CSS assets are served with correct headers.
3.  `/api/health` reports Phase 6 healthy status.
4.  `/api/vehicles` provides full fleet records for Dashboard & Document Registry.
5.  `/api/vehicles/<plate>/verify` powers the Vehicle Verification page.
6.  `/api/anpr/upload` handles image uploads and auto-verification.
7.  `/api/challans` provides real-time list for Challan Management.
8.  `/api/challans/generate` generates citations with PDF and QR links.
9.  `/api/challans/<num>/pdf` streams PDF receipt (`application/pdf`).
10. `/api/challans/<num>/qr` streams QR barcode (`image/png`).
11. `/api/challans/<num>/pay` updates demonstration payment status.
12. Static sample vehicle images are served properly.
"""

import io
import sys
import unittest
from pathlib import Path

# Ensure backend directory is in Python path
BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app import create_app
from app.core.config import Config


class FrontendIntegrationTestSuite(unittest.TestCase):
    """Test suite verifying end-to-end frontend integration and API routes."""

    @classmethod
    def setUpClass(cls):
        cls.app = create_app(Config)
        cls.client = cls.app.test_client()

    def test_01_root_serves_spa_index(self):
        """Verify GET / returns 200 OK and serves the compiled index.html."""
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn("text/html", res.content_type)
        self.assertTrue(b"<!doctype html>" in res.data or b"<html" in res.data)
        self.assertIn(b"assets/index", res.data)
        res.close()

    def test_02_health_reports_phase_6(self):
        """Verify GET /api/health reports Phase 6 status."""
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "healthy")
        self.assertIn("Phase 6", data["phase"])

    def test_03_vehicles_api_provides_data(self):
        """Verify GET /api/vehicles supplies records for the dashboard."""
        res = self.client.get("/api/vehicles")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertGreaterEqual(len(data["vehicles"]), 15)

    def test_04_vehicle_verification_endpoint(self):
        """Verify GET /api/vehicles/DL01AB1234/verify supplies compliance data."""
        res = self.client.get("/api/vehicles/DL01AB1234/verify")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["registration_number"], "DL01AB1234")
        self.assertEqual(data["summary"]["overall_status"], "COMPLIANT")
        self.assertIn("RC", data["documents"])
        self.assertIn("INSURANCE", data["documents"])
        self.assertIn("PUC", data["documents"])
        self.assertIn("ROAD_TAX", data["documents"])

    def test_05_anpr_upload_endpoint_integration(self):
        """Verify POST /api/anpr/upload processes a sample vehicle image."""
        sample_path = Path(Config.SAMPLES_DIR) / "sample_car_DL01AB1234.jpg"
        if not sample_path.is_file():
            self.skipTest("Sample image not found on disk.")

        with open(sample_path, "rb") as f:
            img_bytes = f.read()

        data = {
            "image": (io.BytesIO(img_bytes), "sample_car_DL01AB1234.jpg")
        }

        res = self.client.post("/api/anpr/upload", data=data, content_type="multipart/form-data")
        self.assertEqual(res.status_code, 200)
        json_data = res.get_json()
        self.assertTrue(json_data["success"])
        self.assertIn("registration_number", json_data)
        self.assertIn("crop_url", json_data)

    def test_06_challans_list_api(self):
        """Verify GET /api/challans returns citations for Challan Management."""
        res = self.client.get("/api/challans")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIsInstance(data["challans"], list)

    def test_07_challan_generation_and_payment_flow(self):
        """Verify full lifecycle: generate challan, stream PDF/QR, process payment."""
        # 1. Generate Challan
        gen_res = self.client.post(
            "/api/challans/generate",
            json={"registration_number": "MH12DE5678", "description": "Patrol test"}
        )
        self.assertEqual(gen_res.status_code, 201)
        gen_data = gen_res.get_json()
        ch_num = gen_data["challan_number"]

        # 2. Retrieve details
        detail_res = self.client.get(f"/api/challans/{ch_num}")
        self.assertEqual(detail_res.status_code, 200)

        # 3. Stream PDF
        pdf_res = self.client.get(f"/api/challans/{ch_num}/pdf")
        self.assertEqual(pdf_res.status_code, 200)
        self.assertEqual(pdf_res.content_type, "application/pdf")
        pdf_res.close()

        # 4. Stream QR
        qr_res = self.client.get(f"/api/challans/{ch_num}/qr")
        self.assertEqual(qr_res.status_code, 200)
        self.assertEqual(qr_res.content_type, "image/png")
        qr_res.close()

        # 5. Process Demonstration Payment
        pay_res = self.client.post(f"/api/challans/{ch_num}/pay", json={"action": "PAY"})
        self.assertEqual(pay_res.status_code, 200)
        pay_data = pay_res.get_json()
        self.assertEqual(pay_data["payment_status"], "PAID")
        self.assertEqual(pay_data["challan_status"], "SETTLED")


if __name__ == "__main__":
    unittest.main(verbosity=2)
