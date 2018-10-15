import linecache
import smtplib
from email.mime.text import MIMEText
from log import SimpleLog as sl

PATH = 'info.txt'
SUBJECT = linecache.getline(PATH, 4)
USER = linecache.getline(PATH, 1)
PWD = linecache.getline(PATH, 2)
MAIL_TO = linecache.getline(PATH, 6)
MSG_FORMAT = """
Warning:
名稱：{}
網址：{}
{} - {} 期間為 {} 資料, 檢測網站{}
"""
DATA_ALREADY_UPDATE = '已上傳 {} 資料'
DATA_UPDATE_YET = '尚未上傳'
msg_l = []


def set_msg(already, *args):
    date_range = sl.msg_l
    if already:
        msg_l.append([args[0], args[1], date_range[0], date_range[1], args[2], DATA_ALREADY_UPDATE.format(args[3])])
    else:
        msg_l.append([args[0], args[1], date_range[0], date_range[1], args[2], DATA_UPDATE_YET])


def send_mail():
    """

    :return: None
    """
    data = ''
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.ehlo()
    if len(msg_l) > 0:
        for i in msg_l:
            data += MSG_FORMAT.format(*i) + '\n'
        try:
            server.login(USER, PWD)
            msg = MIMEText('此信件為自動發送，請勿直接回覆。\n' + data)
            msg['Subject'] = SUBJECT
            msg['From'] = USER
            msg['To'] = MAIL_TO
            server.send_message(msg)
        finally:
            server.quit()