import cv2
import pytesseract
import difflib
import re
import os
import pandas as pd
import pdfplumber
from docx import Document


IMAGE_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".bmp",
    ".tif",
    ".tiff",
    ".webp"
}


def extract_text(file_path):

    ext = os.path.splitext(file_path)[1].lower()

    try:

        if ext in IMAGE_EXTENSIONS:
            return extract_image_text(file_path)

        elif ext == ".pdf":
            return extract_pdf_text(file_path)

        elif ext == ".docx":
            return extract_docx_text(file_path)

        elif ext in [".xls", ".xlsx"]:
            return extract_excel_text(file_path)

        elif ext == ".csv":
            return extract_csv_text(file_path)

        elif ext == ".txt":
            return extract_txt_text(file_path)

        else:
            return ""

    except Exception as e:
        return f"READ ERROR : {str(e)}"


def extract_image_text(image_path):

    image = cv2.imread(image_path)

    if image is None:
        return ""

    h, w = image.shape[:2]

    if w > 1000:

        ratio = 1000 / w

        image = cv2.resize(
            image,
            (
                1000,
                int(h * ratio)
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

    gray = cv2.threshold(
        gray,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )[1]

    text = pytesseract.image_to_string(
        gray,
        lang="eng",
        config="--oem 3 --psm 6"
    )

    return text.strip()


def extract_pdf_text(pdf_path):

    text = ""

    with pdfplumber.open(pdf_path) as pdf:

        for page in pdf.pages:

            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

    return text


def extract_docx_text(doc_path):

    doc = Document(doc_path)

    text = []

    for para in doc.paragraphs:
        text.append(para.text)

    return "\n".join(text)


def extract_excel_text(excel_path):

    df = pd.read_excel(
        excel_path,
        header=None
    )

    return df.astype(str).to_string()


def extract_csv_text(csv_path):

    df = pd.read_csv(
        csv_path,
        header=None
    )

    return df.astype(str).to_string()


def extract_txt_text(txt_path):

    with open(
        txt_path,
        "r",
        encoding="utf-8",
        errors="ignore"
    ) as f:

        return f.read()


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


def extract_barcode(text):

    match = re.search(
        r'\b\d{12,14}\b',
        text
    )

    if match:
        return match.group()

    return "NOT FOUND"


def extract_weight(text):

    match = re.search(
        r'(\d+(\.\d+)?)\s?(kg|g|mg|ml|l)',
        text,
        re.IGNORECASE
    )

    if match:
        return match.group()

    return "NOT FOUND"


def extract_dates(text):

    dates = re.findall(
        r'(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
        text
    )

    mfg = dates[0] if len(dates) > 0 else "NOT FOUND"
    exp = dates[1] if len(dates) > 1 else "NOT FOUND"

    return mfg, exp


def extract_brand_name(text):

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    return lines[0] if lines else "NOT FOUND"


def extract_product_name(text):

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    return lines[1] if len(lines) > 1 else "NOT FOUND"


def check_logo(
    approval_path,
    sample_path
):

    ext1 = os.path.splitext(
        approval_path
    )[1].lower()

    ext2 = os.path.splitext(
        sample_path
    )[1].lower()

    if ext1 not in IMAGE_EXTENSIONS:
        return "NOT IMAGE FILE"

    if ext2 not in IMAGE_EXTENSIONS:
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

        orb = cv2.ORB_create(1000)

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
            if m.distance < 50
        ]

        similarity = (
            len(good_matches)
            / max(len(kp1), len(kp2))
        ) * 100

        similarity = round(
            similarity,
            2
        )

        if similarity >= 60:
            return f"MATCH ({similarity}%)"

        return f"MISMATCH ({similarity}%)"

    except Exception as e:

        return f"FAILED ({str(e)})"


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
            approval_words &
            sample_words
        )
    )

    missing_words = sorted(
        list(
            approval_words -
            sample_words
        )
    )

    extra_words = sorted(
        list(
            sample_words -
            approval_words
        )
    )

    verdict = (
        "APPROVED"
        if similarity >= 85
        else "NOT APPROVED"
    )

    return {

        "verdict": verdict,
        "similarity": similarity,
        "logo_status": check_logo(
            approval_path,
            sample_path
        ),

        "approval_text": approval_text,
        "sample_text": sample_text,

        "approval_brand": extract_brand_name(
            approval_text
        ),

        "sample_brand": extract_brand_name(
            sample_text
        ),

        "approval_product": extract_product_name(
            approval_text
        ),

        "sample_product": extract_product_name(
            sample_text
        ),

        "approval_barcode": extract_barcode(
            approval_text
        ),

        "sample_barcode": extract_barcode(
            sample_text
        ),

        "approval_weight": extract_weight(
            approval_text
        ),

        "sample_weight": extract_weight(
            sample_text
        ),

        "approval_mfg": extract_dates(
            approval_text
        )[0],

        "sample_mfg": extract_dates(
            sample_text
        )[0],

        "approval_exp": extract_dates(
            approval_text
        )[1],

        "sample_exp": extract_dates(
            sample_text
        )[1],

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