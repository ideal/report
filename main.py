# -*- encoding: utf-8 -*-
#
# Copyright (C) 2014 Shang Yuanchun <idealities@gmail.com>
#

"""
按照config.py中配置的不同数据库，执行不同的sql，写入到相应的文件。
然后发送邮件。
"""

import logging

from report import Report
from config import settings

if __name__ == '__main__':
    """
    """

    import log
    log.setupLogger(level='info',
                    filename=settings.LOG_FILE,
                    filemode='a')

    import logging
    logger = logging.getLogger(__name__)

    logger.info('Starting...')
    report = Report()
    # 执行sql查询，会将数据写入到~/var/data/report/<date>/<trade_name>
    report.execute()

    # 发送此次查询的结果
    report.send()
    logger.info('Finished')
