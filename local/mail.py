#!/usr/lib/env python3
import smtplib
from email.header import Header
from email.mime.text import MIMEText
from collections import Iterable


class EmailHelper:
    def __init__(self, **kwargs):
        self.host = kwargs.get("host") or "smtp.163.com"  # SMTP服务器
        self.user = kwargs.get("user") or "leanote_phichem@163.com"  # 用户名
        self.sender = kwargs.get("sender") or "leanote_phichem@163.com"  # 发件人邮箱
        self.password = kwargs.get("password")  # 邮箱客户端授权码
        if not self.password:
            from .config import mail as _mail
            self.password = _mail["password"]
        self.receivers = []
        __receivers = kwargs.get("receivers")
        if not __receivers:
            self.receivers = ['277199942@qq.com']
        elif isinstance(__receivers, str):
            self.receivers.append(__receivers)
        elif Iterable(__receivers):
            self.receivers.extend(__receivers)

    def sendmail(self, title, content, **kwargs):
        message = MIMEText(content, 'plain', 'utf-8')
        message['From'] = "{}".format(self.sender)
        receivers = kwargs.get("receivers") or self.receivers
        message['To'] = ",".join(receivers)
        message['Subject'] = title
        try:
            smtpObj = smtplib.SMTP_SSL(self.host, 465)  # 启用SSL发信, 端口一般是465
            smtpObj.login(self.user, self.password)  # 登录验证
            smtpObj.sendmail(self.sender, receivers, message.as_string())  # 发送
            print("mail has been send successfully.")
        except smtplib.SMTPException as e:
            print(e)

    def send():
        pass

# def send_email2(SMTP_host, from_account, from_passwd, to_account, subject, content):
#     email_client = smtplib.SMTP(SMTP_host)
#     email_client.login(from_account, from_passwd)
#     # create msg
#     msg = MIMEText(content, 'plain', 'utf-8')
#     msg['Subject'] = Header(subject, 'utf-8')  # subject
#     msg['From'] = from_account
#     msg['To'] = to_account
#     email_client.sendmail(from_account, to_account, msg.as_string())
#
#     email_client.quit()


if __name__ == '__main__':
    import time
    mail = EmailHelper()
    mail.sendmail(
        "会议时间修改", r"2020-02-14 12:20:00,\n当前: {}".format(
            time.strftime("%Y-%m-%d %H:%M:%S")
        )
    )
