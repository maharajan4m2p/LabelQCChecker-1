import cv2
import pytesseract
import difflib
import re


def extract_text(image_path):

    try:

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

        text = pytesseract.image_to_string(
            gray,
            lang="eng",
            config="--oem 3 --psm 6",
            timeout=60
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


def extract_barcode(text):

    match = re.search(
        r'\b\d{12,14}\b',
        text
    )

    return match.group() if match else "NOT FOUND"


def extract_weight(text):

    match = re.search(
        r'(\d+(\.\d+)?)\s?(kg|g|mg|ml|l)',
        text,
        re.IGNORECASE
    )

    return match.group() if match else "NOT FOUND"


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
        x.strip()
        for x in text.splitlines()
        if x.strip()
    ]

    if len(lines) > 0:
        return lines[0]

    return "NOT FOUND"


def extract_product_name(text):

    lines = [
        x.strip()
        for x in text.splitlines()
        if x.strip()
    ]

    if len(lines) > 1:
        return lines[1]

    return "NOT FOUND"


def check_logo(
    approval_path,
    sample_path
):

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
            m
            for m in matches
            if m.distance < 50
        ]

        similarity = (
            len(good_matches)
            /
            max(
                len(kp1),
                len(kp2)
            )
        ) * 100

        similarity = round(
            similarity,
            2
        )

        if similarity >= 60:
            return f"MATCH ({similarity}%)"

        return f"MISMATCH ({similarity}%)"

    except Exception:

        return "LOGO CHECK FAILED"


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

    approval_brand = extract_brand_name(
        approval_text
    )

    sample_brand = extract_brand_name(
        sample_text
    )

    approval_product = extract_product_name(
        approval_text
    )

    sample_product = extract_product_name(
        sample_text
    )

    approval_barcode = extract_barcode(
        approval_text
    )

    sample_barcode = extract_barcode(
        sample_text
    )

    approval_weight = extract_weight(
        approval_text
    )

    sample_weight = extract_weight(
        sample_text
    )

    approval_mfg, approval_exp = extract_dates(
        approval_text
    )

    sample_mfg, sample_exp = extract_dates(
        sample_text
    )

    logo_status = check_logo(
        approval_path,
        sample_path
    )

    verdict = (
        "APPROVED"
        if similarity >= 85
        else "NOT APPROVED"
    )

    return {

        "verdict": verdict,

        "similarity": similarity,

        "logo_status": logo_status,

        "approval_text": approval_text,
        "sample_text": sample_text,

        "approval_brand": approval_brand,
        "sample_brand": sample_brand,

        "approval_product": approval_product,
        "sample_product": sample_product,

        "approval_barcode": approval_barcode,
        "sample_barcode": sample_barcode,

        "approval_weight": approval_weight,
        "sample_weight": sample_weight,

        "approval_mfg": approval_mfg,
        "sample_mfg": sample_mfg,

        "approval_exp": approval_exp,
        "sample_exp": sample_exp,

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