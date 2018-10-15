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
此信件為自動發送，請勿直接回覆。

Warning:
名稱：{}
網址：{}
{} - {} 期間需為 {} 份資料, 檢測網站已上傳 {} 份資料
"""

msg_l = []


def set_msg(*args):
    date_range = sl.msg_l
    msg_l.append([args[0], args[1], date_range[0], date_range[1], args[2], args[3]])


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
            msg = MIMEText(data)
            msg['Subject'] = SUBJECT
            msg['From'] = USER
            msg['To'] = MAIL_TO
            server.send_message(msg)
        finally:
            server.quit()