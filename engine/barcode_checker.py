"""
=========================================================
Label QC Checker Pro
Barcode Checker
Version 2.0
=========================================================
"""

import cv2
import numpy as np

from config import *

try:
    from pyzbar.pyzbar import decode
    PYZBAR_AVAILABLE = True
except ImportError:
    PYZBAR_AVAILABLE = False


class BarcodeChecker:

    def __init__(self):

        self.available = PYZBAR_AVAILABLE
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
# Convert To Gray
# ---------------------------------------------------------

    def gray(

        self,

        image

)   :

        return cv2.cvtColor(

            image,

            cv2.COLOR_BGR2GRAY

        )
        
    # ---------------------------------------------------------
# Barcode Preprocess
# ---------------------------------------------------------

    def preprocess(

        self,

        image

    ):

        gray = self.gray(

            image

        )

        gray = cv2.GaussianBlur(

            gray,

            (3, 3),

            0

        )

        return gray
    # ---------------------------------------------------------
# Decode Barcode
# ---------------------------------------------------------

    def decode_barcode(

        self,

        image

    ):

        if not self.available:

            return None

        processed = self.preprocess(

            image

        )

        results = decode(

            processed

        )

        if len(results) == 0:

            return None

        return results[0].data.decode(

            "utf-8"

        
        )
        # ---------------------------------------------------------
# Compare Barcodes
# ---------------------------------------------------------

    def compare(

        self,

        approval_image,

        sample_image

    ):

        approval = self.load_image(

            approval_image

        )

        sample = self.load_image(

            sample_image

        )

        approval_barcode = self.decode_barcode(

            approval

        )

        sample_barcode = self.decode_barcode(

            sample

        )

        if approval_barcode is None or sample_barcode is None:

            return {

                "approval": approval_barcode,

                "sample": sample_barcode,

                "status": "NOT FOUND"

            }

        status = "PASS"

        if approval_barcode != sample_barcode:

            status = "FAIL"

        return {

            "approval": approval_barcode,

            "sample": sample_barcode,

            "status": status

        }
        # ---------------------------------------------------------
# Print Result
# ---------------------------------------------------------

    def print_result(

        self,

        result

    ):

        print()

        print("=" * 70)

        print("BARCODE CHECK")

        print("=" * 70)

        print(

            "Approval :",

            result["approval"]

        )

        print(

            "Sample :",

            result["sample"]

        )

        print(

            "Status :",

            result["status"]

        )

        print("=" * 70)
barcode_checker = BarcodeChecker()