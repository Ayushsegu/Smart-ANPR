"""
seed_data.py - Synthetic Dataset Generation & Seeding Script
============================================================
Smart ANPR Vehicle Verification System

This script populates the SQLite database with realistic, completely fictional
Indian vehicle records for testing and demonstration purposes.

Features:
- At least 15 vehicles (18 records created) across:
  * Cars (Sedans, SUVs, Hatchbacks)
  * Motorcycles / Two-Wheelers
  * Commercial Vehicles (Trucks, Pickups, Cabs)
- Document conditions:
  * VALID
  * EXPIRING_SOON (within 30 days)
  * EXPIRED (past expiry date)
- Each vehicle has all 4 standard document records:
  1. RC (Registration Certificate)
  2. INSURANCE
  3. PUC (Pollution Under Control)
  4. ROAD_TAX
- Synthetic challans pre-populated for traffic violation history testing.
- Uses parameterized SQL inserts and enforces foreign key integrity.
"""

import sys
from pathlib import Path
from typing import Dict, List, Any

# Ensure backend directory is in Python path
BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from database import (
    get_db_connection,
    get_db_path,
    init_db,
    insert_vehicle,
    insert_document,
    insert_challan
)


# ============================================================================
# Synthetic Dataset Definitions (Completely Fictional)
# ============================================================================

