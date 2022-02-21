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
    def __init__(self, stock_code, *args, **kwargs):
        """
        初始化对象的属性
        """
        self.stock_code = stock_code

        # 获取区域股票代码
        if len(stock_code) != 6:
            print("please input stock_code which length is 6 !")
            raise ValueError("stock_code股票代码长度必须是6位数")
        else:
            if stock_code[:3] in ['600', '601', '603', '688']:
                self.stock_area_code = 'sh' + stock_code
                self.stock_code = stock_code
            elif stock_code[:2] in ['00', '30']:
                self.stock_area_code = 'sz' + stock_code
                self.stock_code = stock_code
            else:
                raise ValueError("无法识别stock_code归属上证指数还是深证指数，请检查股票代码前三位是否为600、601或000")

        # 监听的股票代码
        self.listen_url_3s = "http://hq.sinajs.cn/list=%s" % self.stock_area_code

    def listen(self):
        """
        监听实时流数据
        :return:
        """
        pass

    def stop_loss(self):
        """
        止损策略
        :return:
        """
        pass

    def stop_benifit(self):
        """
        止盈策略
        :return:
        """
        pass

    def starget_ma(self):
        """
        ma策略
        :return:
        """

    def run(self, *args, **kwargs):
        """
        流式运行
        策略运行返回执行动作act
        :return:
        """
        act = ""
        return act

    def test(self):
        """
        回测
        :return:
        """
        pass

    def plot(self):
        """
        画图
        :return:
        """
        pass



if __name__ == "__main__":
    """
    测试
    """
    test_oject = BaseStragety(unittest.TestCase)
    unittest.main()