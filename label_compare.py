import cv2
import pytesseract
from difflib import SequenceMatcher


def extract_text(image_path):

    image = cv2.imread(image_path)

    if image is None:
        return ""

    height, width = image.shape[:2]

    if width > 1200:
        scale = 1200 / width

        image = cv2.resize(
            image,
            (
                int(width * scale),
                int(height * scale)
            )
        )

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

    approval_words = set(
        approval_text.split()
    )

    sample_words = set(
        sample_text.split()
    )

    matched_words = list(
        approval_words.intersection(
            sample_words
        )
    )

    missing_words = list(
        approval_words - sample_words
    )

    extra_words = list(
        sample_words - approval_words
    )

    similarity = round(
        SequenceMatcher(
            None,
            approval_text.lower(),
            sample_text.lower()
        ).ratio() * 100,
        2
    )

    if similarity >= 90:
        verdict = "APPROVED"
    else:
        verdict = "NOT APPROVED"

    return {
        "verdict": verdict,
        "similarity": similarity,

        "approval_text": approval_text,
        "sample_text": sample_text,

        "matched_words": matched_words,
        "missing_words": missing_words,
        "extra_words": extra_words,

        "matched_count": len(
            matched_words
        ),

        "missing_count": len(
            missing_words
        ),

        "extra_count": len(
            extra_words
        )
    }