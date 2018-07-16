#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/7/15 11:25
# @Author  : zhoujl
# @Site    :
# @File    : scheduler.py
# @Software: PyCharm

# Redis数据库服务
REDIS_HOST = '101.132.68.100'
REDIS_PORT = 6379
REDIS_PASSWORD = ''
REDIS__LIST_NAME = "proxies"

# Flask服务
FLASK_HOST = '0.0.0.0'
FLASK_PORT = 5000
DEBUG = True

# HTTP请求头
User_Agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
HEADERS = {
    'User-Agent' : User_Agent,
}

# 代理测试网址
TEST_API = 'http://www.baidu.com'
# 代理测试时间上限
GET_PROXIES_TIMEOUT = 5

# 代理有效性检查周期(s)
VALID_CHECK_CYCLE = 60
# 代理池ip数量检查周期(s)
POOL_LEN_CHECK_CYCLE = 20
# 代理池ip数量上限
POOL_UPPER_THRESHOLD = 150
# 代理池ip数量下限
POOL_LOWER_THRESHOLD = 30

