import os
import re
import json
import base64
import urllib.request
import urllib.parse
import easyocr

from io import BytesIO
from PIL import Image
from difflib import SequenceMatcher


# --------------------------------------------------
# Tesseract (Windows only)
# --------------------------------------------------

USE_TESSERACT = False

if os.name == "nt":
    try:
        import pytesseract

        pytesseract.pytesseract.tesseract_cmd = (
            r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        )

        USE_TESSERACT = True

    except Exception:
        USE_TESSERACT = False


# --------------------------------------------------
# OCR SPACE
# --------------------------------------------------

OCR_API_KEY = "K86258847888957"
reader = easyocr.Reader(['en'], gpu=False)


def ocr_space_api(image):

    try:

        buffered = BytesIO()

        image = image.convert("RGB")

        image.save(
            buffered,
            format="JPEG",
            quality=90
        )

        img_base64 = base64.b64encode(
            buffered.getvalue()
        ).decode("utf-8")

        payload = urllib.parse.urlencode({
            "apikey": OCR_API_KEY,
            "base64Image":
                f"data:image/jpeg;base64,{img_base64}",
            "language": "eng",
            "OCREngine": 2,
            "scale": True
        }).encode()

        request_obj = urllib.request.Request(
            "https://api.ocr.space/parse/image",
            data=payload
        )

        with urllib.request.urlopen(
            request_obj,
            timeout=60
        ) as response:

            result = json.loads(
                response.read().decode("utf-8")
            )

        print("\nOCR RESPONSE:")
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
# OCR TEXT EXTRACTION
# --------------------------------------------------

def extract_text(image_path):

    try:

        print(f"\nReading image: {image_path}")

        results = reader.readtext(image_path)

        lines = []

        for item in results:

            text = item[1].strip()

            if text:
                lines.append(text)

        extracted_text = "\n".join(lines)

        if extracted_text.strip():

            print("\nOCR TEXT START")
            print(extracted_text)
            print("OCR TEXT END\n")

            return extracted_text

        image = Image.open(image_path)
        image = image.convert("L")

        return ocr_space_api(image)

    except Exception as e:

        print("EasyOCR ERROR:", str(e))

        try:

            image = Image.open(image_path)
            image = image.convert("L")

            return ocr_space_api(image)

        except Exception as e:

            print("OCR ERROR:", str(e))
            return ""


# --------------------------------------------------
# FIELD EXTRACTION
# --------------------------------------------------

