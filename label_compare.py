# ============================================================
# label_compare.py — Complete Fixed Version
# ============================================================

import cv2
import re
import pytesseract
from PIL        import Image
from langdetect import detect, DetectorFactory

DetectorFactory.seed = 0

# ============================================================
# PART A — LANGUAGE MAPS
# ============================================================

LANG_MAP = {
    'en'   : 'eng',
    'cs'   : 'ces',
    'sk'   : 'slk',
    'hu'   : 'hun',
    'de'   : 'deu',
    'fr'   : 'fra',
    'es'   : 'spa',
    'it'   : 'ita',
    'pt'   : 'por',
    'pl'   : 'pol',
    'nl'   : 'nld',
    'sv'   : 'swe',
    'no'   : 'nor',
    'da'   : 'dan',
    'fi'   : 'fin',
    'ro'   : 'ron',
    'bg'   : 'bul',
    'hr'   : 'hrv',
    'sr'   : 'srp',
    'uk'   : 'ukr',
    'ru'   : 'rus',
    'ar'   : 'ara',
    'hi'   : 'hin',
    'zh-cn': 'chi_sim',
    'zh-tw': 'chi_tra',
    'ja'   : 'jpn',
    'ko'   : 'kor',
    'tr'   : 'tur',
    'vi'   : 'vie',
    'th'   : 'tha',
    'id'   : 'ind',
}

LANG_NAMES = {
    'eng'    : 'English',
    'ces'    : 'Czech',
    'slk'    : 'Slovak',
    'hun'    : 'Hungarian',
    'deu'    : 'German',
    'fra'    : 'French',
    'spa'    : 'Spanish',
    'ita'    : 'Italian',
    'por'    : 'Portuguese',
    'pol'    : 'Polish',
    'nld'    : 'Dutch',
    'swe'    : 'Swedish',
    'nor'    : 'Norwegian',
    'dan'    : 'Danish',
    'fin'    : 'Finnish',
    'ron'    : 'Romanian',
    'bul'    : 'Bulgarian',
    'hrv'    : 'Croatian',
    'srp'    : 'Serbian',
    'ukr'    : 'Ukrainian',
    'rus'    : 'Russian',
    'ara'    : 'Arabic',
    'hin'    : 'Hindi',
    'chi_sim': 'Chinese (Simplified)',
    'chi_tra': 'Chinese (Traditional)',
    'jpn'    : 'Japanese',
    'kor'    : 'Korean',
    'tur'    : 'Turkish',
    'vie'    : 'Vietnamese',
    'tha'    : 'Thai',
    'ind'    : 'Indonesian',
}

# ============================================================
# PART B — IMAGE PREPROCESSING
# ============================================================

def preprocess_image(path):
    img = cv2.imread(path)
    if img is None:
        raise ValueError(f"Cannot read image at path: {path}")

    # Resize 2x for better OCR accuracy
    img = cv2.resize(
        img, None, fx=2, fy=2,
        interpolation=cv2.INTER_CUBIC
    )

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Enhance contrast with CLAHE
    clahe    = cv2.createCLAHE(
        clipLimit=2.0, tileGridSize=(8, 8)
    )
    enhanced = clahe.apply(gray)

    # Threshold — pure black and white
    _, thresh = cv2.threshold(
        enhanced, 150, 255, cv2.THRESH_BINARY
    )

    return thresh

# ============================================================
# PART C — LANGUAGE DETECTION
# ============================================================

