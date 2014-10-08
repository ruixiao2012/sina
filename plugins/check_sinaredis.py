__author__ = 'qipanguan'
# Callable SinaRedis Check Module
# Author: Qipan Guan <qipan@staff.sina.com.cn>
import redis
import socket
import logging
import datetime

checker_log = logging.getLogger('dsp_alert')


class check_sinaredis():
    def __init__(self, node, alert_conf_dict):
        domain, port = node.split(":")
        self.domain = domain
        self.host_list = self.hostname2host()
        self.port = port
        self.service_type = "sinaredis"
        self.timeout = self.redis_timeout()
        self.check_items = alert_conf_dict
        if not self.host_list:
            self.hostname_parse_fail()
        else:
            for host in self.host_list:
                self.host = host
                self.meta_data = '%s_%s %s:%s' % (self.get_readable_hostname(self.domain),
                                                  self.service_type, self.host, self.port)
                self.redis_conn = self.conn_redis()
                if self.redis_conn:
                    self.info = self.get_info()
                    self.is_sinaredis = self.redis_version_check()
                    self.role = self.get_redis_role()
                    if self.is_sinaredis:
                        self.start_check()
                else:
                    continue

    @staticmethod
    def redis_timeout():
        now_hour = datetime.datetime.today().hour
        if now_hour <= 7:
            return 60
        else:
            return 3

    def start_check(self):
        check_list = [[self.check_cronbgsave, self.check_items['cronbgsave']],
                      [self.check_readonly, self.check_items['read_only']],
                      [self.check_max_memory, self.check_items['max_mem']],
                      [self.check_conn_num, self.check_items['curr_connections']]]
        if self.role == 'slave':
            check_list.append([self.check_slave_conn, self.check_items['slave_conn']])
            check_list.append([self.check_delay_seconds, self.check_items['delay_seconds']])

        for func, check_item in check_list:
            func(check_item)

    def hostname_parse_fail(self):
        checker_log.warn('[%s %s] parse hostname fail' % (self.domain, self.port))
        return True

    def conn_redis(self):
        try:
            redis_r = redis.Redis(host=self.host, port=self.port, socket_timeout=self.timeout)
            redis_r.ping()
        except Exception as e:
            checker_log.warn('[%s] conn redis fail:%s' % (self.meta_data, e))
            return False
        return redis_r

    def redis_version_check(self):
        if 'redis_version' not in self.info:
            checker_log.info(
                '[%s] get redis_version illegal, it maybe redisscounter or counterservice...' % self.meta_data)
            return False
        else:
            return self.info['redis_version']

    def get_info(self):
        if not self.redis_conn:
            return False
        try:
            info = self.redis_conn.execute_command('info')
        except Exception as e:
            checker_log.warn('[%s] get redis info fail:%s' % (self.meta_data, e))
            return False
        return self.transfer_info_dict(info)

    def get_redis_role(self):
        try:
            redis_role = self.info['role']
        except Exception as e:
            checker_log.warn('[%s] get role fail:%s' % (self.meta_data, e))
            return False
        return redis_role

    @staticmethod
    def transfer_info_dict(info):
        info_list = info.split('\r\n')
        info_dict = {}
        for info in info_list:
            # sina redis 2.4 have a null string , ignore
            if not info:
                continue
            try:
                metric, content = info.split(':')
            except Exception:
                pass
            else:
                info_dict[metric] = content
        return info_dict

    @staticmethod
    def get_readable_hostname(hostname):
        return hostname.split('.grid.sina.com.cn')[0]

    def hostname2host(self):
        try:
            ips = socket.gethostbyname_ex(self.domain)
        except Exception as e:
            checker_log.warn('[%s] hostname2host fail:%s' % (self.domain, e))
            return False
        return ips[2]

    def config_get_commands(self, commands):
        try:
            ret_data = self.redis_conn.execute_command('config', 'get', commands)
        except Exception as e:
            checker_log.warn('[%s] config get [%s] fail:%s' % (self.meta_data, commands, e))
            return False
        return ret_data

    def check_cronbgsave(self, threshold):
        if self.is_sinaredis == '2.4.18':
            if_cronsave = self.config_get_commands('cronbgrewriteaof')
        else:
            if_cronsave = self.config_get_commands('cronbgsave')
        try:
            if not if_cronsave:
                return False
            if_aof = self.config_get_commands('appendonly')
            if not if_aof:
                return False
            cronsave_set = if_cronsave[1]
            aof_set = if_aof[1]
        except Exception as e:
            checker_log.warn('[%s] get aof/cronsave fail:%s' % (self.meta_data, e))
        # Check if cronsave is set
        if not cronsave_set and aof_set == 'yes':
            checker_log.warn('[%s] check redis cronsave set:[%s] error %s' %
                             (self.meta_data, cronsave_set, threshold))
            return True
        else:
            checker_log.debug('[%s] check redis cronsave set %s ok!' %
                              (self.meta_data, cronsave_set))

    def check_slave_conn(self, threshold):
        try:
            link_status = self.info['master_link_status']
        except Exception as e:
            checker_log.error('[%s %s] slave get master_link_status flag fail:%s' %
                              (self.meta_data, self.info, e))
            if link_status != 'up':
                checker_log.warn('[%s] check redis slave conn abnormal[%s] error %s' %
                                 (self.meta_data, link_status, threshold))
            else:
                checker_log.debug('[%s] check redis slave conn %s ok!' %
                                  (self.meta_data, link_status))

    def check_conn_num(self, threshold):
        try:
            now_clients_num = int(self.info['connected_clients'])
            if now_clients_num >= int(threshold[0][0]):
                checker_log.warn('[%s] check connection number:[%s] error' %
                                 (self.meta_data, now_clients_num))
            else:
                checker_log.debug('[%s] check connection number %s ok!' %
                                  (self.meta_data, now_clients_num))
        except Exception as e:
            checker_log.error('[%s %s] get clients num fail:%s' %
                              (self.meta_data, self.info, e))

    def check_delay_seconds(self, threshold):
        try:
            delay_seconds = int(self.info['delay_seconds'])
            if delay_seconds >= int(threshold[0][0]):
                checker_log.warn('[%s] check delay_seconds:[%s] error' %
                                 (self.meta_data, delay_seconds))
            else:
                checker_log.debug('[%s] check delay_seconds %s ok!' %
                                  (self.meta_data, delay_seconds))
        except Exception:
            return False

    def check_readonly(self, threshold):
        try:
            read_only = self.config_get_commands('readonly')
            if self.role == 'slave' and read_only == 'no':
                checker_log.warn(
                    '[%s] check redis slave read only:[%s] error %s' % (self.meta_data, read_only, threshold))
            if self.role == 'master' and read_only == 'yes':
                checker_log.warn(
                    '[%s] check redis master read only:[%s] error %s' % (self.meta_data, read_only, threshold))
        except Exception:
            return False

    def check_max_memory(self, threshold):
        try:
            policy_ret = self.config_get_commands('maxmemory-policy')
            policy = policy_ret[1]
            if policy == 'noeviction':
                max_mem_ret = self.config_get_commands('maxmemory')
                max_mem = int(max_mem_ret[1])
                if max_mem == 0:
                    return False
                used_mem = int(self.info['used_memory'])
                if not max_mem_ret:
                    checker_log.warn('[%s] get maxmemory fail' % self.meta_data)
                    return False
                mem_used_percent = float(used_mem) / max_mem
                used_percent = '%d%%' % int(mem_used_percent * 100)
                if mem_used_percent >= float(threshold[0][0]):
                    checker_log.warn('[%s] check redis mem used:[%s]%% error' % (self.meta_data, used_percent))
                else:
                    checker_log.debug('[%s] check redis mem  used %s ok!' %
                                      (self.meta_data, used_mem))
        except Exception as e:
            checker_log.warn('[%s] redis check max memory illegal %s' % (self.meta_data, e))

