"""
app/services/plate_cleaner.py - License Plate Cleaning & Formatting Engine
==========================================================================
Smart ANPR Vehicle Verification System

This module handles:
1. Normalization (uppercase, whitespace removal, punctuation removal).
2. Optical character recognition (OCR) ambiguity resolution (0 vs O, 1 vs I, etc.).
3. Structural regex validation for Indian vehicle registration formats.
4. Preserving raw OCR text alongside cleaned & corrected variants for audit/review.
5. Flagging uncertainty for officer manual review.
"""

import re
from typing import Any, Dict, Optional, Tuple

# Standard Indian License Plate: State (2 letters) + RTO (1-2 digits) + Series (1-3 letters) + Number (4 digits)
# Examples: DL01AB1234, MH12DE5678, DL1LAA9988, KA03MJ9012
STANDARD_INDIAN_PLATE_REGEX = re.compile(r"^([A-Z]{2})([0-9]{1,2})([A-Z]{1,3})([0-9]{4})$")

# Bharat Series (BH): Year (2 digits) + BH + 4 digits + 1-2 letters
# Example: 22BH1234AA
BHARAT_SERIES_REGEX = re.compile(r"^([0-9]{2})(BH)([0-9]{4})([A-Z]{1,2})$")

# Valid Indian State & UT Codes
VALID_STATE_CODES = {
    "AN", "AP", "AR", "AS", "BR", "CH", "CG", "DD", "DL", "DN", "GA", "GJ",
    "HP", "HR", "JH", "JK", "KA", "KL", "LA", "LD", "MH", "ML", "MN", "MP",
    "MZ", "NL", "OD", "PB", "PY", "RJ", "SK", "TN", "TR", "TS", "UK", "UP",
    "WB"
}

# Character replacement maps for positional disambiguation
CHAR_TO_DIGIT_MAP = {
    "O": "0", "D": "0", "Q": "0",
    "I": "1", "L": "1", "|": "1",
    "Z": "2",
    "E": "3",
    "A": "4",
    "S": "5",
    "G": "6", "b": "6",
    "T": "7",
    "B": "8",
}

DIGIT_TO_CHAR_MAP = {
    "0": "O",
    "1": "I",
    "2": "Z",
    "4": "A",
    "5": "S",
    "6": "G",
    "8": "B",
}


def clean_raw_text(raw_text: str) -> str:
    """
    Remove all whitespace, hyphens, dots, and extraneous punctuation.
    Strips country prefix 'IND' commonly found on High Security Registration Plates (HSRP).
    Converts string to uppercase.
    """
    if not raw_text:
        return ""
    # Strip non-alphanumeric characters
    cleaned = re.sub(r"[^A-Za-z0-9]", "", raw_text).upper()

    # Strip HSRP 'IND' prefix if present (e.g., 'INDDL01AB1234' -> 'DL01AB1234')
    if cleaned.startswith("IND") and len(cleaned) >= 11:
        cleaned = cleaned[3:]
    elif cleaned.endswith("IND") and len(cleaned) >= 11:
        cleaned = cleaned[:-3]

    return cleaned


def correct_ocr_ambiguities(cleaned: str) -> str:
    """
    Apply positional heuristics based on Indian number plate architecture:
    - First 2 chars: Letters (State Code)
    - Next 1-2 chars: Digits (RTO Code)
    - Next 1-3 chars: Letters (Series Code)
    - Last 4 chars: Digits (Registration Number)
    """
    if len(cleaned) < 8 or len(cleaned) > 11:
        return cleaned

    chars = list(cleaned)
    n = len(chars)

    # 1. State Code (First 2 positions must be letters)
    for i in (0, 1):
        if chars[i].isdigit():
            chars[i] = DIGIT_TO_CHAR_MAP.get(chars[i], chars[i])

    # 2. Last 4 positions must be digits
    for i in range(n - 4, n):
        if chars[i].isalpha():
            chars[i] = CHAR_TO_DIGIT_MAP.get(chars[i], chars[i])

    # 3. Positions 2 & 3 (RTO code digits)
    # If standard 10-char plate (e.g. DL 01 AB 1234)
    if n == 10:
        for i in (2, 3):
            if chars[i].isalpha():
                chars[i] = CHAR_TO_DIGIT_MAP.get(chars[i], chars[i])
        for i in (4, 5):
            if chars[i].isdigit():
                chars[i] = DIGIT_TO_CHAR_MAP.get(chars[i], chars[i])

    return "".join(chars)


def validate_plate_format(plate: str) -> Tuple[bool, Optional[str], Optional[Dict[str, str]]]:
    """
    Validates whether a plate adheres to standard Indian or Bharat Series registration formats.

    Returns:
        (is_valid, format_type, components_dict)
    """
    # Check Standard Indian
    match_std = STANDARD_INDIAN_PLATE_REGEX.match(plate)
    if match_std:
        state, rto, series, number = match_std.groups()
        is_known_state = state in VALID_STATE_CODES
        return True, "STANDARD_INDIAN", {
            "state_code": state,
            "rto_code": rto,
            "series": series,
            "number": number,
            "known_state": is_known_state
        }

    # Check Bharat Series
    match_bh = BHARAT_SERIES_REGEX.match(plate)
    if match_bh:
        year, bh, number, series = match_bh.groups()
        return True, "BHARAT_SERIES", {
            "year": year,
            "bh": bh,
            "number": number,
            "series": series
        }

    return False, None, None


def clean_and_validate_plate(
    raw_text: str,
    ocr_confidence: float = 1.0,
    confidence_threshold: float = 0.50
) -> Dict[str, Any]:
    """
    Process raw OCR output into cleaned, corrected, and validated registration number.

    Args:
        raw_text: Unprocessed character output from EasyOCR.
        ocr_confidence: Float confidence score (0.0 to 1.0) reported by EasyOCR.
        confidence_threshold: Minimum threshold below which manual review is recommended.

    Returns:
        Structured evaluation dictionary containing raw, cleaned, corrected text,
        validation status, confidence flags, and parsed plate components.
    """
    cleaned = clean_raw_text(raw_text)
    corrected = correct_ocr_ambiguities(cleaned)

    # First attempt validation on corrected plate; fallback to cleaned
    is_valid, fmt_type, components = validate_plate_format(corrected)
    best_text = corrected

    if not is_valid:
        is_valid_clean, fmt_clean, comp_clean = validate_plate_format(cleaned)
        if is_valid_clean:
            is_valid = True
            fmt_type = fmt_clean
            components = comp_clean
            best_text = cleaned

    low_confidence = ocr_confidence < confidence_threshold
    manual_review_needed = (not is_valid) or low_confidence

    if is_valid and not low_confidence:
        status_msg = "Registration number recognized and successfully validated."
    elif is_valid and low_confidence:
        status_msg = "Format valid, but low OCR confidence detected. Officer verification advised."
    else:
        status_msg = "Non-standard or incomplete plate format detected. Manual correction required."

    return {
        "raw_text": raw_text,
        "cleaned_text": cleaned,
        "corrected_text": corrected,
        "final_registration_number": best_text,
        "is_valid_format": is_valid,
        "format_type": fmt_type,
        "components": components,
        "ocr_confidence": round(float(ocr_confidence), 4),
        "low_confidence_warning": low_confidence,
        "manual_review_needed": manual_review_needed,
        "status_message": status_msg
    }
