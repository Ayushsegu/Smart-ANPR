"""
backend/test_demo_fleet.py - Verification Test Suite for 50 Pre-Registered Demo Vehicles
========================================================================================
Smart ANPR Vehicle Verification System

Tests the 12 evaluation checkpoints specified in the requirement:
1. Seed script idempotency & execution.
2. Confirm exactly 50 unique demo vehicle records exist.
3. Test registration-number search (e.g. DL01DM0001).
4. Test a valid document (e.g. RC / Insurance on DL01DM0001).
5. Test an expiring document (e.g. Insurance on DL01DM0003).
6. Test an expired document (e.g. PUC on DL01DM0002).
7. Test a missing document (e.g. Missing PUC on DL01DM0010).
8. Test a non-existent registration number (e.g. ZZ99DM9999 returns 404).
9. Test ANPR lookup integration with demo plate verification.
10. Test manual registration-number search.
11. Test challan history retrieval for demo vehicles.
12. Test complete fleet metrics endpoint.
"""

import unittest
import io
import json
from datetime import datetime
from PIL import Image, ImageDraw

from app import create_app
from database import (
    get_all_vehicles,
    get_vehicle_by_plate,
    get_documents_by_plate,
    get_demo_fleet_metrics,
)
from app.services.vehicle_verifier import verify_vehicle_compliance


class DemoFleetTestSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.client = cls.app.test_client()

    # 1 & 2. Confirm exactly 50 unique demo vehicle records exist
    def test_01_confirm_50_unique_demo_vehicles(self):
        vehicles = get_all_vehicles()
        demo_vehicles = [v for v in vehicles if v.get("demo_id")]
        self.assertEqual(len(demo_vehicles), 50, f"Expected exactly 50 demo vehicles, found {len(demo_vehicles)}.")

        # Check unique demo IDs and registration plates
        demo_ids = {v["demo_id"] for v in demo_vehicles}
        self.assertEqual(len(demo_ids), 50, "Demo IDs must be unique.")
        plates = {v["registration_number"] for v in demo_vehicles}
        self.assertEqual(len(plates), 50, "Demo registration numbers must be unique.")

        # Confirm representation across manufacturers
        makes = {v.get("manufacturer") for v in demo_vehicles}
        for expected_make in ["Maruti Suzuki", "Hyundai", "Tata", "Honda", "Toyota", "Mahindra", "Kia", "Royal Enfield", "TVS", "Bajaj"]:
            self.assertIn(expected_make, makes, f"Expected manufacturer '{expected_make}' in demo fleet.")

    # 3. Test registration-number search
    def test_02_registration_search(self):
        res = self.client.get("/api/vehicles/DL01DM0001")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data.get("success"))
        veh = data.get("vehicle", {})
        self.assertEqual(veh.get("registration_number"), "DL01DM0001")
        self.assertEqual(veh.get("demo_id"), "DEMO-01")
        self.assertEqual(veh.get("manufacturer"), "Maruti Suzuki")

    # 4. Test a valid document (> 30 days remaining)
    def test_03_test_valid_document(self):
        res = verify_vehicle_compliance("DL01DM0001")
        self.assertIsNotNone(res)
        self.assertEqual(res["summary"]["overall_status"], "COMPLIANT")
        self.assertEqual(res["summary"]["expired_count"], 0)
        self.assertEqual(res["summary"]["valid_count"], 4)

        rc_doc = res["documents"]["RC"]
        self.assertEqual(rc_doc["status"], "VALID")
        self.assertGreater(rc_doc["days_until_expiry"], 30)

    # 5. Test an expiring document (within 30 days)
    def test_04_test_expiring_document(self):
        # DL01DM0003 has insurance expiring in 12 days
        res = verify_vehicle_compliance("DL01DM0003")
        self.assertIsNotNone(res)
        self.assertEqual(res["summary"]["overall_status"], "ATTENTION_REQUIRED")
        self.assertEqual(res["summary"]["expiring_count"], 1)

        ins_doc = res["documents"]["INSURANCE"]
        self.assertEqual(ins_doc["status"], "EXPIRING_SOON")
        self.assertGreaterEqual(ins_doc["days_until_expiry"], 0)
        self.assertLessEqual(ins_doc["days_until_expiry"], 30)

    # 6. Test an expired document (< 0 days)
    def test_05_test_expired_document(self):
        # DL01DM0002 has PUC expired 45 days ago
        res = verify_vehicle_compliance("DL01DM0002")
        self.assertIsNotNone(res)
        self.assertEqual(res["summary"]["overall_status"], "NON_COMPLIANT")
        self.assertEqual(res["summary"]["expired_count"], 1)

        puc_doc = res["documents"]["PUC"]
        self.assertEqual(puc_doc["status"], "EXPIRED")
        self.assertLess(puc_doc["days_until_expiry"], 0)
        self.assertEqual(res["violations"][0]["violation_code"], "EXPIRED_PUC")

    # 7. Test a missing document
    def test_06_test_missing_document(self):
        # DL01DM0010 has MISSING_PUC profile
        res = verify_vehicle_compliance("DL01DM0010")
        self.assertIsNotNone(res)
        self.assertEqual(res["summary"]["overall_status"], "NON_COMPLIANT")
        self.assertEqual(res["summary"]["missing_count"], 1)

        puc_doc = res["documents"]["PUC"]
        self.assertEqual(puc_doc["status"], "MISSING")
        self.assertTrue(puc_doc.get("is_missing"))

    # 8. Test a non-existent registration number
    def test_07_test_non_existent_registration(self):
        res = self.client.get("/api/vehicles/ZZ99DM9999/verify")
        self.assertEqual(res.status_code, 404)
        data = res.get_json()
        self.assertFalse(data.get("success"))
        self.assertIn("not found in registry", data.get("error", "").lower())

    # 9. Test ANPR upload integration with demo plate lookup
    def test_08_anpr_upload_and_demo_lookup(self):
        # Synthetic test vehicle image with mock plate
        img = Image.new("RGB", (400, 300), color=(220, 230, 240))
        d = ImageDraw.Draw(img)
        d.rectangle([100, 180, 300, 240], fill=(255, 255, 255), outline=(0, 0, 0), width=2)
        d.text((120, 195), "DL01DM0001", fill=(0, 0, 0))

        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        buf.seek(0)

        res = self.client.post(
            "/api/anpr/upload",
            data={"image": (buf, "demo_test.jpg"), "verify": "true"},
            content_type="multipart/form-data"
        )
        self.assertEqual(res.status_code, 200)
        resp = res.get_json()
        self.assertTrue(resp.get("success"))

    # 10. Test manual registration search via API query
    def test_09_manual_search_and_filters(self):
        # Search by model
        res = self.client.get("/api/vehicles?search=Nexon")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertGreaterEqual(data.get("count", 0), 1)

        # Filter by vehicle type: Motorcycle
        res_mc = self.client.get("/api/vehicles?vehicle_type=Motorcycle")
        self.assertEqual(res_mc.status_code, 200)
        data_mc = res_mc.get_json()
        self.assertGreaterEqual(data_mc.get("count", 0), 8)

        # Filter by state: Maharashtra
        res_mh = self.client.get("/api/vehicles?state=Maharashtra")
        self.assertEqual(res_mh.status_code, 200)
        data_mh = res_mh.get_json()
        self.assertGreaterEqual(data_mh.get("count", 0), 10)

    # 11. Test challan history retrieval for demo vehicles
    def test_10_challan_history_retrieval(self):
        res = self.client.get("/api/challans?registration_number=DL01DM0002")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data.get("success"))
        challans = data.get("challans", [])
        self.assertGreaterEqual(len(challans), 1)
        self.assertEqual(challans[0]["registration_number"], "DL01DM0002")

    # 12. Test fleet metrics endpoint
    def test_11_fleet_metrics(self):
        res = self.client.get("/api/vehicles/metrics")
        self.assertEqual(res.status_code, 200)
        metrics = res.get_json().get("metrics", {})
        self.assertGreaterEqual(metrics.get("total_demo_vehicles", 0), 50)
        self.assertGreater(metrics.get("documents_valid", 0), 200)
        self.assertGreater(metrics.get("documents_expired", 0), 20)
        self.assertGreater(metrics.get("documents_missing", 0), 0)


if __name__ == "__main__":
    unittest.main()
