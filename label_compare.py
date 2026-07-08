"""
=========================================================
Label QC Checker Pro
Main Label Comparison Engine
Version 6.1
Supports:
✓ Images
✓ PDF
✓ Excel
✓ CSV
=========================================================
"""

import os
import uuid

from config import *

from engine.pdf_processor import PDFProcessor
from engine.excel_processor import ExcelProcessor
from engine.ocr_engine import ocr_engine
from engine.logo_checker import logo_checker
from engine.barcode_checker import barcode_checker
from engine.label_detector import label_detector
from engine.constraint_detector import constraint_detector
from engine.comparison_engine import comparison_engine
from engine.image_highlighter import image_highlighter
from engine.report_generator import report_generator


# ---------------------------------------------------------
# File Type Detection
# ---------------------------------------------------------

def get_file_type(file_path):

    extension = os.path.splitext(file_path)[1].lower()

    image_extensions = [

        ".png",
        ".jpg",
        ".jpeg",
        ".bmp",
        ".tif",
        ".tiff",
        ".webp"

    ]

    if extension in image_extensions:

        return "image"

    elif extension == ".pdf":

        return "pdf"

    elif extension in [

        ".xls",
        ".xlsx",
        ".csv"

    ]:

        return "excel"

    return "unknown"


# ---------------------------------------------------------
# Prepare File
# ---------------------------------------------------------

def prepare_file(file_path):

    file_type = get_file_type(file_path)

    if file_type == "image":

        return file_path

    elif file_type == "pdf":

        pages = PDFProcessor.pdf_to_images(
            file_path,
            first_page=1,
            last_page=1
        )

        if len(pages) == 0:

            raise Exception("PDF contains no pages.")

        output_image = os.path.join(

            UPLOAD_FOLDER,

            f"{uuid.uuid4().hex}.png"

        )

        pages[0].save(output_image)

        return output_image

    elif file_type == "excel":

        return file_path

    raise Exception(

        f"Unsupported file type : {file_path}"

    )


# ---------------------------------------------------------
# Main Class
# ---------------------------------------------------------

