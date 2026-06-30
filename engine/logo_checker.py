"""
=========================================================
Label QC Checker Pro
Logo Checker
Version 4.0
=========================================================
"""

import cv2

from config import *


class LogoChecker:

    def __init__(self):

        self.threshold = LOGO_MATCH

    # ---------------------------------------------------------
    # Load Image
    # ---------------------------------------------------------

    def load(self, image_path):

        image = cv2.imread(image_path)

        if image is None:

            raise Exception(

                f"Cannot load image : {image_path}"

            )

        return image

    # ---------------------------------------------------------
    # Crop Logo Region
    # ---------------------------------------------------------

    def crop_logo(self, image):

        h, w = image.shape[:2]

        logo = image[
            0:int(h * 0.20),
            0:int(w * 0.30)
        ]

        return logo

    # ---------------------------------------------------------
    # Compare Logo
    # ---------------------------------------------------------

    def compare_logo(

        self,

        logo1,

        logo2

    ):

        gray1 = cv2.cvtColor(

            logo1,

            cv2.COLOR_BGR2GRAY

        )

        gray2 = cv2.cvtColor(

            logo2,

            cv2.COLOR_BGR2GRAY

        )

        gray2 = cv2.resize(

            gray2,

            (

                gray1.shape[1],

                gray1.shape[0]

            )

        )

        score = cv2.matchTemplate(

            gray1,

            gray2,

            cv2.TM_CCOEFF_NORMED

        )[0][0]

        similarity = round(

            score * 100,

            2

        )

        return similarity

    # ---------------------------------------------------------
    # Verify Logo
    # ---------------------------------------------------------

    def verify(

        self,

        approval_path,

        sample_path

    ):

        approval = self.load(

            approval_path

        )

        sample = self.load(

            sample_path

        )

        logo1 = self.crop_logo(

            approval

        )

        logo2 = self.crop_logo(

            sample

        )

        similarity = self.compare_logo(

            logo1,

            logo2

        )

        status = (

            "PASS"

            if similarity >= self.threshold

            else "FAIL"

        )

        return {

            "similarity": similarity,

            "status": status

        }


logo_checker = LogoChecker()