"""
=========================================================
Label QC Checker Pro
Advanced Image Preprocessor
Version 5.0
=========================================================
"""

import cv2
import numpy as np

from config import *


class ImagePreprocessor:

    def __init__(self):
        pass

    # ---------------------------------------------------------
    # Resize Image
    # ---------------------------------------------------------

    def resize(self, image):

        h, w = image.shape[:2]

        if w >= RESIZE_WIDTH:

            return image

        ratio = RESIZE_WIDTH / float(w)

        new_h = int(h * ratio)

        return cv2.resize(

            image,

            (RESIZE_WIDTH, new_h),

            interpolation=cv2.INTER_CUBIC

        )

    # ---------------------------------------------------------
    # Convert to Gray
    # ---------------------------------------------------------

    def gray(self, image):

        if len(image.shape) == 2:

            return image

        return cv2.cvtColor(

            image,

            cv2.COLOR_BGR2GRAY

        )

    # ---------------------------------------------------------
    # CLAHE
    # ---------------------------------------------------------

    def clahe(self, gray):

        clahe = cv2.createCLAHE(

            clipLimit=CLAHE_CLIP,

            tileGridSize=CLAHE_GRID

        )

        return clahe.apply(gray)

    # ---------------------------------------------------------
    # Bilateral Filter
    # ---------------------------------------------------------

    def bilateral(self, gray):

        return cv2.bilateralFilter(

            gray,

            9,

            75,

            75

        )

    # ---------------------------------------------------------
    # Fast Denoise
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
    # Gaussian Blur
    # ---------------------------------------------------------

    def blur(self, gray):

        return cv2.GaussianBlur(

            gray,

            BLUR_KERNEL,

            0

        )

    # ---------------------------------------------------------
    # Sharpen
    # ---------------------------------------------------------

    def sharpen(self, gray):

        kernel = np.array([

            [-1,-1,-1],

            [-1,9,-1],

            [-1,-1,-1]

        ])

        return cv2.filter2D(

            gray,

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

            THRESH_BLOCKSIZE,

            THRESH_C

        )
        # ---------------------------------------------------------
    # Morphological Open
    # ---------------------------------------------------------

    def opening(self, image):

        kernel = cv2.getStructuringElement(

            cv2.MORPH_RECT,

            (2, 2)

        )

        return cv2.morphologyEx(

            image,

            cv2.MORPH_OPEN,

            kernel

        )

    # ---------------------------------------------------------
    # Morphological Close
    # ---------------------------------------------------------

    def closing(self, image):

        kernel = cv2.getStructuringElement(

            cv2.MORPH_RECT,

            (2, 2)

        )

        return cv2.morphologyEx(

            image,

            cv2.MORPH_CLOSE,

            kernel

        )

    # ---------------------------------------------------------
    # Dilate
    # ---------------------------------------------------------

    def dilate(self, image):

        kernel = np.ones(

            (1, 1),

            np.uint8

        )

        return cv2.dilate(

            image,

            kernel,

            iterations=1

        )

    # ---------------------------------------------------------
    # Erode
    # ---------------------------------------------------------

    def erode(self, image):

        kernel = np.ones(

            (1, 1),

            np.uint8

        )

        return cv2.erode(

            image,

            kernel,

            iterations=1

        )

    # ---------------------------------------------------------
    # Remove Border Noise
    # ---------------------------------------------------------

    def clean_border(self, image):

        image[0:5, :] = 255
        image[-5:, :] = 255
        image[:, 0:5] = 255
        image[:, -5:] = 255

        return image

    # ---------------------------------------------------------
    # Complete Processing Pipeline
    # ---------------------------------------------------------

    def process(self, image):

        image = self.resize(image)

        gray = self.gray(image)

        gray = self.clahe(gray)

        gray = self.bilateral(gray)

        gray = self.denoise(gray)

        gray = self.blur(gray)

        gray = self.sharpen(gray)

        binary = self.adaptive_threshold(gray)

        binary = self.opening(binary)

        binary = self.closing(binary)

        binary = self.erode(binary)

        binary = self.dilate(binary)

        binary = self.clean_border(binary)

        return binary


# ---------------------------------------------------------
# Singleton
# ---------------------------------------------------------

image_preprocessor = ImagePreprocessor()