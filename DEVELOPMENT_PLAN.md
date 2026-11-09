# 📋 Development Plan & Roadmap

## Project: Smart ANPR-Based Vehicle Document Verification and Digital Challan System for Traffic Enforcement

This document outlines the step-by-step roadmap to build the project from scratch. To ensure high quality, maintainability, and ease of learning, we proceed **one module at a time**. Each phase concludes with explicit testing and verification before advancing to the next.

---

## 📌 Phase Summary Matrix

| Phase | Module Name | Deliverable | Verification Check |
| :---: | :--- | :--- | :--- |
| **0** | **Project Inception & Architecture** | Scaffolding blueprint, `README.md`, `DEVELOPMENT_PLAN.md` | Workspace reviewed, documentation verified |
| **1** | **Environment & Project Scaffolding** | Virtual environment, Flask server skeleton, React + Vite + Tailwind setup | Backend ping test (`200 OK`), Frontend dashboard rendered |
| **2** | **Database Schema & Synthetic Dataset** | SQLite database, schema migration, synthetic vehicle seeder script | Database seeded with 15+ varied vehicle records, query test passed |
| **3** | **Backend Core API & Verification Engine** | Vehicle lookup endpoint, document validity business logic engine | Unit/API tests for valid, expiring, and expired documents |
| **4** | **ANPR & OCR Processing Pipeline** | YOLOv8 plate detector, EasyOCR extraction, license plate cleanser | Test pipeline on sample vehicle images with printed output |
| **5** | **Digital Challan & QR-PDF Engine** | Challan issuance API, ReportLab PDF receipt generator, QR code generator | Generated PDF receipt verified with scannable QR code |
| **6** | **Traffic Police Dashboard (Frontend)** | React interface with plate search, upload preview, status cards, challan modal | Interactive UI tested with mock and live backend endpoints |
| **7** | **End-to-End Integration & Final Polish** | Integrated full flow, error handling, demo dataset guide for viva | Complete demonstration from car photo to issued PDF challan |

---

## 🚀 Detailed Phase Breakdown

### Phase 0: Project Inception & Architecture (Completed)
- [x] Inspect the workspace.
- [x] Establish architecture, data flow, and directory structure.
- [x] Write comprehensive `README.md`.
- [x] Formulate `DEVELOPMENT_PLAN.md`.
- [x] Outline software dependencies.
- [x] Receive user sign-off to begin Phase 1.

---

### Phase 1: Environment Setup & Project Scaffolding (Completed)
*Goal: Create the directory tree, initialize Python virtual environment, install base libraries, set up Vite + React + Tailwind, build dashboard layout, and establish backend-to-frontend communication.*
- **Backend Tasks:**
  - [x] Create directory structure (`backend/app`, `backend/data`, `backend/weights`, etc.).
  - [x] Set up a clean Python virtual environment (`.venv`).
  - [x] Create `requirements.txt` with foundational libraries (Flask, Flask-CORS, python-dotenv).
  - [x] Create minimal `app.py` with a health-check endpoint (`GET /api/health`).
- **Frontend Tasks:**
  - [x] Initialize React application using Vite.
  - [x] Install and configure Tailwind CSS (`tailwind.config.js`, `postcss.config.js`).
  - [x] Build traffic police dashboard layout with sidebar, navigation, and connection status.
  - [x] Connect to backend `/api/health` to verify live communication.
- **Verification:**
  - [x] Backend running on port 5001 returning `{"status": "healthy", ...}`.
  - [x] Frontend running on Vite displaying police dashboard and live backend status indicator.

---

### Phase 2: Database Schema & Synthetic Dataset Generation (Completed)
*Goal: Design relational SQLite database, implement schema with foreign keys and cascading rules, seed realistic synthetic Indian vehicle dataset, and connect Flask backend endpoints.*
- **Database Design & Schema:**
  - [x] Create `anpr.db` SQLite database with `PRAGMA foreign_keys = ON;`.
  - [x] Table 1: `vehicles` (id, registration_number UNIQUE, owner_name, vehicle_type, vehicle_model, registration_date, created_at).
  - [x] Table 2: `documents` (id, vehicle_id FK ON DELETE CASCADE, document_type, document_number, issue_date, expiry_date, status).
  - [x] Table 3: `challans` (id, challan_number UNIQUE, vehicle_id FK ON DELETE CASCADE, violation_type, fine_amount, challan_date, payment_status, description).
  - [x] Create database indexes for fast query lookup by registration plate and vehicle ID.
