# -*- encoding: utf-8 -*-
#
# Copyright (C) 2014 Shang Yuanchun <idealities@gmail.com>
#

import os
import time
import base64
import logging
from collections import OrderedDict as odict

import query
from config import settings

log = logging.getLogger(__name__)

class Report(object):

    def __init__(self):
        self.queries = []
        for name, config in settings.databases.iteritems():
            self.queries.append(query.Query(name, **config))

    def execute(self):
        for query in self.queries:
            log.info('Processing trade: %s', query.name)
            for filename, q in settings.sqls[query.name].iteritems():
                  query.query(filename, *q)

    def send(self):
        result = odict()
        for query in self.queries:
            result[query.name] = {}
            for filename in settings.sqls[query.name]:
                filepath = settings.DATA_DIR + query.name + '/' + filename
                try:
                    st = os.stat(filepath)
                except:
                    result[query.name][filename] = ['ERROR', filepath]
                    continue
                if st.st_size == 0:
                    result[query.name][filename] = ['ERROR', filepath]
                    continue
                result[query.name][filename] = ['OK', filepath]
        log.info('Result: %r', result)
        log.info('Sending email...')
        content = self._generate_mail_content(result)
        self._send_mail(content)

    def _generate_mail_content(self, result):
        """
        """
        # TODO: maybe content is too large, not suitable for storing in memory
        from email import encoders
        from email.message import Message
        from email.mime.base import MIMEBase
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        content = MIMEMultipart()
        content['Subject'] = '=?utf-8?B?' + base64.encodestring('SQL执行结果:' + time.strftime('%Y-%m-%d')).strip() + '?='
        content['From'] = 'no-reply@baidu.com'
        content['To']   = ', '.join(settings.recipients)

        html = """
        <html>
        <head>
        <meta charset='utf-8' />
        <style type='text/css'>
        table, th, td
        {
            border: 1px solid black;
        }
        table
        {
            border-collapse: collapse;
        }
        th
        {
            background-color: green;
            color: white;
        }
        </style>
        </head>
        <body>
        """
        for trade in result:
            html += "<p>行业：<b>%s</b></p>" % trade
            html += "<table><tr><th>文件名</th><th>结果</th><th>对应附件名称</th></tr>"
            for filename, data in result[trade].iteritems():
                html += "<tr><td>%s</td><td>%s</td><td>%s</td></tr>" % (filename, data[0], trade + '_' + filename)
            html += "</table></br>"
        html += """
        </body>
        </html>
        """
        msg = MIMEText(html, 'html', 'utf-8')
        content.attach(msg)

        for trade in result:
            for filename, data in result[trade].iteritems():
                if data[0] == 'ERROR':
                    continue
                fp  = open(data[1], 'rb')
                msg = MIMEBase('application', 'octet-stream')
                msg.set_payload(fp.read())
                fp.close()
                encoders.encode_base64(msg)
                msg.add_header('Content-Disposition', 'attachment', filename=trade + '_' + filename)
                content.attach(msg)

        return content

    def _send_mail(self, content):
        sendmail = '/usr/sbin/sendmail'

        p = os.popen('%s -t -i' % sendmail, 'w')
        p.write(content.as_string())
        status = p.close()
        if status:
            log.info('sendmail failed, status: %r', status)
            return
        log.info('sendmail succeed')
