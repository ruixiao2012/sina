__author__ = 'zengtao'

import time
import logging
from lib import riemann
import subprocess

checker_log = logging.getLogger('dsp_alert')


class check_hadoopzk(object):
    def __init__(self, node, alert_conf):
        self.host, self.port = node.split(":")
        self.check_items = alert_conf
        self.service_name = 'hadoopzk'
        self.meta_data = '%s_%s_%s' % (self.service_name, self.host, self.port)
        self.riemann_client = riemann.MyRiemann()
        for i in range(3):
            self.is_alive = self.alive_check()
            if self.is_alive:
                break
            time.sleep(0.5)
        if not self.is_alive:
            self.riemann_client.send(host='%s-%s' % (self.host, self.port),
                                     service='Sina_dsp_hadoopzk_conn_fail',
                                     ip_port='%s-%s' % (self.host, self.port),
                                     description='hadoopzk conn fail',
                                     alert_level=self.check_items['Sina_dsp_hadoopzk_conn_fail'][0][1],
                                     threshold=self.check_items['Sina_dsp_hadoopzk_conn_fail'][0][0],
                                     sms=self.check_items['Sina_dsp_hadoopzk_conn_fail'][0][2],
                                     mail=self.check_items['Sina_dsp_hadoopzk_conn_fail'][0][3],
                                     watchid=self.check_items['Sina_dsp_hadoopzk_conn_fail'][0][4])

    def alive_check(self):
        server = ['%s:%s' % (self.host, self.port)]
        cmd = '/bin/echo "ruok"| nc %s %s' %(self.host, self.port)
        try:
            is_alive,is_alive_error = self.external_cmd(cmd)
        except Exception as e:
            checker_log.warn('[%s] connect err, get stats queue:%s' %
                             (self.meta_data, e))
            return False
        return is_alive

    def external_cmd(self,cmd, msg_in=''):
        try:
            proc = subprocess.Popen(cmd,
            shell=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,)
            stdout_value, stderr_value = proc.communicate(msg_in)
            return stdout_value, stderr_value

        except ValueError, err:
            return None, None
        except IOError, err:
            return None, None





#<class 'plugins.check_mcq.check_mcq'> (u'10.73.14.178:5027', {u'Sina_dsp_memcacheq_heap_size': [[u'200000000000000', u'Alert_A', u'test_dsp', u'test_dsp', u'2013111310']], u'Sina_dsp_memcacheq_conn_fail': [[u'False', u'Alert_A', u'test_dsp', u'test_dsp', u'2013111310']]}) {}





