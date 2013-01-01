#!/usr/bin/env python
# coding=utf-8
#
# Copyright 2012 F2E.im
# Do have a faith in what you're doing.
# Make your life a story worth telling.

import smtplib
import sys
import email
from email.mime.text import MIMEText

send_mail_host = 'smtp_host'
send_mail_user = 'smtp_user'
send_mail_user_name = u'send_mail_user_name'
send_mail_pswd = 'send_mail_password'
send_mail_postfix = 'send_mail_postfix'
get_mail_user = 'get_mail_user'
charset = 'utf-8'

get_mail_postfix = 'get_mail_postfix'
get_mail_host = 'get_mail_host'

def send(sub, content, reciver = get_mail_user + get_mail_postfix):
    send_mail_address = send_mail_user_name + '<' + send_mail_user + '@' + send_mail_postfix + '>'
    msg = email.mime.text.MIMEText(content,'html',charset)
    msg['Subject'] = email.Header.Header(sub,charset)
    msg['From'] = send_mail_address
    msg['to'] = to_adress = reciver
    try:
        stp = smtplib.SMTP()
        stp.connect(send_mail_host)
        stp.login(send_mail_user,send_mail_pswd)
        stp.sendmail(send_mail_address,to_adress,msg.as_string())
        stp.close()
        return True
    except Exception,e:
        print(e)
        return False

