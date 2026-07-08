"""
=========================================================
Label QC Checker Pro
Advanced Logo Checker
Version 5.0
=========================================================
"""

import cv2
import numpy as np

from config import *


class LogoChecker:

    def __init__(self):

        self.threshold = LOGO_MATCH

        self.orb = cv2.ORB_create(

            nfeatures=1000

        )

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

        x1 = 0

        y1 = 0

        x2 = int(w * 0.30)

        y2 = int(h * 0.20)

        logo = image[

            y1:y2,

            x1:x2

        ]

        return logo

    # ---------------------------------------------------------
    # Preprocess Logo
    # ---------------------------------------------------------

    def preprocess(self, logo):

        gray = cv2.cvtColor(

            logo,

            cv2.COLOR_BGR2GRAY

        )

        gray = cv2.GaussianBlur(

            gray,

            (3,3),

            0

        )

        gray = cv2.equalizeHist(

            gray

        )

        return gray

    # ---------------------------------------------------------
    # Extract Features
    # ---------------------------------------------------------

    def extract_features(

        self,

        image

    ):

        keypoints, descriptors = self.orb.detectAndCompute(

            image,

            None

        )

        return keypoints, descriptors

    # ---------------------------------------------------------
    # Match Features
    # ---------------------------------------------------------

    def match_features(

        self,

        des1,

        des2

    ):

        if des1 is None or des2 is None:

            return []

        matcher = cv2.BFMatcher(

            cv2.NORM_HAMMING,

            crossCheck=True

        )

        matches = matcher.match(

            des1,

            des2

        )

        matches = sorted(

            matches,

            key=lambda x: x.distance

        )

        return matches
    # ---------------------------------------------------------
    # Calculate Similarity
    # ---------------------------------------------------------

    def calculate_similarity(

        self,

        matches,

        kp1,

        kp2

    ):

        if len(kp1) == 0 or len(kp2) == 0:

            return 0

        max_keypoints = max(

            len(kp1),

            len(kp2)

        )

        similarity = (

            len(matches) / max_keypoints

        ) * 100

        return round(

            min(similarity, 100),

            2

        )

    # ---------------------------------------------------------
    # Compare Logo
    # ---------------------------------------------------------

    def compare_logo(

        self,

        logo1,

        logo2

    ):

        logo1 = self.preprocess(

            logo1

        )

        logo2 = self.preprocess(

            logo2

        )

        kp1, des1 = self.extract_features(

            logo1

        )

        kp2, des2 = self.extract_features(

            logo2

        )

        matches = self.match_features(

            des1,

            des2

        )

        orb_similarity = self.calculate_similarity(

            matches,

            kp1,

            kp2

        )

        # -----------------------------------------
        # Template Matching
        # -----------------------------------------

        resized = cv2.resize(

            logo2,

            (

                logo1.shape[1],

                logo1.shape[0]

            )

        )

        template_score = cv2.matchTemplate(

            logo1,

            resized,

            cv2.TM_CCOEFF_NORMED

        )[0][0]

        template_similarity = round(

            template_score * 100,

            2

        )

        similarity = round(

            max(

                orb_similarity,

                template_similarity

            ),

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

            "score": similarity,

            "threshold": self.threshold,

            "status": status

        }


# ---------------------------------------------------------
# Singleton
# ---------------------------------------------------------

logo_checker = LogoChecker()