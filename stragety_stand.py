from BaseStragety import BaseStragety

class Stand(BaseStragety):
    """
    站队策略，观测最近N条记录是否存在大额交易，若是则标记，观察标记后C时间段后的涨跌幅情况，若涨幅明显则做多，反之做空
    """
    def __init__(self, stock_code_list):
        super(Stand, self).__init__(stock_code_list)
        self.mark_list = []
        self.observe_nums = 20
        self.interval_time = 60
        self.change_ratio = 0.008
        self.count = 0
        self.cash_list = []
        self.max_cash = 1

    def stargety(self):
        """
        每天股票交易4个小时，240分钟 *0.37 = 88分钟，即10点28分
        :return:
        """
        self.count += 1
        if (self.count-1)%20 == 0:
            trade_cash = self.main_dict['trade_cash'] - sum(self.cash_list)
            self.cash_list.append(trade_cash)
            print("trade_cash is ", trade_cash )

            # 成交量样本数量足够 且 交易量明显放大，mark
            if len(self.cash_list) > 5 and trade_cash/(sum(self.cash_list[-5:])/5) > 1.5:
                self.main_dict['count'] = self.count
                self.mark_list.append(self.main_dict)


        if len(self.mark_list) > 0 :
            for mark_dict in self.mark_list:
                if self.count - mark_dict['count'] > self.interval_time:
                    ratio = abs(self.main_dict['current_price'] / mark_dict['current_price'] - 1)
                    # 标记后的涨跌幅符合预期
                    if ratio > self.change_ratio:
                        if self.main_dict['current_price'] > mark_dict['current_price']:
                            trade_type = 'buy'
                        else:
                            trade_type = 'sell'

                        self.order = {'trade_type': trade_type, 'trade_time': self.main_dict['trade_time']
                            , 'stock_code': self.main_dict['stock_code']
                            , 'price': self.main_dict['current_price']
                            , 'volume': self.TRADE_PER_VOLUME}
                        self.last_order_time = self.main_dict['trade_time']
                        self.mark_list.remove(mark_dict)

                        return True

                else:
                    break

        return False


if __name__ == "__main__":
    t = Stand(stock_code_list=['600036'])
    # t.run()
    t.backtest(day_list=['2021-03-16'])
    t.plot()
