__author__ = 'qipanguan'
import check_memcached
import logging

checker_log = logging.getLogger('dsp_checker')


class cacheservice():
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.service_type = "cs"
        self.meta_data = '%s_%s_%s' % (self.service_type, self.host, self.port)
        self.is_alive = self.alive_check()
        if self.is_alive:
            self.stats = self.get_stats()
            self.start_check()

    def start_check(self):
        check_list = []
        if self.is_alive:
            check_list.append(self.check_cs_mem, self.check_items['mem_size'])
            check_list.append(self.check_cs_conn, self.check_items['curr_connections'])
        self.close_conn()

    def alive_check(self):
        server = ['%s:%s' % (self.host, self.port)]
        try:
            is_alive = check_memcached.Client(server)
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

    def check_cs_mem(self, check_item):
        if self.stats is False:
            return False
        try:
            stats = self.stats[0][1]
            used_mem = int(stats['used_memory'])
        except Exception as e:
            checker_log.error('[%s] get used_mem occur error:%s\nstats:%s' %
                              (self.meta_data, e, self.stats))
        checker_log.debug('[%s %s %s] check used_memory ok!' %
                          (self.host, self.port, used_mem))

    def check_cs_conn(self, threshold):
        if self.stats is False:
            return False
        try:
            stats = self.stats[0][1]
            conn_num = int(stats['connected_clients'])
        except Exception as e:
            checker_log.error('[%s] check conn num occur error:%s\nstats:%s' %
                            (self.meta_data, e, self.server_stats))
            return False
        checker_log.debug('[%s %s] conn num ok!' %
                        (self.meta_data, conn_num))