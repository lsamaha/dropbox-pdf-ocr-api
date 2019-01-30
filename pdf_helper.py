
class PDFHelper(object):

    def is_image_pdf(self, dropbox_file_path):
        pdf_ext = ".pdf"
        is_pdf = len(dropbox_file_path) > len(pdf_ext) and dropbox_file_path[-1 * len(pdf_ext):].lower() == pdf_ext
        is_image = True
        print("evaluating %s" % dropbox_file_path)
        print("is_pdf %s is_image %s" % (is_pdf, is_image))
        return is_pdf and is_image

    def is_pdf(self, dropbox_file_path):
        pdf_ext = ".pdf"
        is_pdf = len(dropbox_file_path) > len(pdf_ext) and dropbox_file_path[-1 * len(pdf_ext):].lower() == pdf_ext
        is_image = True
        print("evaluating %s" % dropbox_file_path)
        print("is_pdf %s is_image %s" % (is_pdf, is_image))
        return is_pdf and is_image