- **Synthetic Dataset Generation:**
  - [x] Seed 18 realistic, completely fictional Indian vehicles (8 Cars, 5 Motorcycles, 5 Commercial vehicles).
  - [x] Seed all 4 required document types per vehicle (RC, INSURANCE, PUC, ROAD_TAX = 72 documents total).
  - [x] Diverse document validity conditions: Valid, Expiring Soon, Expired.
  - [x] Seed 10 realistic digital challan citations linked to vehicles.
- **Database Modules & Scripts:**
  - [x] `backend/database.py` - Core connection manager, DDL, and parameterized query helpers.
  - [x] `backend/init_db.py` - Standalone idempotent table creator and CLI tool.
  - [x] `backend/seed_data.py` - Synthetic dataset generator with parameterized inserts.
  - [x] `backend/app/models/database.py` - Interface exposed to Flask application.
- **Backend API Integration:**
  - [x] `GET /api/vehicles` - List all vehicles.
  - [x] `GET /api/vehicles/<registration_number>` - Single vehicle lookup by plate.
  - [x] `GET /api/vehicles/<registration_number>/documents` - Fetch all 4 documents for vehicle.
  - [x] `GET /api/challans` - List all challans (with optional query filter).
- **Testing & Verification:**
  - [x] `backend/test_database.py` - 13/13 unit and integration tests passing.
  - [x] `backend/verify_endpoints.py` - Verified JSON responses for all endpoints.

---

### Phase 3: Backend Core API & Verification Engine (Completed)
*Goal: Implement modular document validity engine (RC, Insurance, PUC, Road Tax), automated violation detection, configurable fine schedule, and Flask verification endpoints.*
- **Document Verification Engine:**
  - [x] Date arithmetic rules using Python `datetime` (VALID: >30 days, EXPIRING_SOON: 0..30 days, EXPIRED: <0 days, MISSING: record absent).
  - [x] Service module `backend/app/services/document_verifier.py`.
- **Vehicle Compliance & Violation Detection:**
  - [x] Comprehensive 4-document inspection in `backend/app/services/vehicle_verifier.py`.
  - [x] Aggregated metrics (valid_count, expiring_count, expired_count, missing_count).
  - [x] Compliance verdict determination (`COMPLIANT`, `ATTENTION_REQUIRED`, `NON_COMPLIANT`).
  - [x] Automated violation detection for expired and missing mandatory documents.
- **Fine Calculation Module:**
  - [x] Separate penalty engine `backend/app/services/fine_calculator.py`.
  - [x] Configurable illustrative fine schedule `backend/app/core/fines_config.py`.
  - [x] Automatic deduplication of duplicate violations.
  - [x] Detailed itemized fine breakdowns with statutory citations & academic disclaimer.
- **Flask API Endpoints:**
  - [x] `GET /api/vehicles/<registration_number>/verify`
  - [x] `POST /api/vehicles/verify`
  - [x] `POST /api/challans/calculate`
  - [x] Regression testing: `GET /api/health` and Phase 2 endpoints remain intact.
- **Testing & Verification:**
  - [x] `backend/test_verification_engine.py`: 16/16 tests passing.
  - [x] `backend/test_database.py`: 13/13 tests passing.

---

### Phase 4: ANPR & OCR Processing Pipeline (Completed)
*Goal: Implement license plate localization (YOLOv8 + CV fallback), bounding box extraction, plate cropping, EasyOCR text recognition, Indian plate cleaning regex, and the `/api/anpr/upload` endpoint.*
- **YOLOv8 & Detection Setup:**
  - [x] Installed `ultralytics`, `easyocr`, `torch`, `torchvision`, `opencv-python-headless`.
  - [x] Configurable YOLO weights path in `Config.YOLO_WEIGHTS_PATH`.
  - [x] Modular ANPR detector `backend/app/services/anpr_detector.py` with dual-mode support (Neural YOLOv8 + Classical CV contour fallback).
  - [x] Created `backend/weights/README.md` documenting model acquisition and integration.
