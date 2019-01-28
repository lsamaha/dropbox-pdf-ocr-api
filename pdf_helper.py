
class PDFHelper(object):

    def is_image_pdf(self, dropbox_file_path):
        is_pdf = False
        is_image = False
        print("evaluating %s" % dropbox_file_path)
        print("is_pdf %s is_image %s" % (is_pdf, is_image))
        return is_pdf and is_image