def detect_languages(path):
    processed = preprocess_image(path)
    pil_img   = Image.fromarray(processed)

    # First pass — English only to get raw text
    raw_text = pytesseract.image_to_string(
        pil_img,
        config=r'--oem 3 --psm 6 -l eng'
    )

    # Always include English
    detected = set(['eng'])

    # Method 1 — line by line language detection
    for line in raw_text.splitlines():
        line = line.strip()
        if len(line) > 8:
            try:
                code = detect(line)
                tl   = LANG_MAP.get(code)
                if tl:
                    detected.add(tl)
            except Exception:
                pass

    # Method 2 — Unicode script detection
    if re.search(r'[\u0400-\u04FF]', raw_text):
        detected.add('rus')
    if re.search(r'[\u0600-\u06FF]', raw_text):
        detected.add('ara')
    if re.search(r'[\u0900-\u097F]', raw_text):
        detected.add('hin')
    if re.search(r'[\u4E00-\u9FFF]', raw_text):
        detected.add('chi_sim')
    if re.search(r'[\u3040-\u309F]', raw_text):
        detected.add('jpn')
    if re.search(r'[\uAC00-\uD7AF]', raw_text):
        detected.add('kor')
    if re.search(r'[\u0E00-\u0E7F]', raw_text):
        detected.add('tha')

    # Method 3 — keyword detection
    keyword_langs = [
        (r'UCHOVÁVEJTE|měsíce|Vyrobeno',  'ces'),
        (r'UCHOVÁVAJTE|mesiaca|Vyrobené', 'slk'),
        (r'TŰZTŐL|TARTANDÓ|hónap',        'hun'),
        (r'Fabriqué|flammes|conserver',   'fra'),
        (r'Hergestellt|Feuer|fernhalten', 'deu'),
        (r'Fabricado|fuego|alejar',       'spa'),
        (r'Prodotto|fuoco|tenere',        'ita'),
        (r'Feito|fogo|longe',             'por'),
        (r'Przechowywać|ognia|dzieci',    'pol'),
        (r'Houd|vuur|verwijderd',         'nld'),
    ]
    for pattern, lang in keyword_langs:
        if re.search(pattern, raw_text, re.IGNORECASE):
            detected.add(lang)

    return list(detected), raw_text

# ============================================================
# PART D — FULL OCR WITH ALL DETECTED LANGUAGES
# ============================================================

def extract_text(path):
    detected_langs, _ = detect_languages(path)

    # Combine all languages e.g. "eng+ces+slk+hun"
    lang_str  = '+'.join(detected_langs)

    processed = preprocess_image(path)
    pil_img   = Image.fromarray(processed)

    text = pytesseract.image_to_string(
        pil_img,
        config=f'--oem 3 --psm 6 -l {lang_str}'
    )

    lang_names = [
        LANG_NAMES.get(l, l) for l in detected_langs
    ]

    return text, lang_names

# ============================================================
# PART E — UNIVERSAL FIELD PARSER
# ============================================================

