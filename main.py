import xlrd
import crawler
from const import Base


def extract_url(path) -> dict:
    wb = xlrd.open_workbook(path)
    sheet = wb.sheet_by_index(0)
    return {sheet.row_values(i)[1]: sheet.row_values(i)[2] for i in range(1, sheet.nrows)}


if __name__ == '__main__':
    url_list = extract_url(Base.EXCEL_PATH)
    for key in url_list:
        crawler.start_crawler(key, url_list[key])
