"""
=========================================================
Label QC Checker Pro
OCR Engine
Version 2.0
=========================================================
"""

import os
import cv2
import numpy as np
import pytesseract
import pdfplumber
from pdf2image import convert_from_path
import imutils

from PIL import Image

from config import *

# ---------------------------------------------------------
# EasyOCR
# ---------------------------------------------------------

try:
    import easyocr

    EASYOCR_AVAILABLE = True

except ImportError:

    EASYOCR_AVAILABLE = False

# ---------------------------------------------------------
# Configure Tesseract
# ---------------------------------------------------------

if os.name == "nt":

    possible_paths = [

        r"C:\Program Files\Tesseract-OCR\tesseract.exe",

        r"C:\Users\Maharajan\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"

    ]

    for path in possible_paths:

        if os.path.exists(path):

            pytesseract.pytesseract.tesseract_cmd = path

            break

# ---------------------------------------------------------
# OCR Engine
# ---------------------------------------------------------

class OCREngine:

    def __init__(self):

        self.easy_reader = None

        if EASYOCR_AVAILABLE:

            try:

                print("Loading EasyOCR...")

                self.easy_reader = easyocr.Reader(

                    ['en'],

                    gpu=False

                )

                print("EasyOCR Loaded")

            except Exception as e:

                print("EasyOCR Failed")

                print(e)

                self.easy_reader = None

        else:

            print("EasyOCR Not Installed")
            # ---------------------------------------------------------
# Load Image
# ---------------------------------------------------------

    def load_image(self, image_path):

        image = cv2.imread(image_path)

        if image is None:

            raise Exception(
                f"Cannot load image : {image_path}"
            )

        return image


# ---------------------------------------------------------
# Resize Image
# ---------------------------------------------------------

    def resize(self, image):

        return cv2.resize(

            image,

            None,

            fx=OCR_SCALE,

            fy=OCR_SCALE,

            interpolation=cv2.INTER_CUBIC

        )


# ---------------------------------------------------------
# Convert To Gray
# ---------------------------------------------------------

    def gray(self, image):

        return cv2.cvtColor(

            image,

        cv2.COLOR_BGR2GRAY

    )


# ---------------------------------------------------------
# CLAHE Contrast
# ---------------------------------------------------------

    def clahe(self, gray):

        clahe = cv2.createCLAHE(

            clipLimit=2.5,

            tileGridSize=(8,8)

        )

        return clahe.apply(gray)


# ---------------------------------------------------------
# Noise Removal
# ---------------------------------------------------------

    def denoise(self, gray):

        return cv2.fastNlMeansDenoising(

            gray,

            None,

            10,

            7,

            21

        )


# ---------------------------------------------------------
# Sharpen
# ---------------------------------------------------------

    def sharpen(self, image):

        kernel = np.array(

            [

                [0,-1,0],

                [-1,5,-1],

                [0,-1,0]

            ]

        )

        return cv2.filter2D(

            image,

            -1,

            kernel

        )


# ---------------------------------------------------------
# Adaptive Threshold
# ---------------------------------------------------------

    def adaptive_threshold(self, gray):

            return cv2.adaptiveThreshold(

                gray,

                255,

                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,

                cv2.THRESH_BINARY,

                31,

                15

        )


# ---------------------------------------------------------
# Otsu Threshold
# ---------------------------------------------------------

    def otsu(self, gray):

        _, binary = cv2.threshold(

            gray,

            0,

            255,

            cv2.THRESH_BINARY + cv2.THRESH_OTSU

        )

        return binary

# ---------------------------------------------------------
# Morphological Open
# ---------------------------------------------------------

    def morph_open(self, image):

        kernel = np.ones((2, 2), np.uint8)

        return cv2.morphologyEx(

            image,

            cv2.MORPH_OPEN,

            kernel

        )


# ---------------------------------------------------------
# Morphological Close
# ---------------------------------------------------------

    def morph_close(self, image):

        kernel = np.ones((2, 2), np.uint8)

        return cv2.morphologyEx(

            image,

            cv2.MORPH_CLOSE,

            kernel

        )


# ---------------------------------------------------------
# Deskew Image
# ---------------------------------------------------------

    def deskew(self, image):

        gray = self.gray(image)

        gray = cv2.bitwise_not(gray)

        thresh = cv2.threshold(

            gray,

            0,

            255,

            cv2.THRESH_BINARY | cv2.THRESH_OTSU

        )[1]

        coords = np.column_stack(

            np.where(thresh > 0)

        )

        if len(coords) == 0:

            return image

        angle = cv2.minAreaRect(

            coords

        )[-1]

        if angle < -45:

            angle = -(90 + angle)

        else:

            angle = -angle

        return imutils.rotate_bound(

            image,

            angle

        )


