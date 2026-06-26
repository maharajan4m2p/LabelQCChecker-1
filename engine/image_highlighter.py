"""
=========================================================
Label QC Checker Pro
Image Highlighter
Version 2.0
=========================================================
"""

import cv2
import numpy as np

from config import *


class ImageHighlighter:

    def __init__(self):

        pass
    # ---------------------------------------------------------
# Load Image
# ---------------------------------------------------------

    def load_image(

        self,

        image_path

    ):

        image = cv2.imread(

            image_path

        )

        if image is None:

            raise Exception(

                f"Cannot load image : {image_path}"

            )

        return image
    
# ---------------------------------------------------------
# Draw Bounding Box
# ---------------------------------------------------------

    def draw_box(

        self,

        image,

        x,y,w,h,

        color,

        text

    ):

        cv2.rectangle(

            image,

            (x, y),

            (x + w, y + h),

            color,

            2

        )

        cv2.putText(

            image,

            text,

            (x, y - 5),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.6,

            color,

            2

        )

        return image
# ---------------------------------------------------------
# Highlight OCR Results
# ---------------------------------------------------------

    def highlight(

        self,

        image,

        words,

        status,

        color

    ):

        output = image.copy()

        for word in words:

            output = self.draw_box(

                output,

                word["x"],

                word["y"],

                word["width"],

                word["height"],

                color,

                status

            )

        return output
    # ---------------------------------------------------------
# Save Highlighted Image
# ---------------------------------------------------------

    def save(

        self,

        image,

        output_path

    ):

        cv2.imwrite(

            output_path,

            image

        )

        return output_path

# ---------------------------------------------------------
# Highlight Complete Result
# ---------------------------------------------------------


    def generate(

        self,

        image_path,

        words,

        status,

        color,

        output_path

    ):

        image = self.load_image(

            image_path

        )

        highlighted = self.highlight(

            image,

            words,

            status,

            color

        )

        self.save(

            highlighted,

            output_path
        )

        return output_path
    
image_highlighter = ImageHighlighter()