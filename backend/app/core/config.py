import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Base directory for the backend application
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
STATIC_DIR = BASE_DIR / "app" / "static"
WEIGHTS_DIR = BASE_DIR / "weights"

# Ensure Ultralytics writes configuration to a writable workspace location
os.environ.setdefault("YOLO_CONFIG_DIR", str(DATA_DIR / ".ultralytics"))

class Config:
    BASE_DIR = BASE_DIR
    DATA_DIR = DATA_DIR
    STATIC_DIR = STATIC_DIR
    WEIGHTS_DIR = WEIGHTS_DIR

    DATABASE_PATH = os.getenv("DATABASE_PATH", str(DATA_DIR / "anpr.db"))
    SECRET_KEY = os.getenv("SECRET_KEY", "traffic-enforcement-secret-key-2026")
    PORT = int(os.getenv("PORT", 5001))
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")

    # ANPR & OCR Settings
    YOLO_WEIGHTS_PATH = os.getenv(
        "YOLO_WEIGHTS_PATH",
        str(WEIGHTS_DIR / "license_plate_detector.pt")
    )
    EASYOCR_MODEL_DIR = os.getenv(
        "EASYOCR_MODEL_DIR",
        str(WEIGHTS_DIR / "easyocr")
    )

    # Static Uploads & Crops
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", str(STATIC_DIR / "uploads"))
    CROPS_DIR = os.getenv("CROPS_DIR", str(STATIC_DIR / "crops"))
    SAMPLES_DIR = os.getenv("SAMPLES_DIR", str(STATIC_DIR / "samples"))
    CHALLANS_DIR = os.getenv("CHALLANS_DIR", str(STATIC_DIR / "challans"))
    PDF_OUTPUT_DIR = os.getenv("PDF_OUTPUT_DIR", str(STATIC_DIR / "challans" / "pdf"))
    QR_OUTPUT_DIR = os.getenv("QR_OUTPUT_DIR", str(STATIC_DIR / "challans" / "qr"))
    BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:5001")

    # Upload constraints
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