# ---------------------------------------------------------
# Complete Preprocessing Pipeline
# ---------------------------------------------------------

    def preprocess(self, image):

        image = self.resize(image)

        image = self.deskew(image)

        gray = self.gray(image)

        gray = self.clahe(gray)

        gray = self.denoise(gray)

        gray = self.sharpen(gray)

        gray = self.adaptive_threshold(gray)
    
        gray = self.otsu(gray)
    
        gray = self.morph_open(gray)
    
        gray = self.morph_close(gray)

        return gray
# ---------------------------------------------------------
# Tesseract OCR
# ---------------------------------------------------------


    def tesseract_ocr(self, image):

        config = (
            f"--oem {OCR_OEM} "
            f"--psm {OCR_PSM} "
            f"-l {OCR_LANGUAGE} "
            "-c preserve_interword_spaces=1 "
            "-c tessedit_do_invert=0 "
            "-c textord_heavy_nr=1 "
            "-c textord_min_linesize=2.5 "
        )

        text = pytesseract.image_to_string(

            image,

            config=config

        )

        return text.strip()


# ---------------------------------------------------------
# OCR Confidence + Word Coordinates
# ---------------------------------------------------------

    def image_to_data(self,image):
        data = pytesseract.image_to_data(

        image,

        config=(
            f"--oem {OCR_OEM} "
            f"--psm {OCR_PSM} "
            "-c preserve_interword_spaces=1 "
        ),

        output_type=pytesseract.Output.DICT

        )
    

        words = []

        confidence = []

        total = len(data["text"])

        for i in range(total):

            word = str(data["text"][i]).strip()

            if word == "":
                continue

            try:
                conf = float(data["conf"][i])
            except:
                conf = 0

            if conf < 0:
                continue

            confidence.append(conf)

            words.append({

                "text": word,

                "confidence": round(conf, 2),

                "x": int(data["left"][i]),

                "y": int(data["top"][i]),

                "width": int(data["width"][i]),

                "height": int(data["height"][i])

            })

        if len(confidence):

            avg = round(

                sum(confidence) /

                len(confidence),

                2

            )

        else:

            avg = 0

        return {

            "confidence": avg,

            "words": words

        }

# ---------------------------------------------------------
# Filter Low Confidence Words
# ---------------------------------------------------------

    def filter_confidence(

        self,

        words,

        minimum=50

    ):

        filtered = []

        for word in words:

            if word["confidence"] >= minimum:

                filtered.append(word)

        return filtered

# ---------------------------------------------------------
# Remove Duplicate OCR Words
# ---------------------------------------------------------

    def remove_duplicate_words(

        self,

        words

    ):

        unique = []

        seen = set()

        for word in words:

            key = (

                word["text"].upper(),

                word["x"],

                word["y"]

            )

            if key not in seen:

                seen.add(key)

                unique.append(word)

        return unique

# ---------------------------------------------------------
# Final OCR Word Processing
# ---------------------------------------------------------

    def process_words(

        self,

        words

    ):

        words = self.filter_confidence(

            words,

            minimum=50

        )

        words = self.remove_duplicate_words(

            words

        )

        return words
    
# ---------------------------------------------------------
# EasyOCR
# ---------------------------------------------------------

    def easyocr_data(self, image):

        if self.easy_reader is None:

            return []

        result = self.easy_reader.readtext(image)

        words = []

        for item in result:

            box = item[0]

            text = item[1]

            score = item[2]

            x = int(box[0][0])

            y = int(box[0][1])

            w = int(box[2][0] - box[0][0])

            h = int(box[2][1] - box[0][1])

            words.append({

                "text": text,

                "confidence": round(score * 100, 2),

                "x": x,

                "y": y,

                "width": w,

                "height": h

            })

        return words


# ---------------------------------------------------------
# Draw OCR Bounding Boxes
# ---------------------------------------------------------

    def draw_boxes(self, image, words):

        output = image.copy()

        for item in words:

            x = item["x"]

            y = item["y"]

            w = item["width"]

            h = item["height"]

            cv2.rectangle(

                output,

                (x, y),

                (x + w, y + h),

                GREEN,

                2

            )

            cv2.putText(

                output,

                item["text"],

                (x, y - 5),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.5,

                BLUE,

                1

            )

        return output
