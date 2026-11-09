"""
database.py - Database Management & Connection Module
=====================================================
Smart ANPR Vehicle Verification System

This module handles:
1. SQLite connection management with foreign key enforcement and row factory.
2. Table creation DDL for VEHICLES, DOCUMENTS, and CHALLANS.
3. Modular, parameterized helper functions for querying and inserting records.
"""

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional

# Default database path: backend/data/anpr.db
DEFAULT_DB_DIR = Path(__file__).resolve().parent / "data"
DEFAULT_DB_PATH = DEFAULT_DB_DIR / "anpr.db"


def get_db_path() -> Path:
    """
    Resolve the absolute path to the SQLite anpr.db file.
    Can be overridden via the DATABASE_PATH or ANPR_DATABASE_PATH environment variable.
    Ensures the parent directory exists.
    """
    env_path = os.getenv("DATABASE_PATH") or os.getenv("ANPR_DATABASE_PATH")
    if env_path:
        db_path = Path(env_path).resolve()
    else:
        db_path = DEFAULT_DB_PATH

    # Ensure parent directory exists
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return db_path


def get_db_connection(db_path: Optional[str | Path] = None) -> sqlite3.Connection:
    """
    Establish and return a connection to the SQLite database.

    Key Configuration:
    - row_factory = sqlite3.Row: Allows accessing columns by column name as well as integer index.
    - PRAGMA foreign_keys = ON: Actively enforces relational foreign key constraints in SQLite.
    """
    resolved_path = Path(db_path).resolve() if db_path else get_db_path()
    conn = sqlite3.connect(str(resolved_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


@contextmanager
def db_session(db_path: Optional[str | Path] = None) -> Generator[sqlite3.Connection, None, None]:
    """
    Context manager that yields a database connection and ensures it is closed upon exit.
    """
    conn = get_db_connection(db_path)
    try:
        yield conn
    finally:
        conn.close()


# ============================================================================
# DDL: Database Schema Definitions
# ============================================================================

SCHEMA_SQL = """
-- 1. VEHICLES TABLE
CREATE TABLE IF NOT EXISTS vehicles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    registration_number TEXT NOT NULL UNIQUE,
    owner_name TEXT NOT NULL,
    vehicle_type TEXT NOT NULL,
    vehicle_model TEXT NOT NULL,
    registration_date TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for fast lookup by license plate / registration number
CREATE INDEX IF NOT EXISTS idx_vehicles_registration_number 
ON vehicles(registration_number);


-- 2. DOCUMENTS TABLE
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_id INTEGER NOT NULL,
    document_type TEXT NOT NULL CHECK(document_type IN ('RC', 'INSURANCE', 'PUC', 'ROAD_TAX')),
    document_number TEXT NOT NULL,
    issue_date TEXT NOT NULL,
    expiry_date TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('VALID', 'EXPIRING_SOON', 'EXPIRED')),
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE CASCADE
);

-- Indexes for fast foreign key retrieval and status filtering
CREATE INDEX IF NOT EXISTS idx_documents_vehicle_id 
ON documents(vehicle_id);

CREATE INDEX IF NOT EXISTS idx_documents_status 
ON documents(status);


-- 3. CHALLANS TABLE
CREATE TABLE IF NOT EXISTS challans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    challan_number TEXT NOT NULL UNIQUE,
    vehicle_id INTEGER NOT NULL,
    violation_type TEXT NOT NULL,
    fine_amount REAL NOT NULL,
    challan_date TEXT NOT NULL,
    payment_status TEXT NOT NULL CHECK(payment_status IN ('PENDING', 'PAID', 'FAILED')),
    challan_status TEXT NOT NULL DEFAULT 'ISSUED' CHECK(challan_status IN ('ISSUED', 'SETTLED', 'CANCELLED')),
    description TEXT,
    fine_breakdown_json TEXT,
    pdf_path TEXT,
    qr_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE CASCADE
);

-- Indexes for challan lookup by vehicle and unique citation number
CREATE INDEX IF NOT EXISTS idx_challans_vehicle_id 
ON challans(vehicle_id);

CREATE INDEX IF NOT EXISTS idx_challans_number 
ON challans(challan_number);


-- 4. OFFICERS & ROLES TABLE
CREATE TABLE IF NOT EXISTS officers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    full_name TEXT NOT NULL,
    badge_number TEXT NOT NULL UNIQUE,
    role TEXT NOT NULL CHECK(role IN ('ADMIN', 'OFFICER')),
    station_id TEXT NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1,
    preferences_json TEXT DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_officers_username 
ON officers(username);

CREATE INDEX IF NOT EXISTS idx_officers_badge 
ON officers(badge_number);


-- 5. INSPECTIONS & DETECTION HISTORY TABLE (with GPS Coordinates)
CREATE TABLE IF NOT EXISTS inspections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    inspection_code TEXT NOT NULL UNIQUE,
    registration_number TEXT NOT NULL,
    vehicle_id INTEGER,
    inspection_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    detection_confidence REAL DEFAULT 0.0,
    ocr_confidence REAL DEFAULT 0.0,
    plate_image_url TEXT,
    vehicle_image_url TEXT,
    verification_status TEXT NOT NULL DEFAULT 'COMPLIANT' CHECK(verification_status IN ('COMPLIANT', 'VIOLATION', 'UNREGISTERED', 'MANUAL_REVIEW')),
    violations_summary TEXT,
    violations_json TEXT,
    officer_id INTEGER,
    officer_name TEXT,
    latitude REAL DEFAULT 28.5355,
    longitude REAL DEFAULT 77.3910,
    location_name TEXT DEFAULT 'Sector 04 Expressway Checkpoint',
    notes TEXT,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE SET NULL,
    FOREIGN KEY (officer_id) REFERENCES officers(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_inspections_plate 
ON inspections(registration_number);

CREATE INDEX IF NOT EXISTS idx_inspections_status 
ON inspections(verification_status);

CREATE INDEX IF NOT EXISTS idx_inspections_time 
ON inspections(inspection_time);

"""


def init_db(db_path: Optional[str | Path] = None, drop_existing: bool = False) -> None:
    """
    Initializes the SQLite database tables and indexes.

    Args:
        db_path: Optional specific database file path.
        drop_existing: If True, drops existing tables before re-creating.
    """
    target_path = Path(db_path).resolve() if db_path else get_db_path()
    target_path.parent.mkdir(parents=True, exist_ok=True)

    with db_session(target_path) as conn:
        cursor = conn.cursor()

        if drop_existing:
            cursor.execute("DROP TABLE IF EXISTS challans;")
            cursor.execute("DROP TABLE IF EXISTS documents;")
            cursor.execute("DROP TABLE IF EXISTS vehicles;")

        cursor.executescript(SCHEMA_SQL)

        # Safe migration for officers.preferences_json column
        try:
            cursor.execute("SELECT preferences_json FROM officers LIMIT 1;")
        except sqlite3.OperationalError:
            try:
                cursor.execute("ALTER TABLE officers ADD COLUMN preferences_json TEXT DEFAULT '{}';")
            except Exception:
                pass

        conn.commit()


# ============================================================================
# Parameterized Query & Helper Functions
# ============================================================================

def row_to_dict(row: Optional[sqlite3.Row]) -> Optional[Dict[str, Any]]:
    """Convert an sqlite3.Row object into a standard Python dictionary."""
    if row is None:
        return None
    return {key: row[key] for key in row.keys()}


def rows_to_list(rows: List[sqlite3.Row]) -> List[Dict[str, Any]]:
    """Convert a list of sqlite3.Row objects into a list of dictionaries."""
    return [row_to_dict(row) for row in rows]


def get_all_vehicles(db_path: Optional[str | Path] = None) -> List[Dict[str, Any]]:
    """Retrieve all vehicles from the database ordered by id."""
    with db_session(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vehicles ORDER BY id ASC;")
        rows = cursor.fetchall()
        return rows_to_list(rows)


def get_vehicle_by_plate(registration_number: str, db_path: Optional[str | Path] = None) -> Optional[Dict[str, Any]]:
    """
    Find a vehicle by its license plate number (case-insensitive & trimmed).
    """
    normalized_plate = registration_number.strip().upper()
    with db_session(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM vehicles WHERE UPPER(registration_number) = ? LIMIT 1;",
            (normalized_plate,)
        )
        row = cursor.fetchone()
        return row_to_dict(row)


def get_vehicle_by_id(vehicle_id: int, db_path: Optional[str | Path] = None) -> Optional[Dict[str, Any]]:
    """Find a vehicle by its primary key ID."""
    with db_session(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vehicles WHERE id = ? LIMIT 1;", (vehicle_id,))
        row = cursor.fetchone()
        return row_to_dict(row)


def get_documents_by_vehicle_id(vehicle_id: int, db_path: Optional[str | Path] = None) -> List[Dict[str, Any]]:
    """Retrieve all document records for a specific vehicle by vehicle_id."""
    with db_session(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM documents WHERE vehicle_id = ? ORDER BY id ASC;",
            (vehicle_id,)
        )
        rows = cursor.fetchall()
        return rows_to_list(rows)


def get_documents_by_plate(registration_number: str, db_path: Optional[str | Path] = None) -> Optional[Dict[str, Any]]:
    """
    Retrieve vehicle details and all associated documents for a given plate.
    Returns None if vehicle is not found.
    """
    vehicle = get_vehicle_by_plate(registration_number, db_path)
    if not vehicle:
        return None

    documents = get_documents_by_vehicle_id(vehicle["id"], db_path)
    return {
        "vehicle": vehicle,
        "documents": documents
    }


def get_all_challans(db_path: Optional[str | Path] = None) -> List[Dict[str, Any]]:
    """
    Retrieve all challan citations joined with the vehicle registration number.
    """
    with db_session(db_path) as conn:
        cursor = conn.cursor()
        query = """
            SELECT 
                c.id,
                c.challan_number,
                c.vehicle_id,
                v.registration_number,
                v.owner_name,
                v.vehicle_type,
                v.vehicle_model,
                c.violation_type,
                c.fine_amount,
                c.challan_date,
                c.payment_status,
                COALESCE(c.challan_status, 'ISSUED') AS challan_status,
                c.description,
                c.fine_breakdown_json,
                c.pdf_path,
                c.qr_path
            FROM challans c
            JOIN vehicles v ON c.vehicle_id = v.id
            ORDER BY c.id DESC;
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        return rows_to_list(rows)


def get_challans_by_vehicle_id(vehicle_id: int, db_path: Optional[str | Path] = None) -> List[Dict[str, Any]]:
    """Retrieve all challans issued to a specific vehicle."""
    with db_session(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT 
                c.*, 
                v.registration_number, 
                v.owner_name,
                COALESCE(c.challan_status, 'ISSUED') AS challan_status
            FROM challans c
            JOIN vehicles v ON c.vehicle_id = v.id
            WHERE c.vehicle_id = ? 
            ORDER BY c.id DESC;
            """,
            (vehicle_id,)
        )
        rows = cursor.fetchall()
        return rows_to_list(rows)


def get_challan_by_number(challan_number: str, db_path: Optional[str | Path] = None) -> Optional[Dict[str, Any]]:
    """
    Retrieve full challan details joined with vehicle info by unique challan_number.
    """
    clean_num = challan_number.strip().upper()
    with db_session(db_path) as conn:
        cursor = conn.cursor()
        query = """
            SELECT 
                c.id,
                c.challan_number,
                c.vehicle_id,
                v.registration_number,
                v.owner_name,
                v.vehicle_type,
                v.vehicle_model,
                v.registration_date,
                c.violation_type,
                c.fine_amount,
                c.challan_date,
                c.payment_status,
                COALESCE(c.challan_status, 'ISSUED') AS challan_status,
                c.description,
                c.fine_breakdown_json,
                c.pdf_path,
                c.qr_path
            FROM challans c
            JOIN vehicles v ON c.vehicle_id = v.id
            WHERE UPPER(c.challan_number) = ?
            LIMIT 1;
        """
        cursor.execute(query, (clean_num,))
        row = cursor.fetchone()
        return row_to_dict(row)


def update_challan_payment_status(
    challan_number: str,
    payment_status: str,
    db_path: Optional[str | Path] = None
) -> bool:
    """
    Update payment status for a challan ('PENDING', 'PAID', 'FAILED').
    If payment_status is 'PAID', challan_status is set to 'SETTLED'.
    """
    clean_num = challan_number.strip().upper()
    clean_status = payment_status.strip().upper()

    challan_status = "SETTLED" if clean_status == "PAID" else "ISSUED"

    with db_session(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE challans 
            SET payment_status = ?, challan_status = ?
            WHERE UPPER(challan_number) = ?;
            """,
            (clean_status, challan_status, clean_num)
        )
        conn.commit()
        return cursor.rowcount > 0


def update_challan_artifacts(
    challan_number: str,
    pdf_path: Optional[str] = None,
    qr_path: Optional[str] = None,
    db_path: Optional[str | Path] = None
) -> bool:
    """Update PDF file path and QR file path for a challan."""
    clean_num = challan_number.strip().upper()
    with db_session(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE challans
            SET pdf_path = COALESCE(?, pdf_path),
                qr_path = COALESCE(?, qr_path)
            WHERE UPPER(challan_number) = ?;
            """,
            (pdf_path, qr_path, clean_num)
        )
        conn.commit()
        return cursor.rowcount > 0


def migrate_db_for_phase5(db_path: Optional[str | Path] = None) -> bool:
    """
    Safely migrates challans table to support Phase 5 columns:
    - challan_status (ISSUED, SETTLED, CANCELLED)
    - fine_breakdown_json (TEXT)
    - pdf_path (TEXT)
    - qr_path (TEXT)
    - payment_status CHECK constraint allowing ('PENDING', 'PAID', 'FAILED')
    Preserves all existing records!
    """
    target = db_path or get_db_path()
    with get_db_connection(target) as conn:
        cursor = conn.cursor()

        # Check existing columns
        cursor.execute("PRAGMA table_info(challans);")
        columns = {row["name"] for row in cursor.fetchall()}

        # Check if table already has all columns and payment_status supports FAILED
        if "fine_breakdown_json" in columns and "challan_status" in columns:
            # Table already has new columns; test if FAILED constraint is supported
            cursor.execute("SELECT sql FROM sqlite_master WHERE name='challans';")
            sql_def = cursor.fetchone()["sql"]
            if "'FAILED'" in sql_def:
                return True

        # Perform safe table migration
        cursor.execute("PRAGMA foreign_keys = OFF;")
        cursor.execute("DROP TABLE IF EXISTS challans_migration_backup;")
        cursor.execute("ALTER TABLE challans RENAME TO challans_migration_backup;")

        # Create new table with updated constraints and columns
        cursor.execute(
            """
            CREATE TABLE challans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                challan_number TEXT NOT NULL UNIQUE,
                vehicle_id INTEGER NOT NULL,
                violation_type TEXT NOT NULL,
                fine_amount REAL NOT NULL,
                challan_date TEXT NOT NULL,
                payment_status TEXT NOT NULL CHECK(payment_status IN ('PENDING', 'PAID', 'FAILED')),
                challan_status TEXT NOT NULL DEFAULT 'ISSUED' CHECK(challan_status IN ('ISSUED', 'SETTLED', 'CANCELLED')),
                description TEXT,
                fine_breakdown_json TEXT,
                pdf_path TEXT,
                qr_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE CASCADE
            );
            """
        )

        # Copy existing data back
        cursor.execute(
            """
            INSERT INTO challans (
                id, challan_number, vehicle_id, violation_type, fine_amount, challan_date, payment_status, description
            )
            SELECT 
                id, challan_number, vehicle_id, violation_type, fine_amount, challan_date, payment_status, description
            FROM challans_migration_backup;
            """
        )

        # Clean backup and recreate indexes
        cursor.execute("DROP TABLE challans_migration_backup;")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_challans_vehicle_id ON challans(vehicle_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_challans_number ON challans(challan_number);")
        cursor.execute("PRAGMA foreign_keys = ON;")
        conn.commit()
        return True


def migrate_vehicles_for_demo(db_path: Optional[str | Path] = None) -> bool:
    """
    Safely migrates vehicles and documents tables to support full demo vehicle attributes:
    - demo_id, is_demo, state, rto_code, registration_status
    - owner_phone, owner_address
    - manufacturer, vehicle_class, vehicle_color, fuel_type, manufacturing_year
    - chassis_number, engine_number
    - driver_name, driver_license_number, driver_license_class, driver_license_expiry, driver_license_status
    - documents.provider
    Preserves all existing rows!
    """
    target = db_path or get_db_path()
    with get_db_connection(target) as conn:
        cursor = conn.cursor()

        # 1. Check existing vehicle columns
        cursor.execute("PRAGMA table_info(vehicles);")
        veh_cols = {row["name"] for row in cursor.fetchall()}

        new_veh_cols = [
            ("demo_id", "TEXT"),
            ("is_demo", "INTEGER NOT NULL DEFAULT 1"),
            ("state", "TEXT DEFAULT 'Delhi'"),
            ("rto_code", "TEXT DEFAULT 'DL-01'"),
            ("registration_status", "TEXT DEFAULT 'ACTIVE'"),
            ("owner_phone", "TEXT"),
            ("owner_address", "TEXT"),
            ("manufacturer", "TEXT"),
            ("vehicle_class", "TEXT"),
            ("vehicle_color", "TEXT"),
            ("fuel_type", "TEXT"),
            ("manufacturing_year", "INTEGER"),
            ("chassis_number", "TEXT"),
            ("engine_number", "TEXT"),
            ("driver_name", "TEXT"),
            ("driver_license_number", "TEXT"),
            ("driver_license_class", "TEXT DEFAULT 'LMV'"),
            ("driver_license_expiry", "TEXT"),
            ("driver_license_status", "TEXT DEFAULT 'VALID'"),
        ]

        for col_name, col_type in new_veh_cols:
            if col_name not in veh_cols:
                cursor.execute(f"ALTER TABLE vehicles ADD COLUMN {col_name} {col_type};")

        # 2. Check existing documents columns
        cursor.execute("PRAGMA table_info(documents);")
        doc_cols = {row["name"] for row in cursor.fetchall()}
        if "provider" not in doc_cols:
            cursor.execute("ALTER TABLE documents ADD COLUMN provider TEXT;")

        # 3. Check existing officers columns for preferences_json
        cursor.execute("PRAGMA table_info(officers);")
        off_cols = {row["name"] for row in cursor.fetchall()}
        if "preferences_json" not in off_cols:
            cursor.execute("ALTER TABLE officers ADD COLUMN preferences_json TEXT;")

        # 4. Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_vehicles_demo_id ON vehicles(demo_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_vehicles_is_demo ON vehicles(is_demo);")

        conn.commit()
        return True


def insert_demo_vehicle(
    registration_number: str,
    owner_name: str,
    vehicle_type: str,
    vehicle_model: str,
    registration_date: str,
    demo_id: Optional[str] = None,
    is_demo: int = 1,
    state: str = "Delhi",
    rto_code: str = "DL-01",
    registration_status: str = "ACTIVE",
    owner_phone: str = "+91-98765-00000",
    owner_address: str = "New Delhi, India",
    manufacturer: str = "Maruti Suzuki",
    vehicle_class: str = "LMV",
    vehicle_color: str = "White",
    fuel_type: str = "Petrol",
    manufacturing_year: int = 2022,
    chassis_number: Optional[str] = None,
    engine_number: Optional[str] = None,
    driver_name: Optional[str] = None,
    driver_license_number: Optional[str] = None,
    driver_license_class: str = "LMV",
    driver_license_expiry: Optional[str] = None,
    driver_license_status: str = "VALID",
    db_path: Optional[str | Path] = None
) -> int:
    """
    Insert or update a comprehensive demo vehicle record and return its ID.
    Idempotent: updates existing record if plate matches.
    """
    clean_plate = registration_number.strip().upper()
    with db_session(db_path) as conn:
        cursor = conn.cursor()

        # Check if already exists
        cursor.execute("SELECT id FROM vehicles WHERE UPPER(registration_number) = ?;", (clean_plate,))
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
                    owner_name.strip(), vehicle_type.strip(), vehicle_model.strip(), registration_date.strip(),
                    demo_id, is_demo, state, rto_code, registration_status,
                    owner_phone, owner_address, manufacturer, vehicle_class,
                    vehicle_color, fuel_type, manufacturing_year, chassis_number,
                    engine_number, driver_name or owner_name, driver_license_number,
                    driver_license_class, driver_license_expiry, driver_license_status,
                    veh_id
                )
            )
            conn.commit()
            return veh_id
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
                    clean_plate, owner_name.strip(), vehicle_type.strip(), vehicle_model.strip(), registration_date.strip(),
                    demo_id, is_demo, state, rto_code, registration_status,
                    owner_phone, owner_address, manufacturer, vehicle_class,
                    vehicle_color, fuel_type, manufacturing_year, chassis_number,
                    engine_number, driver_name or owner_name, driver_license_number,
                    driver_license_class, driver_license_expiry, driver_license_status
                )
            )
            conn.commit()
            return cursor.lastrowid


