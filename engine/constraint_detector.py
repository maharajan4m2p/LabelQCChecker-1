"""
=========================================================
Label QC Checker Pro
Constraint Detector
Version 2.0
=========================================================
"""

import re
from rapidfuzz import fuzz

from config import *


class ConstraintDetector:

    def __init__(self):

        # Standard Constraint Fields

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

        # Regex Patterns

        self.patterns = {

            "BUYER":
            r"BUYER\s*[:\-]?\s*(.+)",

            "BUYER CODE":
            r"BUYER\s*CODE\s*[:\-]?\s*(.+)",

            "VENDOR":
            r"VENDOR\s*[:\-]?\s*(.+)",

            "VENDOR CODE":
            r"VENDOR\s*CODE\s*[:\-]?\s*(.+)",

            "PO NO":
            r"P\.?\s*O\.?\s*NO\.?\s*[:\-]?\s*(.+)",

            "STYLE NO":
            r"STYLE\s*NO\.?\s*[:\-]?\s*(.+)",

            "DESCRIPTION":
            r"DESCRIPTION\s*[:\-]?\s*(.+)",

            "COLOR":
            r"COLOR\s*[:\-]?\s*(.+)",

            "SIZE":
            r"SIZE\s*[:\-]?\s*(.+)",

            "SIZE ASSORTMENT":
            r"SIZE\s*ASSORTMENT\s*[:\-]?\s*(.+)",

            "TOTAL QTY":
            r"TOTAL\s*QTY\.?\s*[:\-]?\s*(.+)",

            "MEASUREMENT":
            r"MEASUREMENT\s*[:\-]?\s*(.+)",

            "VOLUME":
            r"VOLUME\s*[:\-]?\s*(.+)",

            "CARTON NO":
            r"CARTON\s*NO\.?\s*[:\-]?\s*(.+)",

            "CARTON TYPE":
            r"CARTON\s*TYPE\s*[:\-]?\s*(.+)",

            "NET WEIGHT":
            r"NET\s*WEIGHT\s*[:\-]?\s*(.+)",

            "GROSS WEIGHT":
            r"GROSS\s*WEIGHT\s*[:\-]?\s*(.+)",

            "DESTINATION":
            r"DESTINATION\s*[:\-]?\s*(.+)",

            "SHIP DATE":
            r"SHIP\s*DATE\s*[:\-]?\s*(.+)",

            "SEASON":
            r"SEASON\s*[:\-]?\s*(.+)",

            "ITEM NO":
            r"ITEM\s*NO\.?\s*[:\-]?\s*(.+)",

            "BARCODE":
            r"BARCODE\s*[:\-]?\s*(.+)",

            "UPC":
            r"UPC\s*[:\-]?\s*(.+)",

            "EAN":
            r"EAN\s*[:\-]?\s*(.+)",

            "SKU":
            r"SKU\s*[:\-]?\s*(.+)",

            "CUSTOMER":
            r"CUSTOMER\s*[:\-]?\s*(.+)",

            "COUNTRY OF ORIGIN":
            r"COUNTRY\s*OF\s*ORIGIN\s*[:\-]?\s*(.+)",

            "MADE IN":
            r"MADE\s*IN\s*[:\-]?\s*(.+)"

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

        text = re.sub(r"\s+", " ", text)

        return text.strip()


# ---------------------------------------------------------
# Clean Extracted Value
# ---------------------------------------------------------

    def clean(self, value):

        if value is None:
            return ""

        value = str(value)

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
# Extract Constraints Using Regex
# ---------------------------------------------------------

    def extract_constraints(

        self,

        text

    ):

        text = self.normalize(text)

        constraints = {}

        for field, pattern in self.patterns.items():

            match = re.search(

                pattern,

                text,

                re.IGNORECASE | re.MULTILINE

            )

            if match:

                constraints[field] = self.clean(

                    match.group(1)

                )

        return constraints
    # ---------------------------------------------------------
# Dynamic Key-Value Detection
# ---------------------------------------------------------

    def detect_dynamic_constraints(

        self,

        text

    ):

        text = self.normalize(text)

        lines = text.splitlines()

        dynamic = {}

        for line in lines:

            line = line.strip()

            if len(line) < 3:

                continue

            # KEY : VALUE

            if ":" in line:

                key, value = line.split(":", 1)

                key = self.clean(key)

                value = self.clean(value)

                if key and value:

                    dynamic[key] = value

            # KEY - VALUE

            elif "-" in line:

                parts = line.split("-", 1)

                if len(parts) == 2:

                    key = self.clean(parts[0])

                    value = self.clean(parts[1])

                    if key and value:

                        dynamic[key] = value

        return dynamic


# ---------------------------------------------------------
# Merge Regex + Dynamic Constraints
# ---------------------------------------------------------

    def get_basic_constraints(

        self,

        text

    ):

        constraints = self.extract_constraints(

            text

        )

        dynamic = self.detect_dynamic_constraints(

            text

        )

        for key, value in dynamic.items():

            if key not in constraints:

                constraints[key] = value

        return constraints
    # ---------------------------------------------------------
# Barcode Detection
# ---------------------------------------------------------

    def extract_barcodes(

        self,

        text

    ):

        text = self.normalize(text)

        barcodes = re.findall(

            r"\b\d{8,20}\b",

            text

        )

        return list(set(barcodes))


# ---------------------------------------------------------
# Country Detection
# ---------------------------------------------------------

    def extract_country(

        self,

        text

    ):

        countries = [

            "BANGLADESH",
            "INDIA",
            "CHINA",
            "VIETNAM",
            "PAKISTAN",
            "CAMBODIA",
            "INDONESIA",
            "SRI LANKA",
            "MYANMAR",
            "TURKEY"

        ]

        text = self.normalize(text)

        for country in countries:

            if country in text:

                return country

        return ""


# ---------------------------------------------------------
# Date Detection
# ---------------------------------------------------------

    def extract_dates(

        self,

        text

    ):

        text = self.normalize(text)

        patterns = [

            r"\b\d{2}[/-]\d{2}[/-]\d{4}\b",

            r"\b\d{4}[/-]\d{2}[/-]\d{2}\b",

            r"\b\d{2}-[A-Z]{3}-\d{4}\b"

        ]

        dates = []

        for pattern in patterns:

            dates.extend(

                re.findall(

                    pattern,

                    text

                )

            )

        return list(set(dates))


# ---------------------------------------------------------
# Quantity Detection
# ---------------------------------------------------------

    def extract_quantities(

        self,

        text

    ):

        text = self.normalize(text)

        quantities = re.findall(

            r"\b\d+\b",

            text

        )

        return quantities


# ---------------------------------------------------------
# Weight Detection
# ---------------------------------------------------------

    def extract_weights(

        self,

        text

    ):

        text = self.normalize(text)

        weights = re.findall(

            r"\d+(?:\.\d+)?\s*(?:KG|KGS|G|GRAM|GRAMS|LB|LBS)",

            text

        )

        return weights


# ---------------------------------------------------------
# Size Detection
# ---------------------------------------------------------

    def extract_sizes(

        self,

        text

    ):

        text = self.normalize(text)

        sizes = re.findall(

            r"\b(XXS|XS|S|M|L|XL|XXL|XXXL)\b",

            text

        )

        return list(set(sizes))
    # ---------------------------------------------------------
# Get All Constraints
# ---------------------------------------------------------

    def get_constraints(

        self,

        text

    ):

        constraints = self.get_basic_constraints(

            text

        )

        country = self.extract_country(

            text

        )

        if country:

            constraints["COUNTRY"] = country

        barcodes = self.extract_barcodes(

            text

        )

        if barcodes:

            constraints["BARCODES"] = barcodes

        dates = self.extract_dates(

            text

        )

        if dates:

            constraints["DATES"] = dates

        quantities = self.extract_quantities(

            text

        )

        if quantities:

            constraints["QUANTITIES"] = quantities

        weights = self.extract_weights(

            text

        )

        if weights:

            constraints["WEIGHTS"] = weights

        sizes = self.extract_sizes(

            text

        )

        if sizes:

            constraints["SIZES"] = sizes

        return constraints


# ---------------------------------------------------------
# Print Constraints
# ---------------------------------------------------------

    def print_constraints(

        self,

        constraints

    ):

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
# Singleton Object
# ---------------------------------------------------------

constraint_detector = ConstraintDetector()