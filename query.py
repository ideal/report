# -*- encoding: utf-8 -*-
#
# Copyright (C) 2014 Shang Yuanchun <idealities@gmail.com>
#

import os
import logging
import mysql.connector

from config import settings

log = logging.getLogger(__name__)

class Query(object):

    def __init__(self, name, **config):

        self.name = name

        config['charset'] = 'utf8'
        try:
            self.conn = mysql.connector.connect(**config)
        except Exception as e:
            self.conn = None
            log.error('Error when processing trade: %s', self.name)
            log.exception(e)

    def __del__(self):
        if self.conn:
            self.conn.close()

    def ok(self):
        return self.conn is not None

    def query(self, output_filename, sql, data = None):

        filedir = settings.DATA_DIR + self.name
        if not os.path.isdir(filedir):
            try:
                os.makedirs(filedir)
            except Exception as e:
                log.error('Error when processing trade: %s', self.name)
                log.exception(e)
                return

        if not self.ok():
            log.error('Error in trade: %s, report skipped.', self.name)
            return

        cursor = self.conn.cursor()
        try:
            cursor.execute(sql, data)
        except Exception as e:
            log.error('Error when processing trade: %s', self.name)
            log.exception(e)
            return

        def _strify(d):
            if isinstance(d, str):
                return d

            if isinstance(d, unicode):
                return d.encode('gbk')

            return str(d)

        fp = open(filedir + '/' + output_filename, 'w')
        for data in cursor:
            try:
                fp.write((','.join(map(_strify, data))) + '\n')
            except Exception as e:
                log.error('Error data when processing trade: %s', self.name)
                log.exception(e)
        fp.close()

