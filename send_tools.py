#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: zhoujiebin
@contact: zhoujiebing@maimiaotech.com
@date: 2012-12-10 17:13
@version: 0.0.0
@license: Copyright maimiaotech.com
@copyright: Copyright maimiaotech.com

"""
import sys
import json
import time
import smtplib, mimetypes
import urllib, urllib2
if __name__ == '__main__':
    sys.path.append('../')

from email.Header import Header
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
'''
#from CommonTools.self.logger import self.logger
import logging
sys.path.append('../../')
from ShopOptimize.conf.settings import getLogger
self.logger = getLogger('message_sender', './log/', logging.DEBUG)
'''
def _toHex(str,charset):
    s = str.encode(charset)
    lst = []
    for ch in s:
        hv = hex(ord(ch)).replace('0x', '')
        if len(hv) == 1:
            hv = '0'+hv
        lst.append(hv)
    return reduce(lambda x,y:x+y, lst)

def _toHex(str,charset):
    s = str.encode(charset)
    lst = []
    for ch in s:
        hv = hex(ord(ch)).replace('0x', '')
        if len(hv) == 1:
            hv = '0'+hv
        lst.append(hv)
    return reduce(lambda x,y:x+y, lst)

def _parse_sms_response(message):
    dict = {}
    response_list = message.split('&')
    for info in response_list:
        key_value = info.split('=')
        dict[key_value[0]] = key_value[1]   
    return dict

class SendTools:
    SEND_COMMAND = 'MT_REQUEST' 
    SPID = '5208'
    SP_PASSWORD = 'mm5208'
    DC = '15'
    SEND_MSG_URL = 'http://esms.etonenet.com/sms/mt'

    def __init__(self, phone, email, secret):
        self.DIRECTOR = {
            'PHONE':phone,
            'EMAIL':email,
            'SECRET':secret
        }
        #self.logger = logger

    def send_email_with_text(self, addressee, text, subject):
        """发送文本email"""

        msg = MIMEMultipart()
        msg.attach(MIMEText(text, _charset='utf-8'))
        msg['Subject'] = Header(subject, 'utf-8')
        msg['From'] = self.DIRECTOR['EMAIL']
        msg['To'] = addressee
        try:
            smtp = smtplib.SMTP()
            smtp.connect('smtp.ym.163.com', 25) 
            smtp.login(msg['From'], self.DIRECTOR['SECRET'])
            smtp.sendmail(msg['From'], msg['To'], msg.as_string())
        except Exception,e:
            print 'send_email: %s' % (str(e))

    def send_email_with_html(self, addressee, html, subject):
        """发送html email"""

        msg = MIMEMultipart()
        msg['Subject'] = Header(subject, 'utf-8')
        msg['From'] = self.DIRECTOR['EMAIL']
        msg['To'] = addressee
        html_att = MIMEText(html, 'html', 'utf-8')
        msg.attach(html_att)
        try:
            smtp = smtplib.SMTP()
            smtp.connect('smtp.ym.163.com', 25) 
            smtp.login(msg['From'], self.DIRECTOR['SECRET'])
            smtp.sendmail(msg['From'], msg['To'], msg.as_string())
        except Exception,e:
            self.logger.exception('send_email: %s' % (str(e)))

    def send_email_with_file(self, addressee, text, subject, file_list):
        """发送file email"""

        msg = MIMEMultipart()
        msg.attach(MIMEText(text, _charset='utf-8'))
        msg['Subject'] = Header(subject, 'utf-8')
        msg['From'] = self.DIRECTOR['EMAIL']
        msg['To'] = addressee

        for file_name in file_list:
            ctype, encoding = mimetypes.guess_type(file_name)
            if ctype is None or encoding is not None:
                ctype = 'application/octet-stream'
            maintype, subtype = ctype.split('/', 1)
            
            attachment = MIMEImage((lambda f: (f.read(), f.close())) \
                    (open(file_name, 'rb'))[0], _subtype =subtype)
            attachment.add_header('Content-Disposition', 'attachment', filename=file_name)
            msg.attach(attachment)

        try:
            smtp = smtplib.SMTP()
            smtp.connect('smtp.ym.163.com', 25) 
            smtp.login(msg['From'], self.DIRECTOR['SECRET']) 
            smtp.sendmail(msg['From'], addressee, msg.as_string())
        except Exception,e:
            print 'send_email: %s' % (str(e))


    def send_sms(self, cellphone, text, retry_times=3):
        """发送短信"""

        retry_times -= 1
        if retry_times < 0:
            self.logger.error('send message to %s unsuccessfully'%(cellphone,))
            return
        dict = {}
        dict['command'] = SendTools.SEND_COMMAND
        dict['spid'] = SendTools.SPID
        dict['sppassword'] = SendTools.SP_PASSWORD
        dict['da'] = '86'+cellphone
        dict['dc'] = SendTools.DC 
        dict['sm']  = _toHex(text,'gbk')
        url_params = urllib.urlencode(dict)
        try:
            response = urllib2.urlopen(SendTools.SEND_MSG_URL,url_params)
            dict = _parse_sms_response(response.read())
            if dict.get('mterrcode',None) != '000':
                self.logger.error('send message to %s unsuccessfully:response error'%(cellphone,))
                send_sms(cellphone,text,retry_times)
        except urllib2.HTTPError,e:
            self.logger.error('send message to %s unsuccessfully:url connect error'%(cellphone,))
            send_sms(cellphone,text,retry_times)
        except Exception,e:
            self.logger.error('send message to %s unsuccessfully:server error'%(cellphone,))
            send_sms(cellphone,text,retry_times)

def usage(argv0):
    print argv0 + "phone mail secret subject_file text_file"

if __name__ == '__main__':
    import logging
    try:
        if (len(sys.argv) != 6):
            usage(sys.argv[0])
            exit(-1)
        logger = logging.getLogger('mylogger')
        logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        phone = sys.argv[1]
        email = sys.argv[2]
        secret = sys.argv[3]
        subject_file = open(sys.argv[4], "r")
        text_file = open(sys.argv[5],"r")
        subject = subject_file.read()
        text = text_file.read()
        
        tools = SendTools(phone, email, secret, logger)
        tools.send_email_with_text(email, text, subject)
        tools.send_sms(phone, "title : " + subject + " text : " + text)
    except Exception, e:
        print "error : " + str(e)
