"""
=========================================================
Label QC Checker Pro
Utility Functions
=========================================================
"""

import re
from difflib import SequenceMatcher


class Utils:

    # ----------------------------------------------------
    # Normalize Text
    # ----------------------------------------------------

    def normalize_text(self, text):

        if text is None:
            return ""

        text = str(text)

        text = text.upper()

        text = text.replace("\r", "")

        text = text.replace("\n", " ")

        text = re.sub(r"\s+", " ", text)

        return text.strip()

    # ----------------------------------------------------
    # Clean Value
    # ----------------------------------------------------

    def clean_value(self, value):

        if value is None:
            return ""

        value = str(value)

        value = value.replace("\n", " ")

        value = value.replace("|", "")

        value = re.sub(r"\s+", " ", value)

        value = value.strip(" :-")

        return value

    # ----------------------------------------------------
    # Similarity
    # ----------------------------------------------------

    def similarity(self, a, b):

        a = self.normalize_text(a)

        b = self.normalize_text(b)

        return round(

            SequenceMatcher(

                None,

                a,

                b

            ).ratio() * 100,

            2

        )

    # ----------------------------------------------------
    # Normalize Weight
    # ----------------------------------------------------

    def normalize_weight(self, value):

        value = self.normalize_text(value)

        value = value.replace("KGS", "KG")

        value = value.replace("KILOGRAM", "KG")

        value = value.replace("GRAMS", "G")

        return value

    # ----------------------------------------------------
    # Normalize Quantity
    # ----------------------------------------------------

    def normalize_quantity(self, value):

        value = self.normalize_text(value)

        value = value.replace("PCS", "")

        value = value.replace("PIECES", "")

        return value.strip()

    # ----------------------------------------------------
    # Normalize Color
    # ----------------------------------------------------

    def normalize_color(self, value):

        colors = {

            "BLK": "BLACK",

            "WHT": "WHITE",

            "NVY": "NAVY",

            "GRY": "GREY"

        }

        value = self.normalize_text(value)

        if value in colors:

            return colors[value]

        return value

    # ----------------------------------------------------
    # Normalize Size
    # ----------------------------------------------------

    def normalize_size(self, value):

        value = self.normalize_text(value)

        size_map = {

            "EXTRA SMALL": "XS",

            "SMALL": "S",

            "MEDIUM": "M",

            "LARGE": "L",

            "EXTRA LARGE": "XL",

            "DOUBLE XL": "XXL"

        }

        return size_map.get(

            value,

            value

        )

    # ----------------------------------------------------
    # Normalize Date
    # ----------------------------------------------------

    def normalize_date(self, value):

        value = self.normalize_text(value)

        value = value.replace("/", "-")

        value = value.replace(".", "-")

        return value

    # ----------------------------------------------------
    # Barcode Validation
    # ----------------------------------------------------

    def is_barcode(self, value):

        value = self.normalize_text(value)

        return bool(

            re.fullmatch(

                r"\d{8,20}",

                value

            )

        )

    # ----------------------------------------------------
    # Remove Empty Values
    # ----------------------------------------------------

    def remove_empty(self, dictionary):

        output = {}

        for key, value in dictionary.items():

            if str(value).strip() != "":

                output[key] = value

        return output

    # ----------------------------------------------------
    # Print Dictionary
    # ----------------------------------------------------

    def print_dictionary(

        self,

        dictionary,

        title="DATA"

    ):

        print()

        print("=" * 80)

        print(title)

        print("=" * 80)

        for k, v in dictionary.items():

            print(f"{k:25} : {v}")

        print("=" * 80)


utils = Utils()