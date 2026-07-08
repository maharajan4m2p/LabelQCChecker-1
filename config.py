"""
=========================================================
Label QC Checker Pro
Configuration File
Version 6.0
=========================================================
"""

import os

# ---------------------------------------------------------
# Project Paths
# ---------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
REPORT_FOLDER = os.path.join(BASE_DIR, "reports")
TEMP_FOLDER = os.path.join(BASE_DIR, "temp")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORT_FOLDER, exist_ok=True)
os.makedirs(TEMP_FOLDER, exist_ok=True)

# ---------------------------------------------------------
# Upload Settings
# ---------------------------------------------------------

MAX_UPLOAD_SIZE = 20 * 1024 * 1024      # 20 MB

MAX_SAMPLE_FILES = 100

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
# PDF Settings
# ---------------------------------------------------------

PDF_DPI = 300

PDF_FIRST_PAGE_ONLY = True

# ---------------------------------------------------------
# Excel Settings
# ---------------------------------------------------------

EXCEL_SHEET = 0

EXCEL_HEADER = None

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
# Report Settings
# ---------------------------------------------------------

REPORT_FORMAT = "HTML"

SAVE_HIGHLIGHT_IMAGES = True

# ---------------------------------------------------------
# Supported File Types
# ---------------------------------------------------------

ALLOWED_EXTENSIONS = {

    "png",
    "jpg",
    "jpeg",
    "bmp",
    "tif",
    "tiff",
    "webp",

    "pdf",

    "xls",
    "xlsx",

    "csv"

}

# ---------------------------------------------------------
# Application Information
# ---------------------------------------------------------

APP_NAME = "Label QC Checker Pro"

APP_VERSION = "6.0"

AUTHOR = "Maharajan"

DESCRIPTION = (
    "OCR-based Label Quality Checker supporting "
    "Images, PDF, Excel and CSV files."
)