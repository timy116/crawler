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


class ForestCreator(BaseCreator):
    KEYWORDS_LENTH = 6
    KEYWORD = '中華民國{}年度'
    DAY = ['', 25, 26, 26, 25, 25, 25, 25, 27, 25, 25, 26, 25]


class InquireAdvanceCreator(BaseCreator):
    KEYWORD = '{}月'
    DAY = ['', 21, 20, 20, 22, 20, 20, 22, 20, 20, 22, 20, 20]

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