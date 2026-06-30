"""
=========================================================
Label QC Checker Pro
Report Generator
Version 4.0
=========================================================
"""


class ReportGenerator:

    def __init__(self):
        pass

    # ---------------------------------------------------------
    # Generate Final Report
    # ---------------------------------------------------------

    def generate(

        self,

        comparison,

        logo_result,

        barcode_result

    ):

        summary = comparison["summary"]

        report = {

            "summary": {

                "similarity": summary["similarity"],

                "qc_score": summary["qc_score"],

                "verdict": summary["verdict"],

                "matched": summary["matched"],

                "modified": summary["modified"],

                "missing": summary["missing"],

                "extra": summary["extra"],

                "total": summary["total"],

                "logo_status": logo_result["status"],

                "logo_similarity": logo_result["similarity"],

                "barcode_status": barcode_result["status"]

            },

            "results": comparison["results"],

            "matched": comparison["matched"],

            "modified": comparison["modified"],

            "missing": comparison["missing"],

            "extra": comparison["extra"],

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

        print("Similarity :", summary["similarity"])

        print("QC Score   :", summary["qc_score"])

        print("Verdict    :", summary["verdict"])

        print()

        print("Matched    :", summary["matched"])

        print("Modified   :", summary["modified"])

        print("Missing    :", summary["missing"])

        print("Extra      :", summary["extra"])

        print()

        print("Logo       :", summary["logo_status"])

        print("Barcode    :", summary["barcode_status"])

        print("=" * 80)


report_generator = ReportGenerator()