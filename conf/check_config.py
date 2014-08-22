__author__ = 'qipanguan'
#!/bin/env python2.6
# -*- coding: utf-8 -*-

ClientConf = {
    'zk_conn': 'h011196.hebe.grid.sina.com.cn:2181',
    'zk_timeout': 3,
    'conf_dir_zk': '/dspalert/conf/',
    'type2file': {
        'mc': 'McMonConf',
        'mcq': 'McqMonConf',
        'cs': 'CsMonConf',
        'dsp': 'AlertConf',
        'redis': 'RedisMonConf',
    },
    'url_get': 'http://10.73.13.99:8888/monitor/get',
    'url_type': 'serviceType',
    'url_idc': 'idc',
    'url_timeout': 5,

    'alert_table': 'dsp_sys_alert_year_month',
    'alert_db': 'dbmon',
    'store_alert_host': 'm3388i.mars.grid.sina.com.cn',
    'store_alert_port': 3388,
    'store_alert_user': 'mysqlha',
    'store_alert_passwd': 'Jxh2MnxeHw',

    'dpadmin_mysql_host': 's3303i.apollo.grid.sina.com.cn',
    'dpadmin_mysql_port': 3303,
    'dpadmin_mysql_user': 'mysqlha',
    'dpadmin_mysql_passwd': 'Jxh2MnxeHw',

    'sina_redis_host': 'rm9999.hebe.grid.sina.com.cn',
    'sina_redis_port': 9999,

    'idc_file': '/data1/dsp/dsp_alert/db/idc'
}

SendAlertConf = {
    'cache_send': 'new_nosql',
    'hbase_send': 'dsp_hbase',
}

McAlertConf = {
    'zk_conf_dir': '/dspalert/mcq/',
    'thread_num': 50,
    'timeout': 3,
    'black_key': 'mc_blacklist',
    'black_hash_key': {
        'mc_conn': 'mc_conn',
        'mcq_conn': 'mcq_conn',
        'mcq_keys_stacking': 'mcq_keys_stacking',
    },

}

McqAlertConf = {
    'zk_conf_dir': '/dspalert/mcq/',
    'thread_num': 50,
    'timeout': 3,
    'black_key': 'mc_blacklist',
    'black_hash_key': {
        'mc_conn': 'mc_conn',
        'mcq_conn': 'mcq_conn',
        'mcq_keys_stacking': 'mcq_keys_stacking',
    },
}

CsAlertConf = {
    'zk_conf_dir': '/dspalert/mcq/',
    'thread_num': 50,
    'timeout': 3,
}

RedisAlertConf = {
    'timeout_day': 3,
    'timeout_night': 60,
}

CommonServiceAlertConf = {
    'thread_num': 150,
    'timeout': 1,
}