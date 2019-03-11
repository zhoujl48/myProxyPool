#!/usr/bin/python
# -*- coding:utf-8 -*-
################################################################################
#
# Copyright (c) 2019 ***.com, Inc. All Rights Reserved
# The Proxy-Pool project
################################################################################
"""
动态代理池 -- 代理IP获取模块

Usage: 供Scheduler调用
Authors: Zhou Jialiang
Email: zjl_sempre@163.com
Date: 2018/7/15
"""

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
from config import HEADERS


class ProxyMetaclass(type):
    """元类
    通过元类构造的类，具有__new__()方法的功能
    即可在后文FreeProxyGetter类中添加两个属性：
        __CrawlFunc__: 爬虫函数组成的列表
        __CrawlFuncCount__: 爬虫函数的数量，即列表的长度
    """

    def __new__(cls, name, bases, attrs):
        """重写__new__方法
        构造一个空对象，在__init__之前执行

        Args:
            name: 构建的类名
            bases: 基类集合元组，若只有一个基类则应写成(base1,)形式
            attrs: 类属性(包括属性和方法)

        Return:
            type.__new__(cls, name, bases, attrs): 由重写的__new__()构造的类
        """
        count = 0
        attrs['__CrawlFunc__'] = []
        for key, value in attrs.items():
            if '_crawl_' in key:
                attrs['__CrawlFunc__'].append(key)
                count += 1
        attrs['__CrawlFuncCount__'] = count
        return type.__new__(cls, name, bases, attrs)


class FreeProxyGetter(object, metaclass=ProxyMetaclass):
    """免费代理获取类
    通过元类ProxyMetaclass构造，
    即天生具有_CrawFunc__和__CrawFuncCount__这两个属性，
    进而方便对爬虫方法进行管理
    """

    def _crawl_xicidaili(self):
        """爬虫方法——www.xicidaili.com
        """
        base_url = 'http://www.xicidaili.com/wt/{page}'
        for page in range(1, 2):
            resp = requests.get(url=base_url.format(page=page), headers=HEADERS)
            if resp.status_code != 200:
                print('Error status code: {}'.format(resp.status_code))
            else:
                soup = BeautifulSoup(resp.text, 'lxml')
                ip_list = soup.find(id='ip_list')
                for child in ip_list.children:
                    if not isinstance(child, str):
                        ip_host = child.contents[3].string
                        ip_port = child.contents[5].string
                        ip = '{host}:{port}'.format(host=ip_host, port=ip_port)
                        if ip[0].isdigit():
                            yield ip

    def _crawl_66ip(self):
        """爬虫方法——www.66ip.cn
        """
        base_url = 'http://www.66ip.cn/{page}.html'
        for page in range(1, 6):
            resp = requests.get(url=base_url.format(page=page), headers=HEADERS)
            if resp.status_code != 200:
                print('Error status code: {}'.format(resp.status_code))
            else:
                soup = BeautifulSoup(resp.text, 'lxml')
                table = soup.find('table', width='100%', border='2px', cellspacing='0px', bordercolor='#6699ff')
                for child in table.children:
                    if isinstance(child, Tag):
                        ip_host = child.contents[0].string
                        ip_port = child.contents[1].string
                        ip = '{host}:{port}'.format(host=ip_host, port=ip_port)
                        if ip[0].isdigit():
                            yield ip

    def _crawl_data5u(self):
        """爬虫方法——www.data5u.com
        """
        base_url = 'http://www.data5u.com/free/{}/index.shtml'
        for i in ['gngn', 'gnpt']:
            resp = requests.get(url=base_url.format(i), headers=HEADERS)
            if resp.status_code != 200:
                print('Error status code: {}'.format(resp.status_code))
            else:
                soup = BeautifulSoup(resp.text, 'lxml')
                for row in soup.find_all('ul', class_='l2'):
                    ip_host = row.contents[1].string
                    ip_port = row.contents[3].string
                    ip = '{host}:{port}'.format(host=ip_host, port=ip_port)
                    yield ip

    def get_raw_proxies(self, callback):
        """调用接口
        指定具体的爬虫方法，获取免费代理IP

        Args:
            callbacks: 具体的爬虫方法

        Return:
            proxies: 爬取的代理IP列表
        """
        proxies = list()
        print('Callback: {}'.format(callback))
        for proxy in eval('self.{}()'.format(callback)):
            print('Getting {} from {}'.format(proxy, callback))
            proxies.append(proxy)
        return proxies


if __name__ == '__main__':

    # 测试用
    getter = FreeProxyGetter()
    for craw_func in getter.__CrawlFunc__:
        getter.get_raw_proxies(callback=craw_func)

