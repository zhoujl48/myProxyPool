#!/usr/bin/python
# -*- coding:utf-8 -*-
################################################################################
#
# Copyright (c) 2019 ***.com, Inc. All Rights Reserved
# The Proxy-Pool project
################################################################################
"""
动态代理池 -- 调度器模块

Usage: 
Authors: Zhou Jialiang
Email: zjl_sempre@163.com
Date: 2018/7/15
"""
import time
import aiohttp
import asyncio
from multiprocessing import Process
from aiohttp import ClientConnectionError as ProxyConnectionError, ServerDisconnectedError, ClientResponseError, ClientConnectorError
from db import RedisClient
from err_raise import ResourceDepletionError
from getter import FreeProxyGetter
from config import TEST_API, GET_PROXIES_TIMEOUT
from config import VALID_CHECK_CYCLE, POOL_LEN_CHECK_CYCLE
from config import POOL_LOWER_THRESHOLD, POOL_UPPER_THRESHOLD


class ValidityTester(object):
    """代理有效性测试类

    Attributes:
        _raw_proxies: list, 待测试有效性的代理IP列表
        _valid_proxies: list, 经测试有效的代理IP列表
    """
    test_api = TEST_API

    def __init__(self):
        self._raw_proxies = None
        self._valid_proxies = list()

    def set_raw_proxies(self, proxies):
        self._raw_proxies = proxies
        self._conn = RedisClient()

    async def _test_single_proxies(self, proxy):
        """单IP有效性测试
        对单个代理(取自self._raw_proxies)进行有效性测试，
        若测试通过，则加入_valid_proxies列表

        Args:
            proxy: 待测试代理IP
        """
        if isinstance(proxy, bytes):
            proxy = proxy.decode('utf8')

        # 尝试开启aiohttp，否则抛出ServerDisconnectedError, ClientConnectorError, ClientResponseError等连接异常
        try:
            async with aiohttp.ClientSession() as session:
                # aiohttp已成功开启，开始验证代理ip的有效性
                # 若代理无效，则抛出 ProxyConnectionError, TimeoutError, ValueError 异常
                try:
                    async with session.get(url=self.test_api, proxy='http://{}'.format(proxy),
                                           timeout=GET_PROXIES_TIMEOUT) as response:
                        if response.status == 200:
                            self._conn.put(proxy)
                            print('Valid proxy: {}'.format(proxy))
                except (ProxyConnectionError, TimeoutError, ValueError):
                    print('Invalid proxy: {}'.format(proxy))
        except (ServerDisconnectedError, ClientConnectorError, ClientResponseError) as s:
            print(s)

    def test(self):
        """有效性测试接口
        """
        print('ValidityTester is working...')
        try:
            loop = asyncio.get_event_loop()
            tasks = [self._test_single_proxies(proxy) for proxy in self._raw_proxies]
            loop.run_until_complete(asyncio.wait(tasks))
        except ValueError:
            print('Async Error')


class PoolAdder(object):
    """代理IP池添加类

    Attributes:
        _upper_threshold: 代理池IP上限
        _conn: Redis连接对象
        _tester: 有效性测试对象
        _crawler: 代理IP爬取对象
    """
    def __init__(self, upper_threshold):
        self._upper_threshold = upper_threshold
        self._conn = RedisClient()
        self._tester = ValidityTester()
        self._crawler = FreeProxyGetter()

    def over_upper_threshold(self):
        """判断代理池是否过盈
        """
        return True if self._conn.list_len >= self._upper_threshold else False

    def add_to_pool(self):
        """添加有效代理IP至代理池接口
        """
        print('PoolAdder is working...')
        raw_proxies_count = 0
        while not self.over_upper_threshold():

            # 遍历爬取方法
            for callback_label in range(self._crawler.__CrawlFuncCount__):

                # 爬取免费代理IP
                callback = self._crawler.__CrawlFunc__[callback_label]
                raw_proxies = self._crawler.get_raw_proxies(callback=callback)

                # 代理IP有效性测试
                self._tester.set_raw_proxies(raw_proxies)
                self._tester.test()

                # 代理池上限检测
                raw_proxies_count += len(raw_proxies)
                if self.over_upper_threshold():
                    print('IPs are enough, waiting to be used')
                    break

            # 资源枯竭异常
            if raw_proxies_count == 0:
                raise ResourceDepletionError



class Scheduler(object):
    """调度器类
    """
    def __init__(self, cycle_valid_check=VALID_CHECK_CYCLE, cycle_pool_check=POOL_LEN_CHECK_CYCLE):
        self._cycle_valid_check = cycle_valid_check
        self._cycle_pool_check = cycle_pool_check

    def test_proxies(self):
        """定时测试有效性
        检查代理队列左半边代理IP有效性，
        无效的剔除，有效的则重新放入队列右侧

        Args:
            cycle: 检测周期, 默认60, 单位S
        """
        conn = RedisClient()
        tester = ValidityTester()

        # 定时执行测试任务
        while True:
            print('testing & refreshing ips...')
            count = int(0.5 * conn.list_len)

            # 若队列为空，则等待60秒
            if count == 0:
                print('0 ip, waiting for adding...')
                time.sleep(self._cycle_valid_check)
                continue

            # 否则，进行有效性测试，并等待60秒
            raw_proxies = conn.get_for_test(count)
            tester.set_raw_proxies(raw_proxies)
            tester.test()
            time.sleep(self._cycle_valid_check)

    def check_pool(self, lower_threshold=POOL_LOWER_THRESHOLD, upper_threshold=POOL_UPPER_THRESHOLD):
        """定时向代理池添加代理IP

        Args:
            lower_threshold: 代理池IP数下限
            upper_threshold: 代理池IP数上限
            cycle: 代理池IP数量检查周期, 默认20, 单位S
        """
        conn = RedisClient()
        adder = PoolAdder(upper_threshold)

        # 定时执行添加任务
        while True:
            if conn.list_len < lower_threshold:
                adder.add_to_pool()
            time.sleep(self._cycle_pool_check)

    def run(self):
        """调度器主接口
        多进程动态维护代理IP池
        """
        print('IP scheduler is running...')
        valid_process = Process(target=self.test_proxies)
        check_process = Process(target=self.check_pool)
        valid_process.start()
        check_process.start()


if __name__ == '__main__':

    s = Scheduler()
    s.run()
