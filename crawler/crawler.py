import io
import mailhandler
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
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from log import SimpleLog as sl
from request_info_creator import (
    AgrstatOfficialInfoCreator as agroff,
    ForestCreator as fc,
    SwcbCreator as sc,
    InquireAdvanceCreator as ia,
    WoodPriceCreator as wc,
    AgrstatBookCreator as abc,
    ApisAfaCreator as aac,
    PirceNaifCreator as pnc,
)

AD_YEAR = date.today().year
# 西元轉民國年
YEAR = AD_YEAR - 1911
# switch-like
LAMBDA_DICT = {
    'kw_list': lambda l: [i.get_text().strip().replace(' ', '') for i in l],
    'file_link_list': lambda url, l: [url.format(i.get('href')) for i in l],
    'specfied_element_text': lambda l, x: l[x].get_text().strip().replace(' ', ''),
    'specfied_file_link': lambda url, l, x: str(url + l[x].get('href').split('/')[1]),
}

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
    #
    if url.find('swcb') != -1:
        extract_swcb(key, url)
    #
    # elif url.find('0000575') != -1:
    #     extract_forest(key, url)
    #
    # elif url.find('InquireAdvance') != -1:
    #     extract_inquire_advance(key, url)
    #
    # elif url.find('woodprice') != -1:
    #     extract_wood_price(key, url)
    #
    # elif url.find('book') != -1:
    #     extract_agrstat_book(key, url)
    # #
    # elif url.find('apis.afa.gov.tw') != -1:
    #     extract_apis_afa(key, url)
    # #
    # elif url.find('price.naif.org.tw') != -1:
    #     extract_price_naif(key, url)


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
                element, soup = get_html_element(agroff.SELECT_DICT['tr_row1'], agroff.SELECT_DICT['tr_row2'],
                                                 page_source=driver.page_source, return_soup=True)
                kw_list = LAMBDA_DICT['kw_list'](element)
                for k in kw_list:
                    if k in kws_d.keys():
                        log.info('find ', k, ' at page ', creator.get_page_index(), unpacking=False)
                        del kws_d[k]

                # 取得最後一個 td tag 的文字，用來判斷是否為最後一頁或者是更多頁面
                flag = LAMBDA_DICT['specfied_element_text'](soup(agroff.SELECT_DICT['td']), -1)
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
                            err_log.warning('not found keyword: ', kws_d.keys(), unpacking=False)
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
                err_log.error('error occurred.\t', t, '\t', v)
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
    kws_l.append(key)
    if len(kws_l) == sc.KEYWORDS_LENTH:
        creator = sc()
        k_f_l_d = {}
        element, soup = get_html_element(sc.SELECT_DICT['h3'], method='get', return_soup=True, url=url, creator=creator)
        # 頁面上的關鍵字
        kw = LAMBDA_DICT['kw_list'](element)
        # 連結網址
        file_link = LAMBDA_DICT['file_link_list']('/'.join(url.split('/')[:-1]) + '/{}', soup(sc.SELECT_DICT['a']))
        # 頁面關鍵字如果有在列表裡，則加到字典裡
        for w, f in zip(kw, file_link):
            if any((w.find(i) != -1) for i in kws_l):
                k_f_l_d[w] = f

        # 迭代搜尋關鍵字
        for k, v in k_f_l_d.items():
            flag_year, datetime_start, datetime_end = datetime_maker()
            format_keyword = sc.KEYWORD.format(flag_year-1)
            find, text = find_kw(v, format_keyword)
            if find:
                log.info(format_keyword, k, text)
            else:
                if text < format_keyword:
                    mailhandler.set_msg(False, k, url, format_keyword)
                else:
                    mailhandler.set_msg(k, url, format_keyword, text)
                err_log.warning(format_keyword, k, text)


def extract_forest(key, url) -> None:
    forest_kws_l.append(key)
    if len(forest_kws_l) == fc.KEYWORDS_LENTH:
        creator = fc()
        k_f_l_d = {}
        element, soup = get_html_element(fc.SELECT_DICT['td_of_1'], method='get',
                                         return_soup=True, url=url, creator=creator)
        kw = LAMBDA_DICT['kw_list'](element)
        file_link = LAMBDA_DICT['file_link_list']('/'.join(url.split('/')[:-1]) + '{}', soup(fc.SELECT_DICT['a']))
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
                sl.set_msg(datetime_start, datetime_end)
                find, text = pdfhandler.extract_text(io.BytesIO(requests.get(v).content), format_keyword)
                if find:
                    log.info(format_keyword, k, text)
                else:
                    err_log.warning(format_keyword, k, text)

            if k == '林務局森林遊樂區收入':
                keyword = '{}年{}月'
                flag_month, datetime_start, datetime_end = datetime_maker(day=fc.DAY)
                format_keyword = keyword.format(YEAR, int(flag_month) - 1)
                find, text = find_kw(v, format_keyword, 'ods')
                if find:
                    log.info(format_keyword, k, text)
                else:
                    err_log.warning(format_keyword, key, text)


