"""
app/services/helmet_detector.py - Two-Wheeler Helmet Detection & Safety Audit Engine
=====================================================================================
Smart ANPR Vehicle Verification System

This service implements:
1. Real Ultralytics YOLOv8 rider/motorcycle localization.
2. Head region extraction and Computer Vision contour/color analysis.
3. Support for specialized neural helmet weights (e.g. helmet_detector.pt) with
   graceful fallback to rider head CV analysis when fine-tuned weights are pending.
4. Saving evidence crops to static storage for review and manual correction.
"""

import os
import uuid
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import cv2
import numpy as np
from PIL import Image

from app.core.config import Config

logger = logging.getLogger(__name__)


class HelmetDetector:
    """
    Rider safety & helmet detection engine.
    """

    def __init__(self, weights_path: Optional[str | Path] = None):
        self.weights_dir = Config.WEIGHTS_DIR
        self.crops_dir = Path(Config.CROPS_DIR)
        self.crops_dir.mkdir(parents=True, exist_ok=True)

        # Check for dedicated helmet model first, then fallback to general COCO yolov8n
        dedicated_path = self.weights_dir / "helmet_detector.pt"
        coco_path = self.weights_dir / "yolov8n.pt"

        self.model = None
        self.is_dedicated_model = False
        self.weights_status = "NOT_LOADED"

        if dedicated_path.exists() and dedicated_path.stat().st_size > 100 * 1024:
            try:
                from ultralytics import YOLO
                self.model = YOLO(str(dedicated_path))
                self.is_dedicated_model = True
                self.weights_status = "DEDICATED_HELMET_MODEL"
                logger.info("Loaded dedicated helmet detection model: %s", dedicated_path)
            except Exception as e:
                logger.warning("Could not load dedicated helmet model: %s", e)

        if not self.model and coco_path.exists() and coco_path.stat().st_size > 100 * 1024:
            try:
                from ultralytics import YOLO
                self.model = YOLO(str(coco_path))
                self.is_dedicated_model = False
                self.weights_status = "COCO_RIDER_LOCALIZATION"
                logger.info("Loaded standard YOLOv8n for rider & motorcycle localization.")
            except Exception as e:
                logger.warning("Could not load YOLOv8n: %s", e)

    def detect_helmet(self, image_input: bytes | str | np.ndarray) -> Dict[str, Any]:
        """
        Analyze an image for rider helmet compliance.
        """
        # Load image into numpy array (BGR)
        if isinstance(image_input, bytes):
            nparr = np.frombuffer(image_input, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        elif isinstance(image_input, (str, Path)):
            img = cv2.imread(str(image_input))
        elif isinstance(image_input, np.ndarray):
            img = image_input.copy()
        else:
            raise ValueError("Unsupported image input type")

        if img is None or img.size == 0:
            return {
                "success": False,
                "error": "Failed to decode input image.",
            }

        h, w = img.shape[:2]
        crop_filename = f"helmet_evidence_{uuid.uuid4().hex[:12]}.jpg"
        crop_path = self.crops_dir / crop_filename
        evidence_url = f"/static/crops/{crop_filename}"

        # 1. Run YOLO inference if model available
        rider_box = None
        motorcycle_detected = False
        person_detected = False

        if self.model:
            try:
                results = self.model(img, verbose=False)
                for r in results:
                    boxes = r.boxes
                    for box in boxes:
                        cls_id = int(box.cls[0].item())
                        cls_name = r.names.get(cls_id, "").lower()

                        if "motorcycle" in cls_name or "bike" in cls_name:
                            motorcycle_detected = True

                        if "person" in cls_name or "rider" in cls_name:
                            person_detected = True
                            coords = box.xyxy[0].tolist()
                            rider_box = [int(coords[0]), int(coords[1]), int(coords[2]), int(coords[3])]

                        # Dedicated helmet classes
                        if "helmet" in cls_name:
                            coords = box.xyxy[0].tolist()
                            conf = float(box.conf[0].item())
                            bbox = [int(coords[0]), int(coords[1]), int(coords[2]), int(coords[3])]
                            cv2.imwrite(str(crop_path), img)
                            return {
                                "success": True,
                                "helmet_detected": True,
                                "status": "HELMET_COMPLIANT",
                                "confidence": round(conf, 4),
                                "bounding_box": bbox,
                                "evidence_url": evidence_url,
                                "is_dedicated_model": True,
                                "weights_status": self.weights_status,
                                "details": "Helmet verified by neural detector.",
                            }
            except Exception as e:
                logger.error("YOLO inference failed in helmet detector: %s", e)

        # 2. If no dedicated helmet box was directly identified, analyze the head region
        # If rider box found, crop top 30% of rider box as head region
        if rider_box:
            rx1, ry1, rx2, ry2 = rider_box
            head_h = max(int((ry2 - ry1) * 0.35), 20)
            head_bbox = [rx1, ry1, rx2, min(ry1 + head_h, h)]
        else:
            # Fallback to upper center crop
            head_bbox = [int(w * 0.25), int(h * 0.1), int(w * 0.75), int(h * 0.5)]

        x1, y1, x2, y2 = head_bbox
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w, x2), min(h, y2)
        head_crop = img[y1:y2, x1:x2]

        if head_crop.size == 0:
            head_crop = img

        # Save evidence crop with annotation box
        annotated = img.copy()
        cv2.rectangle(annotated, (x1, y1), (x2, y2), (220, 69, 69), 3)
        cv2.imwrite(str(crop_path), annotated)

        # 3. CV Contour & Curvature Analysis for Helmet vs Hair
        gray_head = cv2.cvtColor(head_crop, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray_head, (5, 5), 0)
        edges = cv2.Canny(blurred, 40, 120)

        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        has_smooth_dome = False
        confidence = 0.84

        for c in contours:
            area = cv2.contourArea(c)
            if area > 150:
                perimeter = cv2.arcLength(c, True)
                if perimeter > 0:
                    circularity = 4 * np.pi * (area / (perimeter * perimeter))
                    if circularity > 0.45:  # Helmets exhibit distinct curved dome circularity
                        has_smooth_dome = True
                        confidence = min(0.92, 0.75 + circularity * 0.2)
                        break

        # Result packaging
        is_compliant = has_smooth_dome
        status = "HELMET_COMPLIANT" if is_compliant else "NO_HELMET_VIOLATION"

        return {
            "success": True,
            "helmet_detected": is_compliant,
            "status": status,
            "confidence": round(confidence, 4),
            "bounding_box": [x1, y1, x2, y2],
            "evidence_url": evidence_url,
            "rider_detected": person_detected,
            "motorcycle_detected": motorcycle_detected,
            "is_dedicated_model": self.is_dedicated_model,
            "weights_status": self.weights_status,
            "model_notice": (
                "Dedicated neural helmet model active." if self.is_dedicated_model
                else "Rider CV geometry & head curvature analysis active. To upgrade, place helmet_detector.pt into backend/weights/."
            ),
            "manual_review_needed": not self.is_dedicated_model,
        }
