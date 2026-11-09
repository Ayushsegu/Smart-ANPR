"""
init_db.py - Database Initialization Script
===========================================
Smart ANPR Vehicle Verification System

This script initializes the SQLite database schema for:
- VEHICLES
- DOCUMENTS
- CHALLANS

Usage:
    python init_db.py          # Create tables if not exists
    python init_db.py --drop   # Drop existing tables and recreate cleanly
"""

import os
import sys
from pathlib import Path

# Ensure backend directory is in Python path
BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from database import get_db_path, get_db_connection, init_db


def create_anpr_db_symlink(canonical_db_path: Path) -> None:
    """
    Ensure anpr.db is accessible both at backend/data/anpr.db and directly at backend/anpr.db.
    """
    symlink_path = BACKEND_DIR / "anpr.db"
    try:
        if not symlink_path.exists():
            rel_target = Path("data") / canonical_db_path.name
            symlink_path.symlink_to(rel_target)
            print(f"🔗 Linked convenient shortcut: {symlink_path} -> {rel_target}")
    except Exception as e:
        # Non-fatal if symlink cannot be created (e.g. OS permissions)
        pass


def verify_tables(db_path: Path) -> bool:
    """Check that all required tables are present in the database."""
    required_tables = {"vehicles", "documents", "challans"}
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        existing_tables = {row["name"] for row in cursor.fetchall()}

    missing = required_tables - existing_tables
    if missing:
        print(f"❌ Error: Missing tables: {missing}")
        return False

    print(f"✅ Verified tables present: {sorted(list(required_tables))}")
    return True


def main():
    drop_existing = "--drop" in sys.argv or "--reset" in sys.argv
    db_path = get_db_path()

    print("=" * 60)
    print("🚀 ANPR System: Database Initializer")
    print(f"📁 Target Database: {db_path}")
    print(f"🔄 Reset/Drop Mode: {'ENABLED' if drop_existing else 'DISABLED'}")
    print("=" * 60)

    try:
        init_db(db_path=db_path, drop_existing=drop_existing)
        print("✅ Schema created successfully.")

        if verify_tables(db_path):
            create_anpr_db_symlink(db_path)
            print("=" * 60)
            print("🎉 Database initialization completed successfully!")
            print("=" * 60)
            return 0
        else:
            print("❌ Table verification failed.")
            return 1
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
