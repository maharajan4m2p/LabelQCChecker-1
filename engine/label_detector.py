"""
=========================================================
Label QC Checker Pro
Advanced Label Detector
Version 3.0
=========================================================
"""

import os
import sys
import cv2
import numpy as np

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config import *


class LabelDetector:

    def __init__(self):
        pass

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
    # Resize
    # ---------------------------------------------------------

    def resize(self, image):

        h, w = image.shape[:2]

        if w > 1800:

            ratio = 1800 / w

            image = cv2.resize(

                image,

                None,

                fx=ratio,

                fy=ratio,

                interpolation=cv2.INTER_AREA

            )

        return image

    # ---------------------------------------------------------
    # Gray
    # ---------------------------------------------------------

    def gray(self, image):

        return cv2.cvtColor(

            image,

            cv2.COLOR_BGR2GRAY

        )

    # ---------------------------------------------------------
    # CLAHE
    # ---------------------------------------------------------

    def clahe(self, gray):

        clahe = cv2.createCLAHE(

            clipLimit=2.5,

            tileGridSize=(8,8)

        )

        return clahe.apply(gray)

    # ---------------------------------------------------------
    # Blur
    # ---------------------------------------------------------

    def blur(self, gray):

        return cv2.GaussianBlur(

            gray,

            (5,5),

            0

        )

    # ---------------------------------------------------------
    # Threshold
    # ---------------------------------------------------------

    def threshold(self, gray):

        return cv2.adaptiveThreshold(

            gray,

            255,

            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,

            cv2.THRESH_BINARY,

            31,

            15

        )

    # ---------------------------------------------------------
    # Morphology
    # ---------------------------------------------------------

    def morphology(self, image):

        kernel = cv2.getStructuringElement(

            cv2.MORPH_RECT,

            (3,3)

        )

        image = cv2.morphologyEx(

            image,

            cv2.MORPH_CLOSE,

            kernel,

            iterations=2

        )

        image = cv2.morphologyEx(

            image,

            cv2.MORPH_OPEN,

            kernel,

            iterations=1

        )

        return image
    # ---------------------------------------------------------
    # Edge Detection
    # ---------------------------------------------------------

    def edges(self, image):

        return cv2.Canny(

            image,

            50,

            150

        )

    # ---------------------------------------------------------
    # Find Contours
    # ---------------------------------------------------------

    def find_contours(self, edge_image):

        contours, _ = cv2.findContours(

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

    def detect_label(self, contours):

        image_area = None

        for contour in contours:

            area = cv2.contourArea(contour)

            if image_area is None:

                image_area = area

            if area < 3000:

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

        if len(contours):

            return contours[0]

        return None

    # ---------------------------------------------------------
    # Draw Label
    # ---------------------------------------------------------

    def draw_label(self, image, contour):

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

    def crop_label(self, image, contour):

        if contour is None:

            return image

        x, y, w, h = cv2.boundingRect(

            contour

        )

        return image[

            y:y+h,

            x:x+w

        ]

    # ---------------------------------------------------------
    # Order Points
    # ---------------------------------------------------------

    def order_points(self, pts):

        pts = pts.reshape(4,2)

        rect = np.zeros(

            (4,2),

            dtype="float32"

        )

        s = pts.sum(axis=1)

        rect[0] = pts[np.argmin(s)]

        rect[2] = pts[np.argmax(s)]

        diff = np.diff(

            pts,

            axis=1

        )

        rect[1] = pts[np.argmin(diff)]

        rect[3] = pts[np.argmax(diff)]

        return rect

    # ---------------------------------------------------------
    # Perspective Transform
    # ---------------------------------------------------------

    def four_point_transform(self, image, contour):

        if contour is None:

            return image

        if len(contour) != 4:

            return self.crop_label(

                image,

                contour

            )

        rect = self.order_points(

            contour

        )

        (tl, tr, br, bl) = rect

        widthA = np.linalg.norm(

            br-bl

        )

        widthB = np.linalg.norm(

            tr-tl

        )

        maxWidth = max(

            int(widthA),

            int(widthB)

        )

        heightA = np.linalg.norm(

            tr-br

        )

        heightB = np.linalg.norm(

            tl-bl

        )

        maxHeight = max(

            int(heightA),

            int(heightB)

        )

        dst = np.array(

            [

                [0,0],

                [maxWidth-1,0],

                [maxWidth-1,maxHeight-1],

                [0,maxHeight-1]

            ],

            dtype="float32"

        )

        M = cv2.getPerspectiveTransform(

            rect,

            dst

        )

        warped = cv2.warpPerspective(

            image,

            M,

            (maxWidth,maxHeight)

        )

        return warped
    # ---------------------------------------------------------
    # Complete Label Detection
    # ---------------------------------------------------------

    def detect(self, image_path):

        image = self.load_image(

            image_path

        )

        image = self.resize(

            image

        )

        gray = self.gray(

            image

        )

        gray = self.clahe(

            gray

        )

        gray = self.blur(

            gray

        )

        binary = self.threshold(

            gray

        )

        binary = self.morphology(

            binary

        )

        edge = self.edges(

            binary

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

        x = y = w = h = 0

        area = 0

        if contour is not None:

            x, y, w, h = cv2.boundingRect(

                contour

            )

            area = cv2.contourArea(

                contour

            )

        return {

            "image": image,

            "cropped": cropped,

            "highlighted": highlighted,

            "contour": contour,

            "bounding_box": {

                "x": x,

                "y": y,

                "width": w,

                "height": h

            },

            "area": area,

            "found": contour is not None

        }


# ---------------------------------------------------------
# Singleton
# ---------------------------------------------------------

label_detector = LabelDetector()


# ---------------------------------------------------------
# Testing
# ---------------------------------------------------------

if __name__ == "__main__":

    test_image = "test.png"

    if os.path.exists(test_image):

        result = label_detector.detect(

            test_image

        )

        cv2.imwrite(

            "detected_label.png",

            result["highlighted"]

        )

        cv2.imwrite(

            "cropped_label.png",

            result["cropped"]

        )

        print("=" * 60)

        print("Label Detection Completed")

        print("=" * 60)

        print("Label Found :", result["found"])

        print("Area :", result["area"])

        print("Bounding Box :", result["bounding_box"])

        print("=" * 60)

    else:

        print(f"Test image '{test_image}' not found.")