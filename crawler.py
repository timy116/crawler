import pdfhandler
import requests
import sys
import time
from log import SimpleLog
from const import Base
from selenium import webdriver
from bs4 import BeautifulSoup as bs
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from request_info_creator import AgrstatOfficialInfoCreator as agroff

sl = SimpleLog()
sl.set_level(20)
kws_l = {}


def start_crawler(key, url):

    # 公務統計
    if url.find('OfficialInformation') != -1:
        extract_agrstat_official_info(key, url)


# 爬取公務統計網站
def extract_agrstat_official_info(key, url) -> None:
    """
    將關鍵字與網址傳進來，一次創建所有關鍵字的列表，
    將網頁解析後取出網頁的關鍵字跟關鍵字列表比對，若存在就刪除直到關鍵字列表個數為零
    同時判斷若以解析到最後一頁要結束迴圈
    :param key: 關鍵字
    :param url: 網址，解析用
    :return: None
    """
    kws_l[key] = ''

    if len(kws_l) == agroff.KEYWORDS_LENTH:
        creator = agroff()
        driver = get_web_driver()
        driver.get(url)
        while True:
            if len(kws_l) == 0:
                driver.quit()
                break
            try:
                soup = bs(driver.page_source, 'lxml')
                kws1 = soup.select('tr.Row > td:nth-of-type(3)')
                kws2 = soup.select('tr.AlternatingRow > td:nth-of-type(3)')
                for k in kws1+kws2:
                    k = k.get_text().strip()
                    if k in kws_l.keys():
                        print('find', k, 'at page ', creator.get_page_index())
                        del kws_l[k]

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
                        if len(kws_l) != 0:
                            sl.info('not found keyword: ' + str(kws_l.keys()))
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
                sl.info('error occurred.\n' + str(t) + '\n' + str(v))
                break


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
