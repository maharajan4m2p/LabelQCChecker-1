"""
=========================================================
Label QC Checker Pro
Image Highlighter
Version 4.0
=========================================================
"""

import cv2

from config import *


class ImageHighlighter:

    def __init__(self):
        pass

    # ---------------------------------------------------------
    # Load Image
    # ---------------------------------------------------------

    def load_image(self, image_path):

        image = cv2.imread(image_path)

        if image is None:
            raise Exception(f"Cannot load image : {image_path}")

        return image

    # ---------------------------------------------------------
    # Draw Box
    # ---------------------------------------------------------

    def draw_box(

        self,

        image,

        bbox,

        color,

        label

    ):

        if bbox is None:
            return image

        x = int(bbox["x"])
        y = int(bbox["y"])
        w = int(bbox["width"])
        h = int(bbox["height"])

        cv2.rectangle(

            image,

            (x, y),

            (x + w, y + h),

            color,

            2

        )

        cv2.putText(

            image,

            label,

            (x, max(20, y - 5)),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.6,

            color,

            2

        )

        return image

    # ---------------------------------------------------------
    # Generate Highlighted Image
    # ---------------------------------------------------------

    def generate(

        self,

        image_path,

        matched,

        missing,

        modified,

        extra,

        output_path

    ):

        image = self.load_image(image_path)

        highlighted = image.copy()

        # -----------------------------
        # MATCH (GREEN)
        # -----------------------------

        for item in matched:

            highlighted = self.draw_box(

                highlighted,

                item.get("bbox"),

                GREEN,

                "MATCH"

            )

        # -----------------------------
        # MISSING (RED)
        # -----------------------------

        for item in missing:

            highlighted = self.draw_box(

                highlighted,

                item.get("bbox"),

                RED,

                "MISSING"

            )

        # -----------------------------
        # MODIFIED (ORANGE)
        # -----------------------------

        for item in modified:

            bbox = item.get("bbox1")

            if bbox is None:
                bbox = item.get("bbox")

            highlighted = self.draw_box(

                highlighted,

                bbox,

                ORANGE,

                "MODIFIED"

            )

        # -----------------------------
        # EXTRA (BLUE)
        # -----------------------------

        for item in extra:

            highlighted = self.draw_box(

                highlighted,

                item.get("bbox"),

                BLUE,

                "EXTRA"

            )

        cv2.imwrite(

            output_path,

            highlighted

        )

        return output_path


# ---------------------------------------------------------
# Singleton
# ---------------------------------------------------------

image_highlighter = ImageHighlighter()