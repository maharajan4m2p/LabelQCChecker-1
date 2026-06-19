import os
import re
import cv2
import difflib
import platform
import pytesseract
import pdfplumber
import pandas as pd

from docx import Document
from difflib import SequenceMatcher


if platform.system() == "Windows":
    pytesseract.pytesseract.tesseract_cmd = r"C:\Users\Maharajan\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"


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

        elif ext in [".xls", ".xlsx"]:

            df = pd.read_excel(
                file_path,
                dtype=str
            )

            return df.to_string(index=False)

        elif ext == ".docx":

            doc = Document(file_path)

            text = []

            for para in doc.paragraphs:

                if para.text.strip():
                    text.append(para.text.strip())

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
            ".webp"
        ]:

            image = cv2.imread(file_path)

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

            return pytesseract.image_to_string(
                gray,
                lang="eng",
                config="--oem 3 --psm 6"
            )

        return ""

    except Exception as e:

        return f"ERROR: {str(e)}"


def clean_text(text):

    text = text.lower()

    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()
CONSTRAINTS = [
    "up to 1m",
    "56cm",
    "22in",
    "4.5kg",
    "10lbs",
    "41.5cm",
    "5063637905105",
    "uk ean",
    "ce ean",
    "100%",
    "910-3758",
    "polyester",
    "100%",
    "recycled"
]


def check_logo(approval_path, sample_path):

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

        orb = cv2.ORB_create(500)

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
            m for m in matches
            if m.distance < 60
        ]

        similarity = round(
            (
                len(good_matches)
                /
                max(len(kp1), len(kp2))
            ) * 100,
            2
        )

        if similarity >= 40:
            return f"MATCH ({similarity}%)"

        return f"MISMATCH ({similarity}%)"

    except Exception as e:
        return f"FAILED ({str(e)})"


def check_constraints(
    approval_text,
    sample_text
):

    sample_clean = clean_text(
        sample_text
    )

    matched_constraints = []
    missing_constraints = []
    extra_constraints = []

    for item in CONSTRAINTS:

        item_clean = clean_text(item)

        if item_clean in sample_clean:
            matched_constraints.append(item)
        else:
            missing_constraints.append(item)

    return {

        "matched_constraints":
        matched_constraints,

        "missing_constraints":
        missing_constraints,

        "extra_constraints":
        extra_constraints,

        "matched_constraints_count":
        len(matched_constraints),

        "missing_constraints_count":
        len(missing_constraints)

    }


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
        SequenceMatcher(
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

# ===============================
# Side By Side Comparison Rows
# ===============================

    approval_list = approval_text.split()
    sample_list = sample_text.split()

    comparison_rows = []

    max_len = max(
    len(approval_list),
    len(sample_list)
)

    for i in range(max_len):

        approval_word = (
        approval_list[i]
        if i < len(approval_list)
        else ""
    )

    sample_word = (
        sample_list[i]
        if i < len(sample_list)
        else ""
    )

    if approval_word == sample_word:

        status = "matched"

    elif approval_word and not sample_word:

        status = "missing"

    elif sample_word and not approval_word:

        status = "extra"

    else:

        status = "different"

    comparison_rows.append({

        "approval": approval_word,

        "sample": sample_word,

        "status": status

    })
    
    comparison_rows = []

    approval_list = approval_clean.split()
    sample_list = sample_clean.split()

    max_len = max(
    len(approval_list),
    len(sample_list)
    )

    for i in range(max_len):

        approval_word = (
        approval_list[i]
        if i < len(approval_list)
        else ""
        )

    sample_word = (
        sample_list[i]
        if i < len(sample_list)
        else ""
    )

    if approval_word == sample_word:
        status = "matched"

    elif approval_word and not sample_word:
        status = "missing"

    elif sample_word and not approval_word:
        status = "extra"

    else:
        status = "different"

    comparison_rows.append({
        "approval": approval_word,
        "sample": sample_word,
        "status": status
    })

    logo_status = check_logo(
        approval_path,
        sample_path
    )

    constraint_result = check_constraints(
        approval_text,
        sample_text
    )

    if (
        constraint_result[
            "missing_constraints_count"
        ] == 0
        and similarity >= 90
    ):
        verdict = "APPROVED"
    else:
        verdict = "NOT APPROVED"

    result = {

        "similarity":
        similarity,

        "logo_status":
        logo_status,

        "approval_text":
        approval_text,

        "sample_text":
        sample_text,

        "matched_words":
        matched_words,

        "missing_words":
        missing_words,

        "extra_words":
        extra_words,

        "matched_count":
        len(matched_words),

        "missing_count":
        len(missing_words),

        "extra_count":
        len(extra_words),

        "matched_constraints":
        constraint_result[
            "matched_constraints"
        ],

        "missing_constraints":
        constraint_result[
            "missing_constraints"
        ],

        "extra_constraints":
        constraint_result[
            "extra_constraints"
        ],

        "matched_constraints_count":
        constraint_result[
            "matched_constraints_count"
        ],

        "missing_constraints_count":
        constraint_result[
            "missing_constraints_count"
        ],
        
        "comparison_rows":comparison_rows,

        "verdict":
        verdict

    }

    
    return result