def get_demo_fleet_metrics(db_path: Optional[str | Path] = None) -> Dict[str, Any]:
    """
    Calculate high-level dashboard metrics dynamically from real SQLite database records.
    """
    from datetime import datetime
    today = datetime.now().date()

    with db_session(db_path) as conn:
        cursor = conn.cursor()

        # 1. Total demo vehicles
        cursor.execute("SELECT COUNT(*) FROM vehicles WHERE is_demo = 1;")
        total_demo = cursor.fetchone()[0]

        # 2. Total all registered vehicles
        cursor.execute("SELECT COUNT(*) FROM vehicles;")
        total_vehicles = cursor.fetchone()[0]

        # 3. Verified vehicles count (from inspections)
        cursor.execute("SELECT COUNT(DISTINCT registration_number) FROM inspections;")
        vehicles_verified = cursor.fetchone()[0]

        # 4. Total inspections logged
        cursor.execute("SELECT COUNT(*) FROM inspections;")
        total_inspections = cursor.fetchone()[0]

        # 5. Documents dynamic calculation
        cursor.execute("SELECT document_type, expiry_date FROM documents;")
        all_docs = cursor.fetchall()

        valid_docs = 0
        expiring_soon_docs = 0
        expired_docs = 0

        for row in all_docs:
            exp_str = row["expiry_date"]
            try:
                exp_date = datetime.strptime(exp_str[:10], "%Y-%m-%d").date()
                delta = (exp_date - today).days
                if delta < 0:
                    expired_docs += 1
                elif delta <= 30:
                    expiring_soon_docs += 1
                else:
                    valid_docs += 1
            except Exception:
                expired_docs += 1

        # Missing documents calculation (each vehicle expects 4 mandatory docs: RC, INSURANCE, PUC, ROAD_TAX)
        expected_docs = total_vehicles * 4
        total_existing_docs = len(all_docs)
        missing_docs = max(0, expected_docs - total_existing_docs)

        # 6. Challans metrics
        cursor.execute("SELECT COUNT(*), COALESCE(SUM(fine_amount), 0) FROM challans;")
        ch_total_row = cursor.fetchone()
        total_challans = ch_total_row[0]
        total_fine_amount = float(ch_total_row[1])

        cursor.execute("SELECT COUNT(*), COALESCE(SUM(fine_amount), 0) FROM challans WHERE payment_status = 'PAID';")
        ch_paid_row = cursor.fetchone()
        paid_challans = ch_paid_row[0]
        revenue_collected = float(ch_paid_row[1])

        cursor.execute("SELECT COUNT(*), COALESCE(SUM(fine_amount), 0) FROM challans WHERE payment_status != 'PAID';")
        ch_unpaid_row = cursor.fetchone()
        unpaid_challans = ch_unpaid_row[0]
        unpaid_amount = float(ch_unpaid_row[1])

        # 7. Compliance rate calculation
        comp_rate = 0.0
        if total_existing_docs > 0:
            comp_rate = round((valid_docs / (total_existing_docs + missing_docs)) * 100, 1)

        return {
            "total_demo_vehicles": total_demo,
            "total_vehicles": total_vehicles,
            "vehicles_verified": vehicles_verified,
            "total_inspections": total_inspections,
            "documents_total": total_existing_docs,
            "documents_valid": valid_docs,
            "documents_expiring_soon": expiring_soon_docs,
            "documents_expired": expired_docs,
            "documents_missing": missing_docs,
            "compliance_rate": comp_rate,
            "total_challans": total_challans,
            "paid_challans": paid_challans,
            "unpaid_challans": unpaid_challans,
            "revenue_collected": revenue_collected,
            "unpaid_amount": unpaid_amount,
            "total_fine_amount": total_fine_amount,
        }


