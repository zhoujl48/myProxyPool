#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/7/15 11:25
# @Author  : zhoujl
# @Site    :
# @File    : scheduler.py
# @Software: PyCharm
class PoolEmptyError(Exception):
    def __init__(self):
        super.__init__(self)

    def __str__(self):
        return repr('Pool is EMPTY!')

class ResourceDepletionError(Exception):
    def __init__(self):
        super().__init__(self)

    def __str__(self):
        return repr('The proxy source is exhausted, please add new websites for more ip.')