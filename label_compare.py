import os
import pytesseract
from PIL import Image
from difflib import SequenceMatcher

tesseract_cmd = os.environ.get("TESSERACT_CMD")
if tesseract_cmd:
    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
else:
    for default_cmd in ["/usr/bin/tesseract", "/usr/local/bin/tesseract"]:
        if os.path.exists(default_cmd):
            pytesseract.pytesseract.tesseract_cmd = default_cmd
            break


def extract_text(image_path):
    with Image.open(image_path) as img:
        if img.mode not in ("RGB", "L"):
            img = img.convert("RGB")
        text = pytesseract.image_to_string(img)

    return text


def parse_fields(text):

    lines = []

    for line in text.split("\n"):

        line = line.strip()

        if line:
            lines.append(line)

    return lines


def compare_labels(approval_path, sample_path):

    approval_text = extract_text(approval_path)
    sample_text = extract_text(sample_path)

    approval_fields = parse_fields(approval_text)
    sample_fields = parse_fields(sample_text)

    matched_fields = [field for field in approval_fields if field in sample_fields]
    missing_fields = [field for field in approval_fields if field not in sample_fields]
    extra_fields = [field for field in sample_fields if field not in approval_fields]

    total = len(approval_fields)
    matched = len(matched_fields)

    score = round((matched / total) * 100, 2) if total > 0 else 0
    status = "APPROVED" if score >= 95 else "NOT APPROVED"

    rows = []
    seen = set()
    for field in approval_fields + sample_fields:
        if field in seen:
            continue
        seen.add(field)
        rows.append({
            "field": field,
            "approval": field if field in approval_fields else "",
            "sample": field if field in sample_fields else "",
            "status": "MATCHED" if field in matched_fields else ("MISSING" if field in missing_fields else "EXTRA")
        })

    return {
        "status": status,
        "score": score,
        "matched": matched,
        "missing": len(missing_fields),
        "total_fields": total,
        "missing_fields": missing_fields,
        "extra_fields": extra_fields,
        "results": rows
    }


def generate_report(result):

    return f"""
    Status: {result['status']}

    Match Score: {result['score']} %

    Matched Fields: {result['matched']}

    Missing Fields: {result['missing']}
    """


def compare_label_images(approval_path, sample_path):
    """Compatibility wrapper for older callers that used
    `compare_label_images`. Delegates to `compare_labels`.
    """
    return compare_labels(approval_path, sample_path)