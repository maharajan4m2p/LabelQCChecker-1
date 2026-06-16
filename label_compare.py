import cv2
import pytesseract
import difflib
import re
import os
import pdfplumber
import pandas as pd

from docx import Document


# =========================
# TEXT EXTRACTION
# =========================

def extract_text(file_path):

    ext = os.path.splitext(file_path)[1].lower()

    try:

        if ext == ".txt":

            with open(
                file_path,
                "r",
                encoding="utf-8",
                errors="ignore"
            ) as f:

                return f.read()

        elif ext == ".csv":

            df = pd.read_csv(
                file_path,
                dtype=str,
                keep_default_na=False
            )

            return df.to_string(index=False)

        elif ext == ".xls":

            df = pd.read_excel(
                file_path,
                dtype=str,
                engine="xlrd"
            )

            return df.to_string(index=False)

        elif ext == ".xlsx":

            df = pd.read_excel(
                file_path,
                dtype=str,
                engine="openpyxl"
            )

            return df.to_string(index=False)

        elif ext == ".docx":

            doc = Document(file_path)

            text = []

            for para in doc.paragraphs:

                if para.text.strip():

                    text.append(
                        para.text.strip()
                    )

            return "\n".join(text)

        elif ext == ".pdf":

            text = ""

            with pdfplumber.open(file_path) as pdf:

                for page in pdf.pages:

                    page_text = page.extract_text()

                    if page_text:

                        text += page_text + "\n"

            return text

        elif ext in [
            ".png",
            ".jpg",
            ".jpeg",
            ".bmp",
            ".tif",
            ".tiff",
            ".webp",
            ".gif"
        ]:

            image = cv2.imread(file_path)

            if image is None:

                return ""

            image = cv2.resize(
                image,
                None,
                fx=3,
                fy=3,
                interpolation=cv2.INTER_CUBIC
            )

            gray = cv2.cvtColor(
                image,
                cv2.COLOR_BGR2GRAY
            )

            gray = cv2.fastNlMeansDenoising(
                gray,
                None,
                30,
                7,
                21
            )

            gray = cv2.adaptiveThreshold(
                gray,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                31,
                11
            )

            text = pytesseract.image_to_string(
                gray,
                lang="eng",
                config="--oem 3 --psm 4"
            )

            return text

        return ""

    except Exception as e:

        return f"ERROR: {str(e)}"


# =========================
# CLEAN TEXT
# =========================

def clean_text(text):

    text = text.lower()

    text = re.sub(
        r"[^a-zA-Z0-9 ]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# =========================
# LOGO COMPARISON
# =========================

def check_logo(
    approval_path,
    sample_path
):

    image_extensions = [
        ".png",
        ".jpg",
        ".jpeg",
        ".bmp",
        ".tif",
        ".tiff",
        ".webp"
    ]

    approval_ext = os.path.splitext(
        approval_path
    )[1].lower()

    sample_ext = os.path.splitext(
        sample_path
    )[1].lower()

    if (
        approval_ext not in image_extensions
        or
        sample_ext not in image_extensions
    ):

        return "NOT IMAGE FILE"

    try:

        img1 = cv2.imread(
            approval_path,
            cv2.IMREAD_GRAYSCALE
        )

        img2 = cv2.imread(
            sample_path,
            cv2.IMREAD_GRAYSCALE
        )

        if img1 is None or img2 is None:

            return "LOGO NOT FOUND"

        orb = cv2.ORB_create(1500)

        kp1, des1 = orb.detectAndCompute(
            img1,
            None
        )

        kp2, des2 = orb.detectAndCompute(
            img2,
            None
        )

        if des1 is None or des2 is None:

            return "LOGO NOT DETECTED"

        bf = cv2.BFMatcher(
            cv2.NORM_HAMMING,
            crossCheck=True
        )

        matches = bf.match(
            des1,
            des2
        )

        good_matches = [
            m
            for m in matches
            if m.distance < 60
        ]

        denominator = max(
            len(kp1),
            len(kp2)
        )

        if denominator == 0:

            return "LOGO NOT DETECTED"

        similarity = round(
            (
                len(good_matches)
                /
                denominator
            ) * 100,
            2
        )

        if similarity >= 40:

            return f"MATCH ({similarity}%)"
        else:

            return f"MISMATCH ({similarity}%)"

    except Exception as e:

        return f"FAILED ({str(e)})"


# =========================
# MAIN COMPARISON
# =========================

# =========================
# MAIN COMPARISON
# =========================

def compare_labels(
    approval_path,
    sample_path
):

    # Extract Text
    approval_text = extract_text(
        approval_path
    )

    sample_text = extract_text(
        sample_path
    )

    # Clean Text
    approval_clean = clean_text(
        approval_text
    )

    sample_clean = clean_text(
        sample_text
    )

    # Similarity
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
        approval_words &
        sample_words
    )

    missing_words = sorted(
        approval_words -
        sample_words
    )

    extra_words = sorted(
        sample_words -
        approval_words
    )

    logo_status = check_logo(
        approval_path,
        sample_path
    )

    if (
        similarity >= 80
        and len(missing_words) <= 10
    ):
        verdict = "APPROVED"
    else:
        verdict = "NOT APPROVED"

    comparison_table = []

    for word in matched_words:
        comparison_table.append({
            "type": "MATCHED",
            "value": word
        })

    for word in missing_words:
        comparison_table.append({
            "type": "MISSING",
            "value": word
        })

    for word in extra_words:
        comparison_table.append({
            "type": "EXTRA",
            "value": word
        })

    return {

        "verdict": verdict,
        "similarity": similarity,
        "logo_status": logo_status,

        "approval_text": approval_text,
        "sample_text": sample_text,

        "matched_words": matched_words,
        "missing_words": missing_words,
        "extra_words": extra_words,

        "matched_count": len(matched_words),
        "missing_count": len(missing_words),
        "extra_count": len(extra_words),

        "matched_data": matched_words,
        "missing_data": missing_words,
        "extra_data": extra_words,

        "comparison_table": comparison_table
    }