"""
=========================================================
Label QC Checker Pro
Report Generator
Version 2.0
=========================================================
"""

from config import *


class ReportGenerator:

    def __init__(self):

        pass
# ---------------------------------------------------------
# Generate QC Summary
# ---------------------------------------------------------

    def generate_summary(

        self,

        comparison,

        logo,

        barcode

    ):

        summary = {

            "similarity": comparison["summary"]["similarity"],

            "qc_score": comparison["summary"]["qc_score"],

            "matched": comparison["summary"]["matched"],

            "modified": comparison["summary"]["modified"],

            "missing": comparison["summary"]["missing"],

            "extra": comparison["summary"]["extra"],

            "logo_status": logo["status"],

            "barcode_status": barcode["status"]

        }

        return summary
# ---------------------------------------------------------
# Final Verdict
# ---------------------------------------------------------

    def generate_verdict(

        self,

        summary

    ):

        verdict = "PASS"

        if summary["logo_status"] != "PASS":

            verdict = "FAIL"

        elif summary["barcode_status"] != "PASS":

            verdict = "FAIL"

        elif summary["missing"] > 0:

            verdict = "FAIL"

        elif summary["similarity"] < OVERALL_PASS:

            verdict = "FAIL"

        summary["verdict"] = verdict

        return summary
# ---------------------------------------------------------
# Generate Complete Report
# ---------------------------------------------------------

    def generate(

        self,

        comparison,

        logo,

        barcode

    ):

        summary = self.generate_summary(

            comparison,

            logo,

            barcode

        )

        summary = self.generate_verdict(

            summary

        )

        return {

            "summary": summary,

            "comparison": comparison,

            "logo": logo,

            "barcode": barcode

        }
# ---------------------------------------------------------
# Print Report
# ---------------------------------------------------------

    def print_report(

        self,

        report

    ):

        print()

        print("=" * 80)

        print("QC REPORT")

        print("=" * 80)

        for key, value in report["summary"].items():

            print(f"{key:20} : {value}")

        print("=" * 80)
report_generator = ReportGenerator()