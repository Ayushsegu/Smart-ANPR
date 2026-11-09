"""
backend/seed_demo_vehicles.py - 50 Pre-Registered Fictional Demo Vehicles Seed Script
=====================================================================================
Smart ANPR Vehicle Verification System

This script seeds EXACTLY 50 comprehensive, pre-registered demo vehicles into the local
SQLite database (backend/data/anpr.db).

Key Features:
- 100% Fictional Demo Data (labelled with is_demo = 1, DEMO-01 to DEMO-50).
- Realistic variety of Cars, Motorcycles, Scooters, SUVs, Commercial & Transport vehicles.
- Full representation of top Indian manufacturers: Maruti Suzuki, Hyundai, Tata, Honda,
  Toyota, Mahindra, Kia, Royal Enfield, TVS, Bajaj, Ashok Leyland, BharatBenz.
- Distinct vehicle-owner and driver/licence records.
- Date-based document status distribution across all 4 mandatory certificates:
  * VALID (> 30 days in future)
  * EXPIRING SOON (within 30 days)
  * EXPIRED (< 0 days in past)
  * MISSING (document omitted)
- Previous demo traffic citations (both PAID and PENDING).
- Fully idempotent: will NOT duplicate records or delete existing data.
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta

# Ensure backend root is on sys.path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from database import (
    get_db_connection,
    get_db_path,
    migrate_vehicles_for_demo,
    insert_demo_vehicle,
    insert_document,
    insert_challan,
    get_demo_fleet_metrics,
)

# Reference current date for dynamic document calculation
TODAY = datetime.now().date()

# Helper date generators
def future_date(days: int) -> str:
    return (TODAY + timedelta(days=days)).isoformat()

def past_date(days: int) -> str:
    return (TODAY - timedelta(days=days)).isoformat()


# 50 Comprehensive Demo Vehicle Specifications
DEMO_VEHICLES_DATA = [
    # ─────────────────────────────────────────────────────────────────────────────
    # DELHI FLEET (DL-01 Mall Road RTO) - DEMO-01 to DEMO-12
    # ─────────────────────────────────────────────────────────────────────────────
    {
        "demo_id": "DEMO-01",
        "plate": "DL01DM0001",
        "state": "Delhi",
        "rto": "DL-01 (Mall Road RTO)",
        "owner": "Vikramaditya Malhotra [Demo Owner]",
        "phone": "+91-98765-01001",
        "address": "42, Preet Vihar, Vikas Marg, New Delhi",
        "driver": "Vikramaditya Malhotra",
        "dl_num": "DL-012018001001",
        "dl_class": "MCWG / LMV-NT",
        "dl_expiry": future_date(1800),
        "dl_status": "VALID",
        "make": "Maruti Suzuki",
        "model": "Swift Dzire ZXi+ 1.2",
        "class": "Car",
        "type": "Car",
        "color": "Pearl Arctic White",
        "fuel": "Petrol",
        "year": 2022,
        "reg_date": "2022-03-15",
        "status": "ACTIVE",
        "compliance_profile": "FULLY_COMPLIANT",  # All 4 valid
    },
    {
        "demo_id": "DEMO-02",
        "plate": "DL01DM0002",
        "state": "Delhi",
        "rto": "DL-01 (Mall Road RTO)",
        "owner": "Neha Singhania [Demo Owner]",
        "phone": "+91-98765-01002",
        "address": "B-12, Greater Kailash Part 1, New Delhi",
        "driver": "Ramesh Kumar (Chauffeur)",
        "dl_num": "DL-012015001002",
        "dl_class": "LMV-TR",
        "dl_expiry": future_date(900),
        "dl_status": "VALID",
        "make": "Hyundai",
        "model": "Creta 1.5 SX(O) Turbo",
        "class": "SUV",
        "type": "SUV",
        "color": "Titan Grey",
        "fuel": "Petrol",
        "year": 2023,
        "reg_date": "2023-01-20",
        "status": "ACTIVE",
        "compliance_profile": "EXPIRED_PUC",  # PUC expired 45 days ago
    },
    {
        "demo_id": "DEMO-03",
        "plate": "DL01DM0003",
        "state": "Delhi",
        "rto": "DL-01 (Mall Road RTO)",
        "owner": "Karanveer Oberoi [Demo Owner]",
        "phone": "+91-98765-01003",
        "address": "78, Shanti Niketan, New Delhi",
        "driver": "Karanveer Oberoi",
        "dl_num": "DL-012019001003",
        "dl_class": "LMV",
        "dl_expiry": future_date(2200),
        "dl_status": "VALID",
        "make": "Tata",
        "model": "Nexon EV Empowered+",
        "class": "SUV",
        "type": "SUV",
        "color": "Pristine White",
        "fuel": "Electric",
        "year": 2023,
        "reg_date": "2023-06-10",
        "status": "ACTIVE",
        "compliance_profile": "EXPIRING_INSURANCE",  # Insurance expires in 12 days
    },
    {
        "demo_id": "DEMO-04",
        "plate": "DL01DM0004",
        "state": "Delhi",
        "rto": "DL-01 (Mall Road RTO)",
        "owner": "Aditya Kapoor [Demo Owner]",
        "phone": "+91-98765-01004",
        "address": "15, Barakhamba Road, Connaught Place, New Delhi",
        "driver": "Aditya Kapoor",
        "dl_num": "DL-012017001004",
        "dl_class": "MCWG",
        "dl_expiry": future_date(1400),
        "dl_status": "VALID",
        "make": "Royal Enfield",
        "model": "Classic 350 Stealth Black",
        "class": "Motorcycle",
        "type": "Motorcycle",
        "color": "Matte Stealth Black",
        "fuel": "Petrol",
        "year": 2021,
        "reg_date": "2021-08-14",
        "status": "ACTIVE",
        "compliance_profile": "FULLY_COMPLIANT",
    },
    {
        "demo_id": "DEMO-05",
        "plate": "DL01DM0005",
        "state": "Delhi",
        "rto": "DL-01 (Mall Road RTO)",
        "owner": "Pooja Sundaram [Demo Owner]",
        "phone": "+91-98765-01005",
        "address": "C-4, Vasant Kunj Sector C, New Delhi",
        "driver": "Pooja Sundaram",
        "dl_num": "DL-012020001005",
        "dl_class": "MCWG / LMV",
        "dl_expiry": future_date(2500),
        "dl_status": "VALID",
        "make": "Honda",
        "model": "Activa 6G Deluxe",
        "class": "Scooter",
        "type": "Scooter",
        "color": "Decent Blue Metallic",
        "fuel": "Petrol",
        "year": 2022,
        "reg_date": "2022-11-05",
        "status": "ACTIVE",
        "compliance_profile": "EXPIRED_INSURANCE",  # Insurance expired 60 days ago
    },
    {
        "demo_id": "DEMO-06",
        "plate": "DL01DM0006",
        "state": "Delhi",
        "rto": "DL-01 (Mall Road RTO)",
        "owner": "Capital Parcel Express Pvt Ltd [Demo Owner]",
        "phone": "+91-98765-01006",
        "address": "Plot 88, Okhla Industrial Area Phase 2, New Delhi",
        "driver": "Baldev Yadav",
        "dl_num": "DL-012014001006",
        "dl_class": "TRANS",
        "dl_expiry": future_date(600),
        "dl_status": "VALID",
        "make": "Tata",
        "model": "Ace Gold Diesel Plus",
        "class": "Commercial",
        "type": "Commercial",
        "color": "Artic White",
        "fuel": "Diesel",
        "year": 2020,
        "reg_date": "2020-09-18",
        "status": "ACTIVE",
        "compliance_profile": "EXPIRED_TAX_AND_PUC",  # Road Tax & PUC expired
    },
    {
        "demo_id": "DEMO-07",
        "plate": "DL01DM0007",
        "state": "Delhi",
        "rto": "DL-01 (Mall Road RTO)",
        "owner": "Siddharth Chawla [Demo Owner]",
        "phone": "+91-98765-01007",
        "address": "29, Punjabi Bagh West, New Delhi",
        "driver": "Siddharth Chawla",
        "dl_num": "DL-012016001007",
        "dl_class": "LMV",
        "dl_expiry": future_date(1200),
        "dl_status": "VALID",
        "make": "Honda",
        "model": "City ZX e:HEV Hybrid",
        "class": "Car",
        "type": "Car",
        "color": "Radiant Red Metallic",
        "fuel": "Hybrid",
        "year": 2023,
        "reg_date": "2023-04-12",
        "status": "ACTIVE",
        "compliance_profile": "FULLY_COMPLIANT",
    },
    {
        "demo_id": "DEMO-08",
        "plate": "DL01DM0008",
        "state": "Delhi",
        "rto": "DL-01 (Mall Road RTO)",
        "owner": "Harpreet Singh Sodhi [Demo Owner]",
        "phone": "+91-98765-01008",
        "address": "104, Model Town Phase 3, Delhi",
        "driver": "Harpreet Singh Sodhi",
        "dl_num": "DL-012013001008",
        "dl_class": "LMV / MCWG",
        "dl_expiry": future_date(850),
        "dl_status": "VALID",
        "make": "Mahindra",
        "model": "Thar LX 4x4 Hard Top",
        "class": "SUV",
        "type": "SUV",
        "color": "Napoli Black",
        "fuel": "Diesel",
        "year": 2021,
        "reg_date": "2021-12-04",
        "status": "ACTIVE",
        "compliance_profile": "EXPIRING_PUC",  # PUC expires in 8 days
    },
    {
        "demo_id": "DEMO-09",
        "plate": "DL01DM0009",
        "state": "Delhi",
        "rto": "DL-01 (Mall Road RTO)",
        "owner": "Meenakshi Iyer [Demo Owner]",
        "phone": "+91-98765-01009",
        "address": "56, Chittaranjan Park, New Delhi",
        "driver": "Meenakshi Iyer",
        "dl_num": "DL-012021001009",
        "dl_class": "MCWG",
        "dl_expiry": future_date(3000),
        "dl_status": "VALID",
        "make": "TVS",
        "model": "Jupiter 125 Disc SmartXonnect",
        "class": "Scooter",
        "type": "Scooter",
        "color": "Dawn Orange",
        "fuel": "Petrol",
        "year": 2023,
        "reg_date": "2023-08-25",
        "status": "ACTIVE",
        "compliance_profile": "FULLY_COMPLIANT",
    },
    {
        "demo_id": "DEMO-10",
        "plate": "DL01DM0010",
        "state": "Delhi",
        "rto": "DL-01 (Mall Road RTO)",
        "owner": "Varun Batra [Demo Owner]",
        "phone": "+91-98765-01010",
        "address": "18, Civil Lines, North Delhi",
        "driver": "Varun Batra",
        "dl_num": "DL-012012001010",
        "dl_class": "LMV",
        "dl_expiry": past_date(30),  # Lapsed driver licence
        "dl_status": "EXPIRED",
        "make": "Toyota",
        "model": "Innova Crysta 2.4 ZX",
        "class": "SUV",
        "type": "SUV",
        "color": "Silver Metallic",
        "fuel": "Diesel",
        "year": 2020,
        "reg_date": "2020-02-18",
        "status": "ACTIVE",
        "compliance_profile": "MISSING_PUC",  # Missing mandatory PUC record
    },
    {
        "demo_id": "DEMO-11",
        "plate": "DL01DM0011",
        "state": "Delhi",
        "rto": "DL-01 (Mall Road RTO)",
        "owner": "Arjun Khanna [Demo Owner]",
        "phone": "+91-98765-01011",
        "address": "82, Defence Colony, New Delhi",
        "driver": "Arjun Khanna",
        "dl_num": "DL-012019001011",
        "dl_class": "MCWG",
        "dl_expiry": future_date(1900),
        "dl_status": "VALID",
        "make": "Bajaj",
        "model": "Pulsar NS200 Dual ABS",
        "class": "Motorcycle",
        "type": "Motorcycle",
        "color": "Burnt Red",
        "fuel": "Petrol",
        "year": 2022,
        "reg_date": "2022-07-19",
        "status": "ACTIVE",
        "compliance_profile": "FULLY_COMPLIANT",
    },
    {
        "demo_id": "DEMO-12",
        "plate": "DL01DM0012",
        "state": "Delhi",
        "rto": "DL-01 (Mall Road RTO)",
        "owner": "Delhi Regional Express Cargo [Demo Owner]",
        "phone": "+91-98765-01012",
        "address": "Transport Nagar, Sanjay Gandhi Transport Nagar, Delhi",
        "driver": "Surender Pal",
        "dl_num": "DL-012011001012",
        "dl_class": "TRANS / HGV",
        "dl_expiry": future_date(500),
        "dl_status": "VALID",
        "make": "Ashok Leyland",
        "model": "Dost Strong 1.5",
        "class": "Transport",
        "type": "Transport",
        "color": "Cascade White",
        "fuel": "Diesel",
        "year": 2019,
        "reg_date": "2019-10-10",
        "status": "ACTIVE",
        "compliance_profile": "EXPIRED_RC",  # RC expired 90 days ago
    },

    # ─────────────────────────────────────────────────────────────────────────────
    # HARYANA FLEET (HR-26 Gurugram RTO) - DEMO-13 to DEMO-22
    # ─────────────────────────────────────────────────────────────────────────────
    {
        "demo_id": "DEMO-13",
        "plate": "HR26DM0013",
        "state": "Haryana",
        "rto": "HR-26 (Gurugram RTO)",
        "owner": "Rajeshwari Dalmia [Demo Owner]",
        "phone": "+91-98765-01013",
        "address": "Penthouse 14, DLF Phase 5, Golf Course Road, Gurugram",
        "driver": "Sunil Gurjar (Chauffeur)",
        "dl_num": "HR-262016001013",
        "dl_class": "LMV-TR",
        "dl_expiry": future_date(1100),
        "dl_status": "VALID",
        "make": "Kia",
        "model": "Seltos GTX+ Turbo",
        "class": "SUV",
        "type": "SUV",
        "color": "Glacier White Pearl",
        "fuel": "Petrol",
        "year": 2023,
        "reg_date": "2023-09-01",
        "status": "ACTIVE",
        "compliance_profile": "FULLY_COMPLIANT",
    },
    {
        "demo_id": "DEMO-14",
        "plate": "HR26DM0014",
        "state": "Haryana",
        "rto": "HR-26 (Gurugram RTO)",
        "owner": "Anurag Sharma [Demo Owner]",
        "phone": "+91-98765-01014",
        "address": "302, Sector 57, Gurugram",
        "driver": "Anurag Sharma",
        "dl_num": "HR-262018001014",
        "dl_class": "LMV",
        "dl_expiry": future_date(1700),
        "dl_status": "VALID",
        "make": "Maruti Suzuki",
        "model": "Brezza ZXi Smart Hybrid",
        "class": "SUV",
        "type": "SUV",
        "color": "Brave Khaki with White Roof",
        "fuel": "Petrol",
        "year": 2022,
        "reg_date": "2022-05-18",
        "status": "ACTIVE",
        "compliance_profile": "EXPIRING_INSURANCE",  # Insurance expires in 22 days
    },
    {
        "demo_id": "DEMO-15",
        "plate": "HR26DM0015",
        "state": "Haryana",
        "rto": "HR-26 (Gurugram RTO)",
        "owner": "Manish Tewari [Demo Owner]",
        "phone": "+91-98765-01015",
        "address": "12, South City 1, Gurugram",
        "driver": "Manish Tewari",
        "dl_num": "HR-262020001015",
        "dl_class": "MCWG",
        "dl_expiry": future_date(2400),
        "dl_status": "VALID",
        "make": "Royal Enfield",
        "model": "Hunter 350 Rebel Red",
        "class": "Motorcycle",
        "type": "Motorcycle",
        "color": "Rebel Red",
        "fuel": "Petrol",
        "year": 2023,
        "reg_date": "2023-03-30",
        "status": "ACTIVE",
        "compliance_profile": "FULLY_COMPLIANT",
    },
    {
        "demo_id": "DEMO-16",
        "plate": "HR26DM0016",
        "state": "Haryana",
        "rto": "HR-26 (Gurugram RTO)",
        "owner": "Gurugram Mobility Fleet Ltd [Demo Owner]",
        "phone": "+91-98765-01016",
        "address": "Cyber City Building 10, DLF Phase 2, Gurugram",
        "driver": "Dharmender Yadav",
        "dl_num": "HR-262015001016",
        "dl_class": "LMV-TR",
        "dl_expiry": future_date(750),
        "dl_status": "VALID",
        "make": "Maruti Suzuki",
        "model": "Ertiga Tour M CNG",
        "class": "Commercial",
        "type": "Commercial",
        "color": "Silky Silver",
        "fuel": "CNG",
        "year": 2021,
        "reg_date": "2021-06-25",
        "status": "ACTIVE",
        "compliance_profile": "EXPIRED_PUC",  # PUC expired 80 days ago
    },
    {
        "demo_id": "DEMO-17",
        "plate": "HR26DM0017",
        "state": "Haryana",
        "rto": "HR-26 (Gurugram RTO)",
        "owner": "Shalini Mehra [Demo Owner]",
        "phone": "+91-98765-01017",
        "address": "Flat 604, Nirvana Country, Sector 50, Gurugram",
        "driver": "Shalini Mehra",
        "dl_num": "HR-262019001017",
        "dl_class": "MCWG",
        "dl_expiry": future_date(2100),
        "dl_status": "VALID",
        "make": "TVS",
        "model": "iQube Electric S",
        "class": "Scooter",
        "type": "Scooter",
        "color": "Mint Blue",
        "fuel": "Electric",
        "year": 2022,
        "reg_date": "2022-10-14",
        "status": "ACTIVE",
        "compliance_profile": "FULLY_COMPLIANT",
    },
    {
        "demo_id": "DEMO-18",
        "plate": "HR26DM0018",
        "state": "Haryana",
        "rto": "HR-26 (Gurugram RTO)",
        "owner": "Rajat Bhardwaj [Demo Owner]",
        "phone": "+91-98765-01018",
        "address": "45, Sector 15 Part 2, Gurugram",
        "driver": "Rajat Bhardwaj",
        "dl_num": "HR-262017001018",
        "dl_class": "LMV",
        "dl_expiry": future_date(1350),
        "dl_status": "VALID",
        "make": "Toyota",
        "model": "Urban Cruiser Hyryder V",
        "class": "SUV",
        "type": "SUV",
        "color": "Gaming Grey",
        "fuel": "Hybrid",
        "year": 2023,
        "reg_date": "2023-05-19",
        "status": "ACTIVE",
        "compliance_profile": "EXPIRED_INSURANCE",  # Insurance expired 15 days ago
    },
    {
        "demo_id": "DEMO-19",
        "plate": "HR26DM0019",
        "state": "Haryana",
        "rto": "HR-26 (Gurugram RTO)",
        "owner": "Vikas Ahlawat [Demo Owner]",
        "phone": "+91-98765-01019",
        "address": "90, Sector 4, Manesar Industrial Estate, Haryana",
        "driver": "Kuldeep Nain",
        "dl_num": "HR-262013001019",
        "dl_class": "TRANS / HGV",
        "dl_expiry": future_date(400),
        "dl_status": "VALID",
        "make": "Mahindra",
        "model": "Bolero Maxx Pik-Up HD",
        "class": "Commercial",
        "type": "Commercial",
        "color": "Diamond White",
        "fuel": "Diesel",
        "year": 2021,
        "reg_date": "2021-04-11",
        "status": "ACTIVE",
        "compliance_profile": "EXPIRED_TAX_AND_PUC",
    },
    {
        "demo_id": "DEMO-20",
        "plate": "HR26DM0020",
        "state": "Haryana",
        "rto": "HR-26 (Gurugram RTO)",
        "owner": "Tanvi Goswami [Demo Owner]",
        "phone": "+91-98765-01020",
        "address": "Tower 3, Palm Springs, Golf Course Road, Gurugram",
        "driver": "Tanvi Goswami",
        "dl_num": "HR-262021001020",
        "dl_class": "LMV",
        "dl_expiry": future_date(2800),
        "dl_status": "VALID",
        "make": "Tata",
        "model": "Harrier Fearless Dark Edition",
        "class": "SUV",
        "type": "SUV",
        "color": "Oberon Black",
        "fuel": "Diesel",
        "year": 2023,
        "reg_date": "2023-11-15",
        "status": "ACTIVE",
        "compliance_profile": "FULLY_COMPLIANT",
    },
    {
        "demo_id": "DEMO-21",
        "plate": "HR26DM0021",
        "state": "Haryana",
        "rto": "HR-26 (Gurugram RTO)",
        "owner": "Deepak Grewal [Demo Owner]",
        "phone": "+91-98765-01021",
        "address": "22, Sector 23A, Gurugram",
        "driver": "Deepak Grewal",
        "dl_num": "HR-262014001021",
        "dl_class": "MCWG",
        "dl_expiry": future_date(950),
        "dl_status": "VALID",
        "make": "Bajaj",
        "model": "Dominar 400 Touring",
        "class": "Motorcycle",
        "type": "Motorcycle",
        "color": "Aurora Green",
        "fuel": "Petrol",
        "year": 2020,
        "reg_date": "2020-07-22",
        "status": "ACTIVE",
        "compliance_profile": "EXPIRING_PUC",  # PUC expires in 14 days
    },
    {
        "demo_id": "DEMO-22",
        "plate": "HR26DM0022",
        "state": "Haryana",
        "rto": "HR-26 (Gurugram RTO)",
        "owner": "Express Freight Lines Haryana [Demo Owner]",
        "phone": "+91-98765-01022",
        "address": "NH-48 Bilaspur Chowk, Gurugram Corridor",
        "driver": "Sohan Lal",
        "dl_num": "HR-262010001022",
        "dl_class": "TRANS",
        "dl_expiry": future_date(300),
        "dl_status": "VALID",
        "make": "BharatBenz",
        "model": "1217R Medium Duty Truck",
        "class": "Transport",
        "type": "Transport",
        "color": "Golden Brown",
        "fuel": "Diesel",
        "year": 2018,
        "reg_date": "2018-03-12",
        "status": "ACTIVE",
        "compliance_profile": "MISSING_INSURANCE",  # Missing Insurance certificate
    },

    # ─────────────────────────────────────────────────────────────────────────────
    # MAHARASHTRA FLEET (MH-12 Pune RTO) - DEMO-23 to DEMO-32
    # ─────────────────────────────────────────────────────────────────────────────
    {
        "demo_id": "DEMO-23",
        "plate": "MH12DM0023",
        "state": "Maharashtra",
        "rto": "MH-12 (Pune RTO)",
        "owner": "Chinmay Kulkarni [Demo Owner]",
        "phone": "+91-98765-01023",
        "address": "101, Mayur Colony, Kothrud, Pune",
        "driver": "Chinmay Kulkarni",
        "dl_num": "MH-122018001023",
        "dl_class": "LMV",
        "dl_expiry": future_date(1600),
        "dl_status": "VALID",
        "make": "Tata",
        "model": "Punch Creative i-CNG",
        "class": "Car",
        "type": "Car",
        "color": "Tropical Mist",
        "fuel": "CNG",
        "year": 2023,
        "reg_date": "2023-02-14",
        "status": "ACTIVE",
        "compliance_profile": "FULLY_COMPLIANT",
    },
    {
        "demo_id": "DEMO-24",
        "plate": "MH12DM0024",
        "state": "Maharashtra",
        "rto": "MH-12 (Pune RTO)",
        "owner": "Ananya Deshpande [Demo Owner]",
        "phone": "+91-98765-01024",
        "address": "B-5, Baner Pashan Link Road, Pune",
        "driver": "Ananya Deshpande",
        "dl_num": "MH-122020001024",
        "dl_class": "MCWG",
        "dl_expiry": future_date(2300),
        "dl_status": "VALID",
        "make": "TVS",
        "model": "Apache RTR 160 4V Special",
        "class": "Motorcycle",
        "type": "Motorcycle",
        "color": "Matte Black",
        "fuel": "Petrol",
        "year": 2022,
        "reg_date": "2022-09-09",
        "status": "ACTIVE",
        "compliance_profile": "EXPIRED_PUC",  # PUC expired 110 days ago
    },
    {
        "demo_id": "DEMO-25",
        "plate": "MH12DM0025",
        "state": "Maharashtra",
        "rto": "MH-12 (Pune RTO)",
        "owner": "Prasad Joshi [Demo Owner]",
        "phone": "+91-98765-01025",
        "address": "52, Prabhat Road Lane 4, Pune",
        "driver": "Prasad Joshi",
        "dl_num": "MH-122015001025",
        "dl_class": "LMV",
        "dl_expiry": future_date(800),
        "dl_status": "VALID",
        "make": "Mahindra",
        "model": "XUV700 AX7 Luxury AWD",
        "class": "SUV",
        "type": "SUV",
        "color": "Electric Blue",
        "fuel": "Diesel",
        "year": 2022,
        "reg_date": "2022-04-18",
        "status": "ACTIVE",
        "compliance_profile": "FULLY_COMPLIANT",
    },
    {
        "demo_id": "DEMO-26",
        "plate": "MH12DM0026",
        "state": "Maharashtra",
        "rto": "MH-12 (Pune RTO)",
        "owner": "Western Agro Logistics Ltd [Demo Owner]",
        "phone": "+91-98765-01026",
        "address": "Plot 12, Bhosari MIDC, Pune",
        "driver": "Pandurang Shinde",
        "dl_num": "MH-122012001026",
        "dl_class": "TRANS / HGV",
        "dl_expiry": future_date(450),
        "dl_status": "VALID",
        "make": "Tata",
        "model": "Yodha 2.0 Pickup Truck",
        "class": "Commercial",
        "type": "Commercial",
        "color": "Noble White",
        "fuel": "Diesel",
        "year": 2021,
        "reg_date": "2021-01-28",
        "status": "ACTIVE",
        "compliance_profile": "EXPIRING_INSURANCE",  # Insurance expires in 5 days
    },
    {
        "demo_id": "DEMO-27",
        "plate": "MH12DM0027",
        "state": "Maharashtra",
        "rto": "MH-12 (Pune RTO)",
        "owner": "Smita Gokhale [Demo Owner]",
        "phone": "+91-98765-01027",
        "address": "702, Amanora Park Town, Hadapsar, Pune",
        "driver": "Smita Gokhale",
        "dl_num": "MH-122019001027",
        "dl_class": "MCWG",
        "dl_expiry": future_date(2000),
        "dl_status": "VALID",
        "make": "Ather",
        "model": "450X Gen 3 Pro Pack",
        "class": "Scooter",
        "type": "Scooter",
        "color": "Cosmic Black",
        "fuel": "Electric",
        "year": 2023,
        "reg_date": "2023-05-02",
        "status": "ACTIVE",
        "compliance_profile": "FULLY_COMPLIANT",
    },
    {
        "demo_id": "DEMO-28",
        "plate": "MH12DM0028",
        "state": "Maharashtra",
        "rto": "MH-12 (Pune RTO)",
        "owner": "Nikhil Patwardhan [Demo Owner]",
        "phone": "+91-98765-01028",
        "address": "28, Aundh DP Road, Pune",
        "driver": "Nikhil Patwardhan",
        "dl_num": "MH-122017001028",
        "dl_class": "LMV",
        "dl_expiry": future_date(1250),
        "dl_status": "VALID",
        "make": "Hyundai",
        "model": "Verna 1.5 SX Turbo DCT",
        "class": "Car",
        "type": "Car",
        "color": "Abyss Black Pearl",
        "fuel": "Petrol",
        "year": 2023,
        "reg_date": "2023-07-29",
        "status": "ACTIVE",
        "compliance_profile": "EXPIRED_INSURANCE",  # Insurance expired 40 days ago
    },
    {
        "demo_id": "DEMO-29",
        "plate": "MH12DM0029",
        "state": "Maharashtra",
        "rto": "MH-12 (Pune RTO)",
        "owner": "Kailash Jadhav [Demo Owner]",
        "phone": "+91-98765-01029",
        "address": "15, Karve Road, Deccan Gymkhana, Pune",
        "driver": "Kailash Jadhav",
        "dl_num": "MH-122011001029",
        "dl_class": "MCWG",
        "dl_expiry": past_date(60),  # Expired DL
        "dl_status": "EXPIRED",
        "make": "Royal Enfield",
        "model": "Bullet 350 Military Black",
        "class": "Motorcycle",
        "type": "Motorcycle",
        "color": "Military Black",
        "fuel": "Petrol",
        "year": 2019,
        "reg_date": "2019-11-20",
        "status": "ACTIVE",
        "compliance_profile": "EXPIRED_TAX_AND_PUC",
    },
    {
        "demo_id": "DEMO-30",
        "plate": "MH12DM0030",
        "state": "Maharashtra",
        "rto": "MH-12 (Pune RTO)",
        "owner": "Maharashtra Dairy Transport Co [Demo Owner]",
        "phone": "+91-98765-01030",
        "address": "Chakan Industrial Zone Phase 2, Pune",
        "driver": "Vitthal Salunkhe",
        "dl_num": "MH-122013001030",
        "dl_class": "TRANS",
        "dl_expiry": future_date(350),
        "dl_status": "VALID",
        "make": "Ashok Leyland",
        "model": "Bada Dost i4 High Deck",
        "class": "Transport",
        "type": "Transport",
        "color": "Pure White",
        "fuel": "Diesel",
        "year": 2021,
        "reg_date": "2021-08-05",
        "status": "ACTIVE",
        "compliance_profile": "FULLY_COMPLIANT",
    },
    {
        "demo_id": "DEMO-31",
        "plate": "MH12DM0031",
        "state": "Maharashtra",
        "rto": "MH-12 (Pune RTO)",
        "owner": "Rohit Vaidya [Demo Owner]",
        "phone": "+91-98765-01031",
        "address": "8, Koregaon Park North Main Road, Pune",
        "driver": "Rohit Vaidya",
        "dl_num": "MH-122016001031",
        "dl_class": "LMV",
        "dl_expiry": future_date(1150),
        "dl_status": "VALID",
        "make": "Toyota",
        "model": "Fortuner Legender 4x4 AT",
        "class": "SUV",
        "type": "SUV",
        "color": "White Pearl Crystal Shine with Black Roof",
        "fuel": "Diesel",
        "year": 2022,
        "reg_date": "2022-03-01",
        "status": "ACTIVE",
        "compliance_profile": "EXPIRING_PUC",  # PUC expires in 25 days
    },
    {
        "demo_id": "DEMO-32",
        "plate": "MH12DM0032",
        "state": "Maharashtra",
        "rto": "MH-12 (Pune RTO)",
        "owner": "Shubhangi More [Demo Owner]",
        "phone": "+91-98765-01032",
        "address": "33, Model Colony, Shivajinagar, Pune",
        "driver": "Shubhangi More",
        "dl_num": "MH-122021001032",
        "dl_class": "MCWG / LMV",
        "dl_expiry": future_date(2700),
        "dl_status": "VALID",
        "make": "Honda",
        "model": "Dio 125 H-Smart",
        "class": "Scooter",
        "type": "Scooter",
        "color": "Sports Red",
        "fuel": "Petrol",
        "year": 2023,
        "reg_date": "2023-10-18",
        "status": "ACTIVE",
        "compliance_profile": "MISSING_ROAD_TAX",  # Missing commercial road tax
    },

    # ─────────────────────────────────────────────────────────────────────────────
    # KARNATAKA FLEET (KA-05 Bengaluru South RTO) - DEMO-33 to DEMO-40
    # ─────────────────────────────────────────────────────────────────────────────
    {
        "demo_id": "DEMO-33",
        "plate": "KA05DM0033",
        "state": "Karnataka",
        "rto": "KA-05 (Bengaluru South RTO)",
        "owner": "Gautam Venkatesh [Demo Owner]",
        "phone": "+91-98765-01033",
        "address": "14, 100 Feet Road, Indiranagar, Bengaluru",
        "driver": "Gautam Venkatesh",
        "dl_num": "KA-052018001033",
        "dl_class": "LMV",
        "dl_expiry": future_date(1550),
        "dl_status": "VALID",
        "make": "Tata",
        "model": "Safari Accomplished+ 6S",
        "class": "SUV",
        "type": "SUV",
        "color": "Cosmic Gold",
        "fuel": "Diesel",
        "year": 2023,
        "reg_date": "2023-12-05",
        "status": "ACTIVE",
        "compliance_profile": "FULLY_COMPLIANT",
    },
    {
        "demo_id": "DEMO-34",
        "plate": "KA05DM0034",
        "state": "Karnataka",
        "rto": "KA-05 (Bengaluru South RTO)",
        "owner": "Aishwarya Murthy [Demo Owner]",
        "phone": "+91-98765-01034",
        "address": "402, 5th Block, Koramangala, Bengaluru",
        "driver": "Aishwarya Murthy",
        "dl_num": "KA-052020001034",
        "dl_class": "MCWG",
        "dl_expiry": future_date(2250),
        "dl_status": "VALID",
        "make": "TVS",
        "model": "Ronin 225 Special Edition",
        "class": "Motorcycle",
        "type": "Motorcycle",
        "color": "Nimbus Grey",
        "fuel": "Petrol",
        "year": 2023,
        "reg_date": "2023-06-20",
        "status": "ACTIVE",
        "compliance_profile": "EXPIRED_PUC",  # PUC expired 28 days ago
    },
    {
        "demo_id": "DEMO-35",
        "plate": "KA05DM0035",
        "state": "Karnataka",
        "rto": "KA-05 (Bengaluru South RTO)",
        "owner": "Silicon Valley Courier Express [Demo Owner]",
        "phone": "+91-98765-01035",
        "address": "Plot 44, Electronic City Phase 1, Bengaluru",
        "driver": "Basavaraj Gowda",
        "dl_num": "KA-052014001035",
        "dl_class": "TRANS",
        "dl_expiry": future_date(650),
        "dl_status": "VALID",
        "make": "Tata",
        "model": "Ace EV Cargo Electric",
        "class": "Commercial",
        "type": "Commercial",
        "color": "Mint Green",
        "fuel": "Electric",
        "year": 2023,
        "reg_date": "2023-03-10",
        "status": "ACTIVE",
        "compliance_profile": "FULLY_COMPLIANT",
    },
    {
        "demo_id": "DEMO-36",
        "plate": "KA05DM0036",
        "state": "Karnataka",
        "rto": "KA-05 (Bengaluru South RTO)",
        "owner": "Karthik Subramanian [Demo Owner]",
        "phone": "+91-98765-01036",
        "address": "21, 14th Main, HSR Layout Sector 4, Bengaluru",
        "driver": "Karthik Subramanian",
        "dl_num": "KA-052016001036",
        "dl_class": "LMV",
        "dl_expiry": future_date(1100),
        "dl_status": "VALID",
        "make": "Honda",
        "model": "Elevate ZX CVT",
        "class": "SUV",
        "type": "SUV",
        "color": "Phoenix Orange Pearl",
        "fuel": "Petrol",
        "year": 2023,
        "reg_date": "2023-09-14",
        "status": "ACTIVE",
        "compliance_profile": "EXPIRING_INSURANCE",  # Insurance expires in 18 days
    },
    {
        "demo_id": "DEMO-37",
        "plate": "KA05DM0037",
        "state": "Karnataka",
        "rto": "KA-05 (Bengaluru South RTO)",
        "owner": "Pavithra Hedge [Demo Owner]",
        "phone": "+91-98765-01037",
        "address": "76, JP Nagar 3rd Phase, Bengaluru",
        "driver": "Pavithra Hedge",
        "dl_num": "KA-052019001037",
        "dl_class": "MCWG",
        "dl_expiry": future_date(1850),
        "dl_status": "VALID",
        "make": "Bajaj",
        "model": "Chetak Premium 2024",
        "class": "Scooter",
        "type": "Scooter",
        "color": "Brooklyn Black",
        "fuel": "Electric",
        "year": 2024,
        "reg_date": "2024-01-10",
        "status": "ACTIVE",
        "compliance_profile": "FULLY_COMPLIANT",
    },
    {
        "demo_id": "DEMO-38",
        "plate": "KA05DM0038",
        "state": "Karnataka",
        "rto": "KA-05 (Bengaluru South RTO)",
        "owner": "Bangalore Urban Logistics Co [Demo Owner]",
        "phone": "+91-98765-01038",
        "address": "Outer Ring Road, Bellandur, Bengaluru",
        "driver": "Shivakumar Naidu",
        "dl_num": "KA-052011001038",
        "dl_class": "TRANS / HGV",
        "dl_expiry": future_date(280),
        "dl_status": "VALID",
        "make": "Ashok Leyland",
        "model": "Partner 4 Tyre 14ft",
        "class": "Transport",
        "type": "Transport",
        "color": "Signal White",
        "fuel": "Diesel",
        "year": 2020,
        "reg_date": "2020-05-15",
        "status": "ACTIVE",
        "compliance_profile": "EXPIRED_TAX_AND_PUC",
    },
    {
        "demo_id": "DEMO-39",
        "plate": "KA05DM0039",
        "state": "Karnataka",
        "rto": "KA-05 (Bengaluru South RTO)",
        "owner": "Vishal Shenoy [Demo Owner]",
        "phone": "+91-98765-01039",
        "address": "12, 17th Cross, Malleshwaram, Bengaluru",
        "driver": "Vishal Shenoy",
        "dl_num": "KA-052017001039",
        "dl_class": "LMV",
        "dl_expiry": future_date(1300),
        "dl_status": "VALID",
        "make": "Maruti Suzuki",
        "model": "Fronx Alpha 1.0 Turbo AT",
        "class": "Car",
        "type": "Car",
        "color": "Grandeur Grey",
        "fuel": "Petrol",
        "year": 2023,
        "reg_date": "2023-04-25",
        "status": "ACTIVE",
        "compliance_profile": "FULLY_COMPLIANT",
    },
    {
        "demo_id": "DEMO-40",
        "plate": "KA05DM0040",
        "state": "Karnataka",
        "rto": "KA-05 (Bengaluru South RTO)",
        "owner": "Naveen Rajagopal [Demo Owner]",
        "phone": "+91-98765-01040",
        "address": "88, Whitefield Main Road, Bengaluru",
        "driver": "Naveen Rajagopal",
        "dl_num": "KA-052015001040",
        "dl_class": "LMV",
        "dl_expiry": future_date(700),
        "dl_status": "VALID",
        "make": "Toyota",
        "model": "Innova Hycross ZX(O) Hybrid",
        "class": "SUV",
        "type": "SUV",
        "color": "Blackish Ageha Glass Flake",
        "fuel": "Hybrid",
        "year": 2023,
        "reg_date": "2023-01-15",
        "status": "ACTIVE",
        "compliance_profile": "EXPIRED_RC",  # RC Expired
    },

    # ─────────────────────────────────────────────────────────────────────────────
    # TAMIL NADU FLEET (TN-09 Chennai West RTO) - DEMO-41 to DEMO-45
    # ─────────────────────────────────────────────────────────────────────────────
    {
        "demo_id": "DEMO-41",
        "plate": "TN09DM0041",
        "state": "Tamil Nadu",
        "rto": "TN-09 (Chennai West RTO)",
        "owner": "Senthil Nathan [Demo Owner]",
        "phone": "+91-98765-01041",
        "address": "15, Anna Nagar 2nd Avenue, Chennai",
        "driver": "Senthil Nathan",
        "dl_num": "TN-092017001041",
        "dl_class": "LMV",
        "dl_expiry": future_date(1250),
        "dl_status": "VALID",
        "make": "Hyundai",
        "model": "i20 Asta(O) 1.2",
        "class": "Car",
        "type": "Car",
        "color": "Fiery Red",
        "fuel": "Petrol",
        "year": 2022,
        "reg_date": "2022-08-11",
        "status": "ACTIVE",
        "compliance_profile": "FULLY_COMPLIANT",
    },
    {
        "demo_id": "DEMO-42",
        "plate": "TN09DM0042",
        "state": "Tamil Nadu",
        "rto": "TN-09 (Chennai West RTO)",
        "owner": "Madras Coastal Fleet Ltd [Demo Owner]",
        "phone": "+91-98765-01042",
        "address": "Plot 18, Guindy Industrial Estate, Chennai",
        "driver": "K. Murugan",
        "dl_num": "TN-092013001042",
        "dl_class": "TRANS",
        "dl_expiry": future_date(480),
        "dl_status": "VALID",
        "make": "Force",
        "model": "Traveller 3350 14-Seater",
        "class": "Transport",
        "type": "Transport",
        "color": "Traffic White",
        "fuel": "Diesel",
        "year": 2021,
        "reg_date": "2021-02-19",
        "status": "ACTIVE",
        "compliance_profile": "EXPIRED_PUC",  # PUC expired 52 days ago
    },
    {
        "demo_id": "DEMO-43",
        "plate": "TN09DM0043",
        "state": "Tamil Nadu",
        "rto": "TN-09 (Chennai West RTO)",
        "owner": "Anand Ranganathan [Demo Owner]",
        "phone": "+91-98765-01043",
        "address": "32, Besant Theosophical Society Road, Chennai",
        "driver": "Anand Ranganathan",
        "dl_num": "TN-092019001043",
        "dl_class": "MCWG",
        "dl_expiry": future_date(1950),
        "dl_status": "VALID",
        "make": "Royal Enfield",
        "model": "Super Meteor 650 Celestial",
        "class": "Motorcycle",
        "type": "Motorcycle",
        "color": "Celestial Blue",
        "fuel": "Petrol",
        "year": 2023,
        "reg_date": "2023-04-05",
        "status": "ACTIVE",
        "compliance_profile": "FULLY_COMPLIANT",
    },
    {
        "demo_id": "DEMO-44",
        "plate": "TN09DM0044",
        "state": "Tamil Nadu",
        "rto": "TN-09 (Chennai West RTO)",
        "owner": "Gayathri Krishnan [Demo Owner]",
        "phone": "+91-98765-01044",
        "address": "8, TTK Road, Alwarpet, Chennai",
        "driver": "Gayathri Krishnan",
        "dl_num": "TN-092021001044",
        "dl_class": "LMV",
        "dl_expiry": future_date(2600),
        "dl_status": "VALID",
        "make": "Kia",
        "model": "Sonet HTX 1.0 Turbo iMT",
        "class": "SUV",
        "type": "SUV",
        "color": "Imperial Blue",
        "fuel": "Petrol",
        "year": 2022,
        "reg_date": "2022-12-14",
        "status": "ACTIVE",
        "compliance_profile": "EXPIRING_INSURANCE",  # Insurance expires in 28 days
    },
    {
        "demo_id": "DEMO-45",
        "plate": "TN09DM0045",
        "state": "Tamil Nadu",
        "rto": "TN-09 (Chennai West RTO)",
        "owner": "R. Selvakumar [Demo Owner]",
        "phone": "+91-98765-01045",
        "address": "45, Velachery Main Road, Chennai",
        "driver": "R. Selvakumar",
        "dl_num": "TN-092016001045",
        "dl_class": "MCWG",
        "dl_expiry": future_date(1150),
        "dl_status": "VALID",
        "make": "TVS",
        "model": "Ntorq 125 Race XP",
        "class": "Scooter",
        "type": "Scooter",
        "color": "Race Red Black",
        "fuel": "Petrol",
        "year": 2022,
        "reg_date": "2022-06-30",
        "status": "ACTIVE",
        "compliance_profile": "MISSING_PUC",  # Missing PUC
    },

    # ─────────────────────────────────────────────────────────────────────────────
    # UTTAR PRADESH FLEET (UP-32 Lucknow RTO) - DEMO-46 to DEMO-50
    # ─────────────────────────────────────────────────────────────────────────────
    {
        "demo_id": "DEMO-46",
        "plate": "UP32DM0046",
        "state": "Uttar Pradesh",
        "rto": "UP-32 (Lucknow RTO)",
        "owner": "Awadh Agro Logistics Ltd [Demo Owner]",
        "phone": "+91-98765-01046",
        "address": "Faizabad Road, Chinhat Industrial Area, Lucknow",
        "driver": "Ramsevak Yadav",
        "dl_num": "UP-322012001046",
        "dl_class": "TRANS / HGV",
        "dl_expiry": future_date(420),
        "dl_status": "VALID",
        "make": "Mahindra",
        "model": "Bolero Camper 4WD",
        "class": "Commercial",
        "type": "Commercial",
        "color": "Rocky Beige",
        "fuel": "Diesel",
        "year": 2021,
        "reg_date": "2021-03-24",
        "status": "ACTIVE",
        "compliance_profile": "FULLY_COMPLIANT",
    },
    {
        "demo_id": "DEMO-47",
        "plate": "UP32DM0047",
        "state": "Uttar Pradesh",
        "rto": "UP-32 (Lucknow RTO)",
        "owner": "Divya Prakash Mishra [Demo Owner]",
        "phone": "+91-98765-01047",
        "address": "12, Gomti Nagar Vipul Khand 2, Lucknow",
        "driver": "Divya Prakash Mishra",
        "dl_num": "UP-322018001047",
        "dl_class": "LMV",
        "dl_expiry": future_date(1650),
        "dl_status": "VALID",
        "make": "Maruti Suzuki",
        "model": "Grand Vitara Alpha AllGrip",
        "class": "SUV",
        "type": "SUV",
        "color": "Chestnut Brown",
        "fuel": "Hybrid",
        "year": 2023,
        "reg_date": "2023-05-18",
        "status": "ACTIVE",
        "compliance_profile": "EXPIRED_PUC",  # PUC expired 65 days ago
    },
    {
        "demo_id": "DEMO-48",
        "plate": "UP32DM0048",
        "state": "Uttar Pradesh",
        "rto": "UP-32 (Lucknow RTO)",
        "owner": "Shubham Srivastava [Demo Owner]",
        "phone": "+91-98765-01048",
        "address": "78, Aliganj Sector B, Lucknow",
        "driver": "Shubham Srivastava",
        "dl_num": "UP-322020001048",
        "dl_class": "MCWG",
        "dl_expiry": future_date(2350),
        "dl_status": "VALID",
        "make": "Honda",
        "model": "CB350 H'ness Legacy Edition",
        "class": "Motorcycle",
        "type": "Motorcycle",
        "color": "Pearl Siren Blue",
        "fuel": "Petrol",
        "year": 2023,
        "reg_date": "2023-10-02",
        "status": "ACTIVE",
        "compliance_profile": "FULLY_COMPLIANT",
    },
    {
        "demo_id": "DEMO-49",
        "plate": "UP32DM0049",
        "state": "Uttar Pradesh",
        "rto": "UP-32 (Lucknow RTO)",
        "owner": "Lucknow Freight Forwarders [Demo Owner]",
        "phone": "+91-98765-01049",
        "address": "Transport Nagar Phase 1, Kanpur Road, Lucknow",
        "driver": "Chhotey Lal",
        "dl_num": "UP-322010001049",
        "dl_class": "TRANS",
        "dl_expiry": future_date(210),
        "dl_status": "VALID",
        "make": "Eicher",
        "model": "Pro 2049 Light Truck",
        "class": "Transport",
        "type": "Transport",
        "color": "Emerald Green",
        "fuel": "Diesel",
        "year": 2020,
        "reg_date": "2020-11-19",
        "status": "ACTIVE",
        "compliance_profile": "EXPIRED_INSURANCE",  # Insurance expired 75 days ago
    },
    {
        "demo_id": "DEMO-50",
        "plate": "UP32DM0050",
        "state": "Uttar Pradesh",
        "rto": "UP-32 (Lucknow RTO)",
        "owner": "Pratibha Verma [Demo Owner]",
        "phone": "+91-98765-01050",
        "address": "24, Hazratganj Park Road, Lucknow",
        "driver": "Pratibha Verma",
        "dl_num": "UP-322019001050",
        "dl_class": "LMV",
        "dl_expiry": future_date(1800),
        "dl_status": "VALID",
        "make": "Tata",
        "model": "Tiago EV XZ+ Tech LUX",
        "class": "Car",
        "type": "Car",
        "color": "Teal Blue",
        "fuel": "Electric",
        "year": 2023,
        "reg_date": "2023-07-07",
        "status": "ACTIVE",
        "compliance_profile": "EXPIRING_PUC",  # PUC expires in 19 days
    },
]


def seed_demo_vehicles(db_path=None) -> int:
    """
    Seeds exactly 50 demo vehicles, their documents, and associated demo challans.
    Returns the count of seeded/verified vehicles.
    """
    resolved_path = db_path or get_db_path()
    print(f"🚗 Seeding 50 Demo Vehicles into: {resolved_path}")

    # 1. Run migrations to ensure all columns exist
    migrate_vehicles_for_demo(resolved_path)

    conn = get_db_connection(resolved_path)
    cursor = conn.cursor()

    seeded_count = 0

    for v in DEMO_VEHICLES_DATA:
        plate = v["plate"]
        demo_id = v["demo_id"]

        # 1. Insert / Update vehicle directly using cursor
        cursor.execute("SELECT id FROM vehicles WHERE UPPER(registration_number) = ?;", (plate,))
        existing = cursor.fetchone()

        if existing:
            veh_id = existing["id"]
            cursor.execute(
                """
                UPDATE vehicles SET
                    owner_name = ?, vehicle_type = ?, vehicle_model = ?, registration_date = ?,
                    demo_id = ?, is_demo = ?, state = ?, rto_code = ?, registration_status = ?,
                    owner_phone = ?, owner_address = ?, manufacturer = ?, vehicle_class = ?,
                    vehicle_color = ?, fuel_type = ?, manufacturing_year = ?, chassis_number = ?,
                    engine_number = ?, driver_name = ?, driver_license_number = ?,
                    driver_license_class = ?, driver_license_expiry = ?, driver_license_status = ?
                WHERE id = ?;
                """,
                (
                    v["owner"], v["type"], v["model"], v["reg_date"],
                    demo_id, 1, v["state"], v["rto"], v["status"],
                    v["phone"], v["address"], v["make"], v["class"],
                    v["color"], v["fuel"], v["year"], f"SYN-CHAS-{plate}-{v['year']}",
                    f"SYN-ENG-{plate}-{v['fuel'][:3].upper()}", v["driver"], v["dl_num"],
                    v["dl_class"], v["dl_expiry"], v["dl_status"],
                    veh_id
                )
            )
        else:
            cursor.execute(
                """
                INSERT INTO vehicles (
                    registration_number, owner_name, vehicle_type, vehicle_model, registration_date,
                    demo_id, is_demo, state, rto_code, registration_status,
                    owner_phone, owner_address, manufacturer, vehicle_class,
                    vehicle_color, fuel_type, manufacturing_year, chassis_number,
                    engine_number, driver_name, driver_license_number,
                    driver_license_class, driver_license_expiry, driver_license_status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    plate, v["owner"], v["type"], v["model"], v["reg_date"],
                    demo_id, 1, v["state"], v["rto"], v["status"],
                    v["phone"], v["address"], v["make"], v["class"],
                    v["color"], v["fuel"], v["year"], f"SYN-CHAS-{plate}-{v['year']}",
                    f"SYN-ENG-{plate}-{v['fuel'][:3].upper()}", v["driver"], v["dl_num"],
                    v["dl_class"], v["dl_expiry"], v["dl_status"]
                )
            )
            veh_id = cursor.lastrowid

        # 2. Insert documents based on compliance profile
        profile = v["compliance_profile"]

        # Clear existing documents for this vehicle to re-seed clean status
        cursor.execute("DELETE FROM documents WHERE vehicle_id = ?;", (veh_id,))

        # Define document dates based on compliance profile
        # Default: all 4 are valid
        rc_exp = future_date(1800)
        ins_exp = future_date(240)
        puc_exp = future_date(150)
        tax_exp = future_date(300)

        include_rc = True
        include_ins = True
        include_puc = True
        include_tax = True

        if profile == "EXPIRED_PUC":
            puc_exp = past_date(45)
        elif profile == "EXPIRING_INSURANCE":
            ins_exp = future_date(12)
        elif profile == "EXPIRED_INSURANCE":
            ins_exp = past_date(60)
        elif profile == "EXPIRED_TAX_AND_PUC":
            puc_exp = past_date(75)
            tax_exp = past_date(120)
        elif profile == "EXPIRING_PUC":
            puc_exp = future_date(15)
        elif profile == "EXPIRED_RC":
            rc_exp = past_date(90)
        elif profile == "MISSING_PUC":
            include_puc = False
        elif profile == "MISSING_INSURANCE":
            include_ins = False
        elif profile == "MISSING_ROAD_TAX":
            include_tax = False

        # Status calculation helper for stored status
        def calc_st(exp_str):
            exp_d = datetime.strptime(exp_str[:10], "%Y-%m-%d").date()
            d = (exp_d - TODAY).days
            if d < 0: return "EXPIRED"
            if d <= 30: return "EXPIRING_SOON"
            return "VALID"

        docs_to_insert = []
        if include_rc:
            docs_to_insert.append((
                veh_id, "RC", f"RC-{plate}", past_date(600), rc_exp,
                calc_st(rc_exp), f"{v['state']} Transport Authority (Parivahan Vahan 4.0)"
            ))

        if include_ins:
            docs_to_insert.append((
                veh_id, "INSURANCE", f"POL-{plate[:4]}-{demo_id[-2:]}99", past_date(120), ins_exp,
                calc_st(ins_exp), "ICICI Lombard Motor Comprehensive Policy"
            ))

        if include_puc:
            docs_to_insert.append((
                veh_id, "PUC", f"PUC-{plate[:4]}-{demo_id[-2:]}44", past_date(180), puc_exp,
                calc_st(puc_exp), f"Authorized State Emission Testing Centre #{demo_id[-2:]}"
            ))

        if include_tax:
            docs_to_insert.append((
                veh_id, "ROAD_TAX", f"TAX-{plate[:4]}-{demo_id[-2:]}11", past_date(365), tax_exp,
                calc_st(tax_exp), f"{v['state']} State Motor Road Tax Levy Dept."
            ))

        cursor.executemany(
            """
            INSERT INTO documents (vehicle_id, document_type, document_number, issue_date, expiry_date, status, provider)
            VALUES (?, ?, ?, ?, ?, ?, ?);
            """,
            docs_to_insert
        )

        # 3. Add previous demo challans for selected vehicles with violations
        if profile in ("EXPIRED_PUC", "EXPIRED_INSURANCE", "EXPIRED_TAX_AND_PUC", "EXPIRED_RC"):
            challan_code = f"CH-DEMO-{demo_id[-2:]}"
            cursor.execute("SELECT id FROM challans WHERE challan_number = ?;", (challan_code,))
            if not cursor.fetchone():
                v_desc = f"Electronic roadside surveillance identified {profile.replace('_', ' ')}."
                fine = 10000.0 if "PUC" in profile else 5000.0
                pay_st = "PAID" if int(demo_id[-2:]) % 2 == 0 else "PENDING"
                ch_status = "SETTLED" if pay_st == "PAID" else "ISSUED"
                cursor.execute(
                    """
                    INSERT INTO challans (
                        challan_number, vehicle_id, violation_type, fine_amount, challan_date, 
                        payment_status, challan_status, description
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                    """,
                    (challan_code, veh_id, profile, fine, past_date(10), pay_st, ch_status, v_desc)
                )

        seeded_count += 1

    conn.commit()
    conn.close()

    metrics = get_demo_fleet_metrics(resolved_path)
    print(f"✅ Successfully seeded/verified {seeded_count} demo vehicles.")
    print(f"📊 Fleet Metrics: {metrics['total_demo_vehicles']} Demo Vehicles, {metrics['documents_total']} Documents ({metrics['documents_valid']} Valid, {metrics['documents_expiring_soon']} Expiring Soon, {metrics['documents_expired']} Expired, {metrics['documents_missing']} Missing).")
    return seeded_count


if __name__ == "__main__":
    count = seed_demo_vehicles()
    print(f"🚀 Execution completed. Total seeded records: {count}")