- **Image Processing & Cropping:**
  - [x] Image validation (formats, max 16MB, corruption checks).
  - [x] Bounding box extraction with boundary-safe padding.
  - [x] Cropped plate persistence to `backend/app/static/crops/` with URL exposure.
  - [x] Multi-plate handling and negative detection handling.
- **EasyOCR Integration:**
  - [x] Local offline model storage at `backend/weights/easyocr/`.
  - [x] Image preprocessing pipeline (grayscale, CLAHE contrast enhancement, bilateral denoising).
  - [x] Character extraction service `backend/app/services/ocr_service.py`.
- **Plate Cleaning & Validation:**
  - [x] Alphanumeric text sanitizer in `backend/app/services/plate_cleaner.py`.
  - [x] HSRP 'IND' prefix stripping.
  - [x] Positional OCR character ambiguity correction (0 vs O, 1 vs I, etc.).
  - [x] Indian registration regex validation (`^[A-Z]{2}[0-9]{1,2}[A-Z]{1,3}[0-9]{4}$` & Bharat Series).
  - [x] Audit trails retaining `raw_text`, `cleaned_text`, and `ocr_confidence`.
- **Flask API Endpoint:**
  - [x] `POST /api/anpr/upload` in `backend/app/api/anpr_routes.py`.
  - [x] Seamless auto-verification against Phase 3 database records.
  - [x] Error handling: 400 (invalid format), 413 (payload too large), 422 (no plate detected).
- **Testing & Verification:**
  - [x] Synthetic sample test image generator `backend/generate_sample_images.py`.
  - [x] `backend/test_anpr_pipeline.py`: 19/19 tests passing.
  - [x] Full regression suite (Phases 2, 3, and 4): 48/48 tests passing.

---

### Phase 5: Digital Challan & QR-PDF Engine (Completed)
*Goal: Implement automated digital citation generation, ReportLab PDF receipt compilation, scannable QR verification barcode generation, configurable fine calculation integration, demonstration payment simulation, and Flask API endpoints.*
- **Challan Database Model & Schema:**
  - [x] Migrated SQLite `challans` table with `challan_status`, `fine_breakdown_json`, `pdf_path`, `qr_path`, and payment status checks (`PENDING`, `PAID`, `FAILED`).
  - [x] Preserved all existing seeded challan records without loss.
  - [x] Database helpers in `backend/database.py`: `get_challan_by_number`, `update_challan_payment_status`, `update_challan_artifacts`, `insert_challan`.
- **Fine Calculation Integration:**
  - [x] Integrated Phase 3 fine engine `calculate_fine_breakdown`.
  - [x] Itemized violation breakdown with statutory sections and configurable demonstration penalties.
  - [x] Automatic violation deduplication preventing repeated fines for identical offenses.
- **QR Code Generation:**
  - [x] Implemented `backend/app/services/qr_generator.py` using Python `qrcode`.
  - [x] Encodes verification URL (`/api/challans/<challan_number>`) without exposing sensitive PII.
  - [x] Saves barcode to `backend/app/static/challans/qr/` with web-accessible static URLs.
- **ReportLab PDF Receipt Engine:**
  - [x] Implemented `backend/app/services/pdf_generator.py` using ReportLab Platypus.
  - [x] Official layout: Authority header, unique citation ID, formatted date/time, vehicle & owner details.
  - [x] Dynamic payment status badge (`PENDING` in red, `PAID` in green, `FAILED` in slate).
  - [x] Itemized violation particulars table with statutory sections and amounts.
  - [x] Embedded verification QR barcode with scan instructions.
  - [x] Academic demonstration prototype disclaimer banner.
  - [x] Saves PDF receipts to `backend/app/static/challans/pdf/`.
- **Challan Service Engine:**
  - [x] Implemented `backend/app/services/challan_service.py`.
  - [x] Collision-resistant citation numbering (`CH-YYYY-XXXXX`).
  - [x] Automatic vehicle compliance fallback inspection.
  - [x] Demonstration payment status transition (`PENDING` -> `PAID`, `ISSUED` -> `SETTLED`) with automatic PDF badge re-rendering.
