#!/usr/bin/python
# -*- coding:utf-8 -*-
################################################################################
#
# Copyright (c) 2019 ***.com, Inc. All Rights Reserved
# The Proxy-Pool project
################################################################################
"""
动态代理池 -- 网页接口模块

Usage: 供run.py调用
Authors: Zhou Jialiang
Email: zjl_sempre@163.com
Date: 2018/7/15
"""
from flask import Flask, g
from db import RedisClient
from config import FLASK_HOST, FLASK_PORT, DEBUG

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
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Proxy Pool API</title>
</head>
<body>
<h2>Welcome to My Proxy Pool!!</h2>

    Date: Friday, July 13, 2018
    <br>
    Author: Zhou Jialiang
    <br>
    GitHub: <a href="https://github.com/zhoujl48/myProxyPool">https://github.com/zhoujl48/myProxyPool</a>
    <br><br>
    <a href="http://101.132.68.100:5000/count">How many proxy IPs in this pool now?</a>
    <br>
    <a href="http://101.132.68.100:5000/get">GET an IP for use now!</a>

</body>
</html>
"""
@app.route('/')
def index():
    """欢迎页面
    """
    return welcome_page

@app.route('/get')
def get_proxy():
    """获取最新可用代理IP
    """
    conn = get_conn()
    return conn.pop_for_use()

@app.route('/count')
def get_counts():
    """打印代理池当前IP数量
    """
    conn = get_conn()
    return str(conn.list_len)


if __name__ == '__main__':


    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=DEBUG)

