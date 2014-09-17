__author__ = 'qipanguan'

#!/bin/env python2.6
# -*- coding: utf-8 -*-

import ConfigParser

import logging
import logging.handlers

cp = ConfigParser.ConfigParser()
cp.read('conf/checker.conf')

logger_list = ['logger_alerter', 'logger_checker']

for mylog in logger_list:
    log_name = cp.get(mylog, 'name')
    log_level = cp.get(mylog, 'log_level')
    log_file = '%s/%s.log' % (cp.get(mylog, 'log_dir'), log_name)

    logger = logging.getLogger(log_name)
    logger.setLevel(log_level)
    handler = logging.handlers.RotatingFileHandler(log_file, maxBytes=1000000000, backupCount=0)
    formatter = logging.Formatter("%(asctime)s - [%(levelname)s] - [%(name)s/%(filename)s: %(lineno)d] - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)