def parse_fields(text):
    fields = {}
    lines  = [
        l.strip()
        for l in text.splitlines()
        if l.strip()
    ]

    # ── EAN / Barcode numbers ──────────────────────────────
    for line in lines:
        uk = re.search(
            r'UK\s*EAN[:\s]*([\d]{8,14})',
            line, re.IGNORECASE
        )
        ce = re.search(
            r'CE\s*EAN[:\s]*([\d]{8,14})',
            line, re.IGNORECASE
        )
        ean = re.search(
            r'\bEAN[:\s]*([\d]{8,14})',
            line, re.IGNORECASE
        )
        upc = re.search(
            r'\bUPC[:\s]*([\d]{8,14})',
            line, re.IGNORECASE
        )
        if uk:
            fields['UK EAN'] = uk.group(1)
        if ce:
            fields['CE EAN'] = ce.group(1)
        if ean and 'UK EAN' not in fields:
            fields['EAN'] = ean.group(1)
        if upc:
            fields['UPC'] = upc.group(1)

    # ── Size ───────────────────────────────────────────────
    size = re.search(
        r'(up\s*to\s*[\w\s]+(?:m|cm|yr|year|month))',
        text, re.IGNORECASE
    )
    if size:
        fields['Size'] = size.group(1).strip()

    # ── Body Measurements ─────────────────────────────────
    for label, key in [
        ('Height', 'Height'),
        ('Weight', 'Weight'),
        ('Waist',  'Waist'),
        ('Chest',  'Chest'),
        ('Length', 'Length'),
        ('Hip',    'Hip'),
    ]:
        m = re.search(
            rf'{label}[:\s]*([\d.]+\s*'
            rf'(?:cm|kg|g)[^\n]{{0,20}})',
            text, re.IGNORECASE
        )
        if m:
            fields[key] = m.group(1).strip()

    # ── Article / SKU ──────────────────────────────────────
    art = re.search(r'\b(\d{3,4}[-]\d{3,6})\b', text)
    if art:
        fields['Article No.'] = art.group(1)

    sku = re.search(
        r'(?:SKU|Style|Ref)[:\s#]*([\w\d\-]+)',
        text, re.IGNORECASE
    )
    if sku:
        fields['SKU/Style'] = sku.group(1).strip()

    # ── Brand ─────────────────────────────────────────────
    for line in lines:
        if (
            re.match(r'^[A-Z][A-Z&\s]{1,15}$', line)
            and len(line) <= 15
        ):
            fields['Brand'] = line
            break

    # ── Safety Warnings English ───────────────────────────
    if re.search(
        r'KEEP\s*AWAY\s*FROM\s*FIRE',
        text, re.IGNORECASE
    ):
        fields['Fire Warning (EN)'] = 'KEEP AWAY FROM FIRE'

    if re.search(
        r'KEEP\s*AWAY\s*FROM\s*HEAT',
        text, re.IGNORECASE
    ):
        fields['Heat Warning (EN)'] = 'KEEP AWAY FROM HEAT'

    if re.search(
        r'choking\s*hazard',
        text, re.IGNORECASE
    ):
        fields['Choking Hazard'] = 'CHOKING HAZARD PRESENT'

    if re.search(
        r'not\s*suitable\s*for\s*children',
        text, re.IGNORECASE
    ):
        m = re.search(
            r'(not\s*suitable[^\n]+)',
            text, re.IGNORECASE
        )
        if m:
            fields['Age Warning'] = m.group(1).strip()

    # ── Safety Warnings European ──────────────────────────
    warn_patterns = [
        (
            r'UCHOVÁVEJTE\s*MIMO\s*DOSAH',
            'Fire Warning (CZ)',
            r'(UCHOVÁVEJTE[^\n]+)'
        ),
        (
            r'UCHOVÁVAJTE\s*MIMO\s*DOSAH',
            'Fire Warning (SK)',
            r'(UCHOVÁVAJTE[^\n]+)'
        ),
        (
            r'TŰZTŐL',
            'Fire Warning (HU)',
            r'(TŰZTŐL[^\n]+)'
        ),
        (
            r'VON\s*FEUER\s*FERNHALTEN',
            'Fire Warning (DE)',
            r'(VON\s*FEUER[^\n]+)'
        ),
        (
            r'TENIR\s*ÉLOIGNÉ\s*DU\s*FEU',
            'Fire Warning (FR)',
            r'(TENIR[^\n]+)'
        ),
        (
            r'MANTENER\s*ALEJADO',
            'Fire Warning (ES)',
            r'(MANTENER[^\n]+)'
        ),
        (
            r'TENERE\s*LONTANO',
            'Fire Warning (IT)',
            r'(TENERE[^\n]+)'
        ),
        (
            r'TRZYMAĆ\s*Z\s*DALA',
            'Fire Warning (PL)',
            r'(TRZYMAĆ[^\n]+)'
        ),
        (
            r'HOUD\s*WEG\s*VAN\s*VUUR',
            'Fire Warning (NL)',
            r'(HOUD[^\n]+)'
        ),
        (
            r'MANTER\s*AFASTADO',
            'Fire Warning (PT)',
            r'(MANTER[^\n]+)'
        ),
    ]

    for pattern, key, extract in warn_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            m = re.search(extract, text, re.IGNORECASE)
            if m:
                fields[key] = m.group(1).strip()

    # ── Material / Fabric ─────────────────────────────────
    fabric = re.search(
        r'(\d+%\s*(?:cotton|polyester|wool|nylon|'
        r'acrylic|viscose|elastane|spandex|linen|silk)'
        r'[^\n]*)',
        text, re.IGNORECASE
    )
    if fabric:
        fields['Material'] = fabric.group(1).strip()

    # ── Care Instructions ─────────────────────────────────
    care_patterns = [
        (r'machine\s*wash[^\n]*',    'Care - Wash'),
        (r'hand\s*wash[^\n]*',       'Care - Hand Wash'),
        (r'do\s*not\s*bleach',       'Care - Bleach'),
        (r'do\s*not\s*tumble[^\n]*', 'Care - Tumble Dry'),
        (r'dry\s*clean[^\n]*',       'Care - Dry Clean'),
        (r'do\s*not\s*iron',         'Care - Iron'),
        (r'iron\s*on\s*low[^\n]*',   'Care - Iron Temp'),
        (r'do\s*not\s*wring',        'Care - Wringing'),
    ]
    for pattern, key in care_patterns:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            fields[key] = m.group(0).strip()

    # ── Sustainability ────────────────────────────────────
    recycled = re.search(
        r'(\d+)%\s*of\s*the\s*polyester',
        text, re.IGNORECASE
    )
    if recycled:
        fields['Recycled Content'] = (
            recycled.group(1) + '% polyester recycled'
        )

    organic = re.search(
        r'(\d+)%\s*organic',
        text, re.IGNORECASE
    )
    if organic:
        fields['Organic Content'] = (
            organic.group(1) + '% organic'
        )

    if re.search(r'recycl', text, re.IGNORECASE):
        fields['Recycle Symbol'] = 'Present'

    # ── Certifications ────────────────────────────────────
    for cert in [
        'OEKO-TEX', 'GOTS', 'FSC',
        'ISO 9001', 'FCC', 'RoHS', 'REACH'
    ]:
        if re.search(cert, text, re.IGNORECASE):
            fields[f'Cert: {cert}'] = 'Present'

    # ── Country of Origin ─────────────────────────────────
    origin = re.search(
        r'Made\s*in\s+([A-Za-z\s]+)',
        text, re.IGNORECASE
    )
    if origin:
        fields['Made In'] = origin.group(1).strip()

    # ── Legal Numbers ─────────────────────────────────────
    rn = re.search(
        r'RN[:\s#]*(\d+)',
        text, re.IGNORECASE
    )
    if rn:
        fields['RN No.'] = rn.group(1)

    ca = re.search(
        r'\bCA[:\s#]*(\d+)',
        text, re.IGNORECASE
    )
    if ca:
        fields['CA No.'] = ca.group(1)

    # ── Batch / Expiry ────────────────────────────────────
    batch = re.search(
        r'(?:Batch|Lot)[:\s#]*([\w\d\-]+)',
        text, re.IGNORECASE
    )
    if batch:
        fields['Batch/Lot No.'] = batch.group(1).strip()

    expiry = re.search(
        r'(?:Expiry|Best Before|Use By)[:\s]*([\d/\-\.]+)',
        text, re.IGNORECASE
    )
    if expiry:
        fields['Expiry Date'] = expiry.group(1).strip()
    # ── Net Weight / Volume ─────────────────────────────
    net_wt = re.search(
        r'(?:Net\s*Weight|Net\s*Wt)'
        r'[:\s]*([\d.]+\s*(?:g|kg|oz|lb))',
        text, re.IGNORECASE
    )
    if net_wt:
        fields['Net Weight'] = net_wt.group(1).strip()
    net_vol = re.search(
        r'(?:Net\s*Volume|Vol)'
        r'[:\s]*([\d.]+\s*(?:ml|l|fl\s*oz))',
        text, re.IGNORECASE
    )
    if net_vol:
        fields['Net Volume'] = net_vol.group(1).strip()
    # ── Generic Key:Value Fallback ────────────────────────
    for line in lines:
        kv = re.match(
            r'^([A-Za-z][A-Za-z\s]{2,25})[:\-]\s*(.+)$',
            line
        )
        if kv:
            k = kv.group(1).strip().title()
            v = kv.group(2).strip()
            if k not in fields and len(v) < 80:
                fields[f'[Auto] {k}'] = v

    return fields

