"""
=========================================================
Label QC Checker Pro
Configuration
=========================================================
"""

import os

# ---------------------------------------------------------
# Project Folders
# ---------------------------------------------------------

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

UPLOAD_FOLDER = os.path.join(
    BASE_DIR,
    "uploads"
)

OUTPUT_FOLDER = os.path.join(
    BASE_DIR,
    "output"
)

REPORT_FOLDER = os.path.join(
    BASE_DIR,
    "reports"
)

# Create folders automatically

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(REPORT_FOLDER, exist_ok=True)

# ---------------------------------------------------------
# OCR Settings
# ---------------------------------------------------------

OCR_DPI = 300

OCR_SCALE = 3

OCR_LANGUAGE = "eng"

OCR_PSM = 6

OCR_OEM = 3

# ---------------------------------------------------------
# Similarity Thresholds
# ---------------------------------------------------------

WORD_MATCH = 95

WORD_MODIFIED = 80

LOGO_MATCH_THERSHOLD=90

LOGO_PASS = 90

BARCODE_PASS = True

OVERALL_PASS = 95

# ---------------------------------------------------------
# Supported Files
# ---------------------------------------------------------

ALLOWED_EXTENSIONS = {

    "png",

    "jpg",

    "jpeg",

    "bmp",

    "tif",

    "tiff",

    "pdf"

}

# ---------------------------------------------------------
# Label Types
# ---------------------------------------------------------

LABEL_TYPES = [

    "CARE_LABEL",

    "CARTON_LABEL",

    "PRICE_TAG",

    "HANG_TAG",

    "POLYBAG_LABEL",

    "SHIPPING_LABEL"

]

# ---------------------------------------------------------
# Colors
# ---------------------------------------------------------

GREEN = (0, 255, 0)

RED = (0, 0, 255)

YELLOW = (0, 255, 255)

BLUE = (255, 0, 0)

WHITE = (255, 255, 255)

# ---------------------------------------------------------
# Report
# ---------------------------------------------------------

COMPANY_NAME = "Label QC Checker Pro"

REPORT_AUTHOR = "MAHARAJAN"

REPORT_VERSION = "2.0"