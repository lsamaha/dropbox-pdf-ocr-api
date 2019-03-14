import docx2txt
import logging
import os

class DocxHelper(object):

    __logger = logging.getLogger(__name__)
    __logger.setLevel(logging.DEBUG if 'debug' in os.environ and os.environ['debug'].lower()[0] == 't' else logging.INFO)

    def get_text(self, local_doc_path, resolution=120, max_workers=4):
        self.__logger.info("handling docx %s" % local_doc_path)
        return docx2txt.process(local_doc_path)

    def can_handle(self, file_name):
        docx_ext = ".docx"
        return len(file_name) > len(docx_ext) and file_name[-1 * len(docx_ext):].lower() == docx_ext