- **Flask API Endpoints:**
  - [x] `POST /api/challans/generate` (HTTP 201 Created on success, 400 Bad Request, 404 Vehicle Not Found, 422 No Violations).
  - [x] `GET /api/challans/<challan_number>` (HTTP 200 with full details, 404 Not Found).
  - [x] `GET /api/challans/<challan_number>/pdf` (HTTP 200 application/pdf stream with on-the-fly compile fallback).
  - [x] `GET /api/challans/<challan_number>/qr` (HTTP 200 image/png stream with on-the-fly generation fallback).
  - [x] `POST /api/challans/<challan_number>/pay` (HTTP 200 demonstration payment simulation).
  - [x] Registered `challan_bp` in `backend/app/__init__.py`.
- **Testing & Verification:**
  - [x] Comprehensive test suite `backend/test_challan_engine.py`: 17/17 tests passing.
  - [x] Verified file integrity for both PDF (`%PDF-`) and QR (`\x89PNG`) formats.
  - [x] Live end-to-end demonstration script `backend/demo_challan_pipeline.py`.
  - [x] Cumulative test suite across all 4 backend phases: **65/65 tests passing**.

---

### Phase 6: Traffic Police Dashboard Integration (Completed)
*Goal: Create a modern, professional Traffic Police Surveillance Dashboard using React + Vite + Tailwind CSS, Lucide icons, and Axios central API service connected to Flask backend endpoints.*
- **Dashboard Shell & Theme:**
  - [x] Modern dark navy and blue police enforcement aesthetic (`#0B1120`, `#0F172A`, `#1E293B`, `#2563EB`).
  - [x] Responsive layout with collapsible sidebar and top status navbar.
  - [x] Real-time clock and live Flask API connectivity health ping.
  - [x] Dynamic toast notification alerts system (`components/Toast.jsx`).
  - [x] Authentic Indian HSRP license plate badge component (`components/LicensePlateBadge.jsx`).
- **Sidebar Navigation (6 Pages):**
  - [x] **Dashboard Overview**: Live KPI cards for registered vehicles, issued challans, settlement ratios, overdue documents, recent citations feed, and system telemetry (`components/DashboardOverview.jsx`).
  - [x] **ANPR Scanner**: Vehicle image drag-and-drop / file picker, clickable quick samples, YOLOv8 detection & EasyOCR extraction confidence, plate cropping, manual text correction, compliance auto-check, and one-click challan generation (`components/ANPRScanner.jsx`).
  - [x] **Vehicle Verification**: Plate search with quick demo buttons, multi-document inspection (RC, Insurance, PUC, Road Tax), expiry countdowns, overall compliance verdict badge, itemized fine breakdown, and challan trigger (`components/VehicleVerification.jsx`).
  - [x] **Document Verification**: Central document compliance browser, status filters (Valid, Expiring Soon, Expired), type filters (RC, Insurance, PUC, Road Tax), and quick vehicle jump (`components/DocumentVerification.jsx`).
  - [x] **Challan Management**: Complete electronic citations registry, search and status filters, inline demo payment settlement simulation, PDF receipt download, and QR viewer (`components/ChallanManagement.jsx`).
  - [x] **Reports & Analytics**: Real-time traffic intelligence charts: violations breakdown by type, settlement distribution, document health breakdown, fleet distribution, and revenue recovery metrics (`components/ReportsAnalytics.jsx`).
- **Central API Service & Modals:**
  - [x] Centralized Axios service `services/api.js` with error unwrapping and baseURL resolution.
  - [x] `ChallanModal.jsx`: Full citation viewer, embedded verification QR barcode, PDF download action, and demonstration payment toggle (`PAY` / `FAIL`).
  - [x] Vite dev proxy configured for both `/api` and `/static` endpoints.
  - [x] Flask backend serves built React SPA from `frontend/dist` on port 5001.
- **Testing & Verification:**
  - [x] Production build clean: `npm run build` succeeds (1658 modules transformed).
  - [x] `backend/test_frontend_integration.py`: 7/7 tests passing.
  - [x] Full cumulative regression test suite (Phases 2-6): **72/72 tests passing (100% pass rate)**.

---

