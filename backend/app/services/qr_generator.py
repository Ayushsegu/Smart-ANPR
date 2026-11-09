"""
app/services/qr_generator.py - QR Code Generation Engine
=========================================================
Smart ANPR Vehicle Verification System

This module generates unique, scannable QR codes for digital traffic challans.
It encodes a secure verification URL pointing to the challan verification
endpoint, avoiding the inclusion of sensitive Personally Identifiable Information (PII)
directly in the barcode payload.

Key Features:
- Standard ISO/IEC 18004 compliant QR generation using Python `qrcode`.
- Configurable base verification URL (defaults to http://127.0.0.1:5001).
- Error correction level M (up to 15% recovery) for reliable camera scanning.
- Automated static directory creation and file persistence.
- Returns both local filesystem path and web-accessible static URL.
"""

from pathlib import Path
from typing import Optional, Tuple
import qrcode
from qrcode.constants import ERROR_CORRECT_M

from app.core.config import Config


def get_default_qr_dir() -> Path:
    """Get the target directory for saving generated QR code PNG files."""
    qr_dir = Path(Config.QR_OUTPUT_DIR).resolve()
    qr_dir.mkdir(parents=True, exist_ok=True)
    return qr_dir


def generate_challan_qr(
    challan_number: str,
    base_url: Optional[str] = None,
    output_dir: Optional[str | Path] = None
) -> Tuple[str, str]:
    """
    Generate a high-contrast QR code image for a specific challan number.

    The payload encodes the verification URL:
        {base_url}/api/challans/{challan_number}
    No sensitive personal data is embedded directly in the QR code.

    Args:
        challan_number: Unique citation identifier (e.g., 'CH-2026-00001').
        base_url: Optional base server URL (defaults to Config.BASE_URL).
        output_dir: Optional output directory for saving the PNG file.

    Returns:
        Tuple of (absolute_file_path, relative_web_url):
            - absolute_file_path: Full system path to the saved PNG image.
            - relative_web_url: Web path, e.g. '/static/challans/qr/CH-2026-00001.png'.
    """
    clean_number = challan_number.strip().upper()
    server_base = (base_url or Config.BASE_URL).rstrip("/")
    verification_url = f"{server_base}/api/challans/{clean_number}"

    # Determine save directory and file paths
    target_dir = Path(output_dir).resolve() if output_dir else get_default_qr_dir()
    target_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{clean_number}.png"
    file_path = target_dir / filename
    relative_url = f"/static/challans/qr/{filename}"

    # Configure QR code matrix
    qr = qrcode.QRCode(
        version=None,  # Automatic dimension determination
        error_correction=ERROR_CORRECT_M,
        box_size=10,
        border=2,
    )
    qr.add_data(verification_url)
    qr.make(fit=True)

    # Render image with dark blue/black and white background
    img = qr.make_image(fill_color="#0F172A", back_color="#FFFFFF")
    img.save(str(file_path))

    return str(file_path), relative_url
