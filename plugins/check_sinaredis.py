__author__ = 'qipanguan'
import redis
import socket
import logging

checker_log = logging.getLogger('dsp_checker')


class sinaredis():
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.service_type = "sinaredis"
        self.check_items = {}
        # self.start_check()

    def hostname2host(self):
        try:
            ips = socket.gethostbyname_ex(self.hostname)
        except Exception as e:
            checker_log.warn('[%s] hostname2host fail:%s' % (self.hostname, e))
            return False
        return ips[2]

    def start_check(self):
        check_list = []
        check_list.append(self.check_alive, self.check_items['conn_fail'])
        check_list.append(self.check_connections, self.check_items['slave_conn'])
        check_list.append(self.check_delay_seconds, self.check_items['delay_seconds'])
        check_list.append(self.check_cronbgsave, self.check_items['bgsave'])
        check_list.append(self.check_readonly, self.check_items['read_only'])
        check_list.append(self.check_max_mem, self.check_items['max_mem'])

