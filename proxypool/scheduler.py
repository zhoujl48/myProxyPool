#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/7/15 11:25
# @Author  : zhoujl
# @Site    :
# @File    : scheduler.py
# @Software: PyCharm
import aiohttp
import asyncio
import time
from multiprocessing import Process
from aiohttp import ClientConnectionError as ProxyConnectionError, ServerDisconnectedError, ClientResponseError, \
    ClientConnectorError
from proxypool.db import RedisClient
from proxypool.err_raise import ResourceDepletionError
from proxypool.getter import FreeProxyGetter
from proxypool.settings import TEST_API, GET_PROXIES_TIMEOUT
from proxypool.settings import VALID_CHECK_CYCLE, POOL_LEN_CHECK_CYCLE
from proxypool.settings import POOL_LOWER_THRESHOLD, POOL_UPPER_THRESHOLD


class ValidityTester(object):
    test_api = TEST_API

    def __init__(self):
        self._raw_proxies = None
        self._valid_proxies = []

    def set_raw_proxies(self, proxies):
        self._raw_proxies = proxies
        self._conn = RedisClient()

    async def test_single_proxies(self, proxy):
        """
        对单个代理(取自self._raw_proxies)进行有效性测试，若测试通过，则加入_valid_proxies列表
        :param proxy: 单个待测代理
        :return:
        """
        # 尝试开启aiohttp，否则抛出ServerDisconnectedError, ClientConnectorError, ClientResponseError等连接异常
        try:
            async with aiohttp.ClientSession() as session:
                # aiohttp已成功开启，开始验证代理ip的有效性
                # 若代理无效，则抛出 ProxyConnectionError, TimeoutError, ValueError 异常
                try:
                    if isinstance(proxy, bytes):
                        proxy.decode('utf8')
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
        """
        测试所有代理的有效性
        """
        print('ValidityTester is working...')
        try:
            loop = asyncio.get_event_loop()
            tasks = [self.test_single_proxies(proxy) for proxy in self._raw_proxies]
            loop.run_until_complete(asyncio.wait(tasks))
        except ValueError:
            print('Async Error')


class PoolAdder(object):
    def __init__(self, upper_threshold):
        self._upper_threshold = upper_threshold
        self._conn = RedisClient()
        self._tester = ValidityTester()
        self._crawler = FreeProxyGetter()

    def over_upper_threshold(self):
        """
        判断代理池是否过盈
        """
        return True if self._conn.list_len >= self._upper_threshold else False

    def add_to_pool(self):
        print('PoolAdder is working...')
        raw_proxies_count = 0
        while not self.over_upper_threshold():
            for callback_label in range(self._crawler.__CrawlFuncCount__):
                callback = self._crawler.__CrawlFunc__[callback_label]
                raw_proxies = self._crawler.get_raw_proxies(callback=callback)
                self._tester.set_raw_proxies(raw_proxies)
                self._tester.test()
                raw_proxies_count += len(raw_proxies)
                if self.over_upper_threshold():
                    print('IPs are enough, waiting to be used')
                    break
            if raw_proxies_count == 0:
                raise ResourceDepletionError



class Scheduler(object):
    @staticmethod
    def test_proxies(cycle=VALID_CHECK_CYCLE):
        """
        检查代理队列左半边(旧的)队列的代理有效性，无效的剔除，有效的重新放入队列右侧
        :param cycle: 检测周期
        """
        conn = RedisClient()
        tester = ValidityTester()
        while True:
            print('testing & refreshing ips...')
            count = int(0.5 * conn.list_len)
            if count == 0:
                print('0 ip, waiting for adding...')
                time.sleep(cycle)
                continue
            raw_proxies = conn.get_for_test(count)
            tester.set_raw_proxies(raw_proxies)
            tester.test()
            time.sleep(cycle)

    @staticmethod
    def check_pool(lower_threshold=POOL_LOWER_THRESHOLD,
                   upper_threshold=POOL_UPPER_THRESHOLD,
                   cycle=POOL_LEN_CHECK_CYCLE):
        conn = RedisClient()
        adder = PoolAdder(upper_threshold)
        while True:
            if conn.list_len < lower_threshold:
                adder.add_to_pool()
            time.sleep(cycle)

    def run(self):
        print('IP scheduler is running...')
        valid_process = Process(target=Scheduler.test_proxies)
        check_process = Process(target=Scheduler.check_pool)
        valid_process.start()
        check_process.start()



