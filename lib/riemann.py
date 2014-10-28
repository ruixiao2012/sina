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

        :rtype : object
        """
        myconfig = config.Config()
        self.config = myconfig.config_parser
        self.client = bernhard.Client(host=self.config.get('riemann', 'riemann_host'),
                                      port=self.config.get('riemann', 'riemann_port'))

    def send(self, host, service, metric=0, description='',
             alert_level='', domain='', threshold=0,
             sms='', mail='', watchid=''):
        """
         #   "attributes":{"alert-level":"Alert_A","domain":"rm.123456eos",
         #   "description":"connfail","threshold":0,"ctime":"2014-10-01 00:00:01",
         #   "product":"weibo_xxx","sms":"zengtao","mail":"zengtao@staff.sina.com.cn","watchid":"xxx"}})
        :param host:
        :param service:
        :param metric:
        :param description:
        :param alert_level:
        :param domain:
        :param threshold:
        :param sms:
        :param mail:
        :param watchid:
        """
        product = self.get_product(host)
        ctime = time.time()
        attributes = self.aggre_attr(alert_level=alert_level, domain=domain,
                                     threshold=threshold, product=product, ctime=ctime, sms=sms, mail=mail,
                                     watchid=watchid)
        print attributes
        checker_log.warn('send to riemann [host:%s,service:%s,metric:%s,description:%s,'
                         'alert_level:%s,domain:%s,threshold:%s,sms:%s,mail:%s,watchid:%s]' %
                         (host, service, metric, description, alert_level, domain, threshold, sms, mail, watchid))
        return self.client.send({
            "host": host,
            "service": service,
            "metric": metric,
            "description": description,
            "attributes": attributes,
        })

    def aggre_attr(self, **kwargs):
        # return a dict
        return kwargs

    def get_product(self, host_port):
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