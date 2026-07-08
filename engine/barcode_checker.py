"""
=========================================================
Label QC Checker Pro
Advanced Barcode Checker
Version 5.0
=========================================================
"""

import re

from rapidfuzz import fuzz


class BarcodeChecker:

    def __init__(self):

        self.min_length = 8

        self.max_length = 20

    # ---------------------------------------------------------
    # Normalize
    # ---------------------------------------------------------

    def normalize(self, value):

        if value is None:

            return ""

        value = str(value)

        value = value.strip()

        return value

    # ---------------------------------------------------------
    # Extract Barcode Numbers
    # ---------------------------------------------------------

    def extract(self, text):

        if text is None:

            return []

        text = self.normalize(text)

        codes = re.findall(

            r"\b\d{8,20}\b",

            text

        )

        unique = []

        for code in codes:

            if code not in unique:

                unique.append(code)

        return unique

    # ---------------------------------------------------------
    # Barcode Similarity
    # ---------------------------------------------------------

    def similarity(

        self,

        code1,

        code2

    ):

        return round(

            fuzz.ratio(

                self.normalize(code1),

                self.normalize(code2)

            ),

            2

        )

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

        modified = []

        extra = []

        sample_copy = sample_codes.copy()

        for approval in approval_codes:

            found = False

            best_score = 0

            best_code = None

            for sample in sample_copy:

                score = self.similarity(

                    approval,

                    sample

                )

                if score > best_score:

                    best_score = score

                    best_code = sample

            if best_score == 100:

                matched.append({

                    "approval": approval,

                    "sample": best_code,

                    "score": 100

                })

                sample_copy.remove(best_code)

                found = True

            elif best_score >= 90:

                modified.append({

                    "approval": approval,

                    "sample": best_code,

                    "score": best_score

                })

                sample_copy.remove(best_code)

                found = True

            if not found:

                missing.append(approval)
                # ---------------------------------------------------------
        # Extra Barcodes
        # ---------------------------------------------------------

        for code in sample_copy:

            extra.append(code)

        return {

            "matched": matched,

            "modified": modified,

            "missing": missing,

            "extra": extra

        }

    # ---------------------------------------------------------
    # Statistics
    # ---------------------------------------------------------

    def statistics(self, result):

        return {

            "matched": len(result["matched"]),

            "modified": len(result["modified"]),

            "missing": len(result["missing"]),

            "extra": len(result["extra"])

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

        stats = self.statistics(

            result

        )

        result["statistics"] = stats

        if (

            stats["missing"] == 0

            and

            stats["extra"] == 0

            and

            stats["modified"] == 0

        ):

            result["status"] = "PASS"

        elif (

            stats["missing"] == 0

            and

            stats["extra"] == 0

        ):

            result["status"] = "REVIEW"

        else:

            result["status"] = "FAIL"

        result["matched_count"] = stats["matched"]

        result["missing_count"] = stats["missing"]

        result["modified_count"] = stats["modified"]

        result["extra_count"] = stats["extra"]

        result["approval_codes"] = approval_codes

        result["sample_codes"] = sample_codes

        return result


# ---------------------------------------------------------
# Singleton
# ---------------------------------------------------------

barcode_checker = BarcodeChecker()                
        