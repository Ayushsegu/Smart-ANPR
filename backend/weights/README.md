# 🎯 YOLOv8 License Plate Model Weights Guide

## Overview

The generic `yolov8n.pt` model trained on the COCO dataset contains 80 general categories (e.g., cars, motorcycles, buses, people) but **does not contain a dedicated class for vehicle license plates**.

For optimal license plate bounding-box localization, this system supports specialized license-plate-trained YOLOv8 weights (e.g. `license_plate_detector.pt` or `best.pt`).

---

## 📥 Recommended Pre-trained License Plate Weights

You can obtain high-accuracy license plate weights from trusted open repositories:

1. **Roboflow Universe (Vehicle Registration Plates)**:
   - Search: `License Plate Recognition YOLOv8`
   - Direct Export: Download weights trained on Indian/Global license plate datasets (`best.pt`).
2. **Open Model Hub / GitHub**:
   - `keremberke/yolov8n-license-plate`
   - `Muhammad-Raza-Ahmad/Automatic-Number-Plate-Recognition-using-YOLOv8`
3. **Custom Fine-Tuning**:
   - You can fine-tune YOLOv8 using:
     ```python
     from ultralytics import YOLO
     model = YOLO("yolov8n.pt")
     model.train(data="license_plate_dataset.yaml", epochs=50, imgsz=640)
     ```

---

## 📂 Installation Instructions

1. Rename your trained weights file to:
   ```text
   license_plate_detector.pt
   ```
2. Place it directly into this directory:
   ```text
   backend/weights/license_plate_detector.pt
   ```
3. Alternatively, specify any custom weights path using an environment variable in `backend/.env`:
   ```bash
   YOLO_WEIGHTS_PATH=/path/to/your/custom_license_plate_model.pt
   ```

---

## 🔄 Dual Detection Engine (Neural & Classical CV Fallback)

To ensure the system operates reliably even before custom weights are supplied:
- **Neural YOLOv8 Mode**: When `backend/weights/license_plate_detector.pt` is present, the system executes real Ultralytics deep-learning bounding box inference.
- **Classical CV Fallback Mode**: If weights are missing, the system utilizes high-contrast edge contour aspect-ratio detection (standard for rectangular vehicle plates $\approx 2.5:1$ to $5.2:1$) and returns an informative notice (`weights_available: false`).

---

## 📖 EasyOCR Models

The EasyOCR CRAFT text detector (`craft_mlt_25k.pth`) and English recognition model (`english_g2.pth`) are stored in:
```text
backend/weights/easyocr/
```
These models run fully locally and offline without external network dependencies.
