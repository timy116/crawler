import io
import requests
import sys
import time
import pdfhandler
import xlrd
from bs4 import BeautifulSoup as bs
from const import Base
from datetime import date
from log import log
from selenium import webdriver
from request_info_creator import AgrstatOfficialInfoCreator as agroff, ForestCreator, SwcbCreator, InquireAdvanceCreator as ia

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

    # if url.find('0000575') != -1:
    #     extract_forest(key, url)

    if url.find('InquireAdvance') != -1:
        extract_inquire_advance(key, url)


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
                        print('find', k, 'at page ', creator.get_page_index())
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
                            log.info('not found keyword: ' + str(kws_d.keys()))
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
                log.info('error occurred.\n' + str(t) + '\n' + str(v))
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
                log.warning(k + ' 未在指定時間內上傳')


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
                if '07311700' < now <= '10311700':
                    keyword = keyword.format(YEAR, 2)
                    print(keyword)
                elif '10311700' < now <= '01311700':
                    keyword = keyword.format(YEAR, 3)
                elif '01311700' < now <= '04301700':
                    keyword = keyword.format(YEAR, 4)
                else:
                    keyword = keyword.format(YEAR, 1)
                if pdfhandler.extract_text(io.BytesIO(requests.get(v).content), keyword):
                    log.info('find : ' + k + keyword)
                else:
                    log.warning('warning :' + k + ' 必須為 ' + keyword)


def extract_inquire_advance(key, url):
    now = time.strftime('%m%d%H%M')
    dateline = '{}{}1700'
    day = ['', 21, 20, 20, 22, 20, 20, 22, 20, 20, 22, 20, 20]
    month = str(date.today().month).rjust(2, '0')
    flag_month = month if dateline.format(month, day[int(month)]) < now else str(int(month)-1).rjust(2, '0')
    next_flag_month = month if dateline.format(month, day[int(month)]) > now else str(int(month)+1).rjust(2, '0')
    keyword = '{}年{}月'
    creator = ia(key)
    if dateline.format(flag_month, day[int(month)]) < now < dateline.format(next_flag_month, day[int(next_flag_month)]):
        if key == '老年農民福利津貼核付人數' or key == '老年農民福利津貼核付金額':
            creator.set_start_date(str(YEAR) + str(int(flag_month)-2).rjust(2, '0'))
            creator.set_end_date(str(YEAR) + str(int(flag_month)-1).rjust(2, '0'))
            keyword = keyword.format(YEAR, int(flag_month)-2)
        else:
            creator.set_start_date(str(YEAR) + str(int(flag_month) - 2).rjust(2, '0'))
            creator.set_end_date(str(YEAR) + str(int(flag_month) - 1).rjust(2, '0'))
            keyword = keyword.format(YEAR, int(flag_month)-1)
    soup = bs(req.post(url, headers=creator.headers, data=creator.form_data).text, 'lxml')
    if key == '農民生產所得物價指數':
        td = soup.select('td.VerDim')
        print(td)
        for i in td:
            print(i.get_text())
    tr = soup.select('#ctl00_cphMain_uctlInquireAdvance_tabResult > tr:nth-of-type(2)')
    for i in tr:
        text = i.get_text().strip().replace(' ', '')
        if text.find(keyword) != -1:
            log.info(key + ' : ' + text + ', release time = ' + keyword)
        else:
            log.warning(key + ', 未在指定時間上傳 : ' + text + ', release time = ' + keyword)
        print(i.get_text().strip().replace(' ', ''))


def find_kw(link, keyword) -> int:
    """
    開啟 excel 並確認年度是否正確
    :param link: files url
    :param keyword: keyword select
    :return: bool
    """
    wb = xlrd.open_workbook(file_contents=requests.get(link).content)
    sheet = wb.sheet_by_index(0)
    for i in range(sheet.nrows):
        for j in range(sheet.ncols):
            value = str(sheet.row_values(i)[j]).strip().replace(' ', '')
            if keyword in value:
                return True
    return False


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
