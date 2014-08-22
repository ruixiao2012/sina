__author__ = 'qipanguan'
# !/bin/env python2.6
# -*- coding: utf-8 -*-
import time
from lib import thread_pool
from lib import ZKutil
import ConfigParser


class Checker(object):
    service_dict = {}

    def __init__(self):
        cp = ConfigParser.ConfigParser()
        cp.read('config/checker.conf')
        self.config = cp
        self.interval = 60
        self.current_time = time.time
        self.last_check_time = self.now_time - self.interval
        self.checking_nodes={}
        for service in Checker.service_dict.keys():
            self.checking_nodes[service] = ZKutil.NodeFromZK(service)
        self.manager = thread_pool.WorkerManager(self.config('common_service', 'thread_num'))


            


