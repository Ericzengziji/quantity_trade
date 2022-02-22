from BaseStragety import BaseStragety

class BestChoice(BaseStragety):
    """
    一天，苏格拉底带领几个弟子来到一块麦地边，地里满是沉甸甸的麦穗。
    苏格拉底对弟子们说：“你们去麦地里摘一个最大的麦穗，只许进不许退。我在麦地的尽头等你们。”
    弟子们陆续走进了麦地。 地里到处都是大麦穗，哪一个才是最大的呢？弟子们埋头向前走。
    看看这一株，摇了摇头；看看那一株，又摇了摇头。 他们总以为最大的麦穗还在前面。
    虽然弟子们也试着摘了几穗，但并不满意，便随手扔掉了。 他们总以为机会还很多，完全没有必要过早地定夺。
    突然，大家听到苏格拉底苍老的、如同洪钟一般的声音：“你们已经到头了。”这时两手空空的弟子们才如梦初醒

    37% 1/e。什么是37%。以秘书问题（经典选择问题）为例，如果要在3个月内找到合适的秘书。
    那么该如何做呢。算法告诉我们应该在37%的时间段，也就是1个月时做出选择。前面先尽可能的面试，并收集信息，感受自己最需要什么样的秘书，
    然后在37%时选择下一个相对优秀的候选人。
    也就是不要过早选择，先接触并建立标准和认知；也不要过晚选择，发现错过了优秀的候选人，而发现后面的人还不如前面的。
    """
    def __init__(self, stock_code_list):
        super(BestChoice, self).__init__(stock_code_list)
        self.sample_dict = {}
        self.trade_ratio = 0.008
        self.is_stop = False

    def stargety(self):
        """
        每天股票交易4个小时，240分钟 *0.37 = 88分钟，即10点28分
        :return:
        """
        # 只交易一次
        if self.is_stop is False:
            if len(self.sample_dict) == 0:
                if self.main_dict['trade_time'] > '10:28:00':
                    self.sample_dict['max_price'] = self.main_dict['today_high_price']
                    self.sample_dict['min_price'] = self.main_dict['today_low_price']

            else:
                if self.main_dict['trade_time'] > '10:28:00':
                    high_change_ratio = self.main_dict['current_price'] / self.sample_dict['max_price'] - 1
                    low_change_ratio = self.main_dict['current_price'] / self.sample_dict['min_price'] - 1
                    if high_change_ratio > self.trade_ratio:
                        self.order = {'trade_type': 'sell', 'trade_time': self.main_dict['trade_time']
                            , 'stock_code': self.main_dict['stock_code']
                            , 'price': self.main_dict['current_price']
                            , 'volume': self.TRADE_PER_VOLUME}
                        self.last_order_time = self.main_dict['trade_time']
                        self.is_stop = True
                        return True

                    elif -low_change_ratio > self.trade_ratio:
                        self.order = {'trade_type': 'buy', 'trade_time': self.main_dict['trade_time']
                            , 'stock_code': self.main_dict['stock_code']
                            , 'price': self.main_dict['current_price']
                            , 'volume': self.TRADE_PER_VOLUME}
                        self.last_order_time = self.main_dict['trade_time']
                        self.is_stop = True
                        return True

        return False


if __name__ == "__main__":
    t = BestChoice(stock_code_list=['600036'])

    sql = """select cast(trade_day as char(10)) as trade_day
    from stock_db.trade_3second_history_di
    where stock_code='%s'
    group by trade_day 
    HAVING count(1) > 4000
    order by trade_day
    limit 30
    """ % t.main_stock_code
    day_df = t.send_sql(sql)
    day_list = list(day_df['trade_day'])
    profit_list = []

    for index, day in enumerate(day_list):
        print(index)
        t = BestChoice(stock_code_list=['600036'])
        t.backtest(day_list=[day])
        profit_list.append(t.cal_profit())