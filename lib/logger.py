__author__ = 'qipanguan'

#!/bin/env python2.6
# -*- coding: utf-8 -*-


import logging
import logging.handlers
#from lib import config
import config

cp = config.Config().config_parser
logger_list = ['logger']

for mylog in logger_list:
    log_name = cp.get(mylog, 'name')
    #log_level = cp.get(mylog, 'log_level')
    log_level = logging.DEBUG
    log_file = '%s/%s.log' % (cp.get(mylog, 'log_dir'), log_name)

    logger = logging.getLogger(log_name)
    logger.setLevel(log_level)
    handler = logging.handlers.RotatingFileHandler(log_file, maxBytes=1000000000, backupCount=0)
    formatter = logging.Formatter("%(asctime)s - [%(levelname)s] - [%(name)s/%(filename)s: %(lineno)d] - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
