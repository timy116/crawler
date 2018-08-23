import os
from log import SimpleLog as sl
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager, PDFDocument, PDFParser
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LTTextBoxHorizontal, LAParams

log = sl()
log.set_level(20)


def extract_text(pdf) -> int:
    parser = PDFParser(pdf)
    doc = PDFDocument()
    parser.set_document(doc)
    doc.set_parser(parser)
    doc.initialize()

    rsrcmgr = PDFResourceManager()
    laparams = LAParams()
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)

    page = list(doc.get_pages())[0]
    interpreter.process_page(page)
    layout = device.get_result()
    for o in layout:
        if isinstance(o, LTTextBoxHorizontal):
            log.info(o.get_text().strip().replace(' ', ''))
            # if o.get_text().strip().replace(' ', '') in '':
            #     print('find : ', o.get_text())
    #         return True
    # return False


def read_all_pdf(path):
    files = os.listdir(path)
    for f_n in files:
        pdf = open(path + '/' + f_n, 'rb')
        extract_text(pdf)
