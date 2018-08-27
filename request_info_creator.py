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