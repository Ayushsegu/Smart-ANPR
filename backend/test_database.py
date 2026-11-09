"""
test_database.py - Database & API Verification Test Suite
=========================================================
Smart ANPR Vehicle Verification System

Tests all 8 core database requirements for Phase 2:
1. Database connection.
2. All three tables exist (VEHICLES, DOCUMENTS, CHALLANS).
3. At least 15 vehicles are inserted.
4. Each vehicle has four document records (RC, INSURANCE, PUC, ROAD_TAX).
5. Vehicle registration number search works (case-insensitive, exact).
6. Expired documents are identified correctly.
7. Foreign key relationships work (integrity constraints & cascade delete).
8. Challan insertion and retrieval work.

Bonus: Tests Flask API endpoints (GET /api/vehicles, /documents, /challans).
"""

import os
import sys
import unittest
import sqlite3
from datetime import datetime
from pathlib import Path

# Add backend directory to path
BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from database import (
    get_db_connection,
    get_db_path,
    get_all_vehicles,
    get_vehicle_by_plate,
    get_vehicle_by_id,
    get_documents_by_vehicle_id,
    get_documents_by_plate,
    get_all_challans,
    get_challans_by_vehicle_id,
    insert_vehicle,
    insert_document,
    insert_challan
)
from app import create_app
from app.core.config import Config


