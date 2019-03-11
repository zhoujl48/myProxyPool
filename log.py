#!/usr/bin/env python
# -*- coding: utf-8 -*-
################################################################################
#
# Copyright (c) 2019 ***.com, Inc. All Rights Reserved
# The Common Tools Project
################################################################################
"""
日志文件
日志流去向：
    1. ${LOG_DIR}/name.log -- 完整日志
    2. ${LOG_DIR}/name.log.wf-- WARNING及以上级别日志
    3. 控制台 -- 完整日志


Authors: Zhou Jialiang
Email: zjl_sempre@163.com
Date: 2019/02/13
"""
import os
import logging
import logging.handlers

def init_log(log_path, level=logging.INFO, when="D", backup=7,
             format="%(levelname)s: %(asctime)s: %(filename)s:%(lineno)d * %(thread)d %(message)s",
             datefmt="%m-%d %H:%M:%S"):
    """
    init_log - initialize log module

    Args:
        log_path      - Log file path prefix.
                        Log data will go to two files: log_path.log and log_path.log.wf
                        Any non-exist parent directories will be created automatically
        level         - msg above the level will be displayed
                        DEBUG < INFO < WARNING < ERROR < CRITICAL
                        the default value is logging.INFO
        when          - how to split the log file by time interval
                        'S' : Seconds
                        'M' : Minutes
                        'H' : Hours
                        'D' : Days
                        'W' : Week day
                        default value: 'D'
        format        - format of the log
                        default format:
                        %(levelname)s: %(asctime)s: %(filename)s:%(lineno)d * %(thread)d %(message)s
                        INFO: 12-09 18:02:42: log.py:40 * 139814749787872 HELLO WORLD
        backup        - how many backup file to keep
                        default value: 7

    Raises:
        OSError: fail to create log directories
        IOError: fail to open log file
    """
    formatter = logging.Formatter(format, datefmt)
    logger = logging.getLogger()
    logger.setLevel(level)

    dir = os.path.dirname(log_path)
    if not os.path.isdir(dir):
        os.makedirs(dir)

    # 记录完整日志
    handler = logging.handlers.TimedRotatingFileHandler(log_path + ".log",
                                                        when=when,
                                                        backupCount=backup,
                                                        encoding='utf-8')
    handler.setLevel(level)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # 记录warning及以上级别日志
    handler = logging.handlers.TimedRotatingFileHandler(log_path + ".log.wf",
                                                        when=when,
                                                        backupCount=backup,
                                                        encoding='utf-8')
    handler.setLevel(logging.WARNING)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # 打印控制台
    handler = logging.StreamHandler()
    handler.setLevel(level)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

