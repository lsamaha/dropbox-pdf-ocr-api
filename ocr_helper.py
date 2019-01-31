import io
from concurrent.futures import ThreadPoolExecutor
import tesserocr
from wand.image import Image as WandImage
from PIL import Image as PILImage
import datetime


class OCRHelper(object):

    def __init__(self):
        pass

    def convert_image_to_text_lines(self, image_path, resolution=200, max_workers=4):
        pg_texts = []
        image_pdf = WandImage(filename=image_path, resolution=resolution)
        print("opened pdf as image")
        jpg = image_pdf.convert('jpeg')
        print("converted pdf to jpeg")
        img_pgs = []
        for img in jpg.sequence:
            img_pg = WandImage(image=img)
            img_pgs.append(img_pg.make_blob('jpeg'))
        start_time = datetime.datetime.now()
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            result = executor.map(convert_image_bytes_to_text_lines, img_pgs)
        for part in list(result):
            pg_texts += part
        print("completed ocr tasks in %ds" % (datetime.datetime.now() - start_time).seconds)
        return pg_texts


def convert_image_bytes_to_text_lines(img):
    return tesserocr.image_to_text(PILImage.open(io.BytesIO(img))).split("\n")
