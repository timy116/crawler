from const import LongText


class BaseCreator:
    def __init__(self, extra_headers=None):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1',
        }
        if extra_headers is not None:
            headers.update(extra_headers)

        self.headers = headers


# 公務統計
class AgrstatOfficialInfoCreator(BaseCreator):
    KEYWORDS_LENTH = 19
    SELECT_DICT = {
        'tr_row1': 'tr.Row > td:nth-of-type(3)',
        'tr_row2': 'tr.AlternatingRow > td:nth-of-type(3)',
        'td': 'tr.Pager > td > table > tbody > tr > td',
    }

    def __init__(self):
        headers = {
            'Cookie': '_ga=GA1.3.758348857.1534843864; ASP.NET_SessionId=pna0ob55eyuneo45wmltoi55',
            'Referer': 'http://agrstat.coa.gov.tw/sdweb/public/official/OfficialInformation.aspx',

        }
        super().__init__(headers)

        self.form_data = {
            '__EVENTTARGET': 'ctl00$cphMain$uctlOfficialInformation1$grdReport',
            '__EVENTARGUMENT': 'Page$1',
            '__VIEWSTATE': LongText.VIEWSTATE,
            '__VIEWSTATEGENERATOR': '36C3D52C',
            '__EVENTVALIDATION': LongText.EVENTVALIDATION,
            'ctl00$cphMain$uctlOfficialInformation1$ddlQYear': '',
            'ctl00$cphMain$uctlOfficialInformation1$ddlQPeriod': '',
            'ctl00$cphMain$uctlOfficialInformation1$txtQReportCode': '',
            'ctl00$cphMain$uctlOfficialInformation1$chkQNew': 'on',
            'ctl00$cphMain$uctlOfficialInformation1$txtQReportName': '',
            'ctl00$cphMain$uctlOfficialInformation1$ddlQOrganization': '0',
        }
        self.page_index = 1

    def next_page(self):
        self.page_index += 1

    def get_page_index(self) -> str:
        return str(self.page_index)


class SwcbCreator(BaseCreator):
    KEYWORDS_LENTH = 3
    KEYWORD = '中華民國{}年度'
    SPECIFIED_DAY = '05151700'
    SELECT_DICT = {
        'h3': 'div.lastList > ul > li > a > h3',
        'a': 'div.lastList > ul > li > a',
    }


class ForestCreator(BaseCreator):
    KEYWORDS_LENTH = 7
    KEYWORD = '中華民國{}年度'
    INCOME_KEYWORD = '{}年{}月'
    WOOD_KEYWORD = '{}年{}月'
    DAY = ['', 25, 26, 26, 25, 25, 25, 25, 27, 25, 25, 26, 25]
    SELECT_DICT = {
        'td_of_1': '#divContent > div.downloadBox > table > tbody > tr > td:nth-of-type(1)',
        'a': '#divContent > div.downloadBox > table > tbody > tr > td > a',
    }


class InquireAdvanceCreator(BaseCreator):
    KEYWORD = '{}月'
    DAY = ['', 21, 20, 20, 22, 20, 20, 22, 20, 20, 22, 20, 20]
    ELDER_DAY = ['', 22, 21, 20, 20, 21, 20, 20, 20, 20, 15, 15, 17]
    SELECT_DICT = {
        'tr': '#ctl00_cphMain_uctlInquireAdvance_tabResult > tr',
    }

    def __init__(self, kw):
        headers = {
            'Cookie': '_ga=GA1.3.758348857.1534843864; ASP.NET_SessionId=wm50tvjgnavgxtienzqwlc55',
            'Referer': 'http://agrstat.coa.gov.tw/sdweb/public/inquiry/InquireAdvance.aspx',

        }
        super().__init__(headers)

        self.form_data = {
            '__EVENTTARGET': '',
            '__EVENTARGUMENT': '',
            '__VIEWSTATE': LongText.FARMER_INCOME_VIEWSTATE,
            '__VIEWSTATEGENERATOR': '20124335',
            '__EVENTVALIDATION': LongText.FARMER_INCOME_EVENTVALIDATION,
            'ctl00$cphMain$uctlInquireAdvance$lstFieldGroup': '3094',
            'ctl00$cphMain$uctlInquireAdvance$btnQuery': '查詢確認',
            '__LASTFOCUS': '',
        }
        if kw == '農民生產所付物價指數':
            self.form_data['ctl00$cphMain$uctlInquireAdvance$lstFieldGroup'] = '3099'
            self.form_data['__VIEWSTATE'] = LongText.FARMER_PAID_VIEWSTATE
            self.form_data['__EVENTVALIDATION'] = LongText.FARMER_PAID_EVENTVALIDATION
        elif kw == '老年農民福利津貼核付人數':
            self.form_data['ctl00$cphMain$uctlInquireAdvance$lstFieldGroup'] = '56'
            self.form_data['__VIEWSTATE'] = LongText.ELDER_NOP_VIEWSTATE
            self.form_data['__EVENTVALIDATION'] = LongText.ELDER_NOP_EVENTVALIDATION
        elif kw == '老年農民福利津貼核付金額':
            self.form_data['ctl00$cphMain$uctlInquireAdvance$lstFieldGroup'] = '57'
            self.form_data['__VIEWSTATE'] = LongText.ELDER_AMOUNT_VIEWSTATE
            self.form_data['__EVENTVALIDATION'] = LongText.ELDER_AMOUNT_EVENTVALIDATION

    def set_start_date(self, date):
        self.form_data['ctl00$cphMain$uctlInquireAdvance$ddlMonthBegin'] = date

    def set_end_date(self, date):
        self.form_data['ctl00$cphMain$uctlInquireAdvance$ddlMonthEnd'] = date


