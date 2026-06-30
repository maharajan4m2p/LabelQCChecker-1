"""
=========================================================
Label QC Checker Pro
Main Label Comparison Engine
Version 4.0
=========================================================
"""

import os
import uuid

from config import *

from engine.ocr_engine import ocr_engine
from engine.label_detector import label_detector
from engine.constraint_detector import constraint_detector
from engine.comparison_engine import comparison_engine
from engine.logo_checker import logo_checker
from engine.barcode_checker import barcode_checker
from engine.image_highlighter import image_highlighter
from engine.report_generator import report_generator


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

        os.makedirs("uploads", exist_ok=True)

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
        # OCR
        # ---------------------------------------------------------

        approval_ocr = self.ocr.read(

            approval_path

        )

        sample_ocr = self.ocr.read(

            sample_path

        )

        result["approval_ocr"] = approval_ocr

        result["sample_ocr"] = sample_ocr

        # ---------------------------------------------------------
        # Label Detection
        # ---------------------------------------------------------

        approval_label = self.detector.detect(

            approval_path

        )

        sample_label = self.detector.detect(

            sample_path

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

        logo_result = self.logo.verify(

            approval_path,

            sample_path

        )

        result["logo"] = logo_result

        # ---------------------------------------------------------
        # Barcode Check
        # ---------------------------------------------------------

        barcode_result = self.barcode.compare(

            approval_path,

            sample_path

        )

        result["barcode"] = barcode_result

        # ---------------------------------------------------------
        # Approval Highlight
        # ---------------------------------------------------------

        approval_name = f"approval_{uuid.uuid4().hex}.png"

        approval_output = os.path.join(

            "uploads",

            approval_name

        )

        self.highlight.generate(

            approval_path,

            comparison["matched"],

            comparison["missing"],

            comparison["modified"],

            comparison["extra"],

            approval_output

        )

        result["approval_highlight"] = approval_name

        # ---------------------------------------------------------
        # Sample Highlight
        # ---------------------------------------------------------

        sample_name = f"sample_{uuid.uuid4().hex}.png"

        sample_output = os.path.join(

            "uploads",

            sample_name

        )

        self.highlight.generate(

            sample_path,

            comparison["matched"],

            comparison["missing"],

            comparison["modified"],

            comparison["extra"],

            sample_output

        )

        result["sample_highlight"] = sample_name

        # ---------------------------------------------------------
        # Report
        # ---------------------------------------------------------

        report = self.report.generate(

            comparison,

            logo_result,

            barcode_result

        )

        result["report"] = report

        result["summary"] = report["summary"]

        return result


# ---------------------------------------------------------
# Singleton
# ---------------------------------------------------------

label_compare = LabelCompare()


# ---------------------------------------------------------
# Public Function
# ---------------------------------------------------------

def compare_labels(

    approval_path,

    sample_path

):

    return label_compare.compare(

        approval_path,

        sample_path

    )