import io
import tesserocr
from wand.image import Image as WandImage
import PIL


class OCRHelper(object):

    def __init__(self):
        pass

    def convert_image(self, image_path):
        pg_texts = []
        image_pdf = WandImage(filename=image_path, resolution=300)
        jpg = image_pdf.convert('jpeg')
        img_pgs = []
        for img in jpg.sequence:
            img_pg = WandImage(image=img)
            img_pgs.append(img_pg.make_blob('jpeg'))
        for img in img_pgs:
            pillImg = PIL.Image.open(io.BytesIO(img))
            pg_texts.append(tesserocr.image_to_text(pillImg))
        print(pg_texts)
        return "\n".join(pg_texts)
