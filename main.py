import crawler
import xlrd
from const import Base


def extract_url(path) -> dict:
    wb = xlrd.open_workbook(path)
    sheet = wb.sheet_by_index(0)
    return {sheet.row_values(i)[1]: sheet.row_values(i)[2] for i in range(1, sheet.nrows)}


if __name__ == '__main__':

    url_dict = extract_url(Base.EXCEL_PATH)
    for k, v in url_dict.items():
        crawler.start_crawler(k, v)
