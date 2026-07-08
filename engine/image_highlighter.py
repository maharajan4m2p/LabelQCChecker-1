"""
=========================================================
Label QC Checker Pro
Advanced Image Highlighter
Version 5.0
=========================================================
"""

import cv2

from config import *


class ImageHighlighter:

    def __init__(self):

        self.line_thickness = 2

        self.font = cv2.FONT_HERSHEY_SIMPLEX

        self.font_scale = 0.6

        self.font_thickness = 2

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
    # Draw Rectangle
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

            self.line_thickness

        )

        text_size = cv2.getTextSize(

            label,

            self.font,

            self.font_scale,

            self.font_thickness

        )[0]

        cv2.rectangle(

            image,

            (x, max(0, y - 25)),

            (

                x + text_size[0] + 10,

                y

            ),

            color,

            -1

        )

        cv2.putText(

            image,

            label,

            (

                x + 5,

                y - 7

                if y > 25

                else y + 18

            ),

            self.font,

            self.font_scale,

            WHITE,

            self.font_thickness

        )

        return image
    # ---------------------------------------------------------
    # Highlight Objects
    # ---------------------------------------------------------

    def highlight_items(

        self,

        image,

        items,

        color,

        label,

        bbox_key="bbox"

    ):

        for item in items:

            bbox = item.get(bbox_key)

            if bbox is None:

                continue

            image = self.draw_box(

                image,

                bbox,

                color,

                label

            )

        return image

    # ---------------------------------------------------------
    # Draw Legend
    # ---------------------------------------------------------

    def draw_legend(

        self,

        image

    ):

        legend = [

            ("MATCH", GREEN),

            ("MISSING", RED),

            ("MODIFIED", ORANGE),

            ("EXTRA", BLUE)

        ]

        x = 20

        y = 30

        for text, color in legend:

            cv2.rectangle(

                image,

                (x, y - 15),

                (x + 20, y + 5),

                color,

                -1

            )

            cv2.putText(

                image,

                text,

                (x + 30, y),

                self.font,

                0.6,

                BLACK,

                2

            )

            y += 30

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

        image = self.load_image(

            image_path

        )

        highlighted = image.copy()

        highlighted = self.highlight_items(

            highlighted,

            matched,

            GREEN,

            "MATCH"

        )

        highlighted = self.highlight_items(

            highlighted,

            missing,

            RED,

            "MISSING"

        )

        highlighted = self.highlight_items(

            highlighted,

            modified,

            ORANGE,

            "MODIFIED",

            "bbox1"

        )

        highlighted = self.highlight_items(

            highlighted,

            extra,

            BLUE,

            "EXTRA"

        )

        highlighted = self.draw_legend(

            highlighted

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