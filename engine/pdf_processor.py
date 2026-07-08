"""
=========================================================
Label QC Checker Pro
PDF Processor
Version 1.0
=========================================================
"""

import fitz  # PyMuPDF
from PIL import Image


class PDFProcessor:

    @staticmethod
    def pdf_to_images(pdf_path):

        images = []

        doc = fitz.open(pdf_path)

        for page_number in range(len(doc)):

            page = doc.load_page(page_number)

            matrix = fitz.Matrix(3, 3)

            pix = page.get_pixmap(matrix=matrix)

            mode = "RGB"

            if pix.alpha:
                mode = "RGBA"

            img = Image.frombytes(
                mode,
                [pix.width, pix.height],
                pix.samples
            )

            images.append(img)

        doc.close()

        return images

    @staticmethod
    def page_count(pdf_path):

        doc = fitz.open(pdf_path)

        count = len(doc)

        doc.close()

        return count