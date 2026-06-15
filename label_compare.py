import cv2
import pytesseract
from difflib import SequenceMatcher


def extract_text(image_path):

    image = cv2.imread(image_path)

    if image is None:
        return ""

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    gray = cv2.GaussianBlur(
        gray,
        (3, 3),
        0
    )

    text = pytesseract.image_to_string(
        gray,
        lang="eng"
    )

    return text.strip()


def compare_logo(
    approval_path,
    sample_path
):

    try:

        approval_img = cv2.imread(
            approval_path,
            cv2.IMREAD_GRAYSCALE
        )

        sample_img = cv2.imread(
            sample_path,
            cv2.IMREAD_GRAYSCALE
        )

        if approval_img is None or sample_img is None:

            return 0, "FAIL"

        sample_img = cv2.resize(

            sample_img,

            (
                approval_img.shape[1],
                approval_img.shape[0]
            )

        )

        result = cv2.matchTemplate(

            sample_img,
            approval_img,
            cv2.TM_CCOEFF_NORMED

        )

        _, max_val, _, _ = cv2.minMaxLoc(
            result
        )

        similarity = round(
            max_val * 100,
            2
        )

        status = (
            "PASS"
            if similarity >= 90
            else "FAIL"
        )

        return similarity, status

    except Exception:

        return 0, "FAIL"


def compare_labels(
    approval_path,
    sample_path
):

    approval_text = extract_text(
        approval_path
    )

    sample_text = extract_text(
        sample_path
    )

    approval_lines = [

        line.strip()

        for line in approval_text.splitlines()

        if line.strip()

    ]

    sample_lines = [

        line.strip()

        for line in sample_text.splitlines()

        if line.strip()

    ]

    matched_data = []

    missing_data = []

    extra_data = []

    comparison_rows = []

    for approval_line in approval_lines:

        best_score = 0

        best_match = ""

        for sample_line in sample_lines:

            score = SequenceMatcher(

                None,

                approval_line.lower(),

                sample_line.lower()

            ).ratio()

            if score > best_score:

                best_score = score

                best_match = sample_line

        if best_score >= 0.80:

            matched_data.append(
                approval_line
            )

            comparison_rows.append({

                "approval":
                    approval_line,

                "sample":
                    best_match,

                "status":
                    "MATCH"

            })

        else:

            missing_data.append(
                approval_line
            )

            comparison_rows.append({

                "approval":
                    approval_line,

                "sample":
                    "Missing",

                "status":
                    "MISSING"

            })

    for sample_line in sample_lines:

        found = False

        for approval_line in approval_lines:

            score = SequenceMatcher(

                None,

                sample_line.lower(),

                approval_line.lower()

            ).ratio()

            if score >= 0.80:

                found = True

                break

        if not found:

            extra_data.append(
                sample_line
            )

    total_fields = len(
        approval_lines
    )

    matched_count = len(
        matched_data
    )

    missing_count = len(
        missing_data
    )

    extra_count = len(
        extra_data
    )

    if total_fields > 0:

        similarity_percentage = round(

            (
                matched_count
                /
                total_fields
            ) * 100,

            2

        )

    else:

        similarity_percentage = 0

    logo_similarity, logo_status = compare_logo(

        approval_path,
        sample_path

    )

    if (

        similarity_percentage >= 90

        and

        logo_status == "PASS"

    ):

        verdict = "APPROVED"

    elif similarity_percentage >= 75:

        verdict = "PARTIALLY APPROVED"

    else:

        verdict = "NOT APPROVED"

    return {

        "verdict":
            verdict,

        "similarity":
            similarity_percentage,

        "logo_similarity":
            logo_similarity,

        "logo_status":
            logo_status,

        "total_fields":
            total_fields,

        "matched_count":
            matched_count,

        "missing_count":
            missing_count,

        "extra_count":
            extra_count,

        "matched_data":
            matched_data,

        "missing_data":
            missing_data,

        "extra_data":
            extra_data,

        "comparison_rows":
            comparison_rows,

        "approval_text":
            approval_text,

        "sample_text":
            sample_text

    }