VEHICLES_DATA: List[Dict[str, Any]] = [
    # -----------------------------
    # 1. CARS (8 Records)
    # -----------------------------
    {
        "registration_number": "DL01AB1234",
        "owner_name": "Aarav Sharma",
        "vehicle_type": "Car",
        "vehicle_model": "Hyundai Creta 1.5 SX",
        "registration_date": "2021-04-15",
        "documents": [
            {"type": "RC", "num": "RC-DL01-2021-9871", "issue": "2021-04-15", "expiry": "2036-04-14", "status": "VALID"},
            {"type": "INSURANCE", "num": "POL-HDFC-882910", "issue": "2026-04-10", "expiry": "2027-04-09", "status": "VALID"},
            {"type": "PUC", "num": "PUC-DL-2026-1102", "issue": "2026-05-15", "expiry": "2027-05-14", "status": "VALID"},
            {"type": "ROAD_TAX", "num": "TAX-DL-2021-0091", "issue": "2021-04-15", "expiry": "2036-04-14", "status": "VALID"},
        ]
    },
    {
        "registration_number": "MH12DE5678",
        "owner_name": "Priya Deshmukh",
        "vehicle_type": "Car",
        "vehicle_model": "Maruti Suzuki Swift VXi",
        "registration_date": "2019-08-10",
        "documents": [
            {"type": "RC", "num": "RC-MH12-2019-4512", "issue": "2019-08-10", "expiry": "2034-08-09", "status": "VALID"},
            {"type": "INSURANCE", "num": "POL-ICICI-449102", "issue": "2026-01-15", "expiry": "2027-01-14", "status": "VALID"},
            {"type": "PUC", "num": "PUC-MH-2023-5541", "issue": "2023-08-10", "expiry": "2024-08-09", "status": "EXPIRED"},
            {"type": "ROAD_TAX", "num": "TAX-MH-2019-3382", "issue": "2019-08-10", "expiry": "2034-08-09", "status": "VALID"},
        ]
    },
    {
        "registration_number": "KA03MJ9012",
        "owner_name": "Karthik Nair",
        "vehicle_type": "Car",
        "vehicle_model": "Tata Nexon EV Empowered",
        "registration_date": "2022-01-20",
        "documents": [
            {"type": "RC", "num": "RC-KA03-2022-8172", "issue": "2022-01-20", "expiry": "2037-01-19", "status": "VALID"},
            {"type": "INSURANCE", "num": "POL-TATA-330192", "issue": "2025-11-20", "expiry": "2026-11-20", "status": "EXPIRING_SOON"},
            {"type": "PUC", "num": "PUC-KA-2026-9021", "issue": "2026-02-15", "expiry": "2027-02-14", "status": "VALID"},
            {"type": "ROAD_TAX", "num": "TAX-KA-2022-4410", "issue": "2022-01-20", "expiry": "2037-01-19", "status": "VALID"},
        ]
    },
    {
        "registration_number": "TN09BK3456",
        "owner_name": "Suresh Ramachandran",
        "vehicle_type": "Car",
        "vehicle_model": "Honda City ZX",
        "registration_date": "2018-05-12",
        "documents": [
            {"type": "RC", "num": "RC-TN09-2018-7711", "issue": "2018-05-12", "expiry": "2033-05-11", "status": "VALID"},
            {"type": "INSURANCE", "num": "POL-BAJAJ-771239", "issue": "2024-05-12", "expiry": "2025-05-11", "status": "EXPIRED"},
            {"type": "PUC", "num": "PUC-TN-2024-8821", "issue": "2024-11-10", "expiry": "2025-11-09", "status": "EXPIRED"},
            {"type": "ROAD_TAX", "num": "TAX-TN-2018-5529", "issue": "2018-05-12", "expiry": "2033-05-11", "status": "VALID"},
        ]
    },
    {
        "registration_number": "TS07GH7890",
        "owner_name": "Lakshmi Reddy",
        "vehicle_type": "Car",
        "vehicle_model": "Mahindra Thar 4x4",
        "registration_date": "2023-11-05",
        "documents": [
            {"type": "RC", "num": "RC-TS07-2023-1192", "issue": "2023-11-05", "expiry": "2038-11-04", "status": "VALID"},
            {"type": "INSURANCE", "num": "POL-NEWIND-909211", "issue": "2025-11-05", "expiry": "2026-11-28", "status": "EXPIRING_SOON"},
            {"type": "PUC", "num": "PUC-TS-2026-3390", "issue": "2026-05-02", "expiry": "2027-05-01", "status": "VALID"},
            {"type": "ROAD_TAX", "num": "TAX-TS-2023-6621", "issue": "2023-11-05", "expiry": "2038-11-04", "status": "VALID"},
        ]
    },
    {
        "registration_number": "UP32KL2345",
        "owner_name": "Vikramaditya Verma",
        "vehicle_type": "Car",
        "vehicle_model": "Toyota Innova Crysta",
        "registration_date": "2017-03-25",
        "documents": [
            {"type": "RC", "num": "RC-UP32-2017-6601", "issue": "2017-03-25", "expiry": "2032-03-24", "status": "VALID"},
            {"type": "INSURANCE", "num": "POL-ROYAL-112093", "issue": "2026-03-20", "expiry": "2027-03-19", "status": "VALID"},
            {"type": "PUC", "num": "PUC-UP-2025-4421", "issue": "2025-11-18", "expiry": "2026-11-18", "status": "EXPIRING_SOON"},
            {"type": "ROAD_TAX", "num": "TAX-UP-2017-8820", "issue": "2017-03-25", "expiry": "2032-03-24", "status": "VALID"},
        ]
    },
    {
        "registration_number": "GJ01MN1122",
        "owner_name": "Harsh Patel",
        "vehicle_type": "Car",
        "vehicle_model": "Kia Seltos HTX",
        "registration_date": "2020-09-18",
        "documents": [
            {"type": "RC", "num": "RC-GJ01-2020-5544", "issue": "2020-09-18", "expiry": "2035-09-17", "status": "VALID"},
            {"type": "INSURANCE", "num": "POL-DIGIT-776102", "issue": "2026-09-10", "expiry": "2027-09-09", "status": "VALID"},
            {"type": "PUC", "num": "PUC-GJ-2026-9011", "issue": "2026-09-15", "expiry": "2027-09-14", "status": "VALID"},
            {"type": "ROAD_TAX", "num": "TAX-GJ-2020-1129", "issue": "2020-09-18", "expiry": "2035-09-17", "status": "VALID"},
        ]
    },
    {
        "registration_number": "CH01XY2468",
        "owner_name": "Jaspreet Kaur",
        "vehicle_type": "Car",
        "vehicle_model": "Volkswagen Virtus GT",
        "registration_date": "2023-06-14",
        "documents": [
            {"type": "RC", "num": "RC-CH01-2023-9912", "issue": "2023-06-14", "expiry": "2038-06-13", "status": "VALID"},
            {"type": "INSURANCE", "num": "POL-HDFC-993201", "issue": "2026-06-10", "expiry": "2027-06-09", "status": "VALID"},
            {"type": "PUC", "num": "PUC-CH-2026-4409", "issue": "2026-06-12", "expiry": "2027-06-11", "status": "VALID"},
            {"type": "ROAD_TAX", "num": "TAX-CH-2023-7720", "issue": "2023-06-14", "expiry": "2026-06-13", "status": "EXPIRED"},
        ]
    },

    # -----------------------------
    # 2. MOTORCYCLES (5 Records)
    # -----------------------------
    {
        "registration_number": "HR26CV6789",
        "owner_name": "Amit Choudhary",
        "vehicle_type": "Motorcycle",
        "vehicle_model": "Royal Enfield Classic 350",
        "registration_date": "2020-02-14",
        "documents": [
            {"type": "RC", "num": "RC-HR26-2020-3344", "issue": "2020-02-14", "expiry": "2035-02-13", "status": "VALID"},
            {"type": "INSURANCE", "num": "POL-ORIENTAL-8871", "issue": "2024-02-14", "expiry": "2025-02-13", "status": "EXPIRED"},
            {"type": "PUC", "num": "PUC-HR-2026-2211", "issue": "2026-02-10", "expiry": "2027-02-09", "status": "VALID"},
            {"type": "ROAD_TAX", "num": "TAX-HR-2020-5591", "issue": "2020-02-14", "expiry": "2035-02-13", "status": "VALID"},
        ]
    },
    {
        "registration_number": "KA05EF1002",
        "owner_name": "Deepa Srinivas",
        "vehicle_type": "Motorcycle",
        "vehicle_model": "Honda Activa 6G",
        "registration_date": "2022-07-22",
        "documents": [
            {"type": "RC", "num": "RC-KA05-2022-1092", "issue": "2022-07-22", "expiry": "2037-07-21", "status": "VALID"},
            {"type": "INSURANCE", "num": "POL-ICICI-661092", "issue": "2026-07-15", "expiry": "2027-07-14", "status": "VALID"},
            {"type": "PUC", "num": "PUC-KA-2026-7731", "issue": "2026-07-20", "expiry": "2027-07-19", "status": "VALID"},
            {"type": "ROAD_TAX", "num": "TAX-KA-2022-9011", "issue": "2022-07-22", "expiry": "2037-07-21", "status": "VALID"},
        ]
    },
    {
        "registration_number": "MH04GH4321",
        "owner_name": "Rohan Sawant",
        "vehicle_type": "Motorcycle",
        "vehicle_model": "Bajaj Pulsar NS200",
        "registration_date": "2019-12-01",
        "documents": [
            {"type": "RC", "num": "RC-MH04-2019-8833", "issue": "2019-12-01", "expiry": "2034-11-30", "status": "VALID"},
            {"type": "INSURANCE", "num": "POL-BAJAJ-550192", "issue": "2024-11-25", "expiry": "2025-11-24", "status": "EXPIRED"},
            {"type": "PUC", "num": "PUC-MH-2024-6610", "issue": "2024-11-30", "expiry": "2025-11-29", "status": "EXPIRED"},
            {"type": "ROAD_TAX", "num": "TAX-MH-2019-4401", "issue": "2019-12-01", "expiry": "2034-11-30", "status": "VALID"},
        ]
    },
    {
        "registration_number": "TN07JK9876",
        "owner_name": "Kavitha Sundaram",
        "vehicle_type": "Motorcycle",
        "vehicle_model": "TVS Jupiter 125",
        "registration_date": "2023-03-10",
        "documents": [
            {"type": "RC", "num": "RC-TN07-2023-2299", "issue": "2023-03-10", "expiry": "2038-03-09", "status": "VALID"},
            {"type": "INSURANCE", "num": "POL-UNITED-441290", "issue": "2026-03-05", "expiry": "2027-03-04", "status": "VALID"},
            {"type": "PUC", "num": "PUC-TN-2025-8830", "issue": "2025-11-22", "expiry": "2026-11-22", "status": "EXPIRING_SOON"},
            {"type": "ROAD_TAX", "num": "TAX-TN-2023-1102", "issue": "2023-03-10", "expiry": "2038-03-09", "status": "VALID"},
        ]
    },
    {
        "registration_number": "DL08NM5432",
        "owner_name": "Rajesh Khanna",
        "vehicle_type": "Motorcycle",
        "vehicle_model": "Yamaha FZ-S FI",
        "registration_date": "2021-10-05",
        "documents": [
            {"type": "RC", "num": "RC-DL08-2021-4477", "issue": "2021-10-05", "expiry": "2036-10-04", "status": "VALID"},
            {"type": "INSURANCE", "num": "POL-SBI-881903", "issue": "2026-10-01", "expiry": "2027-09-30", "status": "VALID"},
            {"type": "PUC", "num": "PUC-DL-2026-3391", "issue": "2026-10-02", "expiry": "2027-10-01", "status": "VALID"},
            {"type": "ROAD_TAX", "num": "TAX-DL-2021-7781", "issue": "2021-10-05", "expiry": "2036-10-04", "status": "VALID"},
        ]
    },

    # -----------------------------
    # 3. COMMERCIAL VEHICLES (5 Records)
    # -----------------------------
    {
        "registration_number": "DL1LAA9988",
        "owner_name": "Baljit Logistics Services",
        "vehicle_type": "Commercial",
        "vehicle_model": "Tata Ace Gold Mini Truck",
        "registration_date": "2021-06-18",
        "documents": [
            {"type": "RC", "num": "RC-DL1L-2021-9988", "issue": "2021-06-18", "expiry": "2036-06-17", "status": "VALID"},
            {"type": "INSURANCE", "num": "POL-NEWIND-552190", "issue": "2024-06-15", "expiry": "2025-06-14", "status": "EXPIRED"},
            {"type": "PUC", "num": "PUC-DL-2026-8819", "issue": "2026-06-10", "expiry": "2027-06-09", "status": "VALID"},
            {"type": "ROAD_TAX", "num": "TAX-DL-2021-4412", "issue": "2021-06-18", "expiry": "2024-06-17", "status": "EXPIRED"},
        ]
    },
    {
        "registration_number": "MH02CR3322",
        "owner_name": "Metro Freight Lines Ltd",
        "vehicle_type": "Commercial",
        "vehicle_model": "Ashok Leyland Dost+",
        "registration_date": "2022-04-11",
        "documents": [
            {"type": "RC", "num": "RC-MH02-2022-3322", "issue": "2022-04-11", "expiry": "2037-04-10", "status": "VALID"},
            {"type": "INSURANCE", "num": "POL-HDFC-667120", "issue": "2026-04-05", "expiry": "2027-04-04", "status": "VALID"},
            {"type": "PUC", "num": "PUC-MH-2026-9901", "issue": "2026-04-10", "expiry": "2027-04-09", "status": "VALID"},
            {"type": "ROAD_TAX", "num": "TAX-MH-2022-8810", "issue": "2022-04-11", "expiry": "2027-04-10", "status": "VALID"},
        ]
    },
    {
        "registration_number": "KA04TR5544",
        "owner_name": "Bengaluru Cabs Network",
        "vehicle_type": "Commercial",
        "vehicle_model": "Maruti Suzuki Dzire Tour",
        "registration_date": "2020-01-15",
        "documents": [
            {"type": "RC", "num": "RC-KA04-2020-5544", "issue": "2020-01-15", "expiry": "2035-01-14", "status": "VALID"},
            {"type": "INSURANCE", "num": "POL-TATA-771920", "issue": "2025-11-26", "expiry": "2026-11-26", "status": "EXPIRING_SOON"},
            {"type": "PUC", "num": "PUC-KA-2026-3312", "issue": "2026-01-10", "expiry": "2027-01-09", "status": "VALID"},
            {"type": "ROAD_TAX", "num": "TAX-KA-2020-4491", "issue": "2020-01-15", "expiry": "2027-01-14", "status": "VALID"},
        ]
    },
    {
        "registration_number": "WB02PQ3344",
        "owner_name": "Ganga Transport Cargo",
        "vehicle_type": "Commercial",
        "vehicle_model": "BharatBenz 1617R Medium Truck",
        "registration_date": "2018-09-02",
        "documents": [
            {"type": "RC", "num": "RC-WB02-2018-3344", "issue": "2018-09-02", "expiry": "2033-09-01", "status": "VALID"},
            {"type": "INSURANCE", "num": "POL-NATIONAL-119201", "issue": "2026-08-25", "expiry": "2027-08-24", "status": "VALID"},
            {"type": "PUC", "num": "PUC-WB-2024-5540", "issue": "2024-09-01", "expiry": "2025-08-31", "status": "EXPIRED"},
            {"type": "ROAD_TAX", "num": "TAX-WB-2018-7711", "issue": "2018-09-02", "expiry": "2028-09-01", "status": "VALID"},
        ]
    },
    {
        "registration_number": "GJ03TX7766",
        "owner_name": "Western Express Cargo",
        "vehicle_type": "Commercial",
        "vehicle_model": "Mahindra Bolero Maxi Truck Plus",
        "registration_date": "2023-08-29",
        "documents": [
            {"type": "RC", "num": "RC-GJ03-2023-7766", "issue": "2023-08-29", "expiry": "2038-08-28", "status": "VALID"},
            {"type": "INSURANCE", "num": "POL-RELIANCE-882019", "issue": "2026-08-20", "expiry": "2027-08-19", "status": "VALID"},
            {"type": "PUC", "num": "PUC-GJ-2026-6621", "issue": "2026-08-25", "expiry": "2027-08-24", "status": "VALID"},
            {"type": "ROAD_TAX", "num": "TAX-GJ-2023-9930", "issue": "2023-08-29", "expiry": "2028-08-28", "status": "VALID"},
        ]
    }
]


