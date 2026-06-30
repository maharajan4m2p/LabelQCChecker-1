"""
=========================================================
Label QC Checker Pro
OCR Engine
Version 4.0
=========================================================
"""

import cv2
import easyocr

from config import *
from engine.image_preprocessor import image_preprocessor


class OCREngine:

    def __init__(self):

        print("=" * 60)
        print("Loading EasyOCR...")
        print("=" * 60)

        self.reader = easyocr.Reader(
            OCR_LANGUAGE,
            gpu=OCR_GPU
        )

        print("EasyOCR Loaded Successfully")

    # ---------------------------------------------------------
    # Read Image
    # ---------------------------------------------------------

    def read(self, image_path):

        image = cv2.imread(image_path)

        if image is None:
            raise Exception(f"Cannot load image : {image_path}")

        processed = image_preprocessor.process(image)

        results = self.reader.readtext(
            processed,
            detail=1,
            paragraph=False
        )

        words = []

        full_text = []

        for item in results:

            box = item[0]

            text = str(item[1]).strip()

            confidence = float(item[2])

            if text == "":
                continue

            x = int(min(p[0] for p in box))
            y = int(min(p[1] for p in box))
            w = int(max(p[0] for p in box) - x)
            h = int(max(p[1] for p in box) - y)

            words.append({

                "text": text,

                "confidence": confidence,

                "x": x,

                "y": y,

                "width": w,

                "height": h

            })

            full_text.append(text)

        return {

            "text": "\n".join(full_text),

            "words": words

        }

    # ---------------------------------------------------------
    # Print OCR Result
    # ---------------------------------------------------------

    def print_result(self, result):

        print("=" * 60)
        print("OCR RESULT")
        print("=" * 60)

        print(result["text"])

        print("=" * 60)


ocr_engine = OCREngine()