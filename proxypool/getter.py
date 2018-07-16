#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/7/15 11:25
# @Author  : zhoujl
# @Site    :
# @File    : scheduler.py
# @Software: PyCharm
import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
from proxypool.settings import HEADERS


class ProxyMetaclass(type):
    """
    元类， 在FreeProxyGetter中添加两个属性：
    __CrawlFunc__: 爬虫函数组成的列表
    __CrawlFuncCount__: 爬虫函数的数量，即列表的长度
    """

    def __new__(cls, name, bases, attrs):
        count = 0
        attrs['__CrawlFunc__'] = []
        for key, value in attrs.items():
            if 'crawl_' in key:
                attrs['__CrawlFunc__'].append(key)
                count += 1
        attrs['__CrawlFuncCount__'] = count
        return type.__new__(cls, name, bases, attrs)


class FreeProxyGetter(object, metaclass=ProxyMetaclass):
    def get_raw_proxies(self, callback):
        proxies = []
        print('Callback: {}'.format(callback))
        for proxy in eval('self.{}()'.format(callback)):
            print('Getting {} from {}'.format(proxy, callback))
            proxies.append(proxy)
        return proxies

    def crawl_xicidaili(self):
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

    def crawl_66ip(self):
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

    def crawl_data5u(self):
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


def main():
    getter = FreeProxyGetter()
    for ip in getter.crawl_xicidaili():
        print(ip)
    for ip in getter.crawl_66ip():
        print(ip)
    for ip in getter.crawl_data5u():
        print(ip)

if __name__ == '__main__':
    main()

