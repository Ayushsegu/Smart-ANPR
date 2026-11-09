# Smart ANPR-Based Vehicle Document Verification and Digital Challan System for Traffic Enforcement

A comprehensive smart policing solution designed to streamline roadside traffic enforcement. The system detects vehicle number plates using **YOLOv8**, extracts vehicle registration characters using **EasyOCR**, verifies compliance (Registration Certificate, Insurance, Pollution Under Control (PUC), and Road Tax) against an SQLite database, and enables traffic officers to issue instant digital challans with downloadable QR-coded PDF receipts.

---

## 📌 Project Overview

Traffic law enforcement often relies on manual inspections or fragmented systems, causing traffic delays and human errors. This project provides a unified, end-to-end digital dashboard for traffic enforcement officers:

1. **Automatic Number Plate Recognition (ANPR):** Upload or capture a vehicle image to locate the license plate using a YOLOv8 deep learning model.
2. **Optical Character Recognition (OCR):** Accurately parse the alphanumeric registration plate number using EasyOCR and regex cleansing.
3. **Instant Document Verification:** Query an internal vehicle registry to determine status for:
   - Registration Certificate (RC)
   - Insurance Policy
   - Pollution Under Control (PUC) Certificate
   - Road Tax
4. **Colour-Coded Compliance Badges:**
   - 🟢 **Valid / Active**
   - 🟡 **Expiring Soon**
   - 🔴 **Expired / Missing**
5. **Digital Challan Issuance:** Generate traffic violation citations with standard fines, automatic violation reasons, and unique Challan IDs.
6. **QR-Coded PDF Receipts:** Automated generation of formal PDF receipts with embedded QR codes using ReportLab and Python `qrcode`.
7. **Officer Dashboard:** A modern, responsive web application built with React and Tailwind CSS.
8. **Synthetic Vehicle Dataset:** Pre-populated with realistic synthetic vehicle records for educational and demonstration purposes.

---

## 🛠️ Technology Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Frontend** | React.js (Vite) | Modern, fast, and modular user interface |
| **Styling** | Tailwind CSS | Responsive and clean traffic enforcement officer UI |
| **Backend** | Python Flask | REST API service, business logic, and routing |
| **Database** | SQLite | Lightweight, relational local database for vehicles and challans |
| **Object Detection** | YOLOv8 (Ultralytics) | High-speed license plate localization |
| **Text Recognition** | EasyOCR | Deep-learning-based OCR for alphanumeric text parsing |
| **PDF Generation** | ReportLab | Generation of digital traffic challan receipts |
| **QR Code** | `qrcode` (Python) | Generation of verifiable QR codes embedded in PDF receipts |

---

## 🏛️ System Architecture

```text
+---------------------------------------------------------------------------------+
|                       Traffic Officer Web Dashboard (React + Tailwind)           |
|   - Plate Search Bar      - Image Upload / ANPR      - Violation Selector       |
|   - Document Cards        - Challan History Table    - PDF Download & View      |
+----------------------------------------+----------------------------------------+
                                         | HTTP / JSON REST APIs
                                         v
+---------------------------------------------------------------------------------+
|                               Backend Service (Flask)                            |
|                                                                                 |
|   [ ANPR & OCR Module ]          [ Verification Engine ]    [ Challan Service ] |
|   - YOLOv8 plate detector        - Document status check    - Fine calculator   |
|   - Image crop & preprocessing   - Validity classifier      - ReportLab PDF gen |
|   - EasyOCR character reader       (Valid/Expired/Missing)  - QR code generator |
+----------------------------------------+----------------------------------------+
                                         | SQL Queries
                                         v
+---------------------------------------------------------------------------------+
|                            SQLite Database (traffic_system.db)                  |
|   - vehicles (plate, make, model, owner_name, contact)                          |
|   - vehicle_documents (rc_status, insurance_expiry, puc_expiry, tax_expiry)     |
|   - challans (challan_id, plate, violation, fine_amount, date, status, pdf_url)|
+----------------------------------------+----------------------------------------+
```

---

## 📂 Project Structure Overview

```text
ANPR/
├── backend/
│   ├── app/
│   │   ├── api/             # Flask REST API route blueprints
│   │   ├── core/            # Configs, constants, and utilities
│   │   ├── models/          # Database models & database connection
│   │   ├── services/        # Business logic: ANPR, OCR, Document Verifier, PDF/QR
│   │   └── static/          # Generated PDFs and sample test images
│   ├── data/                # SQLite database and seed scripts
│   ├── weights/             # YOLOv8 license plate weights (.pt)
│   ├── app.py               # Flask application entry point
│   ├── requirements.txt     # Python backend dependencies
│   └── .env.example         # Example environment variables
│
├── frontend/
│   ├── public/              # Static assets & icons
│   ├── src/
│   │   ├── assets/          # Images, logos, and styling assets
│   │   ├── components/      # Reusable UI components (Badges, Cards, Modals)
│   │   ├── pages/           # Dashboard, Search, and Reports views
│   │   ├── services/        # Axios API clients
│   │   ├── App.jsx          # Root component
│   │   └── main.jsx         # React application entry point
│   ├── package.json         # Node.js dependencies & scripts
│   ├── tailwind.config.js   # Tailwind CSS configuration
│   └── vite.config.js       # Vite build configuration
│
├── README.md                # Project documentation (this file)
└── DEVELOPMENT_PLAN.md      # Phased development roadmap & progress tracker
```

---

## 🔒 Privacy & Synthetic Data Compliance

In accordance with data privacy guidelines and educational standards:
- **No real-world personal identification information (PII)** or confidential government VAHAN/Parivahan data is stored or accessed.
- All vehicle numbers, owner identities, phone numbers, and addresses are synthetically generated for academic testing and demonstration.
