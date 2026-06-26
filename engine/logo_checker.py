"""
=========================================================
Label QC Checker Pro
Logo Checker
Version 2.0
=========================================================
"""

import cv2
import numpy as np

from config import *


class LogoChecker:

    def __init__(self):

        self.threshold = LOGO_MATCH_THRESHOLD =90

    # ---------------------------------------------------------
    # Load Image
    # ---------------------------------------------------------

    def load_image(

        self,

        image_path

    ):

        image = cv2.imread(image_path)

        if image is None:

            raise Exception(

                f"Cannot load image : {image_path}"

            )

        return image
    # ---------------------------------------------------------
# Convert To Gray
# ---------------------------------------------------------

    def gray(

        self,

        image

    ):

        return cv2.cvtColor(

            image,

            cv2.COLOR_BGR2GRAY

        )


# ---------------------------------------------------------
# Resize Logo
# ---------------------------------------------------------

    def resize(

        self,

        image,

        width=200,

        height=200

    ):

        return cv2.resize(

            image,

            (width, height),

            interpolation=cv2.INTER_AREA

        )


# ---------------------------------------------------------
# Preprocess Logo
# ---------------------------------------------------------

    def preprocess(

        self,

        image

    ):

        gray = self.gray(

            image

        )

        gray = self.resize(

            gray

        )

        return gray
    # ---------------------------------------------------------
# Extract Logo Region
# ---------------------------------------------------------

    def extract_logo(

        self,

        image,

        x=0,

        y=0,

        width=250,

        height=250

    ):

        h, w = image.shape[:2]

        x = max(0, min(x, w))

        y = max(0, min(y, h))

        width = min(width, w - x)

        height = min(height, h - y)

        logo = image[

            y:y+height,

            x:x+width

        ]

        return logo


# ---------------------------------------------------------
# Load And Extract Logo
# ---------------------------------------------------------

    def get_logo(

        self,

        image_path

    ):

        image = self.load_image(

            image_path

        )

        logo = self.extract_logo(

            image

        )

        logo = self.preprocess(

            logo

        )

        return logo
    # ---------------------------------------------------------
# Compare Two Logos
# ---------------------------------------------------------

    def compare_logos(

    self,

        image1,

        image2

    ):

        logo1 = self.get_logo(

            image1

        )

        logo2 = self.get_logo(

            image2

        )

        logo2 = cv2.resize(

            logo2,

            (

                logo1.shape[1],

                logo1.shape[0]

            )

        )   

        score = cv2.matchTemplate(

            logo1,

            logo2,

            cv2.TM_CCOEFF_NORMED

        )[0][0]

        similarity = round(

            float(score) * 100,

            2

        )

        return similarity
    # ---------------------------------------------------------
# Verify Logo
# ---------------------------------------------------------

    def verify(

        self,

        approval_image,

        sample_image

    ):

        similarity = self.compare_logos(

            approval_image,

            sample_image

        )

        if similarity >= self.threshold:

            status = "PASS"

        else:

            status = "FAIL"

        return {

            "similarity": similarity,

            "status": status

        }


# ---------------------------------------------------------
# Print Logo Result
# ---------------------------------------------------------

    def print_result(

        self,

        result

    ):

        print()

        print("=" * 70)

        print("LOGO VERIFICATION")

        print("=" * 70)

        print(

            "Similarity :",

            result["similarity"],

            "%"

        )

        print(

            "Status :",

            result["status"]

        )

        print("=" * 70)


logo_checker = LogoChecker()