### Phase 7: Complete End-to-End Integration Testing (Completed)
*Goal: Execute exhaustive 15-point verification across AI inference, database lookups, multi-document statutory rules, fine computation, digital citation issuance, PDF receipt compilation, QR verification barcodes, demonstration payments, and full-stack responsiveness.*
- [x] **Point 1: Server Architecture & Environment**: Verified SQLite database (18 vehicles, 80+ citations) and production SPA bundle.
- [x] **Point 2: Frontend-Backend API Communication**: Verified `/api/health`, `/api/vehicles`, `/api/challans`, and SPA delivery.
- [x] **Point 3: Vehicle Photograph Upload**: Verified `/api/anpr/upload` multipart file handling with high-resolution vehicle imagery.
- [x] **Point 4: YOLO / Morphological Detection**: Documented that `license_plate_detector.pt` custom weights are missing; verified automatic OpenCV contour localization fallback (91.64% confidence).
- [x] **Point 5: EasyOCR Neural Text Extraction**: Verified actual offline PyTorch deep learning models (`craft_mlt_25k.pth` 79MB and `english_g2.pth` 14MB) extracting text (`MH 12 DE 5678` at 88.55% confidence).
- [x] **Point 6: Indian Registration Number Cleaning**: Verified HSRP 'IND' strip removal, space stripping, positional character correction, and standard Indian regex validation.
- [x] **Point 7: Vehicle Database Lookup**: Verified vehicle retrieval by plate (`Priya Deshmukh`, Swift VXi, Car).
- [x] **Point 8: Document Verification**: Verified 4 mandatory documents (RC, Insurance, PUC, Road Tax) and expired PUC detection.
- [x] **Point 9: Violation Detection & Fines**: Verified penalty mapping (`EXPIRED_PUC` -> ₹10,000 fine) and duplicate violation filtering.
- [x] **Point 10: Digital Challan Generation**: Verified unique citation ID (`CH-2026-XXXXX`), initial `PENDING` payment status, and `ISSUED` challan status.
- [x] **Point 11: PDF Receipt Verification**: Verified ReportLab Platypus compilation, `%PDF-1.4` magic bytes, EOF marker, and `/api/challans/<num>/pdf` streaming.
- [x] **Point 12: QR Barcode Verification**: Verified PNG barcode generation (370x370 px, ISO/IEC 18004), `/api/challans/<num>` verification link, and zero PII exposure.
- [x] **Point 13: Demonstration Payment Updates**: Verified `PENDING` -> `PAID` (status updated to `SETTLED`) and `FAILED` simulations, with automatic PDF stamp re-compilation.
- [x] **Point 14: Error Auditing & Log Inspection**: Verified zero unhandled backend exceptions; documented PyTorch MPS warnings.
- [x] **Point 15: Responsive Design**: Verified breakpoint coverage across mobile, tablet, and desktop viewports for all 9 components.
- [x] **Test Results**: **15/15 Checkpoints PASSED (100%)** | Cumulative Test Suites: **72/72 Tests PASSED (100%)**.

---

### Feature Enhancement: Live Roadside Camera Capture (Completed)
*Goal: Add roadside field officer live camera capture using the HTML5 MediaDevices API, rear-camera prioritization, canvas snapshotting, retake workflow, and seamless integration into the existing YOLO/OCR ANPR pipeline.*
- [x] **Dual-Mode Scanner Interface**: Added segmented toggle between "Capture Live Camera" and "Upload Vehicle Image" in `components/ANPRScanner.jsx`.
- [x] **Live Camera Component**: Implemented `components/LiveCameraCapture.jsx` using `navigator.mediaDevices.getUserMedia`.
- [x] **Rear-Camera Prioritization**: Configured `facingMode: { ideal: "environment" }` with front/back camera switching on mobile and tablet devices.
- [x] **Targeting Reticle**: Added roadside alignment brackets and targeting guide overlay over the live stream.
- [x] **Photo Capture & Review**: Implemented HTML Canvas frame grabbing converting stream to high-resolution JPEG files with Retake and Confirm & Process buttons.
- [x] **Hardware Cleanup**: Verified stream tracks (`track.stop()`) are cleanly released when stopping camera, capturing photo, switching tabs, or unmounting.
- [x] **Existing Upload Preserved**: 100% preservation of drag-and-drop, file picker, and preloaded vehicle sample images.
- [x] **Testing & Verification**: Created `backend/test_camera_anpr_pipeline.py` (12/12 tests passing). Total cumulative test suite: **84/84 tests passing (100%)**.

---

### Project Status: All 7 Development & Verification Phases + Live Camera Enhancement Completed!