class LabelCompare:

            
            

    def __init__(self):

        self.ocr = ocr_engine

        self.detector = label_detector

        self.constraint = constraint_detector

        self.comparison = comparison_engine

        self.logo = logo_checker

        self.barcode = barcode_checker

        self.highlight = image_highlighter

        self.report = report_generator

        os.makedirs(

            UPLOAD_FOLDER,

            exist_ok=True

        )
        # ---------------------------------------------------------
    # Compare Labels
    # ---------------------------------------------------------

    def compare(

        self,

        approval_path,

        sample_path

    ):

        result = {}

        # ---------------------------------------------------------
        # File Types
        # ---------------------------------------------------------

        approval_type = get_file_type(

            approval_path

        )

        sample_type = get_file_type(

            sample_path

        )

        result["approval_type"] = approval_type

        result["sample_type"] = sample_type

        # ---------------------------------------------------------
        # Prepare Files
        # ---------------------------------------------------------

        approval_input = prepare_file(

            approval_path

        )

        sample_input = prepare_file(

            sample_path

        )

        result["approval_input"] = approval_input

        result["sample_input"] = sample_input

        # ---------------------------------------------------------
        # OCR
        # ---------------------------------------------------------

        if approval_type == "excel":

            approval_ocr = {

                "text": ExcelProcessor.read_excel(

                    approval_path

                ),

                "words": []

            }

        else:

            approval_ocr = self.ocr.read(

                approval_input

            )

        if sample_type == "excel":

            sample_ocr = {

                "text": ExcelProcessor.read_excel(

                    sample_path

                ),

                "words": []

            }

        else:

            sample_ocr = self.ocr.read(

                sample_input

            )

        result["approval_ocr"] = approval_ocr

        result["sample_ocr"] = sample_ocr

        # ---------------------------------------------------------
        # Label Detection
        # ---------------------------------------------------------

        if approval_type == "excel":

            approval_label = None

        else:

            approval_label = self.detector.detect(

                approval_input

            )

        if sample_type == "excel":

            sample_label = None

        else:

            sample_label = self.detector.detect(

                sample_input

            )

        result["approval_label"] = approval_label

        result["sample_label"] = sample_label

        # ---------------------------------------------------------
        # Constraint Detection
        # ---------------------------------------------------------

        approval_constraints = self.constraint.get_constraints(

            approval_ocr["text"]

        )

        sample_constraints = self.constraint.get_constraints(

            sample_ocr["text"]

        )

        result["approval_constraints"] = approval_constraints

        result["sample_constraints"] = sample_constraints

        # ---------------------------------------------------------
        # Comparison
        # ---------------------------------------------------------

        comparison = self.comparison.compare(

            approval_constraints,

            sample_constraints,

            approval_ocr["words"],

            sample_ocr["words"]

        )

        result["comparison"] = comparison

        result["summary"] = comparison["summary"]
        # ---------------------------------------------------------
        # Logo Check
        # ---------------------------------------------------------

        if approval_type == "excel" or sample_type == "excel":

            logo_result = {

                "status": "Skipped",

                "similarity": 0,

                "reason": "Excel file"

            }

        else:

            logo_result = self.logo.verify(

                approval_input,

                sample_input

            )

        result["logo"] = logo_result

        # ---------------------------------------------------------
        # Barcode Check
        # ---------------------------------------------------------

        if approval_type == "excel" or sample_type == "excel":

            barcode_result = {

                "status": "Skipped",

                "matched": False,

                "reason": "Excel file"

            }

        else:

            barcode_result = self.barcode.compare(

                approval_input,

                sample_input

            )

        result["barcode"] = barcode_result

        # ---------------------------------------------------------
        # Generate Highlight Images
        # ---------------------------------------------------------

        if approval_type != "excel":

            approval_highlight = f"approval_{uuid.uuid4().hex}.png"

            approval_output = os.path.join(

                UPLOAD_FOLDER,

                approval_highlight

            )

            self.highlight.generate(

                approval_input,

                comparison["matched"],

                comparison["missing"],

                comparison["modified"],

                comparison["extra"],

                approval_output

            )

            result["approval_highlight"] = approval_highlight

        else:

            result["approval_highlight"] = None


        if sample_type != "excel":

            sample_highlight = f"sample_{uuid.uuid4().hex}.png"

            sample_output = os.path.join(

                UPLOAD_FOLDER,

                sample_highlight

            )

            self.highlight.generate(

                sample_input,

                comparison["matched"],

                comparison["missing"],

                comparison["modified"],

                comparison["extra"],

                sample_output

            )

            result["sample_highlight"] = sample_highlight

        else:

            result["sample_highlight"] = None

        # ---------------------------------------------------------
        # Report Generation
        # ---------------------------------------------------------

        report = self.report.generate(

            comparison,

            logo_result,

            barcode_result

        )

        result["report"] = report

        result["summary"] = report.get(

            "summary",

            comparison.get("summary", {})

        )
        # ---------------------------------------------------------
        # Cleanup Temporary Files
        # ---------------------------------------------------------

        try:

            if (

                approval_input != approval_path

                and os.path.exists(approval_input)

                and approval_input.endswith(".png")

            ):

                os.remove(approval_input)

        except Exception:

            pass


        try:

            if (

                sample_input != sample_path

                and os.path.exists(sample_input)

                and sample_input.endswith(".png")

            ):

                os.remove(sample_input)

        except Exception:

            pass

        # ---------------------------------------------------------
        # Additional Information
        # ---------------------------------------------------------

        result["approval_file"] = os.path.basename(

            approval_path

        )

        result["sample_file"] = os.path.basename(

            sample_path

        )

        result["approval_type"] = approval_type

        result["sample_type"] = sample_type

        result["status"] = "Success"

        # ---------------------------------------------------------
        # Overall Score
        # ---------------------------------------------------------

        summary = result.get(

            "summary",

            {}

        )

        overall_score = summary.get(

            "qc_score",

            0

        )

        verdict = summary.get(

            "verdict",

            "FAIL"

        )

        result["overall_score"] = overall_score

        result["overall_status"] = verdict

        # ---------------------------------------------------------
        # Return Result
        # ---------------------------------------------------------

        return result


# ---------------------------------------------------------
# Singleton Instance
# ---------------------------------------------------------

label_compare = LabelCompare()


# ---------------------------------------------------------
# Public Function
# ---------------------------------------------------------

def compare_labels(

    approval_path,

    sample_path

):

    try:

        return label_compare.compare(

            approval_path,

            sample_path

        )

    except Exception as e:

        return {

            "status": "Failed",

            "error": str(e),

            "approval_file": os.path.basename(

                approval_path

            ),

            "sample_file": os.path.basename(

                sample_path

            ),

            "comparison": {

                "results": [],

                "matched": [],

                "missing": [],

                "modified": [],

                "extra": [],

                "summary": {}

            },

            "logo": {

                "status": "Skipped",

                "similarity": 0

            },

            "barcode": {

                "status": "Skipped",

                "matched": [],

                "missing": [],

                "extra": []

            },

            "approval_highlight": None,

            "sample_highlight": None,

            "report": {},

            "summary": {

                "similarity": 0,

                "qc_score": 0,

                "matched": 0,

                "modified": 0,

                "missing": 0,

                "extra": 0,

                "total": 0,

                "verdict": "FAIL"

            }

        }