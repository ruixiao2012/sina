__author__ = 'qipanguan'
# !/bin/env python2.6
# -*- coding: utf-8 -*-
import datetime
import logging
from lib import thread_pool
from lib import ZKutil
import ConfigParser
from lib import logger


checker_log = logging.getLogger(logger.logger_list)


class Checker(object):

    def __init__(self):
        cp = ConfigParser.ConfigParser()
        cp.read('config/checker.conf')
        self.config = cp
        self.interval = 60
        self.current_time = datetime.datetime
        self.last_check_time = self.now_time - self.interval
        self.checking_nodes = {}
        for service in cp.get('global', 'watch_service_dict'):
            self.checking_nodes[service] = ZKutil.NodeFromZK(service)
            print self.checking_nodes[service]
        # self.manager = thread_pool.WorkerManager(self.config('common_service', 'thread_num'))

    def start(self):
        self.manager.start_working()
        checker_log.info('[%s] now start dsp checker ...' % datetime.datetime.now())
            
def main():
    Checker().start()

if __name__ == '__main__':
    main()