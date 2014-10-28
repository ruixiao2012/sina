__author__ = 'qipanguan'
# coding: utf-8
# Author: Qipan Guan <qipan@staff.sina.com.cn>
# Use to url post/get functions

import json
import urllib
import urllib2


def curl_get_data(url):
    retry_times = 0
    while retry_times < 3:
        retry_times += 1
        try:
            req = urllib2.Request(url)
            rsp = urllib2.urlopen(req, timeout=10)
            result = rsp.read()
            return result
        except Exception, e:
            if retry_times == 3:
                raise Exception('post url:%s fail:%s' % (url, e))


def curl_post_data(url, data):
    retry_times = 0
    while retry_times < 3:
        retry_times += 1
        try:
            data = urllib.urlencode(data)
            req = urllib2.Request(url, data)
            rsp = urllib2.urlopen(req, timeout=60)
            result = rsp.read()
            return result
        except Exception, e:
            if retry_times == 3:
                raise Exception('post url:%s %s fail:%s' % (url, data, e))


def curl_load_json(url, ret_info):
    try:
        ret_dict = json.loads(ret_info)
    except Exception as e:
        raise Exception('post url:%s ret_info json parse fail:%s' %
                        (url, e))
    return ret_dict
