#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/7/15 11:25
# @Author  : zhoujl
# @Site    :
# @File    : scheduler.py
# @Software: PyCharm
from flask import Flask, g
from proxypool.db import RedisClient
from proxypool.settings import FLASK_HOST, FLASK_PORT

# __all__ = ['app']
app = Flask(__name__)

def get_conn():
    """
    建立Redis连接；若已连接则直接返回
    :return: 返回一个Redis连接类的全局对象
    """
    if not hasattr(g, 'redis_client'):
        g.redis_client = RedisClient()
    return g.redis_client

welcome_page = """
<h2>
Welcome to zhoujl's Proxy Pool ~ ^_^ ~
<h4>
Friday, July 13, 2018
</h4>
<h4>
宝宝HAHAHA
</h4>
<a href="http://101.132.68.100:5000/count">IP's counts~</a>
<br>
<a href="http://101.132.68.100:5000/get">GET an ip for use now!</a>
</h2>
"""
@app.route('/')
def index():
    """
    欢迎页面
    """
    return welcome_page

@app.route('/get')
def get_proxy():
    """
    打印代理队列的第一个数据
    """
    conn = get_conn()
    return conn.pop_for_use()

@app.route('/count')
def get_counts():
    """
    打印列表队列的长度
    """
    conn = get_conn()
    return str(conn.list_len)

def main():
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=True)

if __name__ == '__main__':
    main()