class WoodPriceCreator(BaseCreator):
    KEYWORD = '{}年{}月'
    DAY = ['', 25, 26, 26, 25, 25, 25, 25, 27, 25, 25, 26, 25]
    SELECT_DICT = {
        'tr_of_2': '#ctl00_Main_q2_gv > tr:nth-of-type(2)',
    }

    def __init__(self):
        headers = {
            'Cookie': '_ga=GA1.3.1949248998.1534385798; __utmz=227712522.1534385798.1.1.utmcsr=(direct)|utmccn=(direct)'
                      '|utmcmd=(none); ASP.NET_SessionId=0kxdbqnbid0bupupgs3yzcch; _gid=GA1.3.1204522383.1537413421;'
                      ' __utma=227712522.1949248998.1534385798.1537171059.1537413421.9; __utmc=227712522;'
                      ' TS0172de76=01215f806c7a994aa6f5188886c7994a55f22d6852b26b1d578850315d8663591cf62af313275fddb2ba'
                      '1cfadc3e42d01316bfe778',
            'Origin': 'https://woodprice.forest.gov.tw',
            'Referer': 'https://woodprice.forest.gov.tw/Compare/Q_CompareProvinceConiferous.aspx',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        super().__init__(headers)
        self.form_data = {
            '__EVENTTARGET': '',
            '__EVENTARGUMENT': '',
            '__VIEWSTATE': LongText.WOOD_PRICE_VIEWSTATE,
            '__VIEWSTATEGENERATOR': 'F06CDE5E',
            'ctl00$Main$CompareQueryUi1$q1_ddl_years': '107',
            'ctl00$Main$CompareQueryUi1$q1_ddl_months': '9',
            'ctl00$Main$CompareQueryUi1$m_DownloadFileTypeDropDownList$m_DownloadFileType': '.xls',
            'ctl00$Main$q2_btn_Query': '查詢',
        }

    def set_years(self, year):
        self.form_data['ctl00$Main$CompareQueryUi1$q1_ddl_years'] = str(year)

    def set_months(self, month):
        self.form_data['ctl00$Main$CompareQueryUi1$q1_ddl_months'] = str(month)


class AgrstatBookCreator(BaseCreator):
    KEYWORD = '{}年'
    NUMBER_OF_PIG_KEYWORD = '{}年{}月底'
    SELECT_DICT = {
        'a': '#ctl00_cphMain_uctlBook_repChapter_ctl07_dtlFile_ctl01_lnkFile',
        'a2': '#ctl00_cphMain_uctlBook_repChapter_ctl09_dtlFile_ctl01_lnkFile',
        'a3': '#ctl00_cphMain_uctlBook_repChapter_ctl56_dtlFile_ctl01_lnkFile',
        'a4': '#ctl00_cphMain_uctlBook_repChapter_ctl00_lnkChapter',
        'a5': '#ctl00_cphMain_uctlBook_repChapter_ctl02_dtlFile_ctl02_lnkFile',
        'a6': '#ctl00_cphMain_uctlBook_repChapter_ctl26_dtlFile_ctl00_lnkFile',
    }

    def __init__(self, kw):
        if kw == '糧食供需統計':
            self.spec_day = '10011700'
            self.a_tag = AgrstatBookCreator.SELECT_DICT['a']
            self.form_data = {
                '__EVENTTARGET': 'ctl00$cphMain$uctlBook$grdBook$ctl03$btnBookName',
                '__EVENTARGUMENT': '',
                '__VIEWSTATE': LongText.PROVISION_VIEWSTATE,
                '__VIEWSTATEGENERATOR': 'AC7AE538',
                '__EVENTVALIDATION': LongText.PROVISION_EVENTVALIDATION
            }
        elif kw == '畜產品生產成本':
            self.spec_day = '07171700'
            self.a_tag = AgrstatBookCreator.SELECT_DICT['a4']
            self.form_data = {
                '__EVENTTARGET': 'ctl00$cphMain$uctlBook$grdBook$ctl06$btnBookName',
                '__EVENTARGUMENT': '',
                '__VIEWSTATE': LongText.LIVESTOCK_PRODUCT_COST_VIEWSTATE,
                '__VIEWSTATEGENERATOR': 'AC7AE538',
                '__EVENTVALIDATION': LongText.LIVESTOCK_PRODUCT_COST_EVENTVALIDATION
            }
        elif kw == '毛豬飼養頭數':
            self.a_tag = AgrstatBookCreator.SELECT_DICT['a5']
            self.form_data = {
                '__EVENTTARGET': 'ctl00$cphMain$uctlBook$grdBook$ctl08$btnBookName',
                '__EVENTARGUMENT': '',
                '__VIEWSTATE': LongText.NUMBER_OF_PIG_VIEWSTATE,
                '__VIEWSTATEGENERATOR': 'AC7AE538',
                '__EVENTVALIDATION': LongText.NUMBER_OF_PIG_EVENTVALIDATION
            }
        elif kw in ['農作物種植面積、產量', '畜牧用地面積', '農業及農食鏈統計']:
            if kw == '農作物種植面積、產量':
                self.spec_day = '05311700'
                self.a_tag = AgrstatBookCreator.SELECT_DICT['a2']
            elif kw == '農業及農食鏈統計':
                self.spec_day = '12101600'
                self.a_tag = AgrstatBookCreator.SELECT_DICT['a6']
            else:
                self.spec_day = '04301700'
                self.a_tag = AgrstatBookCreator.SELECT_DICT['a3']

            self.form_data = {
                '__EVENTTARGET': 'ctl00$cphMain$uctlBook$grdBook$ctl09$btnBookName',
                '__EVENTARGUMENT': '',
                '__VIEWSTATE': LongText.CROP_AREA_YIELD_VIEWSTATE,
                '__VIEWSTATEGENERATOR': 'AC7AE538',
                '__EVENTVALIDATION': LongText.CROP_AREA_YIELD_EVENTVALIDATION
            }

        headers = {
            'Cookie': '_ga=GA1.3.758348857.1534843864; ASP.NET_SessionId=3bv2ewyqvboe2y45g52hri55',
            'Referer': 'http://agrstat.coa.gov.tw/sdweb/public/book/Book.aspx',
        }
        super().__init__(headers)

    def get_selector(self):
        return self.a_tag


class ApisAfaCreator(BaseCreator):
    KEYWORD = '{}年{}月'
    DAY = ['', 15, 21, 15, 16, 15, 15, 16, 15, 17, 15, 5, 5]
    SELECT_DICT = {
        'tr': '#WR1_1_WG1 > tbody > tr',
        'month_start': 'WR1_1_Q_PRSR_Month1_C1',
        'month_end': 'WR1_1_Q_PRSR_Month2_C1',
        'check_box_grape': 'WR1_1_PRMG_02_54',
        'search_button': 'CSS_ABS_NormalLink',
    }


class PirceNaifCreator(BaseCreator):
    DAY = ['', 15, 21, 15, 16, 15, 15, 16, 15, 17, 15, 15, 17]
    SELECT_DICT = {
        'option': '#ContentPlaceHolder_content_DropDownList_month > option'
    }


class BliCreator(BaseCreator):
    KEYWORD = '{}年{}月'
    ELDER_DAY = ['', 22, 21, 20, 20, 21, 20, 20, 20, 20, 15, 15, 17]
    URL = 'https://www.bli.gov.tw/reportM.aspx?m=107{}&f=a7010'
    SELECT_DICT = {
        'a': 'body > p:nth-of-type(2) > a:nth-of-type(1)',
    }