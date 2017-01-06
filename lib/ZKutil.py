__author__ = 'qipanguan'
# !/bin/env python2.6
# -*- coding: utf-8 -*-
# Author: Qipan Guan <qipan@staff.sina.com.cn>
# ZooKeeper Config functions supported by sina wolf API by dashan@staff.sina.com.cn

import ConfigParser
import logging
from lib import urlutil
from lib import logger
from lib import config
#import urlutil
#import logger
#import config

checker_log = logging.getLogger('dsp_alert')


class JsonReturnIllegal(Exception):
    pass


class NodeFromZK(object):
    def __init__(self, service_name, idc=None):
        myconfig = config.Config()
        cp = myconfig.config_parser
        self.service_name = service_name
        self.config = cp

        if not idc:
            self.idc = self.get_idc(self)
        else:
            self.idc = idc

    @staticmethod
    def get_idc(self):
        return self.config.get('global', 'idc')

    def get_check_list(self):
        nodes_list = []
        nodes_dict = self.get_check_nodes()
        default_alert_conf_dict = self.get_default_alert_conf()
        for node, online_alert_conf_dict in nodes_dict.items():
            online_alert_conf_dict = online_alert_conf_dict.strip()
            # if online alert conf dict is None or '' , use the default alert conf
            if online_alert_conf_dict == 'None' or not online_alert_conf_dict or  online_alert_conf_dict == '':
                nodes_list.append([node, default_alert_conf_dict])
            else:
                if is_alert_conf_dict(online_alert_conf_dict):
                    online_alert_conf_dict = parse_alert_conf(online_alert_conf_dict)
                    nodes_list.append([node, online_alert_conf_dict])
                else:
                    checker_log.warn('%s %s online alert etc dict parse error' % (self.service_name, node))
                    continue
        return nodes_list

    def get_default_alert_conf(self):
        try:
            conf_dict = AlertConfFromZK(self.service_name).get_conf()
            conf_dict = parse_alert_conf(conf_dict)
        except Exception as e:
            raise Exception('[%s] configure get from zk api fail:%s' %
                            (self.service_name, e))
        return conf_dict

    def get_check_nodes(self):
        try:
            url = self.config.get('global', 'zk_aggr_api')
            data = {
                'service_type': self.service_name,
                'idc': self.idc
            }
            ret_info = urlutil.curl_post_data(url, data)
            ret_dict = urlutil.curl_load_json(url, ret_info)
        except Exception as e:
            raise Exception('post url to get service:%s alert nodes info fail:%s' % (self.service_name, e))
        # if ret_val status is 0 , means return err
        if ret_dict['status'] == 0:
            raise JsonReturnIllegal('return json status 0,json:%s' % ret_dict)
        # get the node list by idc
        try:
            ret_dict = ret_dict['result'][self.idc]
        except Exception as e:
            raise Exception('post url get [%s,%s] info data illegal:%s' %
                            (self.service_name, ret_dict, e))
        return ret_dict


class AlertConfFromZK(object):
    def __init__(self, server_type):
        self.server_type = server_type
        myconfig = config.Config()
        self.config = myconfig.config_parser

    def get_conf(self):
        try:
            url = self.config.get('global', 'zk_node_api') + "getNode/"
            watch_service_alert_conf_dict = eval(self.config.get('global', 'watch_service_alert_conf_dict'))
            data = {
                "node_path": "%s%s" % (self.config.get('global', 'zk_alert_conf_dir'),
                                       watch_service_alert_conf_dict[self.server_type])
            }
            ret_info = urlutil.curl_post_data(url, data)
            ret_dict = urlutil.curl_load_json(url, ret_info)
        except Exception:
            raise
        return ret_dict['content']


def is_alert_conf_dict(alert_conf_dict):
    try:
        if parse_alert_conf(alert_conf_dict):
            return True
        else:
            return False
    except Exception:
        return False


def parse_alert_conf(conf_data):
    """
    parse configure , configure format metric:content:level
    conf_dict return : {metric:[content, level], metric:[content, level]}
    """
    conf_dict = {}
    try:
        for conf in conf_data.split('\n'):
            conf = conf.strip()
            if not conf:
                continue
            conf_list = conf.split(':')
            metric, threshold, alert_level, sms, mail, watchid = conf_list
            if metric not in conf_dict:
                conf_dict[metric] = []
            conf_dict[metric].append([threshold, alert_level, sms, mail, watchid])
    except Exception as e:
        raise Exception('configure from zk parse fail:%s' %e)
    return conf_dict


if __name__ == '__main__':
    print NodeFromZK('cs').get_check_list()
    # print AlertConfFromZK('cs').get_conf()
