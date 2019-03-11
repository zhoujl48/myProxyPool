#!/usr/bin/python
# -*- coding:utf-8 -*-
################################################################################
#
# Copyright (c) 2019 ***.com, Inc. All Rights Reserved
# The Proxy-Pool project
################################################################################
"""
动态代理池 -- 主接口

Usage: nohup python run.py >/dev/null 2>&1 & (无日志后台运行)
Authors: Zhou Jialiang
Email: zjl_sempre@163.com
Date: 2018/7/15
"""
from api import app
from scheduler import Scheduler
from config import FLASK_HOST, FLASK_PORT

def main():
    s = Scheduler()
    s.run()
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=True)

if __name__ == '__main__':
    main()