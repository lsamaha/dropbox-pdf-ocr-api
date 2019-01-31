from ocr_helper import OCRHelper
from PyPDF2 import PdfFileReader


class PDFHelper(object):

    def __init__(self, ocr_helper):
        self.__ocr_helper = ocr_helper

    def get_text(self, local_doc_path, resolution=120, max_workers=4):
        num_pages = None
        text_lines = None
        with open(local_doc_path, "rb") as f:
            pdf = PdfFileReader(f)
            num_pages = pdf.getNumPages()
            text_lines = self.get_text_lines(pdf)
        print("got %d lines by handling pdf as text" % len(text_lines))
        if num_pages == len(text_lines):
            # suspiciously suspect image pdf
            print("evaluating pdf as image")
            ocr_text_lines = OCRHelper().convert_image_to_text_lines(local_doc_path, resolution, max_workers)
            if len(ocr_text_lines) > len(text_lines):
                print("prefering %d lines of ocr text to %d lines of pdf text" % (len(ocr_text_lines), len(text_lines)))
                text_lines = ocr_text_lines
        return "\n".join(text_lines)

    def get_text_lines(self, pdf):
        all_lines = []

        for p in pdf.pages:
            all_lines += p.extractText().split("\n")
        return all_lines

    def is_pdf(self, file_name):
        pdf_ext = ".pdf"
        return len(file_name) > len(pdf_ext) and file_name[-1 * len(pdf_ext):].lower() == pdf_ext