def insert_vehicle(
    registration_number: str,
    owner_name: str,
    vehicle_type: str,
    vehicle_model: str,
    registration_date: str,
    db_path: Optional[str | Path] = None
) -> int:
    """Insert a vehicle record and return its generated ID."""
    with db_session(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO vehicles (registration_number, owner_name, vehicle_type, vehicle_model, registration_date)
            VALUES (?, ?, ?, ?, ?);
            """,
            (
                registration_number.strip().upper(),
                owner_name.strip(),
                vehicle_type.strip(),
                vehicle_model.strip(),
                registration_date.strip()
            )
        )
        conn.commit()
        return cursor.lastrowid


def insert_document(
    vehicle_id: int,
    document_type: str,
    document_number: str,
    issue_date: str,
    expiry_date: str,
    status: str,
    db_path: Optional[str | Path] = None
) -> int:
    """Insert a document record and return its generated ID."""
    with db_session(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO documents (vehicle_id, document_type, document_number, issue_date, expiry_date, status)
            VALUES (?, ?, ?, ?, ?, ?);
            """,
            (
                vehicle_id,
                document_type.strip().upper(),
                document_number.strip().upper(),
                issue_date.strip(),
                expiry_date.strip(),
                status.strip().upper()
            )
        )
        conn.commit()
        return cursor.lastrowid


