import io
import requests
import sys
import time
import pdfhandler
import pyexcel_ods
import xlrd
from bs4 import BeautifulSoup as bs
from const import Base
from datetime import date
from log import log, err_log
from pprint import pprint
from selenium import webdriver
from request_info_creator import (
    AgrstatOfficialInfoCreator as agroff,
    ForestCreator,
    SwcbCreator,
    InquireAdvanceCreator as ia,
    WoodPriceCreator,
)

# 西元轉民國年
YEAR = date.today().year - 1911
kws_d = {}
kws_l = []
forest_kws_l = []
req = requests.Session()


def start_crawler(key, url) -> None:
    """
    找到對應網址的 fn
    :param key:關鍵字
    :param url: 要解析的網址
    :return: None
    """

    # if url.find('OfficialInformation') != -1:
    #     extract_agrstat_official_info(key, url)

    # if url.find('swcb') != -1:
    #     extract_swcb(key, url)

    if url.find('0000575') != -1:
        extract_forest(key, url)

    # if url.find('InquireAdvance') != -1:
    #     extract_inquire_advance(key, url)

    # if url.find('woodprice') != -1:
    #     extract_wood_price(key, url)


def extract_agrstat_official_info(key, url) -> None:
    """
    將關鍵字與網址傳進來，一次創建所有關鍵字的列表，
    將網頁解析後取出網頁的關鍵字跟關鍵字列表比對，若存在就刪除直到關鍵字列表個數為零
    同時判斷若以解析到最後一頁要結束迴圈
    :param key: 關鍵字
    :param url: 網址，解析用
    :return: None
    """
    kws_d[key] = ''
    if len(kws_d) == agroff.KEYWORDS_LENTH:
        creator = agroff()
        driver = get_web_driver()
        driver.get(url)
        while True:
            if len(kws_d) == 0:
                driver.quit()
                break
            try:
                soup = bs(driver.page_source, 'lxml')
                kws1 = soup.select('tr.Row > td:nth-of-type(3)')
                kws2 = soup.select('tr.AlternatingRow > td:nth-of-type(3)')
                for k in kws1+kws2:
                    k = k.get_text().strip()
                    if k in kws_d.keys():
                        log.info('find ' + k + ' at page ' + str(creator.get_page_index()))
                        del kws_d[k]

                # 取得最後一個 td tag 的文字，用來判斷是否為最後一頁或者是更多頁面
                flag = soup.select('tr.Pager > td > table > tbody > tr > td')[-1].get_text()
                if flag == '...':
                    if creator.get_page_index().endswith('0'):
                        driver.find_element_by_xpath(
                            '//tr[@class="Pager"]/td/table/tbody/tr/td[last()]/a[contains(text(), "...")]').click()
                        creator.next_page()
                        continue
                else:
                    if creator.get_page_index() == flag:
                        driver.quit()
                        if len(kws_d) != 0:
                            err_log.warning('not found keyword: ' + str(kws_d.keys()))
                        print('Page end, ', creator.get_page_index(), 'pages')
                        break
                creator.next_page()
                driver.find_element_by_xpath(
                    '//tr[@class="Pager"]/td/table/tbody/tr/td/a[contains(text(), ' + creator.get_page_index() + ')]')\
                    .click()

                driver.implicitly_wait(3)
            except Exception:
                driver.quit()
                t, v, tr = sys.exc_info()
                err_log.error('error occurred.\n' + str(t) + '\n' + str(v))
                break


