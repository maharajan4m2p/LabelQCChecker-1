"""
=========================================================
Label QC Checker Pro
Label Detector
Version 2.0
=========================================================
"""

import cv2
import numpy as np

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config import *

class LabelDetector:

    def __init__(self):

        pass
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
# Gaussian Blur
# ---------------------------------------------------------

    def blur(

        self,

        gray

    ):

        return cv2.GaussianBlur(

            gray,

            (5, 5),

            0

        )
# ---------------------------------------------------------
# Edge Detection
# ---------------------------------------------------------

    def edges(

        self,

        gray

    ):

        return cv2.Canny(

            gray,

            50,

            150

        )
# ---------------------------------------------------------
# Find Contours
# ---------------------------------------------------------

    def find_contours(

        self,

        edge_image

    ):

        contours,_ = cv2.findContours(

            edge_image,

            cv2.RETR_EXTERNAL,

            cv2.CHAIN_APPROX_SIMPLE

        )

        return sorted(

            contours,

            key=cv2.contourArea,

            reverse=True

        )
# ---------------------------------------------------------
# Detect Label Contour
# ---------------------------------------------------------

    def detect_label(

        self,

        contours

    ):

        for contour in contours:

            area = cv2.contourArea(contour)

            if area < 5000:

                continue

            perimeter = cv2.arcLength(

                contour,

                True

            )

            approx = cv2.approxPolyDP(

                contour,

                0.02 * perimeter,

                True

            )

            if len(approx) == 4:

                return approx

        return None
# ---------------------------------------------------------
# Draw Label Boundary
# ---------------------------------------------------------

    def draw_label(

        self,

        image,

        contour

    ):

        output = image.copy()

        if contour is not None:

            cv2.drawContours(

                output,

                [contour],

                -1,

                GREEN,

                3

            )

        return output
# ---------------------------------------------------------
# Crop Label
# ---------------------------------------------------------

    def crop_label(

        self,

        image,

        contour

    ):

        if contour is None:

            return image

        x,y,w,h = cv2.boundingRect(

            contour

        )

        cropped = image[

            y:y+h,

            x:x+w

        ]

        return cropped

# ---------------------------------------------------------
# Order Corner Points
# ---------------------------------------------------------

    def order_points(

        self,

        pts

    ):

        pts = pts.reshape(4, 2)

        rect = np.zeros((4, 2), dtype="float32")

        s = pts.sum(axis=1)

        rect[0] = pts[np.argmin(s)]

        rect[2] = pts[np.argmax(s)]

        diff = np.diff(pts, axis=1)

        rect[1] = pts[np.argmin(diff)]

        rect[3] = pts[np.argmax(diff)]

        return rect

# ---------------------------------------------------------
# Perspective Correction
# ---------------------------------------------------------

    def four_point_transform(

        self,

        image,

        contour

    ):

        if contour is None:

            return image

        rect = self.order_points(contour)

        (tl, tr, br, bl) = rect

        widthA = np.linalg.norm(br - bl)

        widthB = np.linalg.norm(tr - tl)

        maxWidth = max(int(widthA), int(widthB))

        heightA = np.linalg.norm(tr - br)

        heightB = np.linalg.norm(tl - bl)

        maxHeight = max(int(heightA), int(heightB))

        dst = np.array([

            [0, 0],

            [maxWidth - 1, 0],

            [maxWidth - 1, maxHeight - 1],

            [0, maxHeight - 1]

        ], dtype="float32")

        M = cv2.getPerspectiveTransform(

            rect,

            dst

        )

        warped = cv2.warpPerspective(

            image,

            M,

            (maxWidth, maxHeight)

        )

        return warped


# ---------------------------------------------------------
# Complete Label Detection
# ---------------------------------------------------------

    def detect(

        self,

        image_path

    ):

        image = self.load_image(

            image_path

        )

        gray = self.gray(

            image

        )

        gray = self.blur(

            gray

        )

        edge = self.edges(

            gray

        )

        contours = self.find_contours(

            edge

        )

        contour = self.detect_label(

            contours

        )

        cropped = self.four_point_transform(

            image,

            contour

        )

        highlighted = self.draw_label(

            image,

            contour

        )

        return {

            "image": image,

            "cropped": cropped,

            "highlighted": highlighted,

            "contour": contour

        }
label_detector = LabelDetector()

if __name__ == "__main__":

    result = label_detector.detect("test.png")

    cv2.imwrite("detected_label.png", result["highlighted"])
    cv2.imwrite("cropped_label.png", result["cropped"])

    print("Images saved successfully.")

    
