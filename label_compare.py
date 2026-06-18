from pydoc import text

import cv2
import pytesseract
import difflib
import re
import os
import platform

if platform.system() == "Windows":
    pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Users\Maharajan\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
)

import pdfplumber
import pandas as pd

from docx import Document


# =========================
# TEXT EXTRACTION
# =========================

def extract_text(file_path):

    ext = os.path.splitext(
        file_path
    )[1].lower()

    try:

        # TXT
        if ext == ".txt":

            with open(
                file_path,
                "r",
                encoding="utf-8",
                errors="ignore"
            ) as f:

                return f.read()

        # CSV
        elif ext == ".csv":

            df = pd.read_csv(
                file_path,
                dtype=str,
                keep_default_na=False
            )

            return df.to_string(
                index=False
            )

        # XLS
        elif ext == ".xls":

            df = pd.read_excel(
                file_path,
                dtype=str,
                engine="xlrd"
            )

            return df.to_string(
                index=False
            )

        # XLSX
        elif ext == ".xlsx":

            df = pd.read_excel(
                file_path,
                dtype=str,
                engine="openpyxl"
            )

            return df.to_string(
                index=False
            )

        # DOCX
        elif ext == ".docx":

            doc = Document(
                file_path
            )

            text = []

            for para in doc.paragraphs:

                if para.text.strip():

                    text.append(
                        para.text.strip()
                    )

            return "\n".join(
                text
            )

        # PDF
        elif ext == ".pdf":

            text = ""

            with pdfplumber.open(
                file_path
            ) as pdf:

                for page in pdf.pages:

                    page_text = (
                        page.extract_text()
                    )

                    if page_text:

                        text += (
                            page_text
                            + "\n"
                        )

            return text

        # IMAGE FILES
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

            image = cv2.imread(
                file_path
            )

            if image is None:

                return ""

            image = cv2.resize(
                image,
                None,
                fx=2,
                fy=2,
                interpolation=cv2.INTER_CUBIC
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

            _, gray = cv2.threshold(
                gray,
                150,
                255,
                cv2.THRESH_BINARY
            )

        text = pytesseract.image_to_string(
                gray,
                lang="eng",
                config="--oem 3 --psm 6"
            )

        return text

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

        orb = cv2.ORB_create(
            500
        )

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

            return (
                f"MATCH ({similarity}%)"
            )

        else:

            return (
                f"MISMATCH ({similarity}%)"
            )

    except Exception as e:

        return (
            f"FAILED ({str(e)})"
        )
    

# =========================
# CONSTRAINT CHECKING
# =========================


from difflib import SequenceMatcher
import re

def clean_text(text):
    text = text.lower()

    text = re.sub(
        r'[^a-z0-9\s]',
        ' ',
        text
    )

    text = ' '.join(
        text.split()
    )

    return text

def fuzzy_exists(text, phrase):

    words = text.split()

    phrase_words = phrase.split()

    size = len(phrase_words)

    for i in range(len(words) - size + 1):

        chunk = " ".join(
            words[i:i+size]
        )

        score = SequenceMatcher(
            None,
            chunk,
            phrase
        ).ratio()

        if score >= 0.70:
            print("MATCH:",chunk,phrase,score)

        if score >= 0.80:
            return True
        

    return False

def check_constraints(
    approval_text,
    sample_text
):

    approval_clean = clean_text(
        approval_text
    )

    sample_clean = clean_text(
        sample_text
    )

    constraints = [
        "F&F",
        "UK",
        "EUR",
        "6-9M",
        "up to 1m",
        "56cm",
        "22in",
        "4.5kg",
        "10lbs",
        "41.5cm",
        "5063637905105",
        "UK EAN",
        "CE EAN",
        "100%",
        "910-3758",
        "made in bangladesh"
    ]

    matched_constraints = []
    missing_constraints = []
    extra_constraints = []

    for item in constraints:

        item_clean = clean_text(item)

        if item_clean in sample_clean:
            matched_constraints.append(item)
        else:
            missing_constraints.append(item)

    sample_words = set(sample_clean.split())

    for word in sample_words:

        found = False

        for item in constraints:

            if word in clean_text(item):
                found = True
                break

        if not found and len(word) > 2:
            extra_constraints.append(word)

    return {
        "matched_constraints": matched_constraints,
        "missing_constraints": missing_constraints,
        "extra_constraints": extra_constraints,
        "matched_constraints_count":
            len(matched_constraints),

        "missing_constraints_count":
            len(missing_constraints)
    }
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

    # Similarity %

    similarity = round(

        difflib.SequenceMatcher(

            None,

            approval_clean,

            sample_clean

        ).ratio() * 100,

        2

    )

    # Word Comparison

    approval_words = set(

        word

        for word in approval_clean.split()

        if len(word) > 1

    )

    sample_words = set(

        word

        for word in sample_clean.split()

        if len(word) > 1

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

    # Logo Check

    logo_status = check_logo(
        approval_path,
        sample_path
    )

    # Constraint Check

    constraint_result = check_constraints(
        approval_text,
        sample_text
    )

    total_constraints = (
        constraint_result["matched_constraints_count"]
        +
        constraint_result["missing_constraints_count"]
    )

    constraint_score = round(
        (   
            constraint_result["matched_constraints_count"]
            /
            max(total_constraints, 1)
        ) * 100,
        2


    )

# Verdict
    if constraint_result["missing_constraints_count"] == 0:

        verdict = "APPROVED"

    else:

        verdict = "NOT APPROVED"

    # Detailed Table

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

    result ={
        # Result
        "verdict": verdict,

        "similarity": constraint_score,
        "logo_status": logo_status,
        # OCR Text
        "approval_text": approval_text,
        "sample_text": sample_text,
            # Word Comparison
        "matched_words": matched_words,
        "missing_words": missing_words,
        "extra_words": extra_words,
        "matched_count": len(matched_words),
        "missing_count": len(missing_words),
        "extra_count": len(extra_words),
        # Constraint Results

        "matched_constraints":

            constraint_result["matched_constraints"],
        "missing_constraints":
            constraint_result["missing_constraints"],
        "extra_constraints":

            constraint_result["extra_constraints"],
        "matched_constraints_count":
            constraint_result["matched_constraints_count"],
        "missing_constraints_count":
            constraint_result["missing_constraints_count"],

        # Table

        "comparison_table":comparison_table}
    return result  
            