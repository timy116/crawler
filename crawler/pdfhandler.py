import os
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager, PDFDocument, PDFParser
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LTTextBoxHorizontal, LAParams


def extract_text(pdf, keyword) -> tuple:
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
    text = ''
    for o in layout:
        if isinstance(o, LTTextBoxHorizontal):
            pdf_text = o.get_text().strip().replace(' ', '')
            if pdf_text.find('時期') != -1 or pdf_text.find('農業統計年報') != -1:
                text = pdf_text
            if text.find(keyword) != -1:
                return True, text
    return False, text


def read_all_pdf(path):
    files = os.listdir(path)
    for f_n in files:
        pdf = open(path + '/' + f_n, 'rb')
        extract_text(pdf, '')
