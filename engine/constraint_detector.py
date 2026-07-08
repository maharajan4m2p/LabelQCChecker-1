"""
=========================================================
Label QC Checker Pro
Advanced Constraint Detector
Version 5.0
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
            "MADE IN",
            "LOT NO",
            "BATCH NO",
            "MFG DATE",
            "EXP DATE",
            "MRP",
            "PRICE"

        ]

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
            r"MADE\s*IN\s*[:\-]?\s*(.+)",

            "LOT NO":
            r"LOT\s*NO\.?\s*[:\-]?\s*(.+)",

            "BATCH NO":
            r"BATCH\s*NO\.?\s*[:\-]?\s*(.+)",

            "MFG DATE":
            r"(?:MFG|MANUFACTURED)\s*DATE\s*[:\-]?\s*(.+)",

            "EXP DATE":
            r"(?:EXP|EXPIRY|EXPIRATION)\s*DATE\s*[:\-]?\s*(.+)",

            "MRP":
            r"MRP\s*[:\-]?\s*(.+)",

            "PRICE":
            r"PRICE\s*[:\-]?\s*(.+)"

        }

    # ---------------------------------------------------------
    # Normalize
    # ---------------------------------------------------------

    def normalize(self, text):

        if text is None:

            return ""

        text = str(text).upper()

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

        value = value.replace("\n", " ")

        value = value.replace("\r", " ")

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
    # Extract Standard Constraints
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

                value = self.clean(

                    match.group(1)

                )

                if value != "":

                    constraints[field] = value

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

            if ":" in line:

                parts = line.split(":",1)

            elif "-" in line:

                parts = line.split("-",1)

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
    # Merge Constraints
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

    def extract_barcodes(

        self,

        text

    ):

        text = self.normalize(text)

        return list(

            set(

                re.findall(

                    r"\b\d{8,20}\b",

                    text

                )

            )

        )

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

            r"\b\d{2}-[A-Z]{3}-\d{4}\b",

            r"\b[A-Z]{3}\s+\d{2},\s+\d{4}\b"

        ]

        dates = []

        for pattern in patterns:

            dates.extend(

                re.findall(

                    pattern,

                    text

                )

            )

        return list(

            set(

                dates

            )

        )
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

            r"\d+(?:\.\d+)?\s*(?:KG|KGS|GRAM|GRAMS|G|LB|LBS)",

            text

        )

    # ---------------------------------------------------------
    # Size Detection
    # ---------------------------------------------------------

    def extract_sizes(self, text):

        text = self.normalize(text)

        return list(

            set(

                re.findall(

                    r"\b(XXS|XS|S|M|L|XL|XXL|XXXL|FREE|OS)\b",

                    text

                )

            )

        )

    # ---------------------------------------------------------
    # Price / MRP Detection
    # ---------------------------------------------------------

    def extract_prices(self, text):

        text = self.normalize(text)

        prices = re.findall(

            r"(?:RS\.?|INR|\$|€|£)?\s*\d+(?:\.\d{1,2})?",

            text

        )

        return list(set(prices))

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

        prices = self.extract_prices(text)

        if prices:

            constraints["PRICES"] = prices

        return constraints

    # ---------------------------------------------------------
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

            for key in sorted(constraints.keys()):

                print(f"{key:25} : {constraints[key]}")

        print("=" * 80)


# ---------------------------------------------------------
# Singleton
# ---------------------------------------------------------

constraint_detector = ConstraintDetector()