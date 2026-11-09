"""
test_verification_engine.py - Phase 3 Verification & Fine Engine Test Suite
===========================================================================
Smart ANPR Vehicle Verification System

Tests all Phase 3 requirements:
1. Valid documents (expiry > 30 days).
2. Expired documents (expiry < today).
3. Expiring soon documents (expiry in 0..30 days).
4. Missing documents (record does not exist).
5. Invalid registration number (404 / None handling).
6. Multiple violations handling.
7. Fine calculation & deduplication.
8. Flask API endpoints:
   - GET  /api/vehicles/<registration_number>/verify
   - POST /api/vehicles/verify
   - POST /api/challans/calculate
   - GET  /api/health (regression test)
9. Database integration with existing anpr.db.
"""

import sys
import unittest
from datetime import date, datetime, timedelta
from pathlib import Path

# Add backend directory to sys.path
BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app import create_app
from app.core.config import Config
from app.services.document_verifier import (
    STATUS_EXPIRED,
    STATUS_EXPIRING_SOON,
    STATUS_MISSING,
    STATUS_VALID,
    evaluate_document_status,
    verify_single_document,
)
from app.services.fine_calculator import calculate_fine_breakdown
from app.services.vehicle_verifier import (
    VERDICT_ATTENTION_REQUIRED,
    VERDICT_COMPLIANT,
    VERDICT_NON_COMPLIANT,
    verify_vehicle_compliance,
)
from database import get_db_path, insert_vehicle, insert_document


