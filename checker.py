__author__ = 'qipanguan'
# !/bin/env python2.6
# -*- coding: utf-8 -*-
import datetime
import time
import logging
import threading

from lib import thread_pool
from lib import logger
from lib import ZKutil
from lib import config
from plugins.check_cacheservice import check_cacheservice
from plugins.check_sinaredis import check_sinaredis


checker_log = logging.getLogger('dsp_alert')


class Checker(object):
    def __init__(self):
        myconfig = config.Config()
        self.config = myconfig.config_parser
        self.interval = 60
        self.now_time = time.time()
        self.last_check_time = self.now_time - self.interval
        self.checking_nodes = {}
        self.watch_service_class_dict = eval(self.config.get('global', 'watch_service_class_dict'))
        for service in self.watch_service_class_dict:
            self.checking_nodes[service] = ZKutil.NodeFromZK(service)
        self.thread_num = int(self.config.get('common_service', 'thread_num'))
        self.manager = thread_pool.WorkerManager(self.thread_num)

    def services_init(self, service):
        try:
            nodes_list = self.checking_nodes[service].get_check_list()
        except Exception as e:
            checker_log.fatal('[%s] get server_list fail, ret illegal:%s' %
                              (service, e))
            return False
        for node, alert_conf_dict in nodes_list:
            self.manager.add_job(self.watch_service_class_dict[service],
                                 node, alert_conf_dict)
        return len(service)

    def start(self):
        self.manager.start_working()
        while True:
            self.now_time = time.time()
            if self.now_time - self.last_check_time >= 60:
                if self.now_time - self.last_check_time >= 90:
                    checker_log.fatal('last check time cost time too long:%s' %
                                      (self.now_time - self.last_check_time))
                    self.last_check_time = self.now_time
                else:
                    self.last_check_time += 60
                checker_log.info('[%s] now start dsp checker ...' % datetime.datetime.now())
                for service in self.watch_service_class_dict.keys():
                    checker_log.info('[%s] start %s check now...' % (datetime.datetime.now(), service))
                    len_nodes = self.services_init(service)
                    if not len_nodes:
                        checker_log.info('service: [%s] check occur error!' % service)
                        continue
                self.manager.wait_complete()

                print 'checking service %s now process status: threads_num:%s cost_time:%s' % \
                      (self.watch_service_class_dict, threading.activeCount(), (time.time() - self.now_time))
                checker_log.info('checking service %s now process status: threads_num:%s cost_time:%s' %
                                 (self.watch_service_class_dict, threading.activeCount(),
                                  (time.time() - self.now_time)))
            time.sleep(0.1)


def main():
    Checker().start()

if __name__ == '__main__':
    main()