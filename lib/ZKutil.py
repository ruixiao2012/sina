__author__ = 'qipanguan'
#!/bin/env python2.6 
# -*- coding: utf-8 -*-

import ConfigParser
from lib import urlutil


class JsonReturnIllegal(Exception):
    pass


class NodeFromZK(object):
    def __init__(self, server_type, idc=None):
        cp = ConfigParser.ConfigParser()
        cp.read('../conf/checker.conf')
        self.server_type = server_type
        self.config = cp

        if not idc:
            self.idc = self.get_idc(self)
        else:
            self.idc = idc

    @staticmethod
    def get_idc(self):
        return self.config.get('global', 'idc')

    def get_check_nodes(self):
        try:

            url = self.config.get('global', 'zk_api')
            data = {
                'serviceType': self.server_type,
                'idc': self.idc
            }
            ret_info = urlutil.curl_post_data(url, data)
            ret_dict = urlutil.curl_load_json(url, ret_info)
        except Exception as e:
            raise Exception('post url to get %s info fail:%s' % (self.server_type, e))
        # if ret_val status is 0 , means return err
        if ret_dict['status'] == 0:
            raise JsonReturnIllegal('return json status 0,json:%s' % ret_dict)
        # get the node list by idc
        try:
            ret_dict = ret_dict['result'][self.idc]
        except Exception as e:
            raise Exception('post url get [%s,%s] info data illegal:%s' %
                            (self.server_type, ret_dict, e))
        return ret_dict

def parse_alert_conf(conf_data):
    '''
    parse configure , configure format metric:content:level
    conf_dict return : {metric:[content, level], metric:[content, level]}
    '''
    conf_dict = {}
    try:
        for conf in conf_data.split('\n'):
            conf = conf.strip()
            if not conf:
                continue
            conf_list = conf.split(':')
            metric, content, level = conf_list
            if metric not in conf_dict:
                conf_dict[metric] = []
            conf_dict[metric].append([content, level])
    except Exception as e:
        raise Exception('configure from zk parse fail:%s' % e)
    return conf_dict

if __name__ == '__main__':
    print NodeFromZK('mc').get_check_nodes()