class DatabaseTestSuite(unittest.TestCase):
    """Unit and Integration tests for ANPR SQLite Database and Flask API."""

    @classmethod
    def setUpClass(cls):
        """Ensure database exists and is accessible."""
        cls.db_path = get_db_path()
        if not cls.db_path.exists():
            from seed_data import seed_database
            seed_database(cls.db_path)

        # Flask test client
        cls.app = create_app(Config)
        cls.client = cls.app.test_client()

    # ------------------------------------------------------------------------
    # REQUIREMENT 1: Database connection
    # ------------------------------------------------------------------------
    def test_01_database_connection(self):
        """Verify that a valid connection can be established to anpr.db."""
        conn = get_db_connection()
        self.assertIsNotNone(conn, "Database connection returned None.")
        cursor = conn.cursor()
        cursor.execute("SELECT 1 AS test_val;")
        row = cursor.fetchone()
        self.assertEqual(row["test_val"], 1, "Connection query execution failed.")
        conn.close()

    # ------------------------------------------------------------------------
    # REQUIREMENT 2: All three tables exist
    # ------------------------------------------------------------------------
    def test_02_all_three_tables_exist(self):
        """Verify that VEHICLES, DOCUMENTS, and CHALLANS tables exist."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = {row["name"].lower() for row in cursor.fetchall()}
        conn.close()

        required_tables = {"vehicles", "documents", "challans"}
        for table in required_tables:
            self.assertIn(
                table,
                tables,
                f"Required table '{table}' is missing from the database."
            )

    # ------------------------------------------------------------------------
    # REQUIREMENT 3: At least 15 vehicles are inserted
    # ------------------------------------------------------------------------
    def test_03_at_least_15_vehicles_inserted(self):
        """Verify that at least 15 vehicle records are present in the database."""
        vehicles = get_all_vehicles()
        vehicle_count = len(vehicles)
        self.assertGreaterEqual(
            vehicle_count,
            15,
            f"Expected at least 15 vehicles, but found {vehicle_count}."
        )

        # Verify variety: Cars, Motorcycles, Commercial vehicles
        types = {v["vehicle_type"] for v in vehicles}
        self.assertIn("Car", types, "Missing vehicle type: Car")
        self.assertIn("Motorcycle", types, "Missing vehicle type: Motorcycle")
        self.assertIn("Commercial", types, "Missing vehicle type: Commercial")

    # ------------------------------------------------------------------------
    # REQUIREMENT 4: Each vehicle has four document records
    # ------------------------------------------------------------------------
    def test_04_each_vehicle_has_four_documents(self):
        """Verify that every vehicle has all 4 documents (RC, INSURANCE, PUC, ROAD_TAX)."""
        vehicles = get_all_vehicles()
        expected_doc_types = {"RC", "INSURANCE", "PUC", "ROAD_TAX"}

        for vehicle in [v for v in vehicles if not v.get("demo_id")]:
            v_id = vehicle["id"]
            plate = vehicle["registration_number"]
            docs = get_documents_by_vehicle_id(v_id)

            self.assertEqual(
                len(docs),
                4,
                f"Vehicle {plate} (ID {v_id}) has {len(docs)} documents instead of 4."
            )

            found_types = {d["document_type"] for d in docs}
            self.assertEqual(
                found_types,
                expected_doc_types,
                f"Vehicle {plate} is missing required document types. Found: {found_types}"
            )

            for d in docs:
                self.assertTrue(d["document_number"], f"Missing document number in doc ID {d['id']}")
                self.assertIn(
                    d["status"],
                    ["VALID", "EXPIRING_SOON", "EXPIRED"],
                    f"Invalid status '{d['status']}' in doc ID {d['id']}"
                )

    # ------------------------------------------------------------------------
    # REQUIREMENT 5: Vehicle registration number search works
    # ------------------------------------------------------------------------
    def test_05_vehicle_registration_search(self):
        """Verify search by registration number, including case-insensitivity."""
        # Exact match
        vehicle = get_vehicle_by_plate("DL01AB1234")
        self.assertIsNotNone(vehicle, "Vehicle DL01AB1234 not found.")
        self.assertEqual(vehicle["registration_number"], "DL01AB1234")
        self.assertEqual(vehicle["owner_name"], "Aarav Sharma")
        self.assertEqual(vehicle["vehicle_type"], "Car")

        # Lowercase search
        vehicle_lower = get_vehicle_by_plate("dl01ab1234")
        self.assertIsNotNone(vehicle_lower, "Case-insensitive search for dl01ab1234 failed.")
        self.assertEqual(vehicle_lower["registration_number"], "DL01AB1234")

        # Commercial vehicle search
        comm_vehicle = get_vehicle_by_plate("DL1LAA9988")
        self.assertIsNotNone(comm_vehicle, "Commercial vehicle DL1LAA9988 not found.")
        self.assertEqual(comm_vehicle["vehicle_type"], "Commercial")

        # Non-existent vehicle
        missing = get_vehicle_by_plate("XX99ZZ9999")
        self.assertIsNone(missing, "Non-existent vehicle should return None.")

    # ------------------------------------------------------------------------
    # REQUIREMENT 6: Expired documents are identified correctly
    # ------------------------------------------------------------------------
    def test_06_expired_documents_identified(self):
        """Verify expired documents are flagged and identified with past dates."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM documents WHERE status = 'EXPIRED';")
        expired_docs = cursor.fetchall()
        conn.close()

        self.assertGreater(
            len(expired_docs),
            0,
            "Expected at least one expired document record in the database."
        )

        today = datetime.now().date()
        for doc in expired_docs:
            expiry_date = datetime.strptime(doc["expiry_date"], "%Y-%m-%d").date()
            self.assertLess(
                expiry_date,
                today,
                f"Document {doc['document_number']} marked EXPIRED but expiry {expiry_date} is not in past."
            )

        # Check vehicle with expired PUC: MH12DE5678
        mh_data = get_documents_by_plate("MH12DE5678")
        self.assertIsNotNone(mh_data)
        puc_doc = next(d for d in mh_data["documents"] if d["document_type"] == "PUC")
        self.assertEqual(puc_doc["status"], "EXPIRED", "MH12DE5678 PUC should be EXPIRED.")

    # ------------------------------------------------------------------------
    # REQUIREMENT 7: Foreign key relationships work
    # ------------------------------------------------------------------------
    def test_07_foreign_key_relationships(self):
        """Verify foreign key enforcement on insert and CASCADE on delete."""
        # 1. Foreign key violation on document insertion
        with self.assertRaises(sqlite3.IntegrityError):
            insert_document(
                vehicle_id=999999,  # Non-existent vehicle ID
                document_type="RC",
                document_number="TEST-FK-9999",
                issue_date="2024-01-01",
                expiry_date="2025-01-01",
                status="EXPIRED"
            )

        # 2. Foreign key violation on challan insertion
        with self.assertRaises(sqlite3.IntegrityError):
            insert_challan(
                challan_number="CH-TEST-FK-9999",
                vehicle_id=999999,  # Non-existent vehicle ID
                violation_type="Test Violation",
                fine_amount=500.0,
                challan_date="2026-11-01",
                payment_status="PENDING"
            )

        # 3. Cascade delete verification
        temp_v_id = insert_vehicle(
            registration_number="TEMP99FK1111",
            owner_name="FK Test User",
            vehicle_type="Car",
            vehicle_model="Test Model",
            registration_date="2024-01-01"
        )
        temp_doc_id = insert_document(
            vehicle_id=temp_v_id,
            document_type="RC",
            document_number="TEST-CASCADE-RC",
            issue_date="2024-01-01",
            expiry_date="2039-01-01",
            status="VALID"
        )
        temp_ch_id = insert_challan(
            challan_number="CH-TEMP-CASCADE-01",
            vehicle_id=temp_v_id,
            violation_type="Test Cascade Violation",
            fine_amount=100.0,
            challan_date="2026-11-01",
            payment_status="PENDING"
        )

        # Delete the vehicle
        conn = get_db_connection()
        conn.execute("DELETE FROM vehicles WHERE id = ?;", (temp_v_id,))
        conn.commit()

        # Check cascading deletion of documents and challans
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) AS c FROM documents WHERE vehicle_id = ?;", (temp_v_id,))
        doc_count = cursor.fetchone()["c"]
        cursor.execute("SELECT COUNT(*) AS c FROM challans WHERE vehicle_id = ?;", (temp_v_id,))
        ch_count = cursor.fetchone()["c"]
        conn.close()

        self.assertEqual(doc_count, 0, "CASCADE delete failed for documents table.")
        self.assertEqual(ch_count, 0, "CASCADE delete failed for challans table.")

    # ------------------------------------------------------------------------
    # REQUIREMENT 8: Challan insertion and retrieval work
    # ------------------------------------------------------------------------
    def test_08_challan_insertion_and_retrieval(self):
        """Verify inserting a new challan and retrieving it by vehicle and plate."""
        vehicle = get_vehicle_by_plate("DL01AB1234")
        self.assertIsNotNone(vehicle)
        v_id = vehicle["id"]

        test_challan_number = "CH-TEST-2026-999"
        challan_id = insert_challan(
            challan_number=test_challan_number,
            vehicle_id=v_id,
            violation_type="Signal Jumping",
            fine_amount=1500.0,
            challan_date="2026-11-07",
            payment_status="PENDING",
            description="Automated red-light detection camera at Connaught Place."
        )
        self.assertIsInstance(challan_id, int)
        self.assertGreater(challan_id, 0)

        # Retrieve and verify
        challans = get_challans_by_vehicle_id(v_id)
        found = next((c for c in challans if c["challan_number"] == test_challan_number), None)
        self.assertIsNotNone(found, f"Inserted challan {test_challan_number} not retrieved.")
        self.assertEqual(found["violation_type"], "Signal Jumping")
        self.assertEqual(found["fine_amount"], 1500.0)
        self.assertEqual(found["payment_status"], "PENDING")

        # Cleanup test challan
        conn = get_db_connection()
        conn.execute("DELETE FROM challans WHERE challan_number = ?;", (test_challan_number,))
        conn.commit()
        conn.close()

    # ------------------------------------------------------------------------
    # REQUIREMENT 9: Flask REST API Endpoints Verification
    # ------------------------------------------------------------------------
    def test_09_api_health(self):
        """Verify GET /api/health returns 200 OK."""
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["status"], "healthy")

    def test_10_api_get_all_vehicles(self):
        """Verify GET /api/vehicles returns at least 15 vehicles."""
        response = self.client.get("/api/vehicles")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["success"])
        self.assertGreaterEqual(data["count"], 15)
        self.assertIsInstance(data["vehicles"], list)

    def test_11_api_get_vehicle_by_plate(self):
        """Verify GET /api/vehicles/<plate> returns vehicle details."""
        response = self.client.get("/api/vehicles/DL01AB1234")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["vehicle"]["registration_number"], "DL01AB1234")
        self.assertEqual(data["vehicle"]["owner_name"], "Aarav Sharma")

        # Non-existent vehicle
        missing = self.client.get("/api/vehicles/NOTFOUND99")
        self.assertEqual(missing.status_code, 404)
        missing_data = missing.get_json()
        self.assertFalse(missing_data["success"])

    def test_12_api_get_vehicle_documents(self):
        """Verify GET /api/vehicles/<plate>/documents returns 4 documents."""
        response = self.client.get("/api/vehicles/DL01AB1234/documents")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["registration_number"], "DL01AB1234")
        self.assertEqual(data["documents_count"], 4)
        self.assertEqual(len(data["documents"]), 4)

    def test_13_api_get_challans(self):
        """Verify GET /api/challans returns list of traffic citations."""
        response = self.client.get("/api/challans")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["success"])
        self.assertGreaterEqual(data["count"], 1)
        self.assertIsInstance(data["challans"], list)

        # Filter by registration_number
        filtered = self.client.get("/api/challans?registration_number=MH12DE5678")
        self.assertEqual(filtered.status_code, 200)
        filtered_data = filtered.get_json()
        self.assertTrue(filtered_data["success"])
        for ch in filtered_data["challans"]:
            self.assertEqual(ch["registration_number"], "MH12DE5678")


def run_tests():
    """Run all tests with verbose formatted output."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(DatabaseTestSuite)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
