"""
=========================================================
Label QC Checker Pro
Comparison Engine
Version 2.0
=========================================================
"""

from rapidfuzz import fuzz

from config import *


class ComparisonEngine:

    def __init__(self):

        self.match_threshold = WORD_MATCH

        self.modified_threshold = WORD_MODIFIED

    # ---------------------------------------------------------
    # Normalize
    # ---------------------------------------------------------

    def normalize(self, value):

        if value is None:

            return ""

        value = str(value)

        value = value.upper()

        value = " ".join(value.split())

        return value.strip()

    # ---------------------------------------------------------
    # Similarity
    # ---------------------------------------------------------

    def similarity(

        self,

        approval,

        sample

    ):

        approval = self.normalize(approval)

        sample = self.normalize(sample)

        return round(

            fuzz.token_sort_ratio(

                approval,

                sample

            ),

            2

        )
        # ---------------------------------------------------------
# Compare Constraints
# ---------------------------------------------------------

    def compare_constraints(

        self,

        approval_constraints,

        sample_constraints

    ):

        results = []

        matched = []

        modified = []

        missing = []

        extra = []

        sample_copy = sample_constraints.copy()

        for field, approval_value in approval_constraints.items():

            approval_value = self.normalize(

                approval_value

            )

            if field not in sample_copy:

                results.append({

                    "field": field,

                    "approval": approval_value,

                    "sample": "",

                    "status": "MISSING",

                    "score": 0

                })

                missing.append({

                    "field": field,

                    "approval": approval_value,

                    "sample": "",

                    "score": 0

                })

                continue

            sample_value = self.normalize(

                sample_copy[field]

            )

            score = self.similarity(

                approval_value,

                sample_value

            )

            if score >= self.match_threshold:

                status = "MATCH"

                matched.append({

                    "field": field,

                    "approval": approval_value,

                    "sample": sample_value,

                    "score": score

                })

            elif score >= self.modified_threshold:

                status = "MODIFIED"

                modified.append({

                    "field": field,

                    "approval": approval_value,

                    "sample": sample_value,

                    "score": score

                })

            else:

                status = "FAIL"

                modified.append({

                    "field": field,

                    "approval": approval_value,

                    "sample": sample_value,

                    "score": score

                })

            results.append({

                "field": field,

                "approval": approval_value,

                "sample": sample_value,

                "status": status,

                "score": score

            })

            sample_copy.pop(field)

    # ---------------------------------------------------------
    # Extra Constraints
    # ---------------------------------------------------------

        for field, value in sample_copy.items():

            results.append({

                "field": field,

                "approval": "",

                "sample": value,

                "status": "EXTRA",

                "score": 0

            })

            extra.append({

                "field": field,

                "approval": "",

                "sample": value,

                "score": 0

            })

        return {

            "results": results,

            "matched": matched,

            "modified": modified,

            "missing": missing,

            "extra": extra

        }
    # ---------------------------------------------------------
# Calculate Overall Similarity
# ---------------------------------------------------------

    def calculate_similarity(

        self,

        comparison

    ):

        results = comparison["results"]

        if len(results) == 0:

            return 0

        total_score = 0

        valid_items = 0

        for row in results:

            status = row["status"]

            score = row["score"]

            if status == "MATCH":

                total_score += 100

                valid_items += 1

            elif status == "MODIFIED":

                total_score += score

                valid_items += 1

            elif status == "FAIL":

                total_score += score

                valid_items += 1

            elif status == "MISSING":

                total_score += 0

                valid_items += 1

            elif status == "EXTRA":

                total_score += 0

                valid_items += 1

        if valid_items == 0:

            return 0

        similarity = round(

            total_score / valid_items,

            2

        )

        return similarity


# ---------------------------------------------------------
# Constraint Statistics
# ---------------------------------------------------------

    def get_statistics(

        self,

        comparison

    ):

        return {

            "matched": len(

                comparison["matched"]

            ),

            "modified": len(

                comparison["modified"]

            ),

            "missing": len(

                comparison["missing"]

            ),

            "extra": len(

                comparison["extra"]

            ),

            "total": len(

                comparison["results"]

            )

        }


# ---------------------------------------------------------
# QC Score
# ---------------------------------------------------------

    def qc_score(

        self,

        comparison

    ):

        similarity = self.calculate_similarity(

            comparison

        )

        stats = self.get_statistics(

            comparison

        )

        score = similarity

        if stats["missing"] > 0:

            score -= stats["missing"] * 5

        if stats["extra"] > 0:

            score -= stats["extra"] * 3

        if stats["modified"] > 0:

            score -= stats["modified"] * 2

        score = max(0, round(score, 2))

        return score
# ---------------------------------------------------------
# Generate Summary
# ---------------------------------------------------------

    def generate_summary(

        self,

        comparison

    ):

        similarity = self.calculate_similarity(

            comparison

        )

        statistics = self.get_statistics(

            comparison

        )

        qc = self.qc_score(

            comparison

        )

        if (

            similarity >= OVERALL_PASS

            and

            statistics["missing"] == 0

            and

            statistics["extra"] == 0

        ):

            verdict = "PASS"

        elif similarity >= 80:

            verdict = "REVIEW"

        else:

            verdict = "FAIL"

        summary = {

            "similarity": similarity,

            "qc_score": qc,

            "matched": statistics["matched"],

            "modified": statistics["modified"],

            "missing": statistics["missing"],

            "extra": statistics["extra"],

            "total": statistics["total"],

            "verdict": verdict

        }

        return summary


# ---------------------------------------------------------
# Complete Comparison
# ---------------------------------------------------------

    def compare(

        self,

        approval_constraints,

        sample_constraints

    ):

        comparison = self.compare_constraints(

            approval_constraints,

            sample_constraints

        )

        summary = self.generate_summary(

            comparison

        )

        comparison["summary"] = summary

        return comparison
# ---------------------------------------------------------
# Print Summary
# ---------------------------------------------------------

    def print_summary(

        self,

        comparison

    ):

        summary = comparison["summary"]

        print()

        print("=" * 80)

        print("COMPARISON SUMMARY")

        print("=" * 80)

        print("Similarity :", summary["similarity"], "%")

        print("QC Score   :", summary["qc_score"])

        print("Matched    :", summary["matched"])

        print("Modified   :", summary["modified"])

        print("Missing    :", summary["missing"])

        print("Extra      :", summary["extra"])

        print("Total      :", summary["total"])

        print("Verdict    :", summary["verdict"])

        print("=" * 80)


# ---------------------------------------------------------
# Print Detailed Results
# ---------------------------------------------------------

    def print_results(

        self,

        comparison

    ):

        print()

        print("=" * 100)

        print("DETAILED COMPARISON")

        print("=" * 100)

        for row in comparison["results"]:

            print(

                f'{row["field"]:25} | '

                f'{row["status"]:10} | '

                f'{row["score"]:6}%'

            )

        print("=" * 100)
comparison_engine=ComparisonEngine()