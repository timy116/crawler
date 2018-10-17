from bs4 import BeautifulSoup as bs
from datetime import date
from log import SimpleLog as sl
from selenium import webdriver
import csv
import io
import pyexcel_ods
import requests
import time
import xlrd

AD_YEAR = date.today().year
# 西元轉民國年
YEAR = AD_YEAR - 1911
# switch-like
LAMBDA_DICT = {
    'kw_list': lambda l: [i.get_text().strip().replace(' ', '') for i in l],
    'file_link_list': lambda url, l: [url.format(i.get('href')) for i in l],
    'specified_element_text': lambda l, x: l[x].get_text().strip().replace(' ', ''),
    'specified_file_link_slice': lambda url, l, x: str(url + l[x].get('href').split('/')[1]),
    'specified_file_link': lambda url, l, x: str(url + l[x].get('href')),
}

req = requests.Session()


def get_html_element(*args, method='post', page_source=None, return_soup=False, **kwargs):
    """
    get html element.
    :param args: str, soup selector, 但可能不只取得一個元素
    :param method: post or get
    :param page_source: if use selenium, pass driver.page_source
    :param return_soup: bool, if True, 代表要回傳 soup (reuse)
    :param kwargs: url and creator
    :return: list or tuple
    """
    element_list = []

    if page_source is not None:
        content = page_source
    else:
        creator = kwargs['creator']
        if method != 'post':
            content = req.get(kwargs['url'], headers=creator.headers).text
        else:
            content = req.post(kwargs['url'], headers=creator.headers, data=creator.form_data).content

    soup = bs(content, 'lxml')
    for i in args:
        element_list.extend(soup.select(i))
    if return_soup:
        return element_list, lambda x: soup.select(x)
    else:
        return element_list


def find_kw(link, keyword, file_type='excel') -> tuple:
    """
    開啟 excel 並確認年度是否正確
    :param link: files url
    :param keyword: keyword select
    :param file_type:
    :return: tuple
    """
    text = ''
    if file_type == 'ods':
        calc = pyexcel_ods.get_data(io.BytesIO(req.get(link).content))
        sheet = list(calc.values())[0]
        for row in sheet:
            for cell in row:
                cell_text = str(cell).strip().replace(' ', '')
                if any(cell_text.find(i) != -1 for i in ['時期', '月份']):
                    text = cell_text
                    if keyword in text:
                        return True, text
        return False, text
    elif file_type == 'csv':
        rows = csv.reader(io.BytesIO(req.get(link).content).read().decode('big5'))
        for i in rows:
            for j in i:
                s = str(j).strip().replace('\u3000', '').replace(' ', '')
                if any(s.find(i) != -1 for i in ['中華民國']):
                    text = s
                    if keyword in text:
                        return True, text
                    else:
                        return False, text

    wb = xlrd.open_workbook(file_contents=requests.get(link).content)
    sheet = wb.sheet_by_index(0)
    for i in range(sheet.nrows):
        for j in range(sheet.ncols):
            value = str(sheet.row_values(i)[j]).strip().replace(' ', '')
            if value.find('中華民國') != -1:
                text = value
                if keyword in value:
                    return True, text
    return False, text


def datetime_maker(day=None) -> tuple:
    """
    產生發布日期的期間 ex: X月X日 - X月X日
    :param day: every month's release day
    :return: tuple
    now: 當下時間
    flag month: 是當月還是上個月份, 若為個位數月份前面須補 0
    datetime_start: release date start
    datetime_end: release date end
    """
    now = time.strftime('%m%d%H%M')
    if day:
        dateline = '{}{}1700'
        month = str(date.today().month).rjust(2, '0')

        # 判斷 now 是否大於當月日期, if True month=this month else month=previous month
        # ex: 09251700 < 09121700 ? if True month=09 else month=08
        flag_month = month if dateline.format(month, day[int(month)]) < now else str(int(month) - 1).rjust(2, '0')
        next_flag_month = month if dateline.format(month, day[int(month)]) > now else str(int(month) + 1).rjust(2, '0')
        datetime_start = dateline.format(flag_month, str(day[int(flag_month)]).rjust(2, '0'))
        datetime_end = dateline.format(next_flag_month, str(day[int(next_flag_month)]).rjust(2, '0'))
        sl.set_msg(datetime_start, datetime_end)
        return flag_month, datetime_start, datetime_end
    else:
        dateline = '05151700'
        flag_year = YEAR if '05151700' < now else YEAR-1
        datetime_start = str(flag_year) + dateline
        datetime_end = str(flag_year+1) + dateline
        sl.set_msg(datetime_start, datetime_end)
        return flag_year, datetime_start, datetime_end


def get_web_driver() -> webdriver:
    """
    設定 Chrome 參數並回傳
    :return: webdriver object
    """
    option = webdriver.ChromeOptions()
    option.add_argument('--disable-images')
    option.add_argument('--disable-gpu')
    option.add_argument('headless')
    driver = webdriver.Chrome(chrome_options=option)
    return driver