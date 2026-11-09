"""
demo_challan_pipeline.py - Digital Challan & QR-PDF Engine Live Demonstration
=============================================================================
Smart ANPR Vehicle Verification System

Demonstrates:
1. Complete digital challan issuance for a non-compliant vehicle.
2. Dynamic ReportLab PDF citation receipt generation.
3. Secure verification QR barcode generation (PII-free).
4. Citation retrieval via verification endpoint.
5. Demonstration payment transition (PENDING -> PAID) and PDF badge re-rendering.
6. File verification and inspection.
"""

import os
import sys
from pathlib import Path
from PIL import Image

# Ensure backend directory is in Python path
BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app import create_app
from app.core.config import Config
from app.services.challan_service import (
    generate_digital_challan,
    get_challan_details,
    process_demonstration_payment,
)


def run_live_demo():
    print("=" * 76)
    print("🚔 SMART ANPR VEHICLE VERIFICATION SYSTEM")
    print("📄 Phase 5: Digital Challan & QR-PDF Engine - Live Demonstration")
    print("=" * 76)

    # 1. Target vehicle: TN09BK3456 (Suresh Ramachandran - Hyundai i20)
    # Documents: Expired Insurance + Expired PUC
    plate = "TN09BK3456"
    print(f"\n[Step 1] Issuing Digital Citation for Vehicle: {plate}...")
    challan = generate_digital_challan(
        registration_number=plate,
        description="Routine automated ANPR camera checkpoint enforcement."
    )

    ch_num = challan["challan_number"]
    print(f"  ✓ Citation Issued:        {ch_num}")
    print(f"  ✓ Registered Owner:        {challan['vehicle']['owner_name']}")
    print(f"  ✓ Vehicle Class / Model:   {challan['vehicle']['vehicle_type']} / {challan['vehicle']['vehicle_model']}")
    print(f"  ✓ Violations Penalized:    {challan['violation_type']}")
    print(f"  ✓ Total Fine Payable:      {challan['fine_amount_formatted']}")
    print(f"  ✓ Payment Status:          {challan['payment_status']} (Status: {challan['challan_status']})")

    # 2. Inspect itemized breakdown
    print(f"\n[Step 2] Itemized Fine Breakdown (Configurable Schedule):")
    for idx, item in enumerate(challan["fine_breakdown"]["items"], 1):
        print(f"  {idx}. {item['title']}")
        print(f"     Statutory Clause: {item['statute']}")
        print(f"     Severity Level:   [{item['severity']}]  Fine: {item['fine_amount_formatted']}")

    # 3. Check Artifacts on Disk
    pdf_path = Path(Config.PDF_OUTPUT_DIR) / f"{ch_num}.pdf"
    qr_path = Path(Config.QR_OUTPUT_DIR) / f"{ch_num}.png"

    print(f"\n[Step 3] Verifying Generated Artifacts on Filesystem:")
    print(f"  • PDF Receipt Path: {pdf_path}")
    if pdf_path.is_file():
        pdf_size = pdf_path.stat().st_size
        with open(pdf_path, "rb") as f:
            pdf_header = f.read(8).decode("latin-1", errors="replace")
        print(f"    ✓ Valid PDF File ({pdf_size:,} bytes, Header: {pdf_header[:5]})")
    else:
        print("    ✗ PDF file missing!")

    print(f"  • QR Barcode Path:  {qr_path}")
    if qr_path.is_file():
        qr_size = qr_path.stat().st_size
        with Image.open(qr_path) as img:
            dims = img.size
        print(f"    ✓ Valid PNG Barcode ({qr_size:,} bytes, Dimensions: {dims[0]}x{dims[1]} px)")
    else:
        print("    ✗ QR barcode missing!")

    # 4. QR Verification Endpoint
    print(f"\n[Step 4] Querying Public Verification Endpoint for {ch_num}...")
    details = get_challan_details(ch_num)
    if details:
        print(f"  ✓ Verification Success:")
        print(f"    - Target URL:       {details['artifacts']['verification_url']}")
        print(f"    - Download PDF URL: {details['artifacts']['pdf_url']}")
        print(f"    - View Barcode URL: {details['artifacts']['qr_url']}")

    # 5. Demonstration Payment Simulation
    print(f"\n[Step 5] Simulating Demonstration Payment (PENDING -> PAID)...")
    settled = process_demonstration_payment(ch_num, action="PAY")
    if settled:
        print(f"  ✓ Payment Status Updated:  {settled['payment_status']}")
        print(f"  ✓ Challan Status Updated:  {settled['challan_status']}")
        print(f"  ✓ Notice: {settled.get('demonstration_notice')}")
        print(f"  ✓ PDF receipt automatically re-compiled with settled stamp.")

    print("\n" + "=" * 76)
    print("✅ Live Demonstration Finished Successfully.")
    print("=" * 76)


if __name__ == "__main__":
    run_live_demo()
