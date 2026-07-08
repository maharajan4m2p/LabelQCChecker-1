import fitz  # PyMuPDF
from PIL import Image


class PDFProcessor:

    @staticmethod
    def pdf_to_images(pdf_path, first_page=1, last_page=1):

        images = []

        doc = fitz.open(pdf_path)

        total_pages = len(doc)

        first_page = max(1, first_page)
        last_page = min(last_page, total_pages)

        for page_number in range(first_page - 1, last_page):

            page = doc.load_page(page_number)

            matrix = fitz.Matrix(2, 2)

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

            del pix
            del page

        doc.close()

        return images

    @staticmethod
    def page_count(pdf_path):

        doc = fitz.open(pdf_path)

        count = len(doc)

        doc.close()

        return count