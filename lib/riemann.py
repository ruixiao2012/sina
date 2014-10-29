__author__ = 'qipanguan'

import time
import bernhard
import logging
from lib import config
from lib import urlutil

checker_log = logging.getLogger('dsp_alert')


class MyRiemann():
    def __init__(self):
        """
        Init A riemann client use to send alert info to remote server
        """
        myconfig = config.Config()
        self.config = myconfig.config_parser
        self.client = bernhard.Client(host=self.config.get('riemann', 'riemann_host'),
                                      port=self.config.get('riemann', 'riemann_port'))

    def send(self, host, service, metric=0, description='',
             alert_level='', alert_type='',domain='', threshold=0,
             sms='', mail='', watchid=''):
        """
        :param host: string e.g. 10.10.10.10-1000
        :param service: string e.g. Sinadsp_redis_conn_fail
        :param metric: int,long,float the current metric value e.g. current connection:1000
        :param description: string e.g. 'redis is timeout for 2s..'
        :param alert_level: string e.g. 'Alert_A'
        :param domain: string e.g. 'rm1111.eos'
        :param threshold: int,long,float the threshold value e.g. current connection:1000
        :param sms: sms to
        :param mail: mail to
        :param watchid: use sinawatch kid
        """
        product = self.get_product(host)
        ctime = time.time()
        attributes = self.aggre_attr(alert_level=alert_level, domain=domain,
                                     threshold=threshold, product=product, ctime=ctime, sms=sms, mail=mail,
                                     watchid=watchid)
        print attributes
        checker_log.warn('send to riemann [host:%s,service:%s,metric:%s,description:%s,'
                         'alert_level:%s,domain:%s,threshold:%s,sms:%s,mail:%s,watchid:%s]' %
                         (host, service, metric, description, alert_level, alert_type, domain, threshold, sms, mail, watchid))
        return self.client.send({
            "host": host,
            "service": service,
            "metric": metric,
            "description": description,
            "attributes": attributes,
        })

    def aggre_attr(self, **kwargs):
        """
        Return a dict
        :param kwargs:
        :return:
        """
        #   "attributes":{"alert-level":"Alert_A","domain":"rm.123456eos",
        #   "description":"connfail","threshold":0,"ctime":"2014-10-01 00:00:01",
        #   "product":"weibo_xxx","sms":"zengtao","mail":"zengtao@staff.sina.com.cn","watchid":"xxx"}})
        # return a dict
        return kwargs

    def get_product(self, host_port):
        """
        Get the product name from dpadmint url
        :param host_port:
        :return:
        """
        try:
            host, port = host_port.split('-')
            url = self.config.get('dpadmint', 'dpadmint_url')
            url_argument = '?n2minfo=port==%s&ninfo=ip_in==%s' % (port, host)
            url += url_argument
            ret_data = urlutil.curl_get_data(url)
            ret_data = urlutil.curl_load_json(url, ret_data)
            ret_info = ret_data[0]['cpname']
            return ret_info
        except Exception, e:
            return 'UnknownProduct'


if __name__ == '__main__':
    r = MyRiemann()
    ret = r.send(host='10.73.24.210-10101',
                 service='sinadsp_cacheservice_conn_fail',
                 description='i conn_fail',
                 alert_level='Alert_A',
                 sms='qipan',
                 mail='qipan'
    )
    print ret