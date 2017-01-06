__author__ = 'qipanguan'
# Callable Cacheservcie Check Module
# Author: Qipan Guan <qipan@staff.sina.com.cn>
import memcache
import logging
from lib import riemann

checker_log = logging.getLogger('dsp_alert')


class check_cacheservice(object):
    def __init__(self, node, alert_conf):
        host, port = node.split(":")
        self.host = host
        self.port = port
        self.service_type = "cs"
        self.check_items = alert_conf
        self.meta_data = '%s_%s:%s' % (self.service_type, self.host, self.port)
        self.riemann_client = riemann.MyRiemann()
        self.is_alive = self.alive_check

        if self.is_alive:
            self.stats = self.get_stats()
            self.start_check()

    def start_check(self):
        check_list = [[self.check_cs_mem, 'Sina_dsp_cs_mem_size', self.check_items['Sina_dsp_cs_mem_size']],
                      [self.check_cs_conn, 'Sina_dsp_cs_curr_connections', self.check_items['Sina_dsp_cs_curr_connections']]]
        for func, check_key, check_values in check_list:
            func(check_key, check_values)
        self.close_conn()

    @property
    def alive_check(self):
        server = ['%s:%s' % (self.host, self.port)]
        try:
            is_alive = memcache.Client(server)
            is_alive.socket_timeout = 2
            if not is_alive.get_stats():
                raise Exception
        except Exception as e:
            self.riemann_client.send(host='%s-%s' % (self.host, self.port),
                                     service='Sina_dsp_cs_conn_fail',
                                     ip_port='%s-%s' % (self.host, self.port),
                                     description='cacheservice conn timeout 2s...',
                                     alert_level=self.check_items['Sina_dsp_cs_conn_fail'][0][1],
                                     threshold=self.check_items['Sina_dsp_cs_conn_fail'][0][0],
                                     sms=self.check_items['Sina_dsp_cs_conn_fail'][0][2],
                                     mail=self.check_items['Sina_dsp_cs_conn_fail'][0][3],
                                     watchid=self.check_items['Sina_dsp_cs_conn_fail'][0][4])
            checker_log.error('[%s] connect conn fail,get stats err:%s' %
                              (self.meta_data, e))
            return False
        return is_alive

    def get_stats(self):
        if self.is_alive is False:
            return False
        try:
            stats = self.is_alive.get_stats()
        except Exception as e:
            checker_log.error('[%s] get cs info err:%s,big error!!' %
                              (self.meta_data, e))
            return False
        return stats

    def close_conn(self):
        try:
            self.is_alive.disconnect_all()
        except:
            pass

    def check_cs_mem(self, key, value):
        if self.stats is False:
            return False
        try:
            stats = self.stats[0][1]
            used_mem = int(stats['used_memory'])
        except Exception as e:
            checker_log.error('[%s] get used_mem occur error:%s\nstats:%s' %
                              (self.meta_data, e, self.stats))
        if used_mem >= int(value[0][0]):
            checker_log.warn('[%s ] check used_memory %s >= %s!' %
                             (self.meta_data, used_mem, value[0][0]))
            self.riemann_client.send(host='%s-%s' % (self.host, self.port),
                                     service=key,
                                     ip_port='%s-%s' % (self.host, self.port),
                                     description='%s %s >= %s' % (key, used_mem, value[0][0]),
                                     alert_level=value[0][1],
                                     threshold=value[0][0],
                                     sms=value[0][2],
                                     mail=value[0][3],
                                     watchid=value[0][4])
        else:
            checker_log.debug('[%s] check used_memory %s ok!' %
                              (self.meta_data, used_mem))

    def check_cs_conn(self, key, value):
        if self.stats is False:
            return False
        try:
            stats = self.stats[0][1]
            conn_num = int(stats['connected_clients'])
        except Exception as e:
            checker_log.error('[%s] check conn num occur error:%s\n stats:%s' %
                              (self.meta_data, e, self.stats))
            return False
        if conn_num >= int(value[0][0]):
            checker_log.warn('[%s ] check conn %s >= %s!' %
                             (self.meta_data, conn_num, value[0][0]))
            self.riemann_client.send(host='%s-%s' % (self.host, self.port),
                                     service=key,
                                     description='%s %s >= %s' % (key, conn_num, value[0][0]),
                                     alert_level=value[0][1],
                                     threshold=value[0][0],
                                     sms=value[0][2],
                                     mail=value[0][3],
                                     watchid=value[0][4])
        else:
            checker_log.debug('[%s %s] conn num ok!' %
                              (self.meta_data, conn_num))