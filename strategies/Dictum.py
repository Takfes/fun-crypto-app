import math
import backtrader as bt
import numpy as np
import sys

debug = False

#TODO check quicknotify, cheat-on-open for entry and exit in the same bar
# ===
# quicknotify: Broker notifications are delivered right before the delivery of the next prices. For backtesting this has
# no implications, but with live brokers a notification can take place long before the bar is delivered. When set to
# True notifications will be delivered as soon as possible (see qcheck in live feeds)
# ===
# cheat-on-open: The next_open method of strategies will be called. This happens before next and before the broker has
# had a chance to evaluate orders. The indicators have not yet been recalculated. This allows issuing an orde which
# takes into account the indicators of the previous day but uses the open price for stake calculations
# ===
# For cheat_on_open order execution, it is also necessary to make the call cerebro.broker.set_coo(True) or instantite a
# broker with BackBroker(coo=True) (where coo stands for cheat-on-open) or set the broker_coo parameter to True. Cerebro
# will do it automatically unless disabled below.
# ===
# broker_coo (default: True)
# This will automatically invoke the set_coo method of the broker with True to activate cheat_on_open execution. Will
# only do it if cheat_on_open is also True

# Custom Indicator

class DICK(bt.Indicator):
    # global vwma_list, bbt_list, bbb_list
    # vwma_list = bbt_list = bbb_list = []

    lines = ('vwma', 'bbt', 'bbb')  # output lines (array)
    params = (
        ('period', 110),
        ('factor', 0.618),
        ('multiplier', 3.0)
    )

    def __init__(self):
        # indicate min period ; i.e. buffering period
        self.addminperiod(self.p.period)

    def next(self):
        # calculate vwma
        highp = np.array(self.data.high.get(size=self.p.period))
        lowp = np.array(self.data.low.get(size=self.p.period))
        closep = np.array(self.data.close.get(size=self.p.period))
        volumep = np.array(self.data.volume.get(size=self.p.period))
        hlcp = (highp + lowp + closep) / 3.0
        sumprodp = hlcp * volumep
        vwma = sum(sumprodp) / sum(volumep)
        # add vwma line
        self.lines.vwma[0] = vwma
        # vwma_list.append(vwma[-1])

        # calculate stdev hlc
        std = np.std(hlcp)
        # add bbt & bbb lines
        self.lines.bbt[0] = vwma + (self.p.multiplier * self.p.factor * std)
        self.lines.bbb[0] = vwma - (self.p.multiplier * self.p.factor * std)
        # bbt_list.append(hlcp[-1] + self.p.factor * std)
        # bbb_list.append(hlcp[-1] - self.p.factor * std)

        if debug:
            print('> highp : ', '\n', type(highp), '\n', highp, '\n')
            print('> lowp : ', '\n', type(lowp), '\n', lowp, '\n')
            print('> closep : ', '\n', type(closep), '\n', closep, '\n')
            print('> volumep : ', '\n', type(volumep), '\n', volumep, '\n')
            print('> hlcp : ', '\n', type(hlcp), '\n', hlcp, '\n')
            print('> sumprodp : ', '\n', type(sumprodp), '\n', sumprodp, '\n')
            print('> vwma : ', '\n', type(vwma), '\n', vwma, '\n')
            print('> std(hlcp) : ', '\n', type(std), '\n', std, '\n')
            # print('> vwma_list) : ','\n',vwma_list,'\n')
            # print('> bbt_list) : ','\n',bbt_list,'\n')
            # print('> bbb_list) : ','\n',bbb_list,'\n')


# Strategy

