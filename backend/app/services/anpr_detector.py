"""
app/services/anpr_detector.py - ANPR License Plate Detection & Cropping Engine
==============================================================================
Smart ANPR Vehicle Verification System

This service implements:
1. Configurable YOLOv8 license plate detector model loading.
2. Graceful fallback to classical computer vision contour localization when
   weights are pending user provision.
3. Image format and integrity validation.
4. Bounding box localization, padding, and plate cropping.
5. Saving cropped plate images to static storage for UI presentation.
6. Multi-plate handling and confidence reporting.
"""

import logging
import os
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import cv2
import numpy as np
from PIL import Image

from app.core.config import Config

logger = logging.getLogger(__name__)

# Allowed file extensions
ALLOWED_EXTENSIONS = Config.ALLOWED_EXTENSIONS
MAX_IMAGE_SIZE_BYTES = Config.MAX_CONTENT_LENGTH


class LicensePlateDetector:
    """
    Modular detector supporting both deep learning (YOLOv8) and classical
    computer vision (aspect ratio contour analysis) plate localization.
    """

    def __init__(self, weights_path: Optional[str | Path] = None):
        self.weights_path = Path(weights_path or Config.YOLO_WEIGHTS_PATH)
        self.yolo_model = None
        self.weights_available = False
        self._load_model()

    def _load_model(self) -> None:
        """Attempt to load trained YOLOv8 weights from the configured path."""
        if self.weights_path.exists() and self.weights_path.stat().st_size > 1024 * 100:
            try:
                from ultralytics import YOLO

                logger.info(f"Loading custom YOLOv8 license plate model from: {self.weights_path}")
                self.yolo_model = YOLO(str(self.weights_path))
                self.weights_available = True
                logger.info("YOLOv8 license plate model loaded successfully.")
            except Exception as e:
                logger.warning(f"Failed to load YOLO weights ({self.weights_path}): {e}")
                self.yolo_model = None
                self.weights_available = False
        else:
            logger.info(
                f"No custom weights found at {self.weights_path}. "
                "Detector will use computer vision contour localization until trained weights are supplied."
            )
            self.yolo_model = None
            self.weights_available = False

    def is_yolo_active(self) -> bool:
        """Returns True if a neural YOLO model is actively loaded."""
        return self.yolo_model is not None and self.weights_available

    def detect_plates_yolo(
        self,
        image_bgr: np.ndarray,
        confidence_threshold: float = 0.25
    ) -> List[Dict[str, Any]]:
        """Run deep learning inference using loaded YOLOv8 weights."""
        if not self.is_yolo_active():
            return []

        results = self.yolo_model.predict(
            source=image_bgr,
            conf=confidence_threshold,
            verbose=False
        )

        detections = []
        for r in results:
            boxes = r.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                conf = float(box.conf[0].cpu().numpy())
                cls_id = int(box.cls[0].cpu().numpy())
                cls_name = r.names.get(cls_id, "license_plate")

                detections.append({
                    "box": [int(x1), int(y1), int(x2), int(y2)],
                    "confidence": round(conf, 4),
                    "class_name": cls_name,
                    "method": "yolov8_neural",
                })

        # Sort by confidence descending
        return sorted(detections, key=lambda d: d["confidence"], reverse=True)

    def detect_plates_cv(
        self,
        image_bgr: np.ndarray,
        min_aspect_ratio: float = 2.0,
        max_aspect_ratio: float = 5.8
    ) -> List[Dict[str, Any]]:
        """
        Classical Computer Vision fallback plate localization:
        Identifies high-contrast rectangular contours matching Indian/global
        license plate aspect ratios (typically 2.2:1 to 5.2:1).
        """
        h_img, w_img = image_bgr.shape[:2]
        img_area = h_img * w_img

        # Convert to grayscale
        gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)

        # Bilateral filter to reduce noise while keeping edges sharp
        filtered = cv2.bilateralFilter(gray, 11, 17, 17)

        # Edge detection
        edged = cv2.Canny(filtered, 30, 200)

        # Morphological closing to connect plate borders
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (17, 3))
        closed = cv2.morphologyEx(edged, cv2.MORPH_CLOSE, kernel)

        # Find contours
        contours, _ = cv2.findContours(closed.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        candidates = []
        for c in contours:
            x, y, w, h = cv2.boundingRect(c)
            if h == 0 or w == 0:
                continue

            aspect_ratio = float(w) / float(h)
            area = w * h
            area_ratio = float(area) / float(img_area)
            width_ratio = float(w) / float(w_img)
            y_center = y + (h / 2)

            # Valid license plate proportions:
            # 1. Aspect ratio between 2.2 and 5.5
            # 2. Area between 0.5% and 15% of image
            # 3. Width between 15% and 60% of image width (avoids entire bumper/windshield)
            # 4. Positioned in the lower two-thirds of vehicle view (y_center > 0.3 * h_img)
            if (
                min_aspect_ratio <= aspect_ratio <= max_aspect_ratio
                and 0.005 <= area_ratio <= 0.15
                and 0.15 <= width_ratio <= 0.60
                and y_center >= 0.30 * h_img
            ):
                rect_area = w * h
                c_area = cv2.contourArea(c)
                solidity = c_area / rect_area if rect_area > 0 else 0

                # Score confidence based on ideal plate aspect ratio (~4.0) and vertical position
                aspect_score = 1.0 - min(1.0, abs(aspect_ratio - 4.0) / 4.0)
                position_score = min(1.0, y_center / h_img)
                confidence = min(0.98, max(0.60, 0.50 + 0.30 * aspect_score + 0.20 * position_score))

                candidates.append({
                    "box": [x, y, x + w, y + h],
                    "confidence": round(confidence, 4),
                    "class_name": "license_plate",
                    "method": "cv_contour_fallback",
                })

        return sorted(candidates, key=lambda d: d["confidence"], reverse=True)

    def detect_plates(
        self,
        image_bgr: np.ndarray,
        confidence_threshold: float = 0.25
    ) -> Tuple[List[Dict[str, Any]], str]:
        """
        Locate license plates using neural YOLOv8 if available,
        or classical computer vision fallback.
        """
        if self.is_yolo_active():
            detections = self.detect_plates_yolo(image_bgr, confidence_threshold)
            if detections:
                return detections, "yolov8"

        # If YOLO is unavailable or detected nothing, attempt CV fallback
        cv_detections = self.detect_plates_cv(image_bgr)
        return cv_detections, "cv_contour"


# Global detector singleton
_DETECTOR_INSTANCE: Optional[LicensePlateDetector] = None


def get_detector() -> LicensePlateDetector:
    """Returns the singleton LicensePlateDetector instance."""
    global _DETECTOR_INSTANCE
    if _DETECTOR_INSTANCE is None:
        _DETECTOR_INSTANCE = LicensePlateDetector()
    return _DETECTOR_INSTANCE


def validate_image_file(
    file_bytes: bytes,
    filename: str
) -> Tuple[bool, Optional[str], Optional[np.ndarray]]:
    """
    Validate uploaded image:
    1. Extension whitelist check (.png, .jpg, .jpeg, .webp).
    2. File size limit (16MB).
    3. Structural image integrity via OpenCV decoding.
    """
    if len(file_bytes) > MAX_IMAGE_SIZE_BYTES:
        return False, f"File size exceeds maximum permitted limit ({MAX_IMAGE_SIZE_BYTES // (1024 * 1024)}MB).", None

    ext = Path(filename).suffix.lstrip(".").lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"Unsupported file extension '.{ext}'. Allowed formats: {sorted(list(ALLOWED_EXTENSIONS))}", None

    # Decode image from memory bytes
    np_arr = np.frombuffer(file_bytes, np.uint8)
    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    if image is None or image.size == 0:
        return False, "Failed to decode image. File appears corrupt or invalid.", None

    return True, None, image


def crop_plate(
    image_bgr: np.ndarray,
    box: List[int],
    padding_pct: float = 0.08
) -> Tuple[np.ndarray, List[int]]:
    """
    Crop plate from vehicle image with protective edge padding.
    """
    h_img, w_img = image_bgr.shape[:2]
    x1, y1, x2, y2 = box

    w = x2 - x1
    h = y2 - y1

    pad_w = max(14, int(w * padding_pct))
    pad_h = max(8, int(h * padding_pct))

    # Pad with boundary clamping
    x1_pad = max(0, x1 - pad_w)
    y1_pad = max(0, y1 - pad_h)
    x2_pad = min(w_img, x2 + pad_w)
    y2_pad = min(h_img, y2 + pad_h)

    crop = image_bgr[y1_pad:y2_pad, x1_pad:x2_pad]
    return crop, [x1_pad, y1_pad, x2_pad, y2_pad]


def process_vehicle_image(
    image_input: Union[np.ndarray, str, Path],
    save_crops: bool = True
) -> Dict[str, Any]:
    """
    Full plate detection, cropping, and static storage pipeline.
    Accepts either an existing BGR numpy image or a file path string/Path.
    """
    if isinstance(image_input, (str, Path)):
        image_bgr = cv2.imread(str(image_input))
        if image_bgr is None:
            return {
                "success": False,
                "plate_detected": False,
                "detection_method": "file_error",
                "weights_available": False,
                "message": f"Failed to load image file from {image_input}",
                "detections_count": 0,
                "detections": [],
                "primary_crop": None,
            }
    else:
        image_bgr = image_input

    detector = get_detector()
    detections, method = detector.detect_plates(image_bgr)

    if not detections:
        return {
            "success": False,
            "plate_detected": False,
            "detection_method": method,
            "weights_available": detector.weights_available,
            "message": "No license plate detected in uploaded vehicle image.",
            "detections_count": 0,
            "detections": [],
            "primary_crop": None,
        }

    primary = detections[0]
    box = primary["box"]
    conf = primary["confidence"]

    crop, padded_box = crop_plate(image_bgr, box)

    crop_filename = None
    crop_path = None
    crop_url = None

    if save_crops and crop.size > 0:
        crops_dir = Path(Config.CROPS_DIR)
        crops_dir.mkdir(parents=True, exist_ok=True)

        crop_filename = f"plate_{uuid.uuid4().hex[:12]}.jpg"
        crop_path = str(crops_dir / crop_filename)
        cv2.imwrite(crop_path, crop)
        crop_url = f"/static/crops/{crop_filename}"

    return {
        "success": True,
        "plate_detected": True,
        "detection_method": method,
        "weights_available": detector.weights_available,
        "detections_count": len(detections),
        "detections": detections,
        "primary": {
            "box": box,
            "padded_box": padded_box,
            "confidence": conf,
            "crop_path": crop_path,
            "crop_url": crop_url,
            "crop_image": crop,
        }
    }
