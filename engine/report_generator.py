"""
=========================================================
Label QC Checker Pro
Advanced Report Generator
Version 5.0
=========================================================
"""


class ReportGenerator:

    def __init__(self):

        pass

    # ---------------------------------------------------------
    # Safe Value
    # ---------------------------------------------------------

    def safe(

        self,

        value,

        default=0

    ):

        if value is None:

            return default

        return value

    # ---------------------------------------------------------
    # Generate Summary
    # ---------------------------------------------------------

    def generate_summary(

        self,

        comparison,

        logo_result,

        barcode_result

    ):

        summary = comparison["summary"]

        return {

            "overall_score": self.safe(

                summary.get("overall_score"),

                summary.get("qc_score", 0)

            ),

            "similarity": self.safe(

                summary.get("similarity")

            ),

            "qc_score": self.safe(

                summary.get("qc_score")

            ),

            "verdict": summary.get(

                "verdict",

                "FAIL"

            ),

            "matched": self.safe(

                summary.get("matched")

            ),

            "modified": self.safe(

                summary.get("modified")

            ),

            "missing": self.safe(

                summary.get("missing")

            ),

            "extra": self.safe(

                summary.get("extra")

            ),

            "total": self.safe(

                summary.get("total")

            ),

            "logo_status": logo_result.get(

                "status",

                "Skipped"

            ),

            "logo_similarity": logo_result.get(

                "similarity",

                logo_result.get("score", 0)

            ),

            "barcode_status": barcode_result.get(

                "status",

                "Skipped"

            ),

            "barcode_matched": barcode_result.get(

                "matched_count",

                0

            ),

            "barcode_missing": barcode_result.get(

                "missing_count",

                0

            ),

            "barcode_extra": barcode_result.get(

                "extra_count",

                0

            )

        }
        # ---------------------------------------------------------
    # Generate Final Report
    # ---------------------------------------------------------

    def generate(

        self,

        comparison,

        logo_result,

        barcode_result

    ):

        summary = self.generate_summary(

            comparison,

            logo_result,

            barcode_result

        )

        report = {

            "summary": summary,

            "results": comparison.get(

                "results",

                []

            ),

            "matched": comparison.get(

                "matched",

                []

            ),

            "modified": comparison.get(

                "modified",

                []

            ),

            "missing": comparison.get(

                "missing",

                []

            ),

            "extra": comparison.get(

                "extra",

                []

            ),

            "logo": logo_result,

            "barcode": barcode_result

        }

        return report

    # ---------------------------------------------------------
    # Print Report
    # ---------------------------------------------------------

    def print_report(

        self,

        report

    ):

        summary = report["summary"]

        print("=" * 80)

        print("LABEL QC REPORT")

        print("=" * 80)

        print(f"Overall Score      : {summary['overall_score']}")

        print(f"Similarity         : {summary['similarity']}")

        print(f"QC Score           : {summary['qc_score']}")

        print(f"Verdict            : {summary['verdict']}")

        print()

        print(f"Matched            : {summary['matched']}")

        print(f"Modified           : {summary['modified']}")

        print(f"Missing            : {summary['missing']}")

        print(f"Extra              : {summary['extra']}")

        print(f"Total Fields       : {summary['total']}")

        print()

        print(f"Logo Status        : {summary['logo_status']}")

        print(f"Logo Similarity    : {summary['logo_similarity']}")

        print()

        print(f"Barcode Status     : {summary['barcode_status']}")

        print(f"Barcode Matched    : {summary['barcode_matched']}")

        print(f"Barcode Missing    : {summary['barcode_missing']}")

        print(f"Barcode Extra      : {summary['barcode_extra']}")

        print("=" * 80)


# ---------------------------------------------------------
# Singleton
# ---------------------------------------------------------

report_generator = ReportGenerator()