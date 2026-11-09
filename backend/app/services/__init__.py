"""
app/services/__init__.py - Services Package Initializer
"""

from .document_verifier import (
    STATUS_VALID,
    STATUS_EXPIRING_SOON,
    STATUS_EXPIRED,
    STATUS_MISSING,
    parse_date,
    evaluate_document_status,
    verify_single_document,
)
from .fine_calculator import calculate_fine_breakdown
from .vehicle_verifier import (
    VERDICT_COMPLIANT,
    VERDICT_ATTENTION_REQUIRED,
    VERDICT_NON_COMPLIANT,
    verify_vehicle_compliance,
)
from .plate_cleaner import (
    clean_raw_text,
    correct_ocr_ambiguities,
    validate_plate_format,
    clean_and_validate_plate,
)
from .ocr_service import (
    get_easyocr_reader,
    preprocess_plate_image,
    read_plate_text,
)
from .anpr_detector import (
    LicensePlateDetector,
    get_detector,
    validate_image_file,
    crop_plate,
    process_vehicle_image,
)
from .qr_generator import generate_challan_qr
from .pdf_generator import generate_challan_pdf
from .challan_service import (
    generate_digital_challan,
    get_challan_details,
    process_demonstration_payment,
    generate_unique_challan_number,
)

__all__ = [
    # Phase 3: Verification & Fine Engine
    "STATUS_VALID",
    "STATUS_EXPIRING_SOON",
    "STATUS_EXPIRED",
    "STATUS_MISSING",
    "parse_date",
    "evaluate_document_status",
    "verify_single_document",
    "calculate_fine_breakdown",
    "VERDICT_COMPLIANT",
    "VERDICT_ATTENTION_REQUIRED",
    "VERDICT_NON_COMPLIANT",
    "verify_vehicle_compliance",
    # Phase 4: ANPR & OCR Pipeline
    "clean_raw_text",
    "correct_ocr_ambiguities",
    "validate_plate_format",
    "clean_and_validate_plate",
    "get_easyocr_reader",
    "preprocess_plate_image",
    "read_plate_text",
    "LicensePlateDetector",
    "get_detector",
    "validate_image_file",
    "crop_plate",
    "process_vehicle_image",
    # Phase 5: Digital Challan & QR-PDF Engine
    "generate_challan_qr",
    "generate_challan_pdf",
    "generate_digital_challan",
    "get_challan_details",
    "process_demonstration_payment",
    "generate_unique_challan_number",
]