def extract_swcb(key, url) -> None:
    """
    將關鍵字與網址傳進來，一次創建所有關鍵字的列表，
    將網頁解析後取出網頁的關鍵字跟關鍵字列表比對，若存在則將 key 與 url 加到字典裡
    並迭代開啟 excel 確認年度是否正確
    :param key: 關鍵字
    :param url: 網址，解析用
    :return: None
    """
    # 創建關鍵字列表
    kws_l.append(key)
    if len(kws_l) == SwcbCreator.KEYWORDS_LENTH:
        creator = SwcbCreator()
        k_f_l_d = {}
        soup = bs(requests.get(url, headers=creator.headers).text, 'lxml')
        # 頁面上的關鍵字
        kw = [i.get_text() for i in soup.select('div.lastList > ul > li > a > h3')]
        # 連結網址
        file_link = ['/'.join(url.split('/')[:-1]) + '/{}'.format(i.get('href'))
                     for i in soup.select('div.lastList > ul > li > a')]
        # 頁面關鍵字如果有在列表裡，則加到字典裡
        for w, f in zip(kw, file_link):
            if any((w.find(i) != -1) for i in kws_l):
                k_f_l_d[w] = f

        # 迭代搜尋關鍵字
        for k, v in k_f_l_d.items():
            if find_kw(v, creator.KEYWORD.format(str(YEAR - 1))):
                log.info(k + '年度正確')
            else:
                err_log.warning(k + ' 未在指定時間內上傳')


def extract_forest(key, url) -> None:
    forest_kws_l.append(key)
    if len(forest_kws_l) == ForestCreator.KEYWORDS_LENTH:
        creator = ForestCreator()
        k_f_l_d = {}
        soup = bs(requests.get(url, headers=creator.headers).text, 'lxml')
        kw = [i.get_text() for i in soup.select('#divContent > div.downloadBox > table > tbody > tr > td:nth-of-type(1)')]
        file_link = ['/'.join(url.split('/')[:-1]) + '{}'.format(i.get('href'))
                     for i in soup.select('#divContent > div.downloadBox > table > tbody > tr > td > a')]
        for w, f in zip(kw, file_link):
            if any((w.find(i) != -1) for i in forest_kws_l):
                k_f_l_d[w] = f
        for k, v in k_f_l_d.items():
            if k == '造林面積':
                now = time.strftime('%m%d%H%M')
                keyword = '{}年第{}季'
                month = ['', '01311700', '', '', '04301700', '', '', '07311700', '', '', '10311700']
                if month[1] < now <= month[4]:
                    format_keyword = keyword.format(YEAR, 4)
                    datetime_start = month[1]
                    datetime_end = month[4]
                elif month[4] < now <= month[7]:
                    format_keyword = keyword.format(YEAR, 1)
                    datetime_start = month[4]
                    datetime_end = month[7]
                elif month[7] < now <= month[10]:
                    format_keyword = keyword.format(YEAR, 2)
                    datetime_start = month[7]
                    datetime_end = month[10]
                else:
                    format_keyword = keyword.format(YEAR, 3)
                    datetime_start = month[10]
                    datetime_end = month[1]
                find, text = pdfhandler.extract_text(io.BytesIO(requests.get(v).content), keyword)
                if find:
                    log.info(datetime_start + '-' + datetime_end + '--' + format_keyword + ' | ' + k + ' : ' + text)
                else:
                    err_log.warning(datetime_start + '-' + datetime_end + '--' + format_keyword + ' | ' + k + ' : ' + text)
            if k == '林務局森林遊樂區收入':
                keyword = '{}年{}月'
                flag_month, datetime_start, datetime_end = datetime_maker(creator.DAY)
                format_keyword = keyword.format(YEAR, int(flag_month) - 1)
                find, text = find_kw(v, format_keyword, 'ods')
                if find:
                    log.info(datetime_start + '-' + datetime_end + '--' + format_keyword + ' | ' + k + ' : ' + text)
                else:
                    err_log.warning(datetime_start + '-' + datetime_end + '--' + format_keyword + ' | ' + key + ' : ' + text)