def extract_inquire_advance(key, url) -> None:
    """
    如果 key == 老農津貼相關, 月份為當月的前兩個月, 其他則為前一個月
    last_two_tr: 因最新的月份為倒數第二個 tr 元素, 因此可用來判斷是否未在指定時間內更新資料
    :param key: 農民生產所得物價指數, 農民生產所付物價指數, 老年農民福利津貼核付人數, 老年農民福利津貼核付金額
    :param url: http://agrstat.coa.gov.tw/sdweb/public/inquiry/InquireAdvance.aspx
    :return: None
    """
    creator = ia(key)

    if key == '老年農民福利津貼核付人數' or key == '老年農民福利津貼核付金額':
        flag_month, datetime_start, datetime_end = datetime_maker(day=ia.ELDER_DAY)
        keyword = ia.KEYWORD.format(int(flag_month)-2)
    else:
        flag_month, datetime_start, datetime_end = datetime_maker(day=ia.DAY)
        keyword = ia.KEYWORD.format(int(flag_month)-1)
    element = get_html_element(ia.SELECT_DICT['tr'], url=url, creator=creator)
    text = LAMBDA_DICT['specfied_element_text'](element, -2)
    if text.find(keyword) != -1:
        log.info(keyword, key, text)
    else:
        mailhandler.set_msg(False, key, url, keyword)
        err_log.warning(keyword, key, text)


def extract_wood_price(key, url) -> None:
    """
    爬取 木材市價 website
    :param key: 木材市價
    :param url: https://woodprice.forest.gov.tw/Compare/Q_CompareProvinceConiferous.aspx
    :return: None
    """
    creator = wc()
    flag_month, datetime_start, datetime_end = datetime_maker(day=creator.DAY)

    # 確認前一個月、當月、下個月是否有資料
    for i in range(1, -2, -1):
        creator.set_years(YEAR)
        creator.set_months(int(flag_month) - i)
        format_keyword = wc.KEYWORD.format(YEAR, int(flag_month) - i)
        element = get_html_element(wc.SELECT_DICT['tr_of_2'], url=url, creator=creator)
        text = LAMBDA_DICT['specfied_element_text'](element, 0)
        if i == 1:
            if text.find(format_keyword) != -1:
                log.info(format_keyword, key, text)
            else:
                mailhandler.set_msg(False, key, url, format_keyword, text)
                err_log.warning(format_keyword, key, text)
        else:
            if text.find(format_keyword) != -1:
                kw = wc.KEYWORD.format(YEAR, int(flag_month)-1)
                sl.set_msg(datetime_start, datetime_end)
                mailhandler.set_msg(True, key, url, kw, text)
                err_log.warning(kw, key, text)


def extract_agrstat_book(key, url) -> None:
    now = time.strftime('%m%d%H%M')
    creator = abc(key)
    element, soup = get_html_element(abc.SELECT_DICT['a'], return_soup=True, url=url, creator=creator)
    file_link = LAMBDA_DICT['specfied_file_link']('/'.join(url.split('/')[:-1]) + '/', element, 0)
    if key == '糧食供需統計':
        specified_date = '10011700'
        if specified_date < now:
            format_keyword = creator.KEYWORD.format(YEAR - 1)
        else:
            format_keyword = creator.KEYWORD.format(YEAR - 2)
        find, text = pdfhandler.extract_text(io.BytesIO(requests.get(file_link).content), format_keyword)
        if find:
            log.info(specified_date + '--' + format_keyword + ' | ' + key + ' : ' + text, unpacking=False)
        else:
            err_log.warning(specified_date + '--' + format_keyword + ' | ' + key + ' : ' + text, unpacking=False)


def extract_apis_afa(key, url) -> None:
    flag_month, datetime_start, datetime_end = datetime_maker(day=aac.DAY)
    format_keyword = aac.KEYWORD.format(AD_YEAR, int(flag_month) - 1)
    driver = get_web_driver()
    try:
        driver.get(url)
        # 選擇開始月份
        Select(driver.find_element_by_id(aac.SELECT_DICT['month_start'])).select_by_value('1')
        # 選擇結束月份
        Select(driver.find_element_by_id(aac.SELECT_DICT['month_end'])).select_by_value('12')
        # 選擇指定品項(葡萄)
        driver.find_element_by_id(aac.SELECT_DICT['check_box_grape']).click()
        # 按下搜尋
        driver.find_element_by_class_name(aac.SELECT_DICT['search_button']).click()
        # 等到 time out(5s)
        WebDriverWait(driver, 5).until(lambda d: len(d.window_handles) == 2)
        # 切換到跳出的頁面
        driver.switch_to_window(driver.window_handles[1])
        element = get_html_element(aac.SELECT_DICT['tr'], page_source=driver.page_source)
        texts = LAMBDA_DICT['kw_list'](element)
        # 判斷是否為 當月-1 的月份資料
        if texts[int(flag_month)-1].find('-') == -1:
            log.info(format_keyword, key, texts[int(flag_month)-1])
        else:
            mailhandler.set_msg(False, key, url, str(texts[int(flag_month)-1])+'月')
            err_log.warning(format_keyword, key, texts[int(flag_month)-1])
        # 判斷是否偷跑(是否為 當月 資料)
        if texts[int(flag_month)].find('-') == -1:
            mailhandler.set_msg(True, key, url, str(texts[int(flag_month)-1])+'月', str(texts[int(flag_month)])+'月')
            err_log.warning(format_keyword, key, texts[int(flag_month)])
    finally:
        driver.quit()


def extract_price_naif(key, url):
    flag_month, datetime_start, datetime_end = datetime_maker(day=pnc.DAY)
    soup = bs(req.get(url).text, 'lxml')
    value = soup.select('#ContentPlaceHolder_content_DropDownList_month > option')[0].get_text()
    if int(value) == int(flag_month)-1:
        log.info(str(int(flag_month)-1)+'月', key, value)
    else:
        mailhandler.set_msg(False, key, url, str(int(flag_month)-1)+'月')
        err_log.warning(str(int(flag_month)-1)+'月', key, value)


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


if __name__ == '__main__':
    pdfhandler.read_all_pdf(Base.PDF_PATH)