# ---------------------------------------------------------
# OCR Image
# ---------------------------------------------------------

    def read_image(self, image_path):

        image = self.load_image(image_path)

        processed = self.preprocess(image)

        text = self.tesseract_ocr(processed)
    
        text = self.normalize_text(text)

        data = self.image_to_data(processed)

        data["words"] = self.filter_confidence(

        data["words"],

        minimum=50

        )
        data["words"] = self.process_words(

            data["words"]

        )

        easy_words = self.easyocr_data(processed)

        if len(easy_words) > len(data["words"]):

            words = easy_words

        else:

            words = data["words"]

        return {

            "image": image,

            "processed": processed,

            "text": text,

            "confidence": data["confidence"],

            "words": words

        }


# ---------------------------------------------------------
# OCR PDF
# ---------------------------------------------------------

    def read_pdf(self, pdf_path):

        pages = convert_from_path(

            pdf_path,

            dpi=OCR_DPI

        )

        full_text = ""

        all_words = []

        confidence = []

        for page in pages:

            image = cv2.cvtColor(

                np.array(page),

                cv2.COLOR_RGB2BGR

            )

            processed = self.preprocess(image)

            text = self.tesseract_ocr(processed)
        
            text = self.normalize_text(text)

            data = self.image_to_data(processed)
        
            data["words"] = self.filter_confidence(

                data["words"],

                minimum=50

            )
            data["words"] = self.process_words(

                data["words"]

            )

            full_text += text + "\n"

            all_words.extend(

                data["words"]

            )

            confidence.append(

                data["confidence"]

            )

        if len(confidence):

            avg = round(

                sum(confidence) /

                len(confidence),

                2

            )

        else:

            avg = 0

        return {

            "text": full_text,

            "confidence": avg,

            "words": all_words

        }


# ---------------------------------------------------------
# Universal Read
# ---------------------------------------------------------

    def read(self, file_path):

        extension = os.path.splitext(

            file_path

        )[1].lower()

        if extension == ".pdf":

            return self.read_pdf(

                file_path

            )

        return self.read_image(

            file_path

        )


# ---------------------------------------------------------
# Save Highlighted OCR Image
# ---------------------------------------------------------

    def save_highlighted_image(

        self,

        image,

        words,

        output_path

    ):

        highlighted = self.draw_boxes(

            image,

            words

        )

        cv2.imwrite(

            output_path,

            highlighted

        )

        return output_path


# ---------------------------------------------------------
# OCR Summary
# ---------------------------------------------------------

    def print_summary(

        self,

        result

    ):

        print()

        print("=" * 80)

        print("OCR SUMMARY")

        print("=" * 80)

        print(

            "Confidence :",

            result["confidence"]

        )

        print(

            "Words :",

            len(result["words"])

        )

        print(

            "Characters :",

            len(result["text"])

        )

        print("=" * 80)


# ---------------------------------------------------------
# Debug Word Coordinates
# ---------------------------------------------------------

    def debug_words(

        self,

        result

    ):

        print()

        print("=" * 80)

        print("OCR WORDS")

        print("=" * 80)

        for word in result["words"]:

            print(

                f'{word["text"]} '

                f'({word["x"]}, {word["y"]}) '

                f'{word["confidence"]}%'

            )

        print("=" * 80)
# ---------------------------------------------------------
# Clean OCR Text
# ---------------------------------------------------------

    def clean_text(self, text):

        if text is None:

            return ""

        text = str(text)

        text = text.replace("\r", " ")

        text = text.replace("\n", " ")

        text = text.replace("\t", " ")

        while "  " in text:

            text = text.replace("  ", " ")

        return text.strip()
# ---------------------------------------------------------
# Remove Special Characters
# ---------------------------------------------------------

    def remove_special_characters(self, text):

        import re

        text = re.sub(

            r"[^A-Za-z0-9:/.,()\- ]",

            "",

            text

        )

        return text
# ---------------------------------------------------------
# Normalize OCR Text
# ---------------------------------------------------------

    def normalize_text(self, text):

        text = self.clean_text(text)

        text = self.remove_special_characters(text)

        text = text.upper()
    
        text = self.correct_ocr_errors(text)

        return text
# ---------------------------------------------------------
# OCR Error Correction
# ---------------------------------------------------------

    def correct_ocr_errors(self, text):

        corrections = {

            "|": "I",

            "¥": "Y",

            "§": "S",

            "®": "R",

            "©": "C",

            "€": "E"

        }

        for wrong, correct in corrections.items():

            text = text.replace(

                wrong,

                correct

            )

        return text


    
ocr_engine=OCREngine()