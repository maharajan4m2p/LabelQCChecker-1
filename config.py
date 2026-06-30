"""
=========================================================
Label QC Checker Pro
Configuration File
Version 4.0
=========================================================
"""

import os

# ---------------------------------------------------------
# Project Paths
# ---------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
REPORT_FOLDER = os.path.join(BASE_DIR, "reports")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORT_FOLDER, exist_ok=True)

# ---------------------------------------------------------
# OCR Settings
# ---------------------------------------------------------

OCR_LANGUAGE = ["en"]

OCR_GPU = False

OCR_WIDTH = 2200

OCR_HEIGHT = 2200

OCR_PSM = 6

OCR_OEM = 3

# ---------------------------------------------------------
# Image Processing
# ---------------------------------------------------------

RESIZE_WIDTH = 2200

CLAHE_CLIP = 2.5

CLAHE_GRID = (8, 8)

BLUR_KERNEL = (3, 3)

THRESH_BLOCKSIZE = 31

THRESH_C = 15

# ---------------------------------------------------------
# Similarity Thresholds
# ---------------------------------------------------------

WORD_MATCH = 95

WORD_MODIFIED = 75

FIELD_MATCH = 90

LOGO_MATCH = 90

BARCODE_MATCH = True

OVERALL_PASS = 90

# ---------------------------------------------------------
# Highlight Colors (BGR)
# ---------------------------------------------------------

GREEN = (0, 255, 0)

RED = (0, 0, 255)

ORANGE = (0, 165, 255)

BLUE = (255, 0, 0)

BLACK = (0, 0, 0)

WHITE = (255, 255, 255)

# ---------------------------------------------------------
# Supported Image Types
# ---------------------------------------------------------

ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "bmp",
    "tif",
    "tiff",
    "webp"
}