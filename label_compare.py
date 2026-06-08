import os
import re
import base64
import json
import urllib.request
import urllib.parse
from PIL import Image
from difflib import SequenceMatcher
from io import BytesIO

# Windows local only
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


# ── OCR.space API ──────────────────────────────────────
def ocr_space_api(image):
    try:
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_base64 = base64.b64encode(
            buffered.getvalue()
        ).decode("utf-8")

        # Try engine 2 first, then engine 1
        for engine in [2, 1]:
            try:
                payload = urllib.parse.urlencode({
                    "base64Image": (
                        f"data:image/png;base64,{img_base64}"
                    ),
                    "apikey": "helloworld",
                    "language": "eng",
                    "isOverlayRequired": False,
                    "OCREngine": engine,
                    "scale": True,
                    "isTable": False
                }).encode("utf-8")

                req = urllib.request.Request(
                    "https://api.ocr.space/parse/image",
                    data=payload,
                    method="POST"
                )
                req.add_header(
                    "Content-Type",
                    "application/x-www-form-urlencoded"
                )

                with urllib.request.urlopen(
                    req, timeout=30
                ) as response:
                    result = json.loads(
                        response.read().decode("utf-8")
                    )

                print(f"[OCR] Engine {engine} result:", result)

                if result.get("ParsedResults"):
                    text = result[
                        "ParsedResults"
                    ][0]["ParsedText"]
                    if text and text.strip():
                        return text

            except Exception as e:
                print(
                    f"[OCR Engine {engine} ERROR] {str(e)}"
                )
                continue

        return ""

    except Exception as e:
        print(f"[OCR.space ERROR] {str(e)}")
        return ""


# ── Extract text from image ────────────────────────────
def extract_text(image_path):
    try:
        print(f"\n[OCR] Reading: {image_path}")

        image = Image.open(image_path)

        # Resize large images to save memory
        max_size = 1000
        if image.width > max_size or image.height > max_size:
            image.thumbnail(
                (max_size, max_size),
                Image.LANCZOS
            )

        # Convert to grayscale
        image = image.convert("L")

        if USE_TESSERACT:
            import pytesseract
            config = r"--oem 1 --psm 6"
            text = pytesseract.image_to_string(
                image, config=config
            )
        else:
            # Use OCR.space API on server
            text = ocr_space_api(image)

        print("[OCR] Extracted text:")
        print("-" * 40)
        print(text[:300] if text else "EMPTY")
        print("-" * 40)

        return text if text else ""

    except Exception as e:
        print(f"[OCR ERROR] {str(e)}")
        return ""


# ── Parse key fields from text ─────────────────────────
def parse_fields(text):
    fields = {}

    patterns = {
        "STYLE":   r"STYLE\s*[:\-]?\s*(.+)",
        "SIZE":    r"SIZE\s*[:\-]?\s*(.+)",
        "COLOR":   r"COLOR\s*[:\-]?\s*(.+)",
        "PO":      r"PO\s*[:\-]?\s*(.+)",
        "COUNTRY": r"COUNTRY\s*[:\-]?\s*(.+)",
        "FABRIC":  r"FABRIC\s*[:\-]?\s*(.+)",
        "RN":      r"RN\s*[:\-]?\s*(.+)"
    }

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        for key, pattern in patterns.items():
            if key in fields:
                continue
            match = re.search(
                pattern, line, re.IGNORECASE
            )
            if match:
                value = match.group(1).strip()
                if value:
                    fields[key] = value

    return fields


# ── Compare two label texts ────────────────────────────
def compare_labels(approval_text, sample_text):
    approval_fields = parse_fields(approval_text)
    sample_fields = parse_fields(sample_text)

    print("\n[FIELDS] Approval:", approval_fields)
    print("[FIELDS] Sample:  ", sample_fields)

    all_keys = (
        set(approval_fields.keys()) |
        set(sample_fields.keys())
    )

    results = []
    match_count = 0
    missing_fields = []
    extra_fields = []

    for key in sorted(all_keys):
        approval_value = approval_fields.get(key, "")
        sample_value = sample_fields.get(key, "")

        if sample_value == "" and approval_value != "":
            missing_fields.append(key)

        if approval_value == "" and sample_value != "":
            extra_fields.append(key)

        similarity = SequenceMatcher(
            None,
            approval_value.lower().strip(),
            sample_value.lower().strip()
        ).ratio()

        status = (
            "MATCH" if similarity >= 0.90
            else "MISMATCH"
        )

        if status == "MATCH":
            match_count += 1

        results.append({
            "field": key,
            "approval": approval_value or "-",
            "sample": sample_value or "-",
            "similarity": round(similarity * 100, 1),
            "status": status
        })

    total = len(all_keys)
    accuracy = (
        round((match_count / total) * 100, 2)
        if total > 0 else 0
    )

    return {
        "accuracy": accuracy,
        "match_count": match_count,
        "total_fields": total,
        "results": results,
        "missing_fields": missing_fields,
        "extra_fields": extra_fields
    }


# ── Main entry point ───────────────────────────────────
def compare_label_images(
    approval_image_path,
    sample_image_path
):
    print(f"\n{'='*50}")
    print(f"Approval : {approval_image_path}")
    print(f"Sample   : {sample_image_path}")
    print(f"{'='*50}")

    approval_text = extract_text(approval_image_path)
    sample_text = extract_text(sample_image_path)

    print("\n[TEXT] Approval:\n", approval_text[:200])
    print("\n[TEXT] Sample:\n", sample_text[:200])

    # If both empty return zero result
    if not approval_text and not sample_text:
        return {
            "accuracy": 0,
            "match_count": 0,
            "total_fields": 0,
            "results": [],
            "missing_fields": [],
            "extra_fields": []
        }

    return compare_labels(approval_text, sample_text)