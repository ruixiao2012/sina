__author__ = 'qipanguan'
# Callable MCQ Check Module
# Author: Qipan Guan <qipan@staff.sina.com.cn>
import memcache
import logging
from lib import riemann

checker_log = logging.getLogger('dsp_alert')


class check_mcq(object):
    def __init__(self, node, alert_conf):
        self.host, self.port = node.split(":")
        self.check_items = alert_conf
        self.service_name = 'mcq'
        self.meta_data = '%s_%s_%s' % (self.service_name, self.host, self.port)
        self.riemann_client = riemann.MyRiemann()
        self.is_alive = self.alive_check()
        if self.is_alive:
            self.queue_info_dict = self.get_queue_stats()
            self.start_check()

    def close_mc_conn(self):
        try:
            self.is_alive.disconnect_all()
        except:
            pass

    def alive_check(self):
        server = ['%s:%s' % (self.host, self.port)]
        try:
            is_alive = memcache.Client(server)
            is_alive.socket_timeout = 2
            is_alive.get_stats('queue')[0][1]
        except Exception as e:
            checker_log.warn('[%s] connect err, get stats queue:%s' %
                             (self.meta_data, e))
            self.riemann_client.send(host='%s-%s' % (self.host, self.port),
                                     service='Sina_dsp_mcq_conn_fail',
                                     description='mcq conn timeout 2s...',
                                     alert_level=self.check_items['Sina_dsp_mcq_conn_fail'][0][1],
                                     threshold=self.check_items['Sina_dsp_mcq_conn_fail'][0][0],
                                     sms=self.check_items['Sina_dsp_mcq_conn_fail'][0][2],
                                     mail=self.check_items['Sina_dsp_mcq_conn_fail'][0][3],
                                     watchid=self.check_items['Sina_dsp_mcq_conn_fail'][0][4])
            return False
        return is_alive

    def get_queue_stats(self):
        if self.is_alive is False:
            return False
        try:
            stats = self.is_alive.get_stats('queue')[0][1]
        except Exception as e:
            checker_log.error('[%s] get mcq stats queue err:%s,big error!!' %
                              (self.meta_data, e))
            return False
        return stats

    def start_check(self):
        self.heap_size_check(self.check_items)
        self.close_mc_conn()

    def heap_size_check(self, default_threshold):
        # check queue_info_dict is a dict
        if not isinstance(self.queue_info_dict, dict):
            checker_log.warn('[%s] check heap size get dict like {key:123/123} failed...' % self.meta_data)
            return False
        for key, value in self.queue_info_dict.items():
            # queue_info_dict e.g. {'object_aggr_dataeng': '450499112/450470674'}
            try:
                size_written, size_read = value.split('/')
                size = int(size_written) - int(size_read)
                # this means that the key has a heap size threshold in zk config, compare with it
                if key in self.check_items and size > int(default_threshold[key][0][0]):
                    checker_log.warn('[%s %s] check heap size too much [%d] > threshold [%d]' %
                                     (self.meta_data, key, size, int(default_threshold[key])))
                    self.riemann_client.send(host='%s-%s' % (self.host, self.port),
                                             service=key,
                                             description='mcq key %s heap size too much 2s...' % key,
                                             alert_level=default_threshold[key][0][1],
                                             threshold=default_threshold[key][0][0],
                                             sms=default_threshold[key][0][2],
                                             mail=default_threshold[key][0][3],
                                             watchid=default_threshold[key][0][4])
                # this means don't have a threshold in zk config, use default config ['heap_size'] 200000000000000
                elif key not in self.check_items and size > int(default_threshold[0][0]):
                    checker_log.warn('[%s %s] check heap size too much [%s] > default threshold [%d]' %
                                     (self.meta_data, key, size, int(default_threshold[key][0][0])))
                # the heap size is consider as OK, use log level debug to logger this
                else:
                    checker_log.debug('[%s %s] check heap size [%s] ok!' %
                                      (self.meta_data, key, size))
            except Exception as e:
                checker_log.warn('[%s %s] check heap size error %s' %
                                 (self.meta_data, key, e))