def insert_challan(
    challan_number: str,
    vehicle_id: int,
    violation_type: str,
    fine_amount: float,
    challan_date: str,
    payment_status: str,
    description: str = "",
    challan_status: str = "ISSUED",
    fine_breakdown_json: Optional[str] = None,
    pdf_path: Optional[str] = None,
    qr_path: Optional[str] = None,
    db_path: Optional[str | Path] = None
) -> int:
    """Insert a challan record and return its generated ID."""
    with db_session(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO challans (
                challan_number, vehicle_id, violation_type, fine_amount, challan_date, 
                payment_status, challan_status, description, fine_breakdown_json, pdf_path, qr_path
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            (
                challan_number.strip().upper(),
                vehicle_id,
                violation_type.strip(),
                float(fine_amount),
                challan_date.strip(),
                payment_status.strip().upper(),
                challan_status.strip().upper(),
                description.strip(),
                fine_breakdown_json,
                pdf_path,
                qr_path
            )
        )
        conn.commit()
        return cursor.lastrowid



def get_officer_by_username(username: str, db_path: Optional[str | Path] = None) -> Optional[Dict[str, Any]]:
    """Look up an active officer by username (case-insensitive)."""
    with db_session(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, username, password_hash, full_name, badge_number, role, station_id, is_active, created_at
            FROM officers
            WHERE LOWER(username) = LOWER(?) AND is_active = 1;
            """,
            (username.strip(),)
        )
        row = cursor.fetchone()
        return row_to_dict(row)


def get_officer_by_id(officer_id: int, db_path: Optional[str | Path] = None) -> Optional[Dict[str, Any]]:
    """Look up an officer by their primary key ID."""
    with db_session(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, username, full_name, badge_number, role, station_id, is_active, created_at
            FROM officers
            WHERE id = ?;
            """,
            (officer_id,)
        )
        row = cursor.fetchone()
        return row_to_dict(row)


def get_all_officers(db_path: Optional[str | Path] = None) -> List[Dict[str, Any]]:
    """Retrieve all officer records for administration."""
    with db_session(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, username, full_name, badge_number, role, station_id, is_active, created_at
            FROM officers
            ORDER BY id ASC;
            """
        )
        rows = cursor.fetchall()
        return rows_to_list(rows)


def insert_officer(
    username: str,
    password_hash: str,
    full_name: str,
    badge_number: str,
    role: str = "OFFICER",
    station_id: str = "SEC-04-EXPRESSWAY",
    is_active: int = 1,
    db_path: Optional[str | Path] = None
) -> int:
    """Insert a new officer account and return its ID."""
    with db_session(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO officers (username, password_hash, full_name, badge_number, role, station_id, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?);
            """,
            (
                username.strip().lower(),
                password_hash,
                full_name.strip(),
                badge_number.strip().upper(),
                role.strip().upper(),
                station_id.strip().upper(),
                int(is_active)
            )
        )
        conn.commit()
        return cursor.lastrowid


def update_officer(
    officer_id: int,
    full_name: Optional[str] = None,
    role: Optional[str] = None,
    station_id: Optional[str] = None,
    is_active: Optional[bool] = None,
    db_path: Optional[str | Path] = None,
) -> bool:
    """Update officer attributes in the database."""
    fields = []
    params = []
    if full_name is not None:
        fields.append("full_name = ?")
        params.append(full_name.strip())
    if role is not None:
        fields.append("role = ?")
        params.append(role.strip().upper())
    if station_id is not None:
        fields.append("station_id = ?")
        params.append(station_id.strip().upper())
    if is_active is not None:
        fields.append("is_active = ?")
        params.append(1 if is_active else 0)

    if not fields:
        return False

    params.append(officer_id)
    with db_session(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"UPDATE officers SET {', '.join(fields)} WHERE id = ?;",
            tuple(params)
        )
        conn.commit()
        return cursor.rowcount > 0


def get_officer_preferences(officer_id: int, db_path: Optional[str | Path] = None) -> Dict[str, Any]:
    """Retrieve user customization preferences (theme, language, date/time formats)."""
    import json
    default_prefs = {
        "theme": "light",
        "language": "en",
        "date_format": "DD/MM/YYYY",
        "time_format": "12h",
        "notifications": True
    }
    with db_session(db_path) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT preferences_json FROM officers WHERE id = ?;", (officer_id,))
            row = cursor.fetchone()
            if row and row["preferences_json"]:
                stored = json.loads(row["preferences_json"])
                default_prefs.update(stored)
        except Exception:
            pass
    return default_prefs


def update_officer_preferences(officer_id: int, preferences: Dict[str, Any], db_path: Optional[str | Path] = None) -> bool:
    """Store user customization preferences as JSON in officer record."""
    import json
    with db_session(db_path) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT preferences_json FROM officers WHERE id = ?;", (officer_id,))
            row = cursor.fetchone()
            current = {}
            if row and row["preferences_json"]:
                try:
                    current = json.loads(row["preferences_json"])
                except Exception:
                    current = {}
            current.update(preferences)
            cursor.execute(
                "UPDATE officers SET preferences_json = ? WHERE id = ?;",
                (json.dumps(current), officer_id)
            )
            conn.commit()
            return cursor.rowcount > 0
        except Exception:
            return False


# ============================================================================
# Inspections & Detection History Operations
# ============================================================================

def insert_inspection(
    inspection_code: str,
    registration_number: str,
    detection_confidence: float = 0.95,
    ocr_confidence: float = 0.92,
    plate_image_url: Optional[str] = None,
    vehicle_image_url: Optional[str] = None,
    verification_status: str = "COMPLIANT",
    violations_summary: Optional[str] = None,
    violations_json: Optional[str] = None,
    officer_id: Optional[int] = None,
    officer_name: Optional[str] = None,
    latitude: float = 28.5355,
    longitude: float = 77.3910,
    location_name: str = "Sector 04 Expressway Checkpoint",
    notes: Optional[str] = None,
    vehicle_id: Optional[int] = None,
    inspection_time: Optional[str] = None,
    db_path: Optional[str | Path] = None,
) -> int:
    """Insert a new inspection record."""
    clean_plate = registration_number.strip().upper()
    with db_session(db_path) as conn:
        cursor = conn.cursor()
        if vehicle_id is None:
            cursor.execute("SELECT id FROM vehicles WHERE registration_number = ?;", (clean_plate,))
            v_row = cursor.fetchone()
            if v_row:
                vehicle_id = v_row[0]

        if inspection_time:
            cursor.execute(
                """
                INSERT INTO inspections (
                    inspection_code, registration_number, vehicle_id, inspection_time,
                    detection_confidence, ocr_confidence, plate_image_url, vehicle_image_url,
                    verification_status, violations_summary, violations_json,
                    officer_id, officer_name, latitude, longitude, location_name, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    inspection_code, clean_plate, vehicle_id, inspection_time,
                    detection_confidence, ocr_confidence, plate_image_url, vehicle_image_url,
                    verification_status, violations_summary, violations_json,
                    officer_id, officer_name, latitude, longitude, location_name, notes
                )
            )
        else:
            cursor.execute(
                """
                INSERT INTO inspections (
                    inspection_code, registration_number, vehicle_id,
                    detection_confidence, ocr_confidence, plate_image_url, vehicle_image_url,
                    verification_status, violations_summary, violations_json,
                    officer_id, officer_name, latitude, longitude, location_name, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    inspection_code, clean_plate, vehicle_id,
                    detection_confidence, ocr_confidence, plate_image_url, vehicle_image_url,
                    verification_status, violations_summary, violations_json,
                    officer_id, officer_name, latitude, longitude, location_name, notes
                )
            )
        conn.commit()
        return cursor.lastrowid


def get_all_inspections(
    search: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db_path: Optional[str | Path] = None,
) -> List[Dict[str, Any]]:
    """Retrieve all inspection records with optional search and status filters."""
    query = "SELECT * FROM inspections"
    conditions = []
    params = []

    if search:
        conditions.append("(registration_number LIKE ? OR location_name LIKE ? OR inspection_code LIKE ?)")
        term = f"%{search.strip().upper()}%"
        params.extend([term, f"%{search.strip()}%", term])

    if status and status != "ALL":
        conditions.append("verification_status = ?")
        params.append(status.strip().upper())

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY inspection_time DESC LIMIT ? OFFSET ?;"
    params.extend([limit, offset])

    with db_session(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        return rows_to_list(rows)


def get_inspection_by_id(inspection_id: int, db_path: Optional[str | Path] = None) -> Optional[Dict[str, Any]]:
    """Retrieve an inspection record by its primary key ID."""
    with db_session(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM inspections WHERE id = ?;", (inspection_id,))
        row = cursor.fetchone()
        return row_to_dict(row)


def seed_default_inspections(db_path: Optional[str | Path] = None) -> None:
    """
    Seed initial realistic inspection records linked to existing vehicles and GPS checkpoints.
    """
    import json
    with db_session(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM inspections;")
        count = cursor.fetchone()[0]
        if count == 0:
            sample_inspections = [
                (
                    "INSP-2026-9001",
                    "DL01AB1234",
                    "2026-11-08 20:30:15",
                    0.985,
                    0.962,
                    "/static/crops/plate_8ce2c8df3874.jpg",
                    "/static/samples/sample_car_DL01AB1234.jpg",
                    "COMPLIANT",
                    "All documents (RC, Insurance, PUC, Tax) valid",
                    json.dumps([]),
                    2,
                    "Insp. Vikram Sharma",
                    28.5355,
                    77.3910,
                    "Sector 04 Expressway Checkpoint",
                    "Routine roadside camera verification"
                ),
                (
                    "INSP-2026-9002",
                    "DL02CD5678",
                    "2026-11-08 19:45:22",
                    0.972,
                    0.941,
                    "/static/crops/plate_ba9cae7ef5b9.jpg",
                    "/static/samples/sample_vehicle_no_plate.jpg",
                    "VIOLATION",
                    "Expired PUC, Expired Insurance",
                    json.dumps([{"code": "EXPIRED_PUC", "title": "Expired PUC"}, {"code": "EXPIRED_INSURANCE", "title": "Expired Insurance"}]),
                    2,
                    "Insp. Vikram Sharma",
                    28.6139,
                    77.2090,
                    "Connaught Place Outer Circle Node",
                    "Vehicle flagged for emission check"
                ),
                (
                    "INSP-2026-9003",
                    "HR26DQ5551",
                    "2026-11-08 18:20:00",
                    0.991,
                    0.978,
                    "/static/crops/plate_258725905b89.jpg",
                    "/static/samples/sample_car_DL01AB1234.jpg",
                    "COMPLIANT",
                    "All documents in order",
                    json.dumps([]),
                    3,
                    "Sub-Insp. Anita Singh",
                    28.4595,
                    77.0266,
                    "NH-48 Kherki Daula Toll Plaza",
                    "Automated high-speed gantry pass"
                ),
                (
                    "INSP-2026-9004",
                    "MH12DE5678",
                    "2026-11-08 17:15:40",
                    0.964,
                    0.932,
                    "/static/crops/plate_fb01f2903ce1.jpg",
                    "/static/samples/sample_commercial_MH12DE5678.jpg",
                    "VIOLATION",
                    "Commercial Road Tax Expired",
                    json.dumps([{"code": "EXPIRED_ROAD_TAX", "title": "Expired Road Tax"}]),
                    3,
                    "Sub-Insp. Anita Singh",
                    28.7041,
                    77.1025,
                    "Outer Ring Road G.T. Karnal Node",
                    "Commercial freight inspection"
                ),
                (
                    "INSP-2026-9005",
                    "UP16BC9012",
                    "2026-11-08 16:05:12",
                    0.988,
                    0.954,
                    "/static/crops/plate_b868d733e771.jpg",
                    "/static/samples/sample_car_DL01AB1234.jpg",
                    "COMPLIANT",
                    "Valid HSRP Plate and Documents",
                    json.dumps([]),
                    2,
                    "Insp. Vikram Sharma",
                    28.5700,
                    77.3200,
                    "Noida-Greater Noida Expressway Km 12",
                    "Fixed camera surveillance pass"
                ),
                (
                    "INSP-2026-9006",
                    "DL03EF9012",
                    "2026-11-08 14:30:50",
                    0.951,
                    0.923,
                    "/static/crops/plate_97ab7954bf4a.jpg",
                    "/static/samples/sample_car_DL01AB1234.jpg",
                    "VIOLATION",
                    "Insurance Expired 42 days ago",
                    json.dumps([{"code": "EXPIRED_INSURANCE", "title": "Expired Insurance"}]),
                    2,
                    "Insp. Vikram Sharma",
                    28.5244,
                    77.1855,
                    "Mehrauli Badarpur Border Node",
                    "Mobile patrol roadside check"
                ),
                (
                    "INSP-2026-9007",
                    "KA03HA1234",
                    "2026-11-08 12:10:05",
                    0.979,
                    0.965,
                    "/static/crops/plate_b544921e6b8b.jpg",
                    "/static/samples/sample_car_DL01AB1234.jpg",
                    "COMPLIANT",
                    "Interstate transit verified",
                    json.dumps([]),
                    3,
                    "Sub-Insp. Anita Singh",
                    28.5355,
                    77.3910,
                    "Sector 04 Expressway Checkpoint",
                    "Green corridor transit"
                ),
                (
                    "INSP-2026-9008",
                    "DL04GH3456",
                    "2026-11-08 10:45:18",
                    0.942,
                    0.915,
                    "/static/crops/plate_1c1f376f3be7.jpg",
                    "/static/samples/sample_car_DL01AB1234.jpg",
                    "VIOLATION",
                    "PUC Expired, Road Tax Due",
                    json.dumps([{"code": "EXPIRED_PUC", "title": "Expired PUC"}, {"code": "EXPIRED_ROAD_TAX", "title": "Expired Road Tax"}]),
                    2,
                    "Insp. Vikram Sharma",
                    28.6139,
                    77.2090,
                    "Connaught Place Outer Circle Node",
                    "Morning peak enforcement"
                ),
            ]

            for item in sample_inspections:
                cursor.execute(
                    """
                    INSERT INTO inspections (
                        inspection_code, registration_number, inspection_time,
                        detection_confidence, ocr_confidence, plate_image_url, vehicle_image_url,
                        verification_status, violations_summary, violations_json,
                        officer_id, officer_name, latitude, longitude, location_name, notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """,
                    item
                )
            conn.commit()


def seed_default_officers(db_path: Optional[str | Path] = None) -> None:
    """
    Seed initial Admin and Officer accounts with hashed passwords if officers table is empty.
    """
    from werkzeug.security import generate_password_hash

    with db_session(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM officers;")
        count = cursor.fetchone()[0]
        if count == 0:
            default_users = [
                (
                    "admin",
                    generate_password_hash("Admin@123"),
                    "Administrator Sharma",
                    "ADMIN-001",
                    "ADMIN",
                    "HQ-CENTRAL"
                ),
                (
                    "officer",
                    generate_password_hash("Officer@123"),
                    "Insp. Vikram Sharma",
                    "TP-DEL-8842",
                    "OFFICER",
                    "SEC-04-EXPRESSWAY"
                ),
                (
                    "anita_singh",
                    generate_password_hash("Officer@123"),
                    "Sub-Insp. Anita Singh",
                    "TP-DEL-9104",
                    "OFFICER",
                    "SEC-04-EXPRESSWAY"
                ),
            ]
            cursor.executemany(
                """
                INSERT INTO officers (username, password_hash, full_name, badge_number, role, station_id)
                VALUES (?, ?, ?, ?, ?, ?);
                """,
                default_users
            )
            conn.commit()


if __name__ == "__main__":
    db_file = get_db_path()
    print(f"📦 SQLite Database Path: {db_file}")
    init_db()
    seed_default_officers()
    print("✅ Database initialized and default officers seeded successfully.")
