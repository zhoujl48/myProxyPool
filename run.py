#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/7/16 21:51
# @Author  : zhoujl
# @Site    : 
# @File    : run.py
# @Software: PyCharm
from proxypool.api import app
from proxypool.scheduler import Scheduler
from proxypool.settings import FLASK_HOST, FLASK_PORT

def main():
    s = Scheduler()
    s.run()
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=True)

if __name__ == '__main__':
    main()