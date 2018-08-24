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
def extract_agrstat_official_info(key, url):
    kws_l[key] = ''

    # 一次存取所有關鍵字
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
                if creator.get_page_index() in ['10', '20', '30']:

                    # 取的最後一個 tr 來判斷是否在最後一頁
                    last_tr = soup.select('tr.Pager > td > table > tbody > tr > td')[-1]
                    if last_tr.get_text() != '...':
                        sl.info('end page at ' + creator.get_page_index())
                        break
                    driver.find_element_by_xpath(
                        '//tr[@class="Pager"]/td/table/tbody/tr/td[last()]/a').click()
                    creator.next_page()
                else:
                    driver.find_element_by_xpath(
                        '//tr[@class="Pager"]/td/table/tbody/tr/td/a[contains(text(), ' + creator.next_page() + ')]').click()
                driver.implicitly_wait(3)
            except NoSuchElementException:
                sl.warning('Page end.')
                sl.info('not found keyword: ' + str(kws_l.keys()))
                break


def get_web_driver() -> webdriver:
    option = webdriver.ChromeOptions()
    option.add_argument('--disable-images')
    option.add_argument('--disable-gpu')
    option.add_argument('headless')
    driver = webdriver.Chrome(chrome_options=option)
    return driver


if __name__ == '__main__':
    pdfhandler.read_all_pdf(Base.PDF_PATH)
