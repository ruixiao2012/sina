__author__ = 'qipanguan'
import memcache
import logging

checker_log = logging.getLogger('dsp_alert')


class check_cacheservice(object):
    def __init__(self, node, alert_conf):
        host, port = node.split(":")
        self.host = host
        self.port = port
        self.service_type = "cs"
        self.check_items = alert_conf
        self.meta_data = '%s_%s:%s' % (self.service_type, self.host, self.port)
        self.is_alive = self.alive_check()
        if self.is_alive:
            self.stats = self.get_stats()
            self.start_check()

    def start_check(self):
        check_list = [[self.check_cs_mem, self.check_items['mem_size']],
                      [self.check_cs_conn, self.check_items['curr_connections']]]
        for func, threshold in check_list:
            func(threshold)
        self.close_conn()

    def alive_check(self):
        server = ['%s:%s' % (self.host, self.port)]
        try:
            is_alive = memcache.Client(server)
        except Exception as e:
            checker_log.error('[%s] connect err:%s' %
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

    def check_cs_mem(self, threshold):
        if self.stats is False:
            return False
        try:
            stats = self.stats[0][1]
            used_mem = int(stats['used_memory'])
        except Exception as e:
            checker_log.error('[%s] get used_mem occur error:%s\nstats:%s' %
                              (self.meta_data, e, self.stats))
        if used_mem >= int(threshold[0][0]):
            checker_log.warn('[%s ] check used_memory %s >= %s!' %
                            (self.meta_data, used_mem, threshold))
        else:
            checker_log.debug('[%s] check used_memory %s ok!' %
                              (self.meta_data, used_mem))

    def check_cs_conn(self, threshold):
        if self.stats is False:
            return False
        try:
            stats = self.stats[0][1]
            conn_num = int(stats['connected_clients'])
        except Exception as e:
            checker_log.error('[%s] check conn num occur error:%s\n stats:%s' %
                             (self.meta_data, e, self.stats))
            return False
        if conn_num >= int(threshold[0][0]):
            checker_log.warn('[%s ] check conn %s >= %s!' %
                            (self.meta_data, conn_num, threshold))
        else:
            checker_log.debug('[%s %s] conn num ok!' %
                        (self.meta_data, conn_num))