def normalize_text(text):
    text = re.sub(r"[\r\n]+", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def normalize_key(key):
    key = re.sub(r"[^\w\s]", " ", key)
    key = re.sub(r"\s+", " ", key)
    return key.strip().upper()


def normalize_value(value):
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def parse_fields(text):

    fields = {}

    lines = text.splitlines()

    for line in lines:

        line = line.strip()

        if not line:
            continue

        line = normalize_text(line)

        key = None
        value = None

        if ":" in line:
            parts = line.split(":", 1)
            key = parts[0].strip()
            value = parts[1].strip()

        elif "=" in line:
            parts = line.split("=", 1)
            key = parts[0].strip()
            value = parts[1].strip()

        elif "-" in line:
            parts = line.split("-", 1)
            key = parts[0].strip()
            value = parts[1].strip()

        elif len(line.split()) >= 2:
            parts = line.split(None, 1)
            key = parts[0].strip()
            value = parts[1].strip()

        if not key or not value:
            continue

        key = normalize_key(key)
        value = normalize_value(value)

        if key and value:
            fields[key] = value

    return fields


# --------------------------------------------------
# FIELD COMPARISON
# --------------------------------------------------

def compare_fields(
    approval_fields,
    sample_fields
):

    results = []
    match_count = 0
    missing_fields = []
    extra_fields = []
    mismatch_fields = []

    approval_keys = list(approval_fields.keys())
    sample_keys = list(sample_fields.keys())
    used_sample_keys = set()

    def add_row(
        field,
        approval_value,
        sample_value,
        status,
        key_similarity=0.0,
        value_similarity=0.0,
        note=""
    ):
        nonlocal match_count

        if status == "MATCH":
            match_count += 1

        results.append({
            "field": f"{field}{note}",
            "approval": approval_value or "-",
            "sample": sample_value or "-",
            "key_similarity": round(key_similarity * 100, 1),
            "value_similarity": round(value_similarity * 100, 1),
            "similarity": round(value_similarity * 100, 1),
            "status": status
        })

    for approval_key in approval_keys:
        approval_value = approval_fields[approval_key]
        best_match = None

        for sample_key in sample_keys:
            if sample_key in used_sample_keys:
                continue

            key_similarity = SequenceMatcher(None, approval_key, sample_key).ratio()
            sample_value = sample_fields[sample_key]
            value_similarity = SequenceMatcher(
                None,
                approval_value.lower(),
                sample_value.lower()
            ).ratio() if sample_value else 0.0
            combined_score = (key_similarity * 0.7) + (value_similarity * 0.3)

            if best_match is None or combined_score > best_match[0]:
                best_match = (combined_score, sample_key, key_similarity, value_similarity)

        if best_match and best_match[0] >= 0.75:
            _, sample_key, key_similarity, value_similarity = best_match
            sample_value = sample_fields[sample_key]
            used_sample_keys.add(sample_key)
            note = ""

            if key_similarity < 0.95:
                note = f" (key fuzzy {round(key_similarity * 100, 1)}%)"

            status = "MATCH" if value_similarity >= 0.90 else "MISMATCH"

            if status == "MISMATCH":
                mismatch_fields.append(
                    f"{approval_key}: expected '{approval_value}' but got '{sample_value}'"
                )

            add_row(
                approval_key,
                approval_value,
                sample_value,
                status,
                key_similarity=key_similarity,
                value_similarity=value_similarity,
                note=note
            )

        else:
            missing_fields.append(f"{approval_key}: {approval_value}")
            add_row(approval_key, approval_value, "", "MISSING")

    for sample_key in sample_keys:
        if sample_key in used_sample_keys:
            continue

        sample_value = sample_fields[sample_key]
        extra_fields.append(f"{sample_key}: {sample_value}")
        add_row(sample_key, "", sample_value, "EXTRA")

    total = len(approval_keys) if approval_keys else len(results)
    accuracy = round((match_count / total) * 100, 2) if total > 0 else 0

    return {
        "accuracy": accuracy,
        "match_count": match_count,
        "total_fields": total,
        "results": results,
        "missing_fields": missing_fields,
        "extra_fields": extra_fields,
        "mismatch_fields": mismatch_fields
    }


# --------------------------------------------------
# MAIN FUNCTION
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
            "extra_fields": [],
            "approval_text": "",
            "sample_text": ""
        }

    approval_fields = parse_fields(
        approval_text
    )

    sample_fields = parse_fields(
        sample_text
    )

    print("\nAPPROVAL FIELDS:")
    print(approval_fields)

    print("\nSAMPLE FIELDS:")
    print(sample_fields)

    if approval_fields or sample_fields:

        result = compare_fields(
            approval_fields,
            sample_fields
        )

        result["approval_text"] = approval_text
        result["sample_text"] = sample_text

        return result

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
        "extra_fields": [],
        "approval_text": approval_text,
        "sample_text": sample_text
    }

import pandas as pd

ALLOWED_EXTENSIONS = {"csv", "xlsx", "xls"}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def load_label_frame(file_path: str) -> pd.DataFrame:
    extension = os.path.splitext(file_path)[1].lower().lstrip(".")

    if extension == "csv":
        frame = pd.read_csv(file_path)
    else:
        frame = pd.read_excel(file_path)

    return frame


def extract_label_value(row: pd.Series) -> str:
    for candidate in ("label", "text", "value", "annotation"):
        if candidate in row.index:
            return str(row[candidate]).strip()

    if len(row.index) > 0:
        return str(row.iloc[-1]).strip()

    return ""


def compare_label_files(file_a: str, file_b: str) -> dict:
    frame_a = load_label_frame(file_a)
    frame_b = load_label_frame(file_b)

    labels_a = [extract_label_value(row) for _, row in frame_a.iterrows()]
    labels_b = [extract_label_value(row) for _, row in frame_b.iterrows()]

    total_rows_a = len(labels_a)
    total_rows_b = len(labels_b)
    common_rows = min(total_rows_a, total_rows_b)

    mismatches = []
    for index in range(common_rows):
        left = labels_a[index]
        right = labels_b[index]
        if left != right:
            mismatches.append({
                "row": index + 1,
                "file_a": left,
                "file_b": right,
            })

    if total_rows_a > total_rows_b:
        for index in range(total_rows_b, total_rows_a):
            mismatches.append({
                "row": index + 1,
                "file_a": labels_a[index],
                "file_b": "<missing>",
            })
    elif total_rows_b > total_rows_a:
        for index in range(total_rows_a, total_rows_b):
            mismatches.append({
                "row": index + 1,
                "file_a": "<missing>",
                "file_b": labels_b[index],
            })

    return {
        "file_a_rows": total_rows_a,
        "file_b_rows": total_rows_b,
        "common_rows": common_rows,
        "mismatch_count": len(mismatches),
        "mismatches": mismatches,
    }

