import cv2
import pytesseract
import difflib
import re


def extract_text(image_path):
    try:
        image = cv2.imread(image_path)

        if image is None:
            return ""

        # Resize large images
        h, w = image.shape[:2]

        if w > 1200:
            ratio = 1200 / w
            image = cv2.resize(
                image,
                (1200, int(h * ratio))
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
            lang="eng",
            timeout=20
        )

        return text.strip()

    except Exception as e:
        return f"OCR Error: {str(e)}"


def clean_text(text):
    text = text.lower()

    text = re.sub(
        r'[^a-zA-Z0-9 ]',
        ' ',
        text
    )

    text = re.sub(
        r'\s+',
        ' ',
        text
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

    approval_clean = clean_text(
        approval_text
    )

    sample_clean = clean_text(
        sample_text
    )

    similarity = round(
        difflib.SequenceMatcher(
            None,
            approval_clean,
            sample_clean
        ).ratio() * 100,
        2
    )

    approval_words = set(
        approval_clean.split()
    )

    sample_words = set(
        sample_clean.split()
    )

    matched_words = sorted(
        list(
            approval_words.intersection(
                sample_words
            )
        )
    )

    missing_words = sorted(
        list(
            approval_words - sample_words
        )
    )

    extra_words = sorted(
        list(
            sample_words - approval_words
        )
    )

    if similarity >= 95:
        verdict = "APPROVED"
    else:
        verdict = "NOT APPROVED"

    # Placeholder logo check
    logo_status = "NOT CHECKED"

    return {
        "verdict": verdict,

        "similarity": similarity,

        "logo_status": logo_status,

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