class Dictum(bt.Strategy):

    params = (
        ('symbol','unknown'),
        ('cash',1000),
        ('risk',0.1),
        ('wma_period',300),
        ('stoploss',0.01),
        ('takeprofit',0.01),
        ('short_positions',0),
        ('period', 110),
        ('factor', 0.618),
        ('multiplier', 3.0)
        )

    def __init__(self):

        # print('>> Dictum Strategy Params :')
        # for k,v in self.params.items():
        #     print(f'{k} : {v}')
        # print()
        # self.dataopen1 = self.datas[1].open
        # self.dataclose1 = self.datas[1].close
        # self.datalow1 = self.datas[1].low
        # self.datahigh1 = self.datas[1].high
        self.dataopen = self.datas[0].open
        self.dataclose = self.datas[0].close
        self.datalow = self.datas[0].low
        self.datahigh = self.datas[0].high
        self.PnL = 0
        self.starting_cash = self.broker.getvalue()
        self.accuracy_rate = 0
        self.total_signals = 0
        self.wma = bt.indicators.WeightedMovingAverage(self.data, period=self.params.wma_period)
        dick = self.dick = DICK(self.data)
        dick.plotinfo.subplot = False

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.datetime(0)
        print(f'{dt.isoformat()} {txt}')  # Print date and close

    def sizer(self):
        amount_to_invest = (self.params.risk * self.broker.cash)/self.params.stoploss
        size = self.size = round((amount_to_invest / self.datas[0].close), 3)
        return size

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status in [order.Completed]:
            if order.isbuy():
                self.executed_price = order.executed.price
                if self.position:
                    self.entry_price = self.executed_price
                    self.log(f'BUY EXECUTED : {round(self.entry_price, self.currency_format)}')
                else:
                    if self.profit_loss == "profit":
                        self.log(f'BUY EXECUTED : {round(order.executed.price, self.currency_format)}. PROFIT: {(self.broker.getvalue() - self.wallet):.2f} - {((self.broker.getvalue() - self.wallet)/self.starting_cash)*100:.2f}%')
                        self.log(f"Current Wallet : {self.broker.getvalue():.2f}")
                        self.accuracy_rate += 1
                        self.total_signals += 1
                        self.log(f"Accuracy Rate : {self.accuracy_rate}/{self.total_signals} - {(self.accuracy_rate/self.total_signals)*100:.2f}%")
                        print(f'========================================================================')
                    elif self.profit_loss == "loss":
                        self.log(f'BUY EXECUTED : {round(order.executed.price, self.currency_format)}. LOSS: {(self.broker.getvalue() - self.wallet):.2f} - {((self.broker.getvalue() - self.wallet)/self.starting_cash)*100:.2f}%')
                        self.log(f"Current Wallet : {self.broker.getvalue():.2f}")
                        self.total_signals += 1
                        self.log(f"Accuracy Rate : {self.accuracy_rate}/{self.total_signals} - {(self.accuracy_rate/self.total_signals)*100:.2f}%")
                        print(f'========================================================================')
            elif order.issell():
                self.executed_price = order.executed.price
                if self.position:
                    self.entry_price = order.executed.price
                    self.log(f'SELL EXECUTED : {round(order.executed.price, self.currency_format)}')
                else:
                    if self.profit_loss == "profit":
                        self.log(f'SELL EXECUTED : {round(order.executed.price, self.currency_format)}. PROFIT: {(self.broker.getvalue() - self.wallet):.2f} - {((self.broker.getvalue() - self.wallet)/self.starting_cash)*100:.2f}%')
                        self.log(f"Current Wallet : {self.broker.getvalue():.2f}")
                        self.accuracy_rate += 1
                        self.total_signals += 1
                        self.log(f"Accuracy Rate : {self.accuracy_rate}/{self.total_signals} - {(self.accuracy_rate/self.total_signals)*100:.2f}%")
                        print(f'========================================================================')
                    elif self.profit_loss == "loss":
                        self.log(f'SELL EXECUTED : {round(order.executed.price, self.currency_format)}. LOSS: {(self.broker.getvalue() - self.wallet):.2f} - {((self.broker.getvalue() - self.wallet)/self.starting_cash)*100:.2f}%')
                        self.log(f"Current Wallet : {self.broker.getvalue():.2f}")
                        self.total_signals += 1
                        self.log(f"Accuracy Rate : {self.accuracy_rate}/{self.total_signals} - {(self.accuracy_rate/self.total_signals)*100:.2f}%")
                        print(f'========================================================================')
            self.bar_executed = len(self)
        self.order = None

    def next(self):

        if not self.position:

            if (self.dataclose[0] > self.dick.lines.bbt) and (self.dataclose[0] > self.wma):
                amount_to_invest = (self.params.risk * self.broker.cash)/self.params.stoploss
                self.size = round((amount_to_invest / self.dataclose[0]), 3)
                # print(f'========================================================================')
                self.log(f"SIGNAL NOTICE: Buy {self.size:.2f} shares of {self.params.symbol} at {self.data.close[0]}")
                self.currency_format = str(self.data.close[0])[::-1].find('.')
                self.buy(exectype=bt.Order.Market, size=self.size)
                self.wallet = self.broker.getvalue()

            if self.params.short_positions:
                if (self.dataclose[0] < self.dick.lines.bbb) and (self.dataclose[0] < self.wma):
                    amount_to_invest = (self.params.risk * self.broker.cash)/self.params.stoploss
                    self.size = round((amount_to_invest / self.dataclose[0]), 3)
                    # print(f'========================================================================')
                    self.log(f"SIGNAL NOTICE: Sell {self.size:.2f} shares of {self.params.symbol} at {self.data.close[0]}")
                    self.currency_format = str(self.data.close[0])[::-1].find('.')
                    self.sell(exectype=bt.Order.Market, size=self.size)
                    self.wallet = self.broker.getvalue()

        else:
            if self.position.size > 0:
                if self.datahigh[0] >= self.executed_price * (1 + self.params.takeprofit):
                    # self.close()
                    self.sell(exectype=bt.Order.Limit, size=self.size, price=self.executed_price * (1 + self.params.takeprofit))
                    self.log(f'> CLOSE LONG position at {round(self.executed_price * (1 + self.params.takeprofit), self.currency_format)}')
                    self.profit_loss = "profit"
                if self.datalow[0] <= self.executed_price * (1 - self.params.stoploss):
                    self.close()
                    # self.sell(exectype=bt.Order.Market, size=self.size)
                    self.log(f'> CLOSE LONG position at {round(self.executed_price * (1 - self.params.stoploss), self.currency_format)}')
                    self.profit_loss = "loss"

            if self.params.short_positions:
                if self.position.size < 0:
                    if self.datalow[0] <= self.executed_price * (1 - self.params.takeprofit):
                        # self.close()
                        self.buy(exectype=bt.Order.Limit, size=self.size, price=self.executed_price * (1 - self.params.takeprofit))
                        self.log(f'> CLOSE SHORT position at {round(self.executed_price * (1 - self.params.takeprofit), self.currency_format)}')
                        self.profit_loss = "profit"
                    if self.datahigh[0] >= self.executed_price * (1 + self.params.stoploss):
                        self.close()
                        # self.buy(exectype=bt.Order.Market, size=self.size)
                        self.log(f'> CLOSE SHORT position at {round(self.executed_price * (1 + self.params.stoploss), self.currency_format)}')
                        self.profit_loss = "loss"

        # stopLoss
        # takeProfit (target)
        # number of singals
        # accuracy (takeProfit/num of signals)
        # net profit