"""
=========================================================
Label QC Checker Pro
Image Preprocessor
Version 4.0
=========================================================
"""

import cv2
import numpy as np

from config import *


class ImagePreprocessor:

    def __init__(self):
        pass

    # ---------------------------------------------------------
    # Resize
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
    # Grayscale
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
            clipLimit=CLAHE_CLIP,
            tileGridSize=CLAHE_GRID
        )

        return clahe.apply(gray)

    # ---------------------------------------------------------
    # Denoise
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

    def sharpen(self, gray):

        kernel = np.array([
            [-1, -1, -1],
            [-1, 9, -1],
            [-1, -1, -1]
        ])

        return cv2.filter2D(
            gray,
            -1,
            kernel
        )

    # ---------------------------------------------------------
    # Adaptive Threshold
    # ---------------------------------------------------------

    def threshold(self, gray):

        return cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            THRESH_BLOCKSIZE,
            THRESH_C
        )

    # ---------------------------------------------------------
    # Complete Pipeline
    # ---------------------------------------------------------

    def process(self, image):

        image = self.resize(image)

        gray = self.gray(image)

        gray = self.clahe(gray)

        gray = self.denoise(gray)

        gray = self.sharpen(gray)

        binary = self.threshold(gray)

        return binary


image_preprocessor = ImagePreprocessor()