class VerificationEngineTestSuite(unittest.TestCase):
    """Test suite covering Document Verifier, Vehicle Verifier, Fine Calculator and APIs."""

    @classmethod
    def setUpClass(cls):
        """Set up Flask test client and ensure DB is seeded."""
        cls.db_path = get_db_path()
        if not cls.db_path.exists():
            from seed_data import seed_database
            seed_database(cls.db_path)

        cls.app = create_app(Config)
        cls.client = cls.app.test_client()

    # ------------------------------------------------------------------------
    # 1. Document Verification Rules (Date Arithmetic)
    # ------------------------------------------------------------------------
    def test_01_valid_document_rule(self):
        """Expiry > 30 days away must evaluate to STATUS_VALID."""
        today = date(2026, 11, 7)
        future_date = today + timedelta(days=90)  # 90 days away
        res = evaluate_document_status(future_date.isoformat(), reference_date=today)

        self.assertEqual(res["status"], STATUS_VALID)
        self.assertEqual(res["days_until_expiry"], 90)
        self.assertTrue(res["is_valid"])
        self.assertFalse(res["is_expired"])
        self.assertFalse(res["is_expiring_soon"])
        self.assertEqual(res["badge_color"], "green")

    def test_02_expiring_soon_document_rule(self):
        """Expiry between 0 and 30 days away must evaluate to STATUS_EXPIRING_SOON."""
        today = date(2026, 11, 7)
        expiring_date = today + timedelta(days=15)  # 15 days away
        res = evaluate_document_status(expiring_date.isoformat(), reference_date=today)

        self.assertEqual(res["status"], STATUS_EXPIRING_SOON)
        self.assertEqual(res["days_until_expiry"], 15)
        self.assertTrue(res["is_expiring_soon"])
        self.assertFalse(res["is_valid"])
        self.assertFalse(res["is_expired"])
        self.assertEqual(res["badge_color"], "yellow")

        # Boundary condition: expires today (0 days)
        res_today = evaluate_document_status(today.isoformat(), reference_date=today)
        self.assertEqual(res_today["status"], STATUS_EXPIRING_SOON)
        self.assertEqual(res_today["days_until_expiry"], 0)

        # Boundary condition: exactly 30 days
        res_30 = evaluate_document_status((today + timedelta(days=30)).isoformat(), reference_date=today)
        self.assertEqual(res_30["status"], STATUS_EXPIRING_SOON)
        self.assertEqual(res_30["days_until_expiry"], 30)

        # Boundary condition: 31 days (should be VALID)
        res_31 = evaluate_document_status((today + timedelta(days=31)).isoformat(), reference_date=today)
        self.assertEqual(res_31["status"], STATUS_VALID)

    def test_03_expired_document_rule(self):
        """Expiry before today must evaluate to STATUS_EXPIRED."""
        today = date(2026, 11, 7)
        past_date = today - timedelta(days=45)  # 45 days in past
        res = evaluate_document_status(past_date.isoformat(), reference_date=today)

        self.assertEqual(res["status"], STATUS_EXPIRED)
        self.assertEqual(res["days_until_expiry"], -45)
        self.assertTrue(res["is_expired"])
        self.assertFalse(res["is_valid"])
        self.assertFalse(res["is_expiring_soon"])
        self.assertEqual(res["badge_color"], "red")

    def test_04_missing_document_rule(self):
        """None or missing record must evaluate to STATUS_MISSING."""
        res = verify_single_document(None, "INSURANCE")
        self.assertEqual(res["status"], STATUS_MISSING)
        self.assertIsNone(res["days_until_expiry"])
        self.assertTrue(res["is_missing"])
        self.assertEqual(res["badge_color"], "gray")
        self.assertIn("missing", res["message"].lower())

    # ------------------------------------------------------------------------
    # 2. Vehicle Verification Compliance Scenarios (Live Database)
    # ------------------------------------------------------------------------
    def test_05_vehicle_verification_clean(self):
        """Vehicle DL01AB1234 has all 4 documents valid -> COMPLIANT, 0 violations, ₹0 fines."""
        today = date(2026, 11, 7)
        res = verify_vehicle_compliance("DL01AB1234", reference_date=today)

        self.assertIsNotNone(res)
        self.assertEqual(res["registration_number"], "DL01AB1234")
        self.assertEqual(res["vehicle"]["owner_name"], "Aarav Sharma")
        self.assertEqual(res["summary"]["overall_status"], VERDICT_COMPLIANT)
        self.assertEqual(res["summary"]["valid_count"], 4)
        self.assertEqual(res["summary"]["expired_count"], 0)
        self.assertEqual(res["summary"]["expiring_count"], 0)
        self.assertEqual(res["summary"]["missing_count"], 0)
        self.assertFalse(res["summary"]["has_violations"])
        self.assertEqual(len(res["violations"]), 0)
        self.assertEqual(res["fines"]["total_fine"], 0.0)

    def test_06_vehicle_verification_single_expired_puc(self):
        """Vehicle MH12DE5678 has expired PUC -> NON_COMPLIANT, 1 violation, ₹10,000 fine."""
        today = date(2026, 11, 7)
        res = verify_vehicle_compliance("MH12DE5678", reference_date=today)

        self.assertIsNotNone(res)
        self.assertEqual(res["summary"]["overall_status"], VERDICT_NON_COMPLIANT)
        self.assertEqual(res["summary"]["expired_count"], 1)
        self.assertTrue(res["summary"]["has_violations"])

        # Check document specifics
        puc_doc = res["documents"]["PUC"]
        self.assertEqual(puc_doc["status"], STATUS_EXPIRED)

        # Check violation detection
        self.assertEqual(len(res["violations"]), 1)
        self.assertEqual(res["violations"][0]["violation_code"], "EXPIRED_PUC")
        self.assertEqual(res["violations"][0]["fine_amount"], 10000.0)
        self.assertEqual(res["fines"]["total_fine"], 10000.0)

    def test_07_vehicle_verification_multiple_violations(self):
        """Vehicle TN09BK3456 has expired Insurance & PUC -> 2 violations, ₹12,000 fine."""
        today = date(2026, 11, 7)
        res = verify_vehicle_compliance("TN09BK3456", reference_date=today)

        self.assertIsNotNone(res)
        self.assertEqual(res["summary"]["overall_status"], VERDICT_NON_COMPLIANT)
        self.assertEqual(res["summary"]["expired_count"], 2)

        violation_codes = {v["violation_code"] for v in res["violations"]}
        self.assertIn("EXPIRED_INSURANCE", violation_codes)
        self.assertIn("EXPIRED_PUC", violation_codes)

        # 2,000 (Insurance) + 10,000 (PUC) = 12,000
        self.assertEqual(res["fines"]["total_fine"], 12000.0)
        self.assertEqual(len(res["fines"]["items"]), 2)

    def test_08_vehicle_verification_expiring_soon(self):
        """Vehicle KA03MJ9012 has Insurance expiring soon -> ATTENTION_REQUIRED, 0 fines."""
        today = date(2026, 11, 7)
        res = verify_vehicle_compliance("KA03MJ9012", reference_date=today)

        self.assertIsNotNone(res)
        self.assertEqual(res["summary"]["overall_status"], VERDICT_ATTENTION_REQUIRED)
        self.assertEqual(res["summary"]["expiring_count"], 1)
        self.assertEqual(res["summary"]["expired_count"], 0)
        self.assertFalse(res["summary"]["has_violations"])
        self.assertEqual(res["fines"]["total_fine"], 0.0)

    def test_09_vehicle_verification_missing_document(self):
        """Test vehicle with missing document record correctly detects MISSING violation."""
        conn = get_db_path()
        # Clean up any leftover test vehicle
        from database import get_db_connection
        with get_db_connection(conn) as db:
            db.execute("DELETE FROM vehicles WHERE registration_number = 'TEST99MISS1';")
            db.commit()

        temp_v_id = insert_vehicle(
            registration_number="TEST99MISS1",
            owner_name="Test Missing Docs",
            vehicle_type="Car",
            vehicle_model="Test Model",
            registration_date="2024-01-01"
        )
        try:
            insert_document(
                vehicle_id=temp_v_id,
                document_type="RC",
                document_number="RC-TEST-99",
                issue_date="2024-01-01",
                expiry_date="2039-01-01",
                status="VALID"
            )
            insert_document(
                vehicle_id=temp_v_id,
                document_type="INSURANCE",
                document_number="POL-TEST-99",
                issue_date="2026-01-01",
                expiry_date="2027-01-01",
                status="VALID"
            )

            res = verify_vehicle_compliance("TEST99MISS1", reference_date=date(2026, 11, 7))
            self.assertIsNotNone(res)
            self.assertEqual(res["summary"]["missing_count"], 2)  # PUC and ROAD_TAX are missing
            self.assertEqual(res["documents"]["PUC"]["status"], STATUS_MISSING)
            self.assertEqual(res["documents"]["ROAD_TAX"]["status"], STATUS_MISSING)

            violation_codes = {v["violation_code"] for v in res["violations"]}
            self.assertIn("MISSING_PUC", violation_codes)
            self.assertIn("MISSING_ROAD_TAX", violation_codes)
            self.assertEqual(res["summary"]["overall_status"], VERDICT_NON_COMPLIANT)
        finally:
            with get_db_connection(conn) as db:
                db.execute("DELETE FROM vehicles WHERE id = ?;", (temp_v_id,))
                db.commit()

    def test_10_invalid_registration_number(self):
        """Non-existent vehicle returns None."""
        res = verify_vehicle_compliance("NOTFOUND9999")
        self.assertIsNone(res)

    # ------------------------------------------------------------------------
    # 3. Fine Calculation Module
    # ------------------------------------------------------------------------
    def test_11_fine_calculation_deduplication(self):
        """Duplicate violations in input must be deduplicated to avoid double charging."""
        input_violations = [
            "EXPIRED_INSURANCE",
            "EXPIRED_INSURANCE",  # Duplicate
            "SIGNAL_JUMP",
            "SIGNAL_JUMP",        # Duplicate
            "EXPIRED_PUC",
        ]
        breakdown = calculate_fine_breakdown(input_violations)

        self.assertEqual(breakdown["violations_count"], 3)
        self.assertEqual(breakdown["duplicate_violations_ignored"], 2)
        # 2000 (Insurance) + 1000 (Signal) + 10000 (PUC) = 13000
        self.assertEqual(breakdown["total_fine"], 13000.0)

    def test_12_fine_calculation_custom_overrides(self):
        """Fine calculation supports custom monetary overrides."""
        input_violations = ["EXPIRED_INSURANCE", "SIGNAL_JUMP"]
        overrides = {
            "EXPIRED_INSURANCE": 3000.0,  # Increased fine
            "SIGNAL_JUMP": 1500.0,
        }
        breakdown = calculate_fine_breakdown(input_violations, custom_overrides=overrides)

        self.assertEqual(breakdown["total_fine"], 4500.0)
        ins_item = next(i for i in breakdown["items"] if i["violation_code"] == "EXPIRED_INSURANCE")
        self.assertEqual(ins_item["fine_amount"], 3000.0)

    # ------------------------------------------------------------------------
    # 4. Flask REST API Integration Endpoints
    # ------------------------------------------------------------------------
    def test_13_api_get_verify_endpoint(self):
        """GET /api/vehicles/<plate>/verify returns 200 with full verification JSON."""
        # 1. Valid clean vehicle
        res_clean = self.client.get("/api/vehicles/DL01AB1234/verify?reference_date=2026-11-07")
        self.assertEqual(res_clean.status_code, 200)
        data_clean = res_clean.get_json()
        self.assertTrue(data_clean["success"])
        self.assertEqual(data_clean["summary"]["overall_status"], VERDICT_COMPLIANT)
        self.assertEqual(data_clean["summary"]["valid_count"], 4)

        # 2. Vehicle with violation
        res_viol = self.client.get("/api/vehicles/MH12DE5678/verify?reference_date=2026-11-07")
        self.assertEqual(res_viol.status_code, 200)
        data_viol = res_viol.get_json()
        self.assertEqual(data_viol["summary"]["overall_status"], VERDICT_NON_COMPLIANT)
        self.assertEqual(data_viol["summary"]["expired_count"], 1)

        # 3. Non-existent vehicle returns 404
        res_404 = self.client.get("/api/vehicles/NOTREAL99/verify")
        self.assertEqual(res_404.status_code, 404)
        data_404 = res_404.get_json()
        self.assertFalse(data_404["success"])

    def test_14_api_post_verify_endpoint(self):
        """POST /api/vehicles/verify returns 200 on success, 400 on missing plate."""
        # 1. Successful POST verification
        payload = {
            "registration_number": "TN09BK3456",
            "reference_date": "2026-11-07"
        }
        res = self.client.post("/api/vehicles/verify", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["summary"]["overall_status"], VERDICT_NON_COMPLIANT)
        self.assertEqual(data["summary"]["expired_count"], 2)

        # 2. Missing registration_number -> 400 Bad Request
        res_bad = self.client.post("/api/vehicles/verify", json={})
        self.assertEqual(res_bad.status_code, 400)
        self.assertFalse(res_bad.get_json()["success"])

        # 3. Non-existent vehicle -> 404 Not Found
        res_missing = self.client.post("/api/vehicles/verify", json={"registration_number": "NOPE1111"})
        self.assertEqual(res_missing.status_code, 404)

    def test_15_api_post_challans_calculate(self):
        """POST /api/challans/calculate calculates fines for violations or vehicle plate."""
        # 1. By explicit list of violation codes
        res_codes = self.client.post("/api/challans/calculate", json={
            "violations": ["EXPIRED_INSURANCE", "SIGNAL_JUMP"]
        })
        self.assertEqual(res_codes.status_code, 200)
        data_codes = res_codes.get_json()
        self.assertTrue(data_codes["success"])
        self.assertEqual(data_codes["calculation"]["total_fine"], 3000.0)
        self.assertEqual(data_codes["calculation"]["violations_count"], 2)

        # 2. By vehicle registration number
        res_veh = self.client.post("/api/challans/calculate", json={
            "registration_number": "MH12DE5678",
            "reference_date": "2026-11-07",
            "additional_violations": ["NO_HELMET"]
        })
        self.assertEqual(res_veh.status_code, 200)
        data_veh = res_veh.get_json()
        self.assertTrue(data_veh["success"])
        # 10,000 (Expired PUC from DB) + 1,000 (No Helmet) = 11,000
        self.assertEqual(data_veh["calculation"]["total_fine"], 11000.0)

        # 3. Empty request body -> 400 Bad Request
        res_bad = self.client.post("/api/challans/calculate", json={})
        self.assertEqual(res_bad.status_code, 400)

    # ------------------------------------------------------------------------
    # 5. Regression Check: Existing Phase 1 & Phase 2 Endpoints
    # ------------------------------------------------------------------------
    def test_16_regression_existing_endpoints(self):
        """Verify GET /api/health and Phase 2 endpoints remain intact."""
        # Health check
        res_health = self.client.get("/api/health")
        self.assertEqual(res_health.status_code, 200)
        self.assertEqual(res_health.get_json()["status"], "healthy")

        # Vehicles list
        res_veh = self.client.get("/api/vehicles")
        self.assertEqual(res_veh.status_code, 200)
        self.assertGreaterEqual(res_veh.get_json()["count"], 15)

        # Challans list
        res_ch = self.client.get("/api/challans")
        self.assertEqual(res_ch.status_code, 200)
        self.assertGreaterEqual(res_ch.get_json()["count"], 1)


def run_tests():
    """Run all Phase 3 tests with formatted verbose output."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(VerificationEngineTestSuite)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
