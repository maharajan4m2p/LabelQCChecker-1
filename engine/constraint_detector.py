"""
=========================================================
Label QC Checker Pro
Constraint Detector
Version 4.0
=========================================================
"""

import re
from rapidfuzz import fuzz

from config import *


class ConstraintDetector:

    def __init__(self):

        self.fields = [

            "BUYER",
            "BUYER CODE",
            "VENDOR",
            "VENDOR CODE",
            "PO NO",
            "STYLE NO",
            "DESCRIPTION",
            "COLOR",
            "SIZE",
            "SIZE ASSORTMENT",
            "TOTAL QTY",
            "MEASUREMENT",
            "VOLUME",
            "CARTON NO",
            "CARTON TYPE",
            "NET WEIGHT",
            "GROSS WEIGHT",
            "DESTINATION",
            "SHIP DATE",
            "SEASON",
            "ITEM NO",
            "BARCODE",
            "UPC",
            "EAN",
            "SKU",
            "CUSTOMER",
            "COUNTRY OF ORIGIN",
            "MADE IN"

        ]

        self.patterns = {

            "BUYER":
            r"BUYER\s*[:\-]?\s*([^\n\r]+)",

            "BUYER CODE":
            r"BUYER\s*CODE\s*[:\-]?\s*([^\n\r]+)",

            "VENDOR":
            r"VENDOR\s*[:\-]?\s*([^\n\r]+)",

            "VENDOR CODE":
            r"VENDOR\s*CODE\s*[:\-]?\s*([^\n\r]+)",

            "PO NO":
            r"P\.?\s*O\.?\s*NO\.?\s*[:\-]?\s*([^\n\r]+)",

            "STYLE NO":
            r"STYLE\s*NO\.?\s*[:\-]?\s*([^\n\r]+)",

            "DESCRIPTION":
            r"DESCRIPTION\s*[:\-]?\s*([^\n\r]+)",

            "COLOR":
            r"COLOR\s*[:\-]?\s*([^\n\r]+)",

            "SIZE":
            r"SIZE\s*[:\-]?\s*([^\n\r]+)",

            "SIZE ASSORTMENT":
            r"SIZE\s*ASSORTMENT\s*[:\-]?\s*([^\n\r]+)",

            "TOTAL QTY":
            r"TOTAL\s*QTY\.?\s*[:\-]?\s*([^\n\r]+)",

            "MEASUREMENT":
            r"MEASUREMENT\s*[:\-]?\s*([^\n\r]+)",

            "VOLUME":
            r"VOLUME\s*[:\-]?\s*([^\n\r]+)",

            "CARTON NO":
            r"CARTON\s*NO\.?\s*[:\-]?\s*([^\n\r]+)",

            "CARTON TYPE":
            r"CARTON\s*TYPE\s*[:\-]?\s*([^\n\r]+)",

            "NET WEIGHT":
            r"NET\s*WEIGHT\s*[:\-]?\s*([^\n\r]+)",

            "GROSS WEIGHT":
            r"GROSS\s*WEIGHT\s*[:\-]?\s*([^\n\r]+)",

            "DESTINATION":
            r"DESTINATION\s*[:\-]?\s*([^\n\r]+)",

            "SHIP DATE":
            r"SHIP\s*DATE\s*[:\-]?\s*([^\n\r]+)",

            "SEASON":
            r"SEASON\s*[:\-]?\s*([^\n\r]+)",

            "ITEM NO":
            r"ITEM\s*NO\.?\s*[:\-]?\s*([^\n\r]+)",

            "BARCODE":
            r"BARCODE\s*[:\-]?\s*([^\n\r]+)",

            "UPC":
            r"UPC\s*[:\-]?\s*([^\n\r]+)",

            "EAN":
            r"EAN\s*[:\-]?\s*([^\n\r]+)",

            "SKU":
            r"SKU\s*[:\-]?\s*([^\n\r]+)",

            "CUSTOMER":
            r"CUSTOMER\s*[:\-]?\s*([^\n\r]+)",

            "COUNTRY OF ORIGIN":
            r"COUNTRY\s*OF\s*ORIGIN\s*[:\-]?\s*([^\n\r]+)",

            "MADE IN":
            r"MADE\s*IN\s*[:\-]?\s*([^\n\r]+)"

        }
        # ---------------------------------------------------------
# Normalize Text
# ---------------------------------------------------------

    def normalize(self, text):

        if text is None:
            return ""

        text = str(text)

        text = text.upper()

        text = text.replace("\r", "")

        lines = []

        for line in text.split("\n"):

            line = re.sub(r"\s+", " ", line).strip()

            if line:

                lines.append(line)

        return "\n".join(lines)


# ---------------------------------------------------------
# Clean Value
# ---------------------------------------------------------

    def clean(self, value):

        if value is None:
            return ""

        value = str(value)

        value = value.replace("\r", "")

        value = value.replace("\n", " ")

        value = re.sub(r"\s+", " ", value)

        return value.strip()


# ---------------------------------------------------------
# Fuzzy Similarity
# ---------------------------------------------------------

    def similarity(

        self,

        value1,

        value2

    ):

        return fuzz.token_sort_ratio(

            self.normalize(value1),

            self.normalize(value2)

        )


