"""
=========================================================
Label QC Checker Pro
Barcode Checker
Version 4.0
=========================================================
"""

import re

from rapidfuzz import fuzz


class BarcodeChecker:

    def __init__(self):

        pass

# ---------------------------------------------------------
# Extract Barcode Numbers
# ---------------------------------------------------------

    def extract(self, text):

        if text is None:

            return []

        text = str(text)

        barcodes = re.findall(

            r"\b\d{8,20}\b",

            text

        )

        return list(set(barcodes))

# ---------------------------------------------------------
# Compare Barcode Lists
# ---------------------------------------------------------

    def compare_list(

        self,

        approval_codes,

        sample_codes

    ):

        matched = []

        missing = []

        extra = []

        sample_copy = sample_codes.copy()

        for code in approval_codes:

            if code in sample_copy:

                matched.append(code)

                sample_copy.remove(code)

            else:

                missing.append(code)

        extra.extend(sample_copy)

        return {

            "matched": matched,

            "missing": missing,

            "extra": extra

        }

# ---------------------------------------------------------
# Compare OCR Results
# ---------------------------------------------------------

    def compare(

        self,

        approval_path,

        sample_path

    ):

        from engine.ocr_engine import ocr_engine

        approval = ocr_engine.read(

            approval_path

        )

        sample = ocr_engine.read(

            sample_path

        )

        approval_codes = self.extract(

            approval["text"]

        )

        sample_codes = self.extract(

            sample["text"]

        )

        result = self.compare_list(

            approval_codes,

            sample_codes

        )

        result["status"] = (

            "PASS"

            if

            len(result["missing"]) == 0

            and

            len(result["extra"]) == 0

            else

            "FAIL"

        )

        return result


barcode_checker = BarcodeChecker()