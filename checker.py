__author__ = 'qipanguan'
# !/bin/env python2.6
# -*- coding: utf-8 -*-
# Author: Qipan Guan <qipan@staff.sina.com.cn>
# Sina Alert Checker Main Class
import datetime
import time
import logging
import threading

from lib import thread_pool
from lib import logger
from lib import ZKutil
from lib import config
#from plugins.check_hadoopzk import check_hadoopzk
from plugins.check_hadoop import check_hadoop


checker_log = logging.getLogger('dsp_alert')


class Checker(object):
    def __init__(self):
        """
        Init checker
        config -- read config from config file
        is working -- always be True
        interval -- default 60 TODO add to config file
        last_check_time -- checker last work time
        watch_service_class_dict -- {service: service check class}
                    e.g. {
                      'mcq': check_mcq,
                      'cs': check_cs
                      }
        thread_num -- thread pool thread_num
        manager -- thread pool manager
        :return:
        """
        myconfig = config.Config()
        self.config = myconfig.config_parser
        self.is_working = True
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
        """
        :param service:
        :return: len of init service nodes
        """
        try:
            # get check list from ZooKeeper API supported by sina wolf api
            nodes_list = self.checking_nodes[service].get_check_list()
        except Exception as e:
            checker_log.fatal('[%s] get server_list fail, ret illegal:%s' %
                              (service, e))
            return False
        for node, alert_conf_dict in nodes_list:
            self.manager.add_job(self.watch_service_class_dict[service],
                                 node, alert_conf_dict)
        return len(nodes_list)

    def start(self):
        """
        Start the checker to watch every node in every service
        :return:
        """
        self.manager.start_working()
        while self.is_working:
            self.now_time = time.time()
            # Check every self.interval = 60 seconds
            if self.now_time - self.last_check_time >= self.interval:
                # If last check cost too much time, that means the performance is too low :-(
                if self.now_time - self.last_check_time >= 90:
                    checker_log.fatal('last check time cost time too long:%s' %
                                      (self.now_time - self.last_check_time))
                    self.last_check_time = self.now_time
                else:
                    self.last_check_time += 60
                checker_log.info('Now Sina Alert Checker Main Start...')
                # Init each service by service_init function
                for service in self.watch_service_class_dict.keys():
                    len_nodes = self.services_init(service)
                    if not len_nodes:
                        checker_log.info('service: [%s] check occur error!' % service)
                        continue
                    checker_log.info('start check service [%s] now... nodes count [%s] ' % (service, len_nodes))
                # Wait all check nodes init function finished...
                self.manager.wait_complete()

                print 'checking service %s now process status: threads_num:%s cost_time:%s' % \
                      (self.watch_service_class_dict, threading.activeCount(), (time.time() - self.now_time))
                checker_log.info('checking service %s now process status: threads_num:%s cost_time:%s' %
                                 (self.watch_service_class_dict, threading.activeCount(),
                                  (time.time() - self.now_time)))
            time.sleep(0.1)


def main():
    """
    Test your checker start from here
    """
    Checker().start()

if __name__ == '__main__':
    main()