# ---------------------------------------------------------
# Extract Constraints
# ---------------------------------------------------------

    def extract_constraints(

        self,

        text

    ):

        text = self.normalize(text)

        constraints = {}

        print("=" * 80)
        print("OCR TEXT")
        print("=" * 80)
        print(text)
        print("=" * 80)

        for field, pattern in self.patterns.items():

            match = re.search(

                pattern,

                text,

                re.IGNORECASE | re.MULTILINE

            )

            if match:

                value = self.clean(

                    match.group(1)

                )

                constraints[field] = value

                print(f"{field:25} -> {value}")

        return constraints
    # ---------------------------------------------------------
# Dynamic Key : Value Detection
# ---------------------------------------------------------

    def detect_dynamic_constraints(

        self,

        text

    ):

        text = self.normalize(text)

        lines = text.split("\n")

        constraints = {}

        for line in lines:

            line = line.strip()

            if len(line) < 3:
                continue

        # KEY : VALUE

            if ":" in line:

                parts = line.split(":", 1)

        # KEY - VALUE

            elif "-" in line:

                parts = line.split("-", 1)

            else:
                continue

            if len(parts) != 2:
                continue

            key = self.clean(parts[0])

            value = self.clean(parts[1])

            if key != "" and value != "":

                constraints[key] = value

        return constraints


# ---------------------------------------------------------
# Merge Standard + Dynamic Constraints
# ---------------------------------------------------------

    def get_basic_constraints(

        self,

        text

    ):

        standard = self.extract_constraints(

            text

        )

        dynamic = self.detect_dynamic_constraints(

            text

        )

        for key, value in dynamic.items():

            if key not in standard:

                standard[key] = value

        return standard
    # ---------------------------------------------------------
# Barcode Detection
# ---------------------------------------------------------

    def extract_barcodes(self, text):

        text = self.normalize(text)

        return list(set(
            re.findall(r"\b\d{8,20}\b", text)
        ))


# ---------------------------------------------------------
# Date Detection
# ---------------------------------------------------------

    def extract_dates(self, text):

        text = self.normalize(text)

        patterns = [

            r"\b\d{2}[/-]\d{2}[/-]\d{4}\b",

            r"\b\d{4}[/-]\d{2}[/-]\d{2}\b",

            r"\b\d{2}-[A-Z]{3}-\d{4}\b"

        ]

        dates = []

        for pattern in patterns:

            dates.extend(

                re.findall(pattern, text)

            )

        return list(set(dates))


# ---------------------------------------------------------
# Country Detection
# ---------------------------------------------------------

    def extract_country(self, text):

        countries = [

            "INDIA",
            "BANGLADESH",
            "CHINA",
            "VIETNAM",
            "PAKISTAN",
            "SRI LANKA",
            "CAMBODIA",
            "INDONESIA",
            "MYANMAR",
            "TURKEY"

        ]

        text = self.normalize(text)

        for country in countries:

            if country in text:

                return country

        return ""
    # ---------------------------------------------------------
# Quantity Detection
# ---------------------------------------------------------

    def extract_quantities(self, text):

        text = self.normalize(text)

        return re.findall(

            r"\b\d+\b",

            text

    )


# ---------------------------------------------------------
# Weight Detection
# ---------------------------------------------------------

    def extract_weights(self, text):

        text = self.normalize(text)

        return re.findall(

            r"\d+(?:\.\d+)?\s*(?:KG|KGS|GRAM|GRAMS|LB|LBS|G)",

        text

        )


# ---------------------------------------------------------
# Size Detection
# ---------------------------------------------------------

    def extract_sizes(self, text):

        text = self.normalize(text)

        return list(set(

            re.findall(

                r"\b(XXS|XS|S|M|L|XL|XXL|XXXL)\b",

            text

        )

    ))
        # ---------------------------------------------------------
# Get All Constraints
# ---------------------------------------------------------

    def get_constraints(self, text):

        constraints = self.get_basic_constraints(text)

        country = self.extract_country(text)

        if country:

            constraints["COUNTRY"] = country

        barcodes = self.extract_barcodes(text)

        if barcodes:

            constraints["BARCODES"] = barcodes

        dates = self.extract_dates(text)

        if dates:

            constraints["DATES"] = dates

        quantities = self.extract_quantities(text)

        if quantities:

            constraints["QUANTITIES"] = quantities

        weights = self.extract_weights(text)

        if weights:

            constraints["WEIGHTS"] = weights

        sizes = self.extract_sizes(text)

        if sizes:

            constraints["SIZES"] = sizes

        return constraints# ---------------------------------------------------------
# Print Constraints
# ---------------------------------------------------------

    def print_constraints(self, constraints):

        print()

        print("=" * 80)

        print("DETECTED CONSTRAINTS")

        print("=" * 80)

        if not constraints:

            print("No constraints detected.")

        else:

            for key, value in constraints.items():

                print(f"{key:25} : {value}")

        print("=" * 80)


# ---------------------------------------------------------
# Singleton
# ---------------------------------------------------------

constraint_detector = ConstraintDetector()