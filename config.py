# -*- encoding: utf-8 -*-
#
# Copyright (C) 2014 Shang Yuanchun <idealities@gmail.com>
#

from collections import OrderedDict as odict

import os
import time

class Settings(object):

    databases = odict()
    sqls      = odict()

    LOG_FILE = os.getenv('HOME') + '/var/log/report.log'
    DATA_DIR = os.getenv('HOME') + '/var/data/report/' + time.strftime('%Y-%m-%d') + '/'

    recipients = ['idealities@gmail.com']

    def __init__(self):

        # FOR TEST
        trade = 'test'
        self.databases[trade] = {
            'host': 'localhost',
            'port':  3306,
            'user': '',
            'password': '',
        }
        self.sqls[trade] = {
            'test1.csv': ['SELECT * FROM comments.api_comment WHERE comment_date >=%s', (time.strftime('%Y-%m-%d'), )],
            'test2.csv': ['SELECT * FROM comments.api_comment'],
        }

        return

# single instance
settings = Settings()
