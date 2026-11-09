"""
app/services/ocr_service.py - Optical Character Recognition (EasyOCR) Engine
=============================================================================
Smart ANPR Vehicle Verification System

This service handles:
1. Lazy loading & singleton management of the EasyOCR Reader using offline weights.
2. Image preprocessing (contrast stretching, bilateral filtering, sharpening) to optimize character detection.
3. Reading text from cropped number plate regions.
4. Returning bounding boxes, extracted characters, and confidence scores.
5. Integration with the plate cleaner module for Indian registration validation.
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import cv2
import numpy as np

from app.core.config import Config
from app.services.plate_cleaner import clean_and_validate_plate

logger = logging.getLogger(__name__)

# Global singleton EasyOCR reader instance
_READER_INSTANCE = None


def get_easyocr_reader():
    """
    Returns the singleton EasyOCR Reader instance.
    Loads models from the offline workspace storage directory.
    """
    global _READER_INSTANCE
    if _READER_INSTANCE is None:
        import easyocr

        model_dir = Config.EASYOCR_MODEL_DIR
        os.makedirs(model_dir, exist_ok=True)
        logger.info(f"Initializing EasyOCR reader from offline model dir: {model_dir}")

        _READER_INSTANCE = easyocr.Reader(
            ["en"],
            gpu=False,
            model_storage_directory=str(model_dir),
            verbose=False,
        )
    return _READER_INSTANCE


def preprocess_plate_image(image_input: Union[str, Path, np.ndarray]) -> np.ndarray:
    """
    Preprocess license plate crop to maximize EasyOCR character recognition accuracy:
    1. Load image (if path provided).
    2. Convert to grayscale.
    3. Resize up if height is under 70px to preserve stroke resolution.
    4. Apply bilateral filter to eliminate background speckle while preserving sharp edges.
    5. Enhance contrast using CLAHE (Contrast Limited Adaptive Histogram Equalization).
    """
    if isinstance(image_input, (str, Path)):
        img = cv2.imread(str(image_input))
        if img is None:
            raise ValueError(f"Failed to load image from path: {image_input}")
    elif isinstance(image_input, np.ndarray):
        img = image_input.copy()
    else:
        raise TypeError("image_input must be a file path string or numpy array.")

    # Convert to grayscale
    if len(img.shape) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img

    # Resize up if plate is small
    h, w = gray.shape[:2]
    if h < 80:
        scale = 80.0 / h
        new_w = int(w * scale)
        gray = cv2.resize(gray, (new_w, 80), interpolation=cv2.INTER_CUBIC)

    # Denoise while keeping edges sharp
    denoised = cv2.bilateralFilter(gray, d=9, sigmaColor=75, sigmaSpace=75)

    # Contrast enhancement
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(denoised)

    return enhanced


def read_plate_text(
    image_input: Union[str, Path, np.ndarray],
    preprocess: bool = True
) -> Dict[str, Any]:
    """
    Extract text from a cropped number plate image using EasyOCR.

    Args:
        image_input: File path or OpenCV numpy image of the cropped license plate.
        preprocess: Whether to apply grayscale contrast enhancement before OCR.

    Returns:
        Structured dictionary containing raw text, confidence, cleaned text,
        validation status, and individual text bounding boxes.
    """
    reader = get_easyocr_reader()

    if isinstance(image_input, (str, Path)):
        original_img = cv2.imread(str(image_input))
    else:
        original_img = image_input

    if original_img is None or original_img.size == 0:
        return {
            "success": False,
            "error": "Empty or invalid plate image provided for OCR.",
            "raw_text": "",
            "ocr_confidence": 0.0,
            "cleaned": clean_and_validate_plate("", 0.0),
        }

    # Execute OCR
    processed = preprocess_plate_image(original_img) if preprocess else original_img
    ocr_results = reader.readtext(processed)

    # If first pass produces nothing, fallback to raw unprocessed image
    if not ocr_results and preprocess:
        ocr_results = reader.readtext(original_img)

    if not ocr_results:
        return {
            "success": True,
            "text_found": False,
            "raw_text": "",
            "ocr_confidence": 0.0,
            "segments": [],
            "cleaned": clean_and_validate_plate("", 0.0),
            "status": "NO_TEXT_DETECTED",
        }

    # Extract detected segments [(bbox, text, confidence)]
    segments = []
    text_parts = []
    confidences = []

    # Sort segments primarily by vertical position then horizontal
    sorted_results = sorted(ocr_results, key=lambda x: (x[0][0][1] // 20, x[0][0][0]))

    for bbox, text, conf in sorted_results:
        clean_piece = text.strip()
        if clean_piece:
            text_parts.append(clean_piece)
            confidences.append(float(conf))
            # Convert bbox points to standard integer list
            points = [[int(pt[0]), int(pt[1])] for pt in bbox]
            segments.append({
                "text": clean_piece,
                "confidence": round(float(conf), 4),
                "box": points,
            })

    raw_text = " ".join(text_parts)
    avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

    # Clean and validate against Indian license plate architecture
    cleaned_result = clean_and_validate_plate(raw_text, ocr_confidence=avg_confidence)

    return {
        "success": True,
        "text_found": True,
        "raw_text": raw_text,
        "ocr_confidence": round(avg_confidence, 4),
        "segments": segments,
        "cleaned": cleaned_result,
        "status": "TEXT_EXTRACTED",
    }
