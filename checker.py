__author__ = 'qipanguan'
# !/bin/env python2.6
# -*- coding: utf-8 -*-
import datetime
import time
import logging
import threading
import ConfigParser

from lib import thread_pool
from lib import logger
from lib import ZKutil


checker_log = logging.getLogger('dsp_checker')


class Checker(object):
    def __init__(self):
        cp = ConfigParser.ConfigParser()
        cp.read('conf/checker.conf')
        self.config = cp
        self.interval = 60
        self.now_time = time.time()
        self.last_check_time = self.now_time - self.interval
        self.checking_nodes = {}
        self.watch_service_dict = eval(self.config.get('global', 'watch_service_class_dict'))
        for service in self.watch_service_dict:
            self.checking_nodes[service] = ZKutil.NodeFromZK(service)
        self.thread_num = int(self.config.get('common_service', 'thread_num'))
        self.manager = thread_pool.WorkerManager(self.thread_num)

    def services_init(self, service):
        """

        :rtype : object
        """
        try:
            nodes_list = self.checking_nodes[service].get_check_list()
            print nodes_list
        except Exception as e:
            checker_log.fatal('[%s] get server_list fail, ret illegal:%s' %
                              (service, e))
            return False
        for host, port, threshold in nodes_list:
            self.manager.add_job(self.watch_service_dict[service],
                                 host, port, threshold)
        return len(service)

    def start(self):
        self.manager.start_working()
        while True:
            self.now_time = time.time()
            print 'now process status: threads_num:%s cost_time:%s' % \
                  (threading.activeCount(), (time.time() - self.now_time))
            checker_log.info('[%s] now start dsp checker ...' % datetime.datetime.now())
            checker_log.info('now process status: threads_num:%s cost_time:%s' %
                             (threading.activeCount(), (time.time() - self.now_time)))
            for service in self.watch_service_dict.keys():
                len_nodes = self.services_init(service)
                if not len_nodes:
                    checker_log.info('[%s] check occur error' % service)
                    continue
                print len_nodes
            self.manager.wait_complete()
            time.sleep(30)


def main():
    Checker().start()


if __name__ == '__main__':
    main()