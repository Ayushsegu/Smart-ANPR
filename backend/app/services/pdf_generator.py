"""
app/services/pdf_generator.py - Digital Challan PDF Generation Service
=====================================================================
Smart ANPR Vehicle Verification System

This module generates professional digital traffic challan receipts in PDF format
using Python ReportLab Platypus.

Key Features:
- Official document styling with authority branding and layout hierarchy.
- Unique citation ID and formatted timestamp.
- Registered vehicle details (Registration No, Owner Name, Vehicle Model/Type).
- Itemized violation and fine breakdown table with statutory references.
- Dynamic payment status stamp ('PENDING' in amber/red, 'PAID' in green, 'FAILED' in slate).
- Embedded verification QR code image.
- Academic demonstration prototype disclaimer.
- Output persistence in static directory with web URL resolution.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    HRFlowable,
    Image,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.core.config import Config


def get_default_pdf_dir() -> Path:
    """Get the target directory for saving generated PDF challan receipts."""
    pdf_dir = Path(Config.PDF_OUTPUT_DIR).resolve()
    pdf_dir.mkdir(parents=True, exist_ok=True)
    return pdf_dir


def generate_challan_pdf(
    challan_data: Dict[str, Any],
    qr_image_path: Optional[str] = None,
    output_dir: Optional[str | Path] = None
) -> Tuple[str, str]:
    """
    Generate an official-format Digital Traffic Challan PDF document.

    Args:
        challan_data: Dictionary containing:
            - challan_number (str)
            - registration_number (str)
            - owner_name (str)
            - vehicle_type (str)
            - vehicle_model (str)
            - violation_type (str)
            - fine_amount (float)
            - challan_date (str)
            - payment_status (str: PENDING, PAID, FAILED)
            - challan_status (str: ISSUED, SETTLED, CANCELLED)
            - description (str)
            - fine_breakdown / fine_breakdown_json (list or JSON string)
        qr_image_path: Optional path to pre-generated QR code PNG file.
        output_dir: Optional custom destination folder.

    Returns:
        Tuple of (absolute_file_path, relative_web_url):
            - absolute_file_path: Full disk path to saved PDF.
            - relative_web_url: Web path, e.g. '/static/challans/pdf/CH-2026-00001.pdf'.
    """
    clean_num = str(challan_data.get("challan_number", "CH-DEMO-0000")).strip().upper()
    target_dir = Path(output_dir).resolve() if output_dir else get_default_pdf_dir()
    target_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{clean_num}.pdf"
    file_path = target_dir / filename
    relative_url = f"/static/challans/pdf/{filename}"

    # Setup document template with A4 page size and 36pt (0.5 inch) margins
    doc = SimpleDocTemplate(
        str(file_path),
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=32,
        bottomMargin=32,
        title=f"Digital Challan - {clean_num}",
        author="Smart ANPR Traffic Enforcement System",
    )

    # Prepare typography styles
    base_styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ChallanTitle",
        parent=base_styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=2,
    )

    subtitle_style = ParagraphStyle(
        "ChallanSubtitle",
        parent=base_styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#2563EB"),
        spaceAfter=1,
    )

    agency_style = ParagraphStyle(
        "ChallanAgency",
        parent=base_styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#64748B"),
    )

    section_heading = ParagraphStyle(
        "SectionHeading",
        parent=base_styles["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#0F172A"),
        spaceBefore=6,
        spaceAfter=3,
    )

    label_style = ParagraphStyle(
        "FieldLabel",
        parent=base_styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#475569"),
    )

    value_style = ParagraphStyle(
        "FieldValue",
        parent=base_styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#0F172A"),
    )

    table_header_style = ParagraphStyle(
        "TableHeader",
        parent=base_styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        textColor=colors.white,
    )

    table_cell_style = ParagraphStyle(
        "TableCell",
        parent=base_styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#1E293B"),
    )

    total_label_style = ParagraphStyle(
        "TotalLabel",
        parent=base_styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=12,
        textColor=colors.HexColor("#0F172A"),
        alignment=2,  # Right-aligned
    )

    total_value_style = ParagraphStyle(
        "TotalValue",
        parent=base_styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=13,
        textColor=colors.HexColor("#DC2626"),
        alignment=2,  # Right-aligned
    )

    disclaimer_style = ParagraphStyle(
        "DisclaimerText",
        parent=base_styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=7,
        leading=9,
        textColor=colors.HexColor("#475569"),
        alignment=1,  # Centered
    )

    elements: List[Any] = []

    # -------------------------------------------------------------------------
    # 1. HEADER SECTION
    # -------------------------------------------------------------------------
    payment_status = str(challan_data.get("payment_status", "PENDING")).strip().upper()
    if payment_status == "PAID":
        badge_bg = colors.HexColor("#16A34A")
        badge_text = "PAID / SETTLED"
    elif payment_status == "FAILED":
        badge_bg = colors.HexColor("#64748B")
        badge_text = "PAYMENT FAILED"
    else:
        badge_bg = colors.HexColor("#DC2626")
        badge_text = "PAYMENT PENDING"

    header_left = [
        Paragraph("DIGITAL TRAFFIC CHALLAN", title_style),
        Paragraph("TRAFFIC ENFORCEMENT & HIGHWAY SURVEILLANCE BRANCH", subtitle_style),
        Paragraph("Smart ANPR Automated Electronic Violation Notice (Demo System)", agency_style),
    ]

    status_badge_p = Paragraph(
        f"<font color='white'><b>&nbsp;{badge_text}&nbsp;</b></font>",
        ParagraphStyle(
            "BadgeP",
            fontName="Helvetica-Bold",
            fontSize=9,
            leading=11,
            alignment=1,  # Center
        )
    )

    date_str = str(challan_data.get("challan_date", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    header_right = [
        Paragraph(f"<b>Challan No:</b> {clean_num}", value_style),
        Paragraph(f"<b>Issued Date:</b> {date_str}", value_style),
        Spacer(1, 4),
        Table([[status_badge_p]], colWidths=[130], rowHeights=[18], style=[
            ("BACKGROUND", (0, 0), (-1, -1), badge_bg),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
        ]),
    ]

    header_table = Table([[header_left, header_right]], colWidths=[360, 163])
    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(header_table)

    # Accent decorative bar
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#2563EB"), spaceBefore=6, spaceAfter=8))

    # -------------------------------------------------------------------------
    # 2. VEHICLE & OFFENDER PARTICULARS
    # -------------------------------------------------------------------------
    elements.append(Paragraph("VEHICLE & REGISTERED OWNER PARTICULARS", section_heading))

    reg_plate = str(challan_data.get("registration_number", "UNKNOWN")).strip().upper()
    owner = str(challan_data.get("owner_name", "N/A")).strip()
    v_type = str(challan_data.get("vehicle_type", "N/A")).strip()
    v_model = str(challan_data.get("vehicle_model", "N/A")).strip()
    c_status = str(challan_data.get("challan_status", "ISSUED")).strip().upper()

    particulars_data = [
        [
            Paragraph("Registration Number:", label_style),
            Paragraph(f"<b>{reg_plate}</b>", value_style),
            Paragraph("Registered Owner:", label_style),
            Paragraph(f"<b>{owner}</b>", value_style),
        ],
        [
            Paragraph("Vehicle Class / Type:", label_style),
            Paragraph(v_type, value_style),
            Paragraph("Vehicle Model:", label_style),
            Paragraph(v_model, value_style),
        ],
        [
            Paragraph("Challan Status:", label_style),
            Paragraph(c_status, value_style),
            Paragraph("Enforcement Station:", label_style),
            Paragraph("Central ANPR Surveillance Node 01", value_style),
        ]
    ]

    particulars_table = Table(particulars_data, colWidths=[120, 145, 115, 143])
    particulars_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    elements.append(particulars_table)
    elements.append(Spacer(1, 8))

    # -------------------------------------------------------------------------
    # 3. ITEMIZED VIOLATION PARTICULARS & FINE SCHEDULE
    # -------------------------------------------------------------------------
    elements.append(Paragraph("VIOLATION PARTICULARS & FINE BREAKDOWN", section_heading))

    # Parse fine breakdown items
    raw_breakdown = challan_data.get("fine_breakdown") or challan_data.get("fine_breakdown_json")
    items_list: List[Dict[str, Any]] = []

    if isinstance(raw_breakdown, str):
        try:
            parsed = json.loads(raw_breakdown)
            if isinstance(parsed, dict) and "items" in parsed:
                items_list = parsed["items"]
            elif isinstance(parsed, list):
                items_list = parsed
        except Exception:
            items_list = []
    elif isinstance(raw_breakdown, dict) and "items" in raw_breakdown:
        items_list = raw_breakdown["items"]
    elif isinstance(raw_breakdown, list):
        items_list = raw_breakdown

    # If items list is empty, construct a fallback single entry from violation_type & fine_amount
    fine_amount_val = float(challan_data.get("fine_amount", 0.0))
    if not items_list:
        v_title = str(challan_data.get("violation_type", "Traffic Violation")).replace("_", " ").title()
        items_list = [{
            "violation_code": str(challan_data.get("violation_type", "VIOLATION")),
            "title": v_title,
            "statute": "Motor Vehicles Act 1988",
            "severity": "HIGH",
            "fine_amount": fine_amount_val,
            "fine_amount_formatted": f"₹{fine_amount_val:,.2f}",
            "description": str(challan_data.get("description", "Non-compliance identified."))
        }]

    # Build breakdown table rows
    breakdown_rows = [
        [
            Paragraph("<b>#</b>", table_header_style),
            Paragraph("<b>Violation Particulars</b>", table_header_style),
            Paragraph("<b>Statutory Reference</b>", table_header_style),
            Paragraph("<b>Severity</b>", table_header_style),
            Paragraph("<b>Fine Amount (₹)</b>", table_header_style),
        ]
    ]

    for idx, item in enumerate(items_list, 1):
        i_title = item.get("title") or item.get("violation_code", "Violation")
        i_desc = item.get("description", "")
        desc_text = f"<b>{i_title}</b>"
        if i_desc and i_desc != i_title:
            desc_text += f"<br/><font color='#64748B' size='6.5'>{i_desc}</font>"

        i_statute = item.get("statute", "Motor Vehicles Act")
        i_severity = item.get("severity", "MEDIUM")
        i_amount = float(item.get("fine_amount", 0.0))

        breakdown_rows.append([
            Paragraph(str(idx), table_cell_style),
            Paragraph(desc_text, table_cell_style),
            Paragraph(i_statute, table_cell_style),
            Paragraph(f"<b>{i_severity}</b>", table_cell_style),
            Paragraph(f"₹{i_amount:,.2f}", table_cell_style),
        ])

    # Summary row for total payable amount
    total_payable_str = f"₹{fine_amount_val:,.2f}"
    breakdown_rows.append([
        "",
        "",
        "",
        Paragraph("<b>TOTAL PAYABLE FINE:</b>", total_label_style),
        Paragraph(f"<b>{total_payable_str}</b>", total_value_style),
    ])

    breakdown_table = Table(breakdown_rows, colWidths=[24, 210, 134, 65, 90])
    num_items = len(items_list)
    breakdown_table.setStyle(TableStyle([
        # Header style
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
        ("ALIGN", (0, 0), (-1, 0), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("GRID", (0, 0), (-1, num_items), 0.5, colors.HexColor("#CBD5E1")),
        # Alternating row colors
        *[("BACKGROUND", (0, r), (-1, r), colors.HexColor("#F8FAFC") if r % 2 == 0 else colors.white)
          for r in range(1, num_items + 1)],
        # Right alignment for amount column
        ("ALIGN", (4, 1), (4, -1), "RIGHT"),
        # Total row style
        ("SPAN", (0, num_items + 1), (2, num_items + 1)),
        ("BACKGROUND", (0, num_items + 1), (-1, num_items + 1), colors.HexColor("#EFF6FF")),
        ("LINEABOVE", (0, num_items + 1), (-1, num_items + 1), 1.5, colors.HexColor("#2563EB")),
        ("LINEBELOW", (0, num_items + 1), (-1, num_items + 1), 1.5, colors.HexColor("#2563EB")),
    ]))
    elements.append(breakdown_table)
    elements.append(Spacer(1, 10))

    # -------------------------------------------------------------------------
    # 4. QR CODE & VERIFICATION INSTRUCTIONS
    # -------------------------------------------------------------------------
    qr_element: Any
    if qr_image_path and Path(qr_image_path).is_file():
        qr_element = Image(str(qr_image_path), width=85, height=85)
    else:
        # Fallback text placeholder if QR is not generated
        qr_element = Paragraph("[QR Code Available Online]", value_style)

    inst_heading = ParagraphStyle(
        "InstHeading",
        parent=base_styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#0F172A"),
    )
    inst_body = ParagraphStyle(
        "InstBody",
        parent=base_styles["Normal"],
        fontName="Helvetica",
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#334155"),
    )

    instructions_flowables = [
        Paragraph("VERIFICATION & PAYMENT INSTRUCTIONS", inst_heading),
        Spacer(1, 2),
        Paragraph("1. <b>Digital Verification:</b> Scan the QR code to verify this citation's validity and check live settlement status via the Smart ANPR portal.", inst_body),
        Paragraph("2. <b>Dispute / Settlement:</b> Payment or formal grievance may be lodged within 30 days of issuance.", inst_body),
        Paragraph("3. <b>Online Portal URL:</b> <code>/api/challans/" + clean_num + "</code>", inst_body),
        Paragraph("4. <b>Reference Statute:</b> Motor Vehicles (Amendment) Act 2019 & Central Motor Vehicles Rules 1989.", inst_body),
    ]

    qr_caption = Paragraph(
        "<font size='6.5' color='#64748B'>Scan to Authenticate</font>",
        ParagraphStyle("QRCaption", alignment=1, fontName="Helvetica", leading=8)
    )

    qr_cell = [
        qr_element,
        Spacer(1, 2),
        qr_caption
    ]

    auth_table = Table([[qr_cell, instructions_flowables]], colWidths=[95, 428])
    auth_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (0, 0), "CENTER"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
    ]))
    elements.append(auth_table)
    elements.append(Spacer(1, 10))

    # -------------------------------------------------------------------------
    # 5. ACADEMIC DEMONSTRATION DISCLAIMER
    # -------------------------------------------------------------------------
    disclaimer_text = (
        "<b>ACADEMIC DEMONSTRATION PROTOTYPE DISCLAIMER:</b><br/>"
        "This digital document is generated by an academic prototype Smart ANPR Vehicle Verification System "
        "for educational evaluation and demonstration purposes only. It is <b>NOT</b> an official Government of India "
        "e-Challan, Parivahan notice, or state police traffic citation. It carries no legal validity, statutory authority, "
        "or enforceable financial liability. Fictional owner and vehicle profiles are utilized."
    )

    disclaimer_table = Table([[Paragraph(disclaimer_text, disclaimer_style)]], colWidths=[523])
    disclaimer_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FEF3C7")),  # Soft amber background
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#F59E0B")),     # Amber border
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    elements.append(KeepTogether(disclaimer_table))

    # Build the PDF document
    doc.build(elements)

    return str(file_path), relative_url
