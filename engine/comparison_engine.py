"""
=========================================================
Label QC Checker Pro
Advanced Comparison Engine
Version 5.0
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

        token = fuzz.token_sort_ratio(

            approval,

            sample

        )

        partial = fuzz.partial_ratio(

            approval,

            sample

        )

        ratio = fuzz.ratio(

            approval,

            sample

        )

        return round(

            max(

                token,

                partial,

                ratio

            ),

            2

        )

    # ---------------------------------------------------------
    # Find OCR Bounding Box
    # ---------------------------------------------------------

    def find_bbox(

        self,

        words,

        value

    ):

        value = self.normalize(value)

        best_score = 0

        best_box = None

        for word in words:

            word_text = self.normalize(

                word["text"]

            )

            score = fuzz.partial_ratio(

                value,

                word_text

            )

            if score > best_score:

                best_score = score

                best_box = {

                    "x": word["x"],

                    "y": word["y"],

                    "width": word["width"],

                    "height": word["height"]

                }

        if best_score >= 70:

            return best_box

        return None

    # ---------------------------------------------------------
    # Compare One Field
    # ---------------------------------------------------------

    def compare_field(

        self,

        field,

        approval_value,

        sample_value,

        approval_words,

        sample_words

    ):

        approval_value = self.normalize(

            approval_value

        )

        sample_value = self.normalize(

            sample_value

        )

        approval_bbox = self.find_bbox(

            approval_words,

            approval_value

        )

        sample_bbox = self.find_bbox(

            sample_words,

            sample_value

        )

        score = self.similarity(

            approval_value,

            sample_value

        )

        if score >= self.match_threshold:

            status = "MATCH"

        elif score >= self.modified_threshold:

            status = "MODIFIED"

        else:

            status = "FAIL"

        return {

            "field": field,

            "approval": approval_value,

            "sample": sample_value,

            "score": score,

            "status": status,

            "approval_bbox": approval_bbox,

            "sample_bbox": sample_bbox

        }
        # ---------------------------------------------------------
    # Compare Constraints
    # ---------------------------------------------------------

    def compare_constraints(

        self,

        approval_constraints,

        sample_constraints,

        approval_words,

        sample_words

    ):

        results = []

        matched = []

        modified = []

        missing = []

        extra = []

        sample_copy = sample_constraints.copy()

        # ---------------------------------------------------------
        # Compare Approval Fields
        # ---------------------------------------------------------

        for field, approval_value in approval_constraints.items():

            approval_value = self.normalize(

                approval_value

            )

            approval_bbox = self.find_bbox(

                approval_words,

                approval_value

            )

            # -------------------------
            # Missing Field
            # -------------------------

            if field not in sample_copy:

                row = {

                    "field": field,

                    "approval": approval_value,

                    "sample": "",

                    "score": 0,

                    "status": "MISSING"

                }

                results.append(row)

                missing.append({

                    "field": field,

                    "approval": approval_value,

                    "bbox": approval_bbox,

                    "status": "MISSING"

                })

                continue

            sample_value = sample_copy[field]

            compare = self.compare_field(

                field,

                approval_value,

                sample_value,

                approval_words,

                sample_words

            )

            results.append(compare)

            # -------------------------
            # Match
            # -------------------------

            if compare["status"] == "MATCH":

                matched.append({

                    "field": field,

                    "approval": approval_value,

                    "sample": sample_value,

                    "bbox": compare["approval_bbox"],

                    "status": "MATCH"

                })

            # -------------------------
            # Modified / Fail
            # -------------------------

            else:

                modified.append({

                    "field": field,

                    "approval": approval_value,

                    "sample": sample_value,

                    "bbox1": compare["approval_bbox"],

                    "bbox2": compare["sample_bbox"],

                    "status": compare["status"]

                })

            sample_copy.pop(field)

        # ---------------------------------------------------------
        # Extra Fields
        # ---------------------------------------------------------

        for field, value in sample_copy.items():

            bbox = self.find_bbox(

                sample_words,

                value

            )

            results.append({

                "field": field,

                "approval": "",

                "sample": value,

                "score": 0,

                "status": "EXTRA"

            })

            extra.append({

                "field": field,

                "value": value,

                "bbox": bbox,

                "status": "EXTRA"

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

        total = 0

        count = 0

        for row in results:

            if row["status"] == "MATCH":

                total += 100

            elif row["status"] == "MODIFIED":

                total += row["score"]

            elif row["status"] == "FAIL":

                total += row["score"]

            elif row["status"] == "MISSING":

                total += 0

            elif row["status"] == "EXTRA":

                total += 0

            count += 1

        return round(

            total / count,

            2

        )

    # ---------------------------------------------------------
    # Statistics
    # ---------------------------------------------------------

    def get_statistics(

        self,

        comparison

    ):

        return {

            "matched": len(comparison["matched"]),

            "modified": len(comparison["modified"]),

            "missing": len(comparison["missing"]),

            "extra": len(comparison["extra"]),

            "total": len(comparison["results"])

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

        score -= stats["missing"] * 5

        score -= stats["extra"] * 3

        score -= stats["modified"] * 2

        score = max(

            0,

            round(score, 2)

        )

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

        return {

            "overall_score": qc,

            "similarity": similarity,

            "qc_score": qc,

            "matched": statistics["matched"],

            "modified": statistics["modified"],

            "missing": statistics["missing"],

            "extra": statistics["extra"],

            "total": statistics["total"],

            "verdict": verdict

        }

    # ---------------------------------------------------------
    # Complete Comparison
    # ---------------------------------------------------------

    def compare(

        self,

        approval_constraints,

        sample_constraints,

        approval_words,

        sample_words

    ):

        comparison = self.compare_constraints(

            approval_constraints,

            sample_constraints,

            approval_words,

            sample_words

        )

        comparison["summary"] = self.generate_summary(

            comparison

        )

        return comparison


# ---------------------------------------------------------
# Singleton
# ---------------------------------------------------------

comparison_engine = ComparisonEngine()