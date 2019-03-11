#!/usr/bin/python
# -*- coding:utf-8 -*-
################################################################################
#
# Copyright (c) 2019 ***.com, Inc. All Rights Reserved
# The Proxy-Pool project
################################################################################
"""
动态代理池 -- Redis队列操纵模块

Usage: 供Scheduler调用
Authors: Zhou Jialiang
Email: zjl_sempre@163.com
Date: 2018/7/15
"""
import redis
from err_raise import PoolEmptyError
from config import REDIS_LIST_NAME, REDIS_HOST, REDIS_PASSWORD, REDIS_PORT


class RedisClient(object):
    """Redis连接类
    用于连接Redis数据库并操纵其中的代理IP列表

    Attributes:
        _db: redis队列
    """
    def __init__(self, host=REDIS_HOST, port=REDIS_PORT):
        """
        连接Redis数据库

        Args:
            host: Redis的IP地址
            port: Redis的port端口号
        """
        if REDIS_PASSWORD:
            self._db = redis.Redis(host=host, port=port, password=REDIS_PASSWORD)
        else:
            self._db = redis.Redis(host=host, port=port)

    @property
    def list_len(self):
        return self._db.llen(REDIS_LIST_NAME)

    def flush(self):
        """清空队列
        """
        self._db.flushall()

    def get_for_test(self, num=1):
        """测试代理可用性
        从Redis队列左端获取num个代理，用于测试有效性

        Args:
            num: 用于测试有效性的代理IP个数，默认为1
        Returns:
            proxies_to_get: 获取代理(bytes类型)构成的列表
        """

        # 获取Redis队列左数num个元素
        proxies_to_get = self._db.lrange(REDIS_LIST_NAME, 0, num - 1)

        # 保留Redis队列[num, -1]个元素，
        # 即从队列中删除用于测试的代理IP
        self._db.ltrim(REDIS_LIST_NAME, num, -1)

        return proxies_to_get

    def put(self, proxy):
        """插入代理IP
        当代理IP经测试为可用后，
        从Redis队列右侧插入此代理IP

        Args:
            proxy: 插入的代理，类型为bytes
        """
        self._db.rpush(REDIS_LIST_NAME, proxy)

    def pop_for_use(self):
        """获取代理IP
        从Redis队列右端获取一个代理IP
        理论上队列右侧代理为测试可用代理IP
        """
        try:
            return self._db.rpop(REDIS_LIST_NAME)
        except:
            raise PoolEmptyError


if __name__ == '__main__':
    client = RedisClient()
    print("Init, list's legnth: {}".format(client.list_len))

    for i in range(40):
        client.put('{}.{}.{}.{}:{}'.format(i, i, i, i, i))
    print("After put() 40 times, list's legnth: {}".format(client.list_len))

    num = 3
    proxies_got = client.get_for_test(num)
    print('Get {} proxies from list: '.format(num))
    for proxy in proxies_got:
        print('\t' + proxy.decode('utf8'))
    print("After get(), list's legnth: {}".format(client.list_len))

    print(client.pop_for_use())
    print("After pop(), list's legnth: {}".format(client.list_len))

    client.flush()
    print("After flush(), list's legnth: {}".format(client.list_len))
