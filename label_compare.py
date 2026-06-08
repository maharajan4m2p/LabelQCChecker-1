import os
import re
import base64
import json
import urllib.request
import urllib.parse

from PIL import Image
from io import BytesIO
from difflib import SequenceMatcher

# --------------------------------------------------
# OCR Configuration
# --------------------------------------------------

if os.name == "nt":
    try:
        import pytesseract

        pytesseract.pytesseract.tesseract_cmd = (
            r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        )

        USE_TESSERACT = True

    except Exception:
        USE_TESSERACT = False
else:
    USE_TESSERACT = False


# --------------------------------------------------
# OCR.Space API
# --------------------------------------------------

OCR_API_KEY = "K86258847888957"


def ocr_space_api(image):
    try:
        buffered = BytesIO()

        image = image.convert("RGB")

        max_size = 1200

        if image.width > max_size or image.height > max_size:
            image.thumbnail((max_size, max_size))

        image.save(
            buffered,
            format="JPEG",
            quality=90
        )

        img_base64 = base64.b64encode(
            buffered.getvalue()
        ).decode()

        payload = urllib.parse.urlencode({
            "apikey": OCR_API_KEY,
            "base64Image": (
                f"data:image/jpeg;base64,{img_base64}"
            ),
            "language": "eng",
            "OCREngine": 2,
            "scale": True
        }).encode()

        req = urllib.request.Request(
            "https://api.ocr.space/parse/image",
            data=payload
        )

        with urllib.request.urlopen(
            req,
            timeout=60
        ) as response:

            result = json.loads(
                response.read().decode("utf-8")
            )

        print("OCR API RESPONSE:")
        print(result)

        parsed = result.get(
            "ParsedResults",
            []
        )

        if parsed:
            return parsed[0].get(
                "ParsedText",
                ""
            )

        return ""

    except Exception as e:
        print("OCR API ERROR:", str(e))
        return ""


# --------------------------------------------------
# Extract OCR Text
# --------------------------------------------------

def extract_text(image_path):
    try:

        print(f"\nReading image: {image_path}")

        image = Image.open(image_path)

        image = image.convert("L")

        if USE_TESSERACT:

            import pytesseract

            text = pytesseract.image_to_string(
                image,
                config="--oem 1 --psm 6"
            )

        else:

            text = ocr_space_api(image)

        print("\nOCR TEXT START")
        print(text)
        print("OCR TEXT END\n")

        return text.strip()

    except Exception as e:

        print("TEXT EXTRACTION ERROR:", str(e))
        return ""


# --------------------------------------------------
# Parse Common Fields
# --------------------------------------------------

def parse_fields(text):

    fields = {}

    patterns = {
        "STYLE": r"STYLE\s*[:\-]?\s*(.+)",
        "SIZE": r"SIZE\s*[:\-]?\s*(.+)",
        "COLOR": r"COLOR\s*[:\-]?\s*(.+)",
        "PO": r"PO\s*[:\-]?\s*(.+)",
        "COUNTRY": r"COUNTRY\s*[:\-]?\s*(.+)",
        "FABRIC": r"FABRIC\s*[:\-]?\s*(.+)",
        "RN": r"RN\s*[:\-]?\s*(.+)"
    }

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        for key, pattern in patterns.items():

            if key in fields:
                continue

            match = re.search(
                pattern,
                line,
                re.IGNORECASE
            )

            if match:

                value = match.group(1).strip()

                if value:
                    fields[key] = value

    return fields


# --------------------------------------------------
# Compare Fields
# --------------------------------------------------

def compare_fields(
    approval_fields,
    sample_fields
):

    all_keys = (
        set(approval_fields.keys()) |
        set(sample_fields.keys())
    )

    results = []

    matches = 0

    missing_fields = []
    extra_fields = []

    for key in sorted(all_keys):

        approval_value = approval_fields.get(
            key,
            ""
        )

        sample_value = sample_fields.get(
            key,
            ""
        )

        if approval_value and not sample_value:
            missing_fields.append(key)

        if sample_value and not approval_value:
            extra_fields.append(key)

        similarity = SequenceMatcher(
            None,
            approval_value.lower(),
            sample_value.lower()
        ).ratio()

        similarity_pct = round(
            similarity * 100,
            1
        )

        status = (
            "MATCH"
            if similarity >= 0.90
            else "MISMATCH"
        )

        if status == "MATCH":
            matches += 1

        results.append({
            "field": key,
            "approval": approval_value or "-",
            "sample": sample_value or "-",
            "similarity": similarity_pct,
            "status": status
        })

    total = len(all_keys)

    accuracy = (
        round(
            matches / total * 100,
            2
        )
        if total
        else 0
    )

    return {
        "accuracy": accuracy,
        "match_count": matches,
        "total_fields": total,
        "results": results,
        "missing_fields": missing_fields,
        "extra_fields": extra_fields
    }


# --------------------------------------------------
# Main Comparison Function
# --------------------------------------------------

def compare_label_images(
    approval_image_path,
    sample_image_path
):

    approval_text = extract_text(
        approval_image_path
    )

    sample_text = extract_text(
        sample_image_path
    )

    if not approval_text and not sample_text:

        return {
            "accuracy": 0,
            "match_count": 0,
            "total_fields": 0,
            "results": [],
            "missing_fields": [],
            "extra_fields": []
        }

    approval_fields = parse_fields(
        approval_text
    )

    sample_fields = parse_fields(
        sample_text
    )

    # If fields detected, compare fields
    if approval_fields or sample_fields:

        return compare_fields(
            approval_fields,
            sample_fields
        )

    # Fallback to full text comparison
    similarity = SequenceMatcher(
        None,
        approval_text.lower(),
        sample_text.lower()
    ).ratio()

    accuracy = round(
        similarity * 100,
        2
    )

    return {
        "accuracy": accuracy,
        "match_count": 1,
        "total_fields": 1,
        "results": [
            {
                "field": "FULL LABEL TEXT",
                "approval": approval_text[:500],
                "sample": sample_text[:500],
                "similarity": accuracy,
                "status": (
                    "MATCH"
                    if accuracy >= 90
                    else "MISMATCH"
                )
            }
        ],
        "missing_fields": [],
        "extra_fields": []
    }