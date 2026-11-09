"""
app/models/__init__.py - Models package initializer
"""

from .database import (
    get_db_connection,
    get_db_path,
    init_db,
    row_to_dict,
    rows_to_list,
    get_all_vehicles,
    get_vehicle_by_plate,
    get_vehicle_by_id,
    get_documents_by_vehicle_id,
    get_documents_by_plate,
    get_all_challans,
    get_challans_by_vehicle_id,
    get_challan_by_number,
    update_challan_payment_status,
    update_challan_artifacts,
    migrate_db_for_phase5,
    insert_vehicle,
    insert_document,
    insert_challan
)

__all__ = [
    "get_db_connection",
    "get_db_path",
    "init_db",
    "row_to_dict",
    "rows_to_list",
    "get_all_vehicles",
    "get_vehicle_by_plate",
    "get_vehicle_by_id",
    "get_documents_by_vehicle_id",
    "get_documents_by_plate",
    "get_all_challans",
    "get_challans_by_vehicle_id",
    "get_challan_by_number",
    "update_challan_payment_status",
    "update_challan_artifacts",
    "migrate_db_for_phase5",
    "insert_vehicle",
    "insert_document",
    "insert_challan"
]