def extract_inquire_advance(key, url) -> None:
    """
    如果 key == 老農津貼相關, 月份為當月的前兩個月, 其他則為前一個月
    last_two_tr: 因最新的月份為倒數第二個 tr 元素, 因此可用來判斷是否未在指定時間內更新資料
    :param key: 農民生產所得物價指數, 農民生產所付物價指數, 老年農民福利津貼核付人數, 老年農民福利津貼核付金額
    :param url: http://agrstat.coa.gov.tw/sdweb/public/inquiry/InquireAdvance.aspx
    :return: None
    """
    creator = ia(key)
    flag_month, datetime_start, datetime_end = datetime_maker(creator.DAY)

    if key == '老年農民福利津貼核付人數' or key == '老年農民福利津貼核付金額':
        keyword = creator.KEYWORD.format(int(flag_month)-2)
    else:
        keyword = creator.KEYWORD.format(int(flag_month)-1)
    soup = bs(req.post(url, headers=creator.headers, data=creator.form_data).text, 'lxml')
    last_two_tr = soup.select('#ctl00_cphMain_uctlInquireAdvance_tabResult > tr')[-2]
    text = last_two_tr.get_text().strip().replace(' ', '')
    if text.find(keyword) != -1:
        log.info(datetime_start + '-' + datetime_end + '--' + keyword + ' | ' + key + ' : ' + text)
    else:
        err_log.warning(datetime_start + '-' + datetime_end + '--' + keyword + ' | ' + key + ' : ' + text)


def extract_wood_price(key, url) -> None:
    """
    爬取 木材市價 website
    :param key: 木材市價
    :param url: https://woodprice.forest.gov.tw/Compare/Q_CompareProvinceConiferous.aspx
    :return: None
    """
    creator = WoodPriceCreator()
    flag_month, datetime_start, datetime_end = datetime_maker(creator.DAY)

    def request(i=0):
        creator.set_years(YEAR)
        creator.set_months(int(flag_month) - i)
        format_keyword = creator.KEYWORD.format(YEAR, int(flag_month) - i)
        soup = bs(req.post(url, headers=creator.headers, data=creator.form_data).content, 'lxml')
        tr = soup.select('#ctl00_Main_q2_gv > tr:nth-of-type(2)')[0]
        text = tr.get_text().strip().replace(' ', '')
        if i != 0:
            if text.find(format_keyword) != -1:
                log.info(datetime_start + '-' + datetime_end + '--' + format_keyword + ' | ' + key + ' : ' + text)
            else:
                err_log.warning(datetime_start + '-' + datetime_end + '--' + format_keyword + ' | ' + key + ' : ' + text)
        else:
            if text.find(format_keyword) != -1:
                err_log.warning(datetime_start + '-' + datetime_end + '--' +
                                creator.KEYWORD.format(YEAR, int(flag_month) - 1) + ' | ' + key + ' : ' + text)
    request(1)
    request()


def find_kw(link, keyword, file_type='excel') -> tuple:
    """
    開啟 excel 並確認年度是否正確
    :param link: files url
    :param keyword: keyword select
    :param file_type:
    :return: tuple
    """
    if file_type != 'excel':
        calc = pyexcel_ods.get_data(io.BytesIO(req.get(link).content))
        sheet = list(calc.values())[0]
        text = ''
        for row in sheet:
            for cell in row:
                cell_text = str(cell).strip().replace(' ', '')
                if cell_text.find('時期') != -1:
                    text = cell_text
                    if keyword in text:
                        return True, text
        return False, text

    wb = xlrd.open_workbook(file_contents=requests.get(link).content)
    sheet = wb.sheet_by_index(0)
    text = ''
    for i in range(sheet.nrows):
        for j in range(sheet.ncols):
            value = str(sheet.row_values(i)[j]).strip().replace(' ', '')
            if value.find('中華民國') != -1:
                text = value
                if keyword in value:
                    return True, text
        return False, text


def datetime_maker(day) -> tuple:
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
    dateline = '{}{}1700'
    month = str(date.today().month).rjust(2, '0')
    flag_month = month if dateline.format(month, day[int(month)]) < now else str(int(month) - 1).rjust(2, '0')
    next_flag_month = month if dateline.format(month, day[int(month)]) > now else str(int(month) + 1).rjust(2, '0')
    datetime_start = dateline.format(flag_month, day[int(month)])
    datetime_end = dateline.format(next_flag_month, day[int(next_flag_month)])
    return flag_month, datetime_start, datetime_end


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


if __name__ == '__main__':
    pdfhandler.read_all_pdf(Base.PDF_PATH)