# ============================================================
# PART F — MAIN COMPARISON FUNCTION
# Called by app.py
# ============================================================

def compare_label_images(approval_path, sample_path):
    try:
        # Extract text from both labels
        approval_text, approval_langs = extract_text(approval_path)
        sample_text,   sample_langs   = extract_text(sample_path)

        # Parse fields from both labels
        approval_fields = parse_fields(approval_text)
        sample_fields   = parse_fields(sample_text)

        rows       = []
        matched    = 0
        mismatched = 0
        missing    = 0

        # Compare every field
        for field, approved_val in approval_fields.items():
            sample_val = sample_fields.get(field, "")

            if not sample_val:
                status = "MISSING"
                missing += 1
            elif (
                approved_val.strip().lower()
                != sample_val.strip().lower()
            ):
                status = "MISMATCH"
                mismatched += 1
            else:
                status = "MATCH"
                matched += 1

            rows.append({
                "field":        field,
                "approved_val": approved_val,
                "sample_val":   sample_val,
                "status":       status,
            })

        # Final verdict
        verdict = (
            "NOT APPROVED"
            if (missing + mismatched) > 0
            else "APPROVED"
        )

        return {
            "verdict":        verdict,
            "matched":        matched,
            "mismatched":     mismatched,
            "missing":        missing,
            "rows":           rows,
            "approval_langs": approval_langs,
            "sample_langs":   sample_langs,
            "issues": [
                r for r in rows
                if r["status"] != "MATCH"
            ],
        }

    except Exception as e:
        # Returns error safely without crashing server
        return {
            "verdict":        "ERROR",
            "matched":        0,
            "mismatched":     0,
            "missing":        0,
            "rows":           [],
            "approval_langs": [],
            "sample_langs":   [],
            "issues":         [],
            "error":          str(e),
        }