#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: zengziji
@time: 2022/1/28 2:05 下午
@file: BaseStragety.py
@version: python3.6
@desc: 基础策略对象
"""
import unittest


class BaseStragety(object):
    """
    基础策略对象
    """
    def __init__(self, *args, **kwargs):
        """
        初始化对象的属性
        """
        self.count = 0
        self.max_count = 10

    def run(self, *args, **kwargs):
        """
        流式运行
        策略运行返回执行动作act
        :return:
        """
        act = ""
        return act


    def __iter__(self, *args, **kwargs):
        """
        可以被next()函数调用并不断返回下一个值的对象称为迭代器：Iterator
        生成器都是Iterator对象，但list、dict、str虽然是Iterable，却不是Iterator
        意义：可节省内存空间，它与列表的区别在于，构建迭代器的时候，不像列表把所有元素一次性加载到内存，而是以一种延迟计算
        :return:
        """
        return self


    def __next__(self, *args, **kwargs):
        """
        可以被next()函数调用并不断返回下一个值的对象称为迭代器：Iterator。
        :param args:
        :param kwargs:
        :return:
        """
        if self.count < self.max_count:
            print(self.count)
            self.count += 1
        else:
            raise StopIteration()


if __name__ == "__main__":
    """
    测试
    """
    test_oject = BaseStragety(unittest.TestCase)
    unittest.main()