# ============================================================================
# Synthetic Challans Data (Linked to Vehicles)
# ============================================================================

CHALLANS_DATA: List[Dict[str, Any]] = [
    {
        "challan_number": "CH-2026-00101",
        "vehicle_plate": "MH12DE5678",
        "violation_type": "Pollution Under Control (PUC) Violation",
        "fine_amount": 10000.0,
        "challan_date": "2026-10-15",
        "payment_status": "PENDING",
        "description": "Vehicle operating with expired emissions test certificate on Karve Road."
    },
    {
        "challan_number": "CH-2026-00102",
        "vehicle_plate": "TN09BK3456",
        "violation_type": "Driving Without Valid Insurance",
        "fine_amount": 2000.0,
        "challan_date": "2026-09-20",
        "payment_status": "PENDING",
        "description": "Failed to produce active third-party motor insurance policy at Anna Salai."
    },
    {
        "challan_number": "CH-2026-00103",
        "vehicle_plate": "TN09BK3456",
        "violation_type": "Over Speeding (82 km/h in 50 km/h Zone)",
        "fine_amount": 2000.0,
        "challan_date": "2026-07-14",
        "payment_status": "PAID",
        "description": "Automated speed radar camera detection at Inner Ring Road Junction."
    },
    {
        "challan_number": "CH-2026-00104",
        "vehicle_plate": "CH01XY2468",
        "violation_type": "Non-Payment of Road Tax",
        "fine_amount": 5000.0,
        "challan_date": "2026-08-30",
        "payment_status": "PENDING",
        "description": "Defaulted road tax payment beyond 60-day statutory grace period."
    },
    {
        "challan_number": "CH-2026-00105",
        "vehicle_plate": "HR26CV6789",
        "violation_type": "Driving Without Valid Insurance",
        "fine_amount": 2000.0,
        "challan_date": "2026-06-11",
        "payment_status": "PENDING",
        "description": "Expired two-wheeler insurance policy observed during NH-48 checkpoint."
    },
    {
        "challan_number": "CH-2026-00106",
        "vehicle_plate": "MH04GH4321",
        "violation_type": "Riding Without Helmet",
        "fine_amount": 1000.0,
        "challan_date": "2026-05-18",
        "payment_status": "PAID",
        "description": "Rider observed without protective headgear at Majiwada traffic intersection."
    },
    {
        "challan_number": "CH-2026-00107",
        "vehicle_plate": "MH04GH4321",
        "violation_type": "Pollution Under Control (PUC) Violation",
        "fine_amount": 10000.0,
        "challan_date": "2026-10-28",
        "payment_status": "PENDING",
        "description": "Lapsed PUC certificate past grace timeline."
    },
    {
        "challan_number": "CH-2026-00108",
        "vehicle_plate": "DL1LAA9988",
        "violation_type": "Overloading Goods Vehicle",
        "fine_amount": 20000.0,
        "challan_date": "2026-09-05",
        "payment_status": "PENDING",
        "description": "Gross vehicle weight exceeded authorized payload capacity by 45% on GT Karnal Road."
    },
    {
        "challan_number": "CH-2026-00109",
        "vehicle_plate": "WB02PQ3344",
        "violation_type": "Pollution Under Control (PUC) Violation",
        "fine_amount": 10000.0,
        "challan_date": "2026-08-12",
        "payment_status": "PENDING",
        "description": "Heavy commercial vehicle failed mandatory roadside smoke density check on Vidyasagar Setu."
    },
    {
        "challan_number": "CH-2026-00110",
        "vehicle_plate": "DL01AB1234",
        "violation_type": "Improper Lane Driving on Expressway",
        "fine_amount": 1000.0,
        "challan_date": "2026-04-02",
        "payment_status": "PAID",
        "description": "Crossing solid white line and unauthorized right-lane overtaking on Barapullah Corridor."
    }
]


def seed_database(db_path=None, reset_first: bool = True) -> Dict[str, int]:
    """
    Populates the database with synthetic vehicle, document, and challan records.
    Returns counts of inserted records.
    """
    target_path = Path(db_path).resolve() if db_path else get_db_path()

    if reset_first:
        init_db(target_path, drop_existing=True)

    plate_to_id: Dict[str, int] = {}
    inserted_vehicles = 0
    inserted_docs = 0
    inserted_challans = 0

    print("=" * 65)
    print("🌱 ANPR System: Synthetic Data Generator")
    print(f"📁 Target Database: {target_path}")
    print("=" * 65)

    # 1. Insert Vehicles & Documents
    print("🚗 Seeding vehicles and associated 4-document sets...")
    for v in VEHICLES_DATA:
        v_id = insert_vehicle(
            registration_number=v["registration_number"],
            owner_name=v["owner_name"],
            vehicle_type=v["vehicle_type"],
            vehicle_model=v["vehicle_model"],
            registration_date=v["registration_date"],
            db_path=target_path
        )
        plate_to_id[v["registration_number"]] = v_id
        inserted_vehicles += 1

        for doc in v["documents"]:
            insert_document(
                vehicle_id=v_id,
                document_type=doc["type"],
                document_number=doc["num"],
                issue_date=doc["issue"],
                expiry_date=doc["expiry"],
                status=doc["status"],
                db_path=target_path
            )
            inserted_docs += 1

        print(f"  • [{v['vehicle_type']:<10}] {v['registration_number']:<12} | {v['vehicle_model']:<28} (ID: {v_id}) -> 4 Docs Seeded")

    # 2. Insert Challans
    print("\n📜 Seeding synthetic challan history records...")
    for ch in CHALLANS_DATA:
        plate = ch["vehicle_plate"]
        v_id = plate_to_id.get(plate)
        if not v_id:
            print(f"  ⚠️ Warning: Skipping challan {ch['challan_number']} - plate {plate} not found.")
            continue

        insert_challan(
            challan_number=ch["challan_number"],
            vehicle_id=v_id,
            violation_type=ch["violation_type"],
            fine_amount=ch["fine_amount"],
            challan_date=ch["challan_date"],
            payment_status=ch["payment_status"],
            description=ch.get("description", ""),
            db_path=target_path
        )
        inserted_challans += 1
        print(f"  • Citation #{ch['challan_number']:<16} | Vehicle: {plate:<12} | Fine: ₹{ch['fine_amount']:>7,.0f} | Status: {ch['payment_status']}")

    summary = {
        "vehicles": inserted_vehicles,
        "documents": inserted_docs,
        "challans": inserted_challans
    }

    print("=" * 65)
    print("🎉 Synthetic Data Seeding Summary:")
    print(f"   • Total Vehicles Seeded:   {inserted_vehicles} (Target: >= 15)")
    print(f"   • Total Documents Seeded:  {inserted_docs} (4 per vehicle = {inserted_vehicles * 4})")
    print(f"   • Total Challans Seeded:   {inserted_challans}")
    print("=" * 65)

    return summary


if __name__ == "__main__":
    reset = "--no-reset" not in sys.argv
    seed_database(reset_first=reset)
