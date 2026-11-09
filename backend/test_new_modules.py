"""
backend/test_new_modules.py - Verification for Inspections, Helmet & Officer Updates
"""

import unittest
import io
import json
from PIL import Image, ImageDraw
from app import create_app


class NewModulesTestSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.client = cls.app.test_client()

        # Login as admin to get auth token
        res = cls.client.post("/api/auth/login", json={"username": "admin", "password": "Admin@123"})
        cls.admin_token = res.get_json()["token"]
        cls.auth_headers = {"Authorization": f"Bearer {cls.admin_token}"}

    def test_01_helmet_status(self):
        res = self.client.get("/api/helmet/status")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data.get("success"))
        self.assertTrue(data.get("model_loaded"))
        self.assertIn("weights_status", data)

    def test_02_helmet_detect_with_synthetic_image(self):
        # Create a test synthetic image (motorcyclist scenario)
        img = Image.new("RGB", (320, 240), color=(180, 200, 220))
        d = ImageDraw.Draw(img)
        d.ellipse([130, 40, 190, 100], fill=(20, 40, 80))  # Head-like ellipse
        d.rectangle([110, 100, 210, 200], fill=(40, 60, 120))  # Torso

        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        buf.seek(0)

        data = {
            "image": (buf, "test_rider.jpg"),
            "plate_number": "MH12AB1234",
            "station_id": "SEC-04-EXPRESSWAY",
            "officer_badge": "TP-DEL-8842"
        }

        res = self.client.post(
            "/api/helmet/detect",
            data=data,
            content_type="multipart/form-data"
        )
        self.assertEqual(res.status_code, 200)
        resp = res.get_json()
        self.assertTrue(resp.get("success"))
        self.assertIn("helmet_detected", resp)
        self.assertIn("confidence", resp)
        self.assertIn("status", resp)

    def test_03_inspections_list(self):
        res = self.client.get("/api/inspections", headers=self.auth_headers)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data.get("success"))
        self.assertGreaterEqual(len(data.get("inspections", [])), 8)

    def test_04_create_and_retrieve_inspection(self):
        payload = {
            "plate_number": "DL01TEST99",
            "confidence": 0.96,
            "status": "NON_COMPLIANT",
            "source": "CAMERA",
            "station_id": "SEC-04-EXPRESSWAY",
            "latitude": 28.5355,
            "longitude": 77.3910,
            "violations_found": ["EXPIRED_PUC"],
            "challan_issued": 1,
            "challan_id": "CH-2026-TEST99",
            "fine_amount": 10000.0,
            "officer_badge": "TP-DEL-8842",
        }
        res = self.client.post("/api/inspections", json=payload, headers=self.auth_headers)
        self.assertEqual(res.status_code, 201)
        created = res.get_json()
        inspection_id = created.get("inspection", {}).get("id")
        self.assertIsNotNone(inspection_id)

        # Retrieve specific inspection
        res_get = self.client.get(f"/api/inspections/{inspection_id}", headers=self.auth_headers)
        self.assertEqual(res_get.status_code, 200)
        retrieved = res_get.get_json().get("inspection", {})
        self.assertEqual(retrieved.get("registration_number"), "DL01TEST99")

    def test_05_update_officer_account(self):
        res_officers = self.client.get("/api/auth/officers", headers=self.auth_headers)
        officers = res_officers.get_json().get("officers", [])
        self.assertGreater(len(officers), 0)

        target = officers[-1]
        target_id = target["id"]
        original_station = target.get("station_id", "HQ")

        # Update station
        new_station = "SEC-08-AIRPORT-EXPWY"
        res_update = self.client.put(
            f"/api/auth/officers/{target_id}",
            json={"station_id": new_station},
            headers=self.auth_headers
        )
        self.assertEqual(res_update.status_code, 200)

        # Restore original station
        self.client.put(
            f"/api/auth/officers/{target_id}",
            json={"station_id": original_station},
            headers=self.auth_headers
        )


if __name__ == "__main__":
    unittest.main()
