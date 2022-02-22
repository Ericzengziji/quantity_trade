#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: zengziji
@time: 2022/1/28 2:05 下午
@file: BaseStragety.py
@version: python3.6
@desc: 基础策略对象，自动交易的软件控制可以参考github：https://github.com/nladuo/THSTrader
"""
import pandas as pd
import pymysql
import requests
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from constant_setting import STOP_LOSS_RATIO, STOP_BENIFIT_RATIO, TRADE_PER_VOLUME, TRADE_CD_TIME
import MySQL_SET
from datetime import datetime,timedelta

class BaseStragety(object):
    """
    基础策略对象
    """

    def __init__(self, stock_code_list, *args, **kwargs):
        """
        :param stock_code_list:列表，股票代码列表，其中第一位为main_stock_code
        :param args:
        :param kwargs:
        """
        self.main_stock_code = stock_code_list[0]
        self.stock_area_code_list = []
        self.stock_code_list = stock_code_list

        for stock_code in stock_code_list:
            # 获取区域股票代码
            if len(stock_code) != 6:
                print("please input stock_code which length is 6 !")
                raise ValueError("stock_code股票代码长度必须是6位数")
            else:
                if stock_code[:3] in ['600', '601', '603', '688']:
                    stock_area_code = 'sh' + stock_code
                elif stock_code[:2] in ['00', '30']:
                    stock_area_code = 'sz' + stock_code
                else:
                    raise ValueError("无法识别stock_code归属上证指数还是深证指数，请检查股票代码前三位是否为600、601或000")

            self.stock_area_code_list.append(stock_area_code)

        # 是否回测
        self.is_backtest = False
        # 订单列表，存储买卖信息，必须是有序的
        self.order_list = []
        # 订单信息，买还是卖、啥时候、哪只、交易哪个、交易多少，{'trade_type': '', 'trade_time': '', 'stock_code': '', 'price': '', 'volume': 0}
        self.order = None

        # DataFrame存储数据
        self.columns_name = ["stock_code", "today_open_price", "yester_close_price", "current_price"
            , "today_high_price", "today_low_price", "trade_volume", "trade_cash"
            , "bid1_buy_volume", "bid1_buy_price", "bid2_buy_volume", "bid2_buy_price"
            , "bid3_buy_volume", "bid3_buy_price", "bid4_buy_volume", "bid4_buy_price"
            , "bid5_buy_volume", "bid5_buy_price", "bid1_sell_volume", "bid1_sell_price"
            , "bid2_sell_volume", "bid2_sell_price", "bid3_sell_volume", "bid3_sell_price"
            , "bid4_sell_volume", "bid4_sell_price", "bid5_sell_volume", "bid5_sell_price"
            , "trade_day", "trade_time"]

        self.df = pd.DataFrame([], columns=self.columns_name)
        self.main_df = None
        #
        self.main_dict = {}
        #
        self.test_df = None

        self.last_order_time = '09:00:00'

    def sina_3s_listen(self, **kwargs):
        """
        监听实时流数据
        :return:
        """
        # 监听的地址 https://hq.sinajs.cn/list=sh510300,sz162411

        if self.is_backtest:
            # 添加df的行
            index = kwargs.get('index')
            # print(row_dict)
            self.df = self.test_df.iloc[:index, :]
            row = self.test_df.iloc[index, :]
            if self.test_df.iloc[1, 0] == self.main_stock_code:
                self.main_dict = self.test_df.iloc[index, :].to_dict()
            # 只是指针而已，不是copy
            self.main_df = self.df[self.df['stock_code'] == self.main_stock_code]

        else:
            url = "https://hq.sinajs.cn/list=%s" % ','.join(self.stock_area_code_list)
            res = requests.get(url, headers={'Referer': 'https://finance.sina.com.cn'})
            lines = res.text.split('\n')
            print(lines)
            # ['var hq_str_sh510300="沪深300ETF,4.590,4.627,4.558,4.597,4.549,4.557,4.558,183292769,836727724.000,138800,4.557,1112700,4.556,60400,4.555,1095900,4.554,1519400,4.553,102100,4.558,312000,4.559,520300,4.560,702400,4.561,75500,4.562,2022-02-22,11:17:20,00,";'
            # , 'var hq_str_sz002371="北方华创,263.740,263.700,269.540,269.570,255.510,269.400,269.540,3048254,796944528.890,2700,269.400,400,269.380,200,269.320,100,269.300,500,269.240,100,269.540,5100,269.570,700,269.600,100,269.660,200,269.700,2022-02-22,11:17:18,00";', '']

            for line in lines:
                if len(line) > 1:
                    line_list = line.split('=')
                    stock_code = line_list[0][-6:]
                    value_list = line_list[1].split(',')

                    pos = len(self.df.columns) - 6 - len(value_list[8:])
                    append_row = [stock_code] + value_list[1:6] + value_list[8:pos]
                    # 默认都是str，需数据类型转化
                    tmp_dict = {}
                    for index, col in enumerate(self.columns_name):
                        if 'volume' in col:
                            tmp_dict[col] = int(append_row[index])
                        elif 'price' in col or 'cash' in col:
                            tmp_dict[col] = float(append_row[index])
                        else:
                            tmp_dict[col] = append_row[index]
                    # 添加df的行
                    self.df = self.df.append(tmp_dict, ignore_index=True)
                    if stock_code == self.main_stock_code:
                        self.main_dict = tmp_dict.copy()

            # 只是指针而已，不是copy
            self.main_df = self.df[self.df['stock_code'] == self.main_stock_code]

    def stop(self):
        """
        止盈或止损策略
        :return:
        """
        is_act = False
        if len(self.order_list) % 2 == 1:
            last_order_dict = self.order_list[-1]
            trade_price = float(last_order_dict.get('price'))
            current_price = float(self.main_dict.get('current_price'))
            change_ration = current_price / trade_price - 1
            # 止损
            if change_ration < 0 and -change_ration > STOP_LOSS_RATIO:
                is_act =  True

            elif change_ration > 0 and change_ration > STOP_BENIFIT_RATIO:
                is_act = True

            elif self.main_dict['trade_time'] > '14:56:20':
                is_act =  True

            else:
                is_act = False

        if is_act:
            if last_order_dict['trade_type'] == 'buy':
                trade_type = 'sell'
            else:
                trade_type = 'buy'

            self.order = {'trade_type': trade_type, 'trade_time': self.main_dict['trade_time']
                , 'stock_code': self.main_dict['stock_code']
                , 'price': self.main_dict['current_price']
                , 'volume': TRADE_PER_VOLUME}
            self.last_order_time = self.main_dict['trade_time']

        return is_act

    def stargety(self):
        """
        形成买卖点时需定义self.order，且返回True
        策略，默认简单的ma策略
        :return: True or False
        """
        ma30 = self.df.current_price[-30:].sum()/30
        if self.main_dict.get('current_price') < ma30:
            delta_time = (datetime.strptime(self.main_dict['trade_time'], "%H:%M:%S") - datetime.strptime(self.last_order_time,"%H:%M:%S")).seconds
            if delta_time > TRADE_CD_TIME:
                self.order = {'trade_type': 'buy', 'trade_time': self.main_dict['trade_time']
                    , 'stock_code': self.main_dict['stock_code']
                    , 'price': self.main_dict['current_price']
                    , 'volume': TRADE_PER_VOLUME}
                return True
        return False

    def exec_stargety(self):
        if len(self.order_list) % 2 == 0:
            if '09:40:00' < self.main_dict['trade_time'] < '14:56:00':
                return self.stargety()

    def run(self, **kwargs):
        """
        流式运行
        策略运行返回执行动作act
        :return:
        """
        # 监听, 更新属性
        self.sina_3s_listen(**kwargs)
        # 止损或止盈
        if self.stop() or self.exec_stargety():
            print(self.order)
            self.order_list.append(self.order)

    def backtest(self, day_list=[]):
        """
        回测
        :return:
        """
        col_str = (','.join(self.columns_name)) \
            .replace('trade_time', 'cast(trade_time as char(10)) as trade_time') \
            .replace('trade_day', 'cast(trade_day as char(10)) as trade_day')
        day_str = "','".join(day_list)
        code_str = "','".join(self.stock_code_list)
        select_sql = """select %s
        from stock_db.trade_3second_history_di
        where trade_day in ('%s')
        and stock_code in ('%s')
        order by trade_day, trade_time
        """ % (col_str, day_str, code_str)
        print(select_sql)

        self.test_df = self.send_sql(select_sql)

        if len(self.test_df) == 0:
            raise ValueError('无对于日期的stock信息')
        else:
            for col in self.columns_name:
                if 'price' in col:
                    self.test_df[col] = self.test_df[col].astype('float')

            self.is_backtest = True
            for index in range(len(self.test_df)):
                self.run(index=index)

    def plot(self):
        """
        画图
        :return:
        """

        fig = plt.figure()
        # 画价格曲线图
        pic = fig.add_subplot(111)
        pic.plot(self.main_df.trade_time, self.main_df.current_price, c='black', label='price')
        pic.xaxis.set_major_locator(ticker.MultipleLocator(600))

        ##叠加买入散点图
        x_list = list(self.main_df.trade_time)
        buy_x, buy_y, sell_x, sell_y = [], [], [], []
        for order in self.order_list:
            if order['trade_type'] == 'buy':
                buy_x.append(x_list.index(order['trade_time']))
                buy_y.append(order['price'])
            elif order['trade_type'] == 'sell':
                sell_x.append(x_list.index(order['trade_time']))
                sell_y.append(order['price'])

        plt.scatter(buy_x, buy_y, c='r')
        # 标记文字
        for i, v in enumerate(buy_x):
            plt.annotate('buy:%.2f' % buy_y[i], (buy_x[i], buy_y[i]))
        plt.scatter(sell_x, sell_y, c='g')
        # 标记文字
        for i, v in enumerate(sell_x):
            plt.annotate('sell:%.2f' % sell_y[i], (sell_x[i], sell_y[i]))

    def send_sql(self, sql, is_return=1):
        """
        :param sql: 提交的sql，如'select 1 as t;'
        :param is_return: 是否要返回值, 1返回，0不返回
        :return: DataFrame
        """
        server_conn = pymysql.connect(host=MySQL_SET.HOST, port=MySQL_SET.PORT, user=MySQL_SET.USER, passwd=MySQL_SET.PWD, charset='utf8', local_infile=True)

        server_cursor = server_conn.cursor()
        server_cursor.execute(sql)

        # 将查询结果cur.fetchall()从list[tuple]转化为df
        if is_return == 0:
            output = None
        else:
            results = list(server_cursor.fetchall())
            # 获取查询结果的字段名
            descriptions = server_cursor.description
            description_list = []
            for description in descriptions:
                description_list.append(description[0])

            output = pd.DataFrame(results, columns=description_list)

        server_conn.commit()
        server_cursor.close()
        server_conn.close()

        return output


if __name__ == "__main__":
    t = BaseStragety(stock_code_list=['600036'])
    # t.run()
    t.backtest(day_list=['2021-03-15'])
    t.plot()
