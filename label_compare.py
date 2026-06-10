import cv2
import pytesseract


def extract_text(image_path):

    image = cv2.imread(image_path)

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
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

    if approval_text == sample_text:
        verdict = "APPROVED"
    else:
        verdict = "NOT APPROVED"

    return {
        "verdict": verdict,
        "approval_text": approval_text,
        "sample_text": sample_text
    }