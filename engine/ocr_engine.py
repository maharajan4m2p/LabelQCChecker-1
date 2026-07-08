"""
=========================================================
Label QC Checker Pro
OCR Engine
Version 5.0
Supports:
✓ Images
✓ PDF Images
✓ Better OCR Accuracy
=========================================================
"""

import gc
import os
import cv2
import easyocr
import numpy as np

from config import *
from engine.image_preprocessor import image_preprocessor


class OCREngine:

    def __init__(self):

        self.reader = None


    def load_image(self, image_path):

        if not os.path.exists(image_path):

            raise Exception(
                f"File not found : {image_path}"
            )

        image = cv2.imread(image_path)

        if image is None:

            raise Exception(
                f"Cannot load image : {image_path}"
            )

        return image


    def read(self, image_path):

        image = self.load_image(

            image_path

        )

        processed = image_preprocessor.process(

            image

        )
        
        if self.reader is None:
            self.reader = easyocr.Reader(
                OCR_LANGUAGE,
                gpu=False,
                verbose=False
            )

        results = self.reader.readtext(

            processed,

            detail=1,

            paragraph=False,

            decoder="greedy",

        )
        del image
        del processed
        del results
        gc.collect()

        words = []

        full_text = []

        for item in results:

            box = item[0]

            text = str(item[1]).strip()

            confidence = float(item[2])

            if text == "":

                continue

            x = int(

                min(

                    p[0]

                    for p in box

                )

            )

            y = int(

                min(

                    p[1]

                    for p in box

                )

            )

            w = int(

                max(

                    p[0]

                    for p in box

                ) - x

            )

            h = int(

                max(

                    p[1]

                    for p in box

                ) - y

            )

            words.append(

                {

                    "text": text,

                    "confidence": confidence,

                    "x": x,

                    "y": y,

                    "width": w,

                    "height": h

                }

            )

            full_text.append(text)
            # Build complete OCR text

        # ---------------------------------------------
        # Remove duplicate empty lines
        # ---------------------------------------------

        cleaned_text = "\n".join(full_text)

        return {

            "text": cleaned_text,

            "words": words

        }

    # ---------------------------------------------------------
    # Read Only Text
    # ---------------------------------------------------------

    def read_text(

        self,

        image_path

    ):

        result = self.read(

            image_path

        )

        return result["text"]

    # ---------------------------------------------------------
    # Read Only Words
    # ---------------------------------------------------------

    def read_words(

        self,

        image_path

    ):

        result = self.read(

            image_path

        )

        return result["words"]

    # ---------------------------------------------------------
    # OCR Statistics
    # ---------------------------------------------------------

    def statistics(

        self,

        image_path

    ):

        result = self.read(

            image_path

        )

        total_words = len(

            result["words"]

        )

        if total_words == 0:

            average_confidence = 0

        else:

            average_confidence = sum(

                word["confidence"]

                for word in result["words"]

            ) / total_words

        return {

            "word_count": total_words,

            "average_confidence": round(

                average_confidence,

                2

            )

        }

    # ---------------------------------------------------------
    # Print OCR Result
    # ---------------------------------------------------------

    def print_result(

        self,

        result

    ):

        print("=" * 60)

        print("OCR RESULT")

        print("=" * 60)

        print(result["text"])

        print("=" * 60)

        print("TOTAL WORDS :", len(result["words"]))

        print("=" * 60)

    # ---------------------------------------------------------
    # Debug OCR
    # ---------------------------------------------------------

    def debug(

        self,

        image_path

    ):

        result = self.read(

            image_path

        )

        self.print_result(

            result

        )

        stats = self.statistics(

            image_path

        )

        print(

            "Average Confidence :",

            stats["average_confidence"]

        )

        return result


# ---------------------------------------------------------
# Singleton
# ---------------------------------------------------------

ocr_engine = OCREngine()