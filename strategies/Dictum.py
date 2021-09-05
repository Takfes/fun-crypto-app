import math
import backtrader as bt
import numpy as np
import sys

debug = False

# Custom Indicator

class DICK(bt.Indicator):

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


        if debug:
            print('> highp : ', '\n', type(highp), '\n', highp, '\n')
            print('> lowp : ', '\n', type(lowp), '\n', lowp, '\n')
            print('> closep : ', '\n', type(closep), '\n', closep, '\n')
            print('> volumep : ', '\n', type(volumep), '\n', volumep, '\n')
            print('> hlcp : ', '\n', type(hlcp), '\n', hlcp, '\n')
            print('> sumprodp : ', '\n', type(sumprodp), '\n', sumprodp, '\n')
            print('> vwma : ', '\n', type(vwma), '\n', vwma, '\n')
            print('> std(hlcp) : ', '\n', type(std), '\n', std, '\n')


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

        self.params.printlog = False
        self.dataopen = self.datas[0].open
        self.dataclose = self.datas[0].close
        self.datalow = self.datas[0].low
        self.datahigh = self.datas[0].high
        self.starting_cash = self.broker.getvalue()
        self.wma = bt.indicators.WeightedMovingAverage(self.data, period=self.params.wma_period)
        dick = self.dick = DICK(self.data)
        dick.plotinfo.subplot = False
        
    def log(self, txt, dt=None, doprint=False):
        ''' Logging function fot this strategy'''
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.datetime(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def sizer(self):
        amount_to_invest = (self.params.risk * self.broker.cash)
        self.size = round((amount_to_invest / self.datas[0].close), 3)

    def notify_trade(self, trade):
            if not trade.isclosed:
                return
            self.log('(6) OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                    (trade.pnl, trade.pnlcomm))
            self.log(f'{50*"-"}\n')

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status in [order.Completed]:
            if order.isbuy():
                self.executed_price = order.executed.price
                if self.position:
                    self.entry_price = self.executed_price
                    self.log(f'(2) BUY EXECUTED : {self.entry_price}')
                else:
                    if self.profit_loss == "profit":
                        self.log(f'(4) BUY EXECUTED : {order.executed.price}. PROFIT: {self.broker.getvalue() - self.wallet}')
                        self.log(f"(5) CURRENT WALLET : {self.broker.getvalue()}")
                    elif self.profit_loss == "loss":
                        self.log(f'(4) BUY EXECUTED : {order.executed.price}. LOSS: {self.broker.getvalue() - self.wallet}')
                        self.log(f"(5) CURRENT WALLET : {self.broker.getvalue()}")
            elif order.issell():
                self.executed_price = order.executed.price
                if self.position:
                    self.entry_price = order.executed.price
                    self.log(f'(2) SELL EXECUTED : {order.executed.price}')
                else:
                    if self.profit_loss == "profit":
                        self.log(f'(4) SELL EXECUTED : {order.executed.price}. PROFIT: {self.broker.getvalue() - self.wallet}')
                        self.log(f"(5) CURRENT WALLET : {self.broker.getvalue()}")
                    elif self.profit_loss == "loss":
                        self.log(f'(4) SELL EXECUTED : {order.executed.price}. LOSS: {self.broker.getvalue() - self.wallet}')
                        self.log(f"(5) CURRENT WALLET : {self.broker.getvalue()}")
            self.bar_executed = len(self)
        self.order = None

    def next(self):

        if not self.position:

            if (self.dataclose[0] > self.dick.lines.bbt) and (self.dataclose[0] > self.wma):
                amount_to_invest = (self.params.risk * self.broker.cash)
                self.size = round((amount_to_invest / self.dataclose[0]), 3)
                self.log(f"(1) SIGNAL NOTICE: Buy {self.size} shares of {self.params.symbol} at {self.data.close[0]}")
                self.buy(size=self.size)
                self.wallet = self.broker.getvalue()

            if self.params.short_positions:
                if (self.dataclose[0] < self.dick.lines.bbb) and (self.dataclose[0] < self.wma):
                    amount_to_invest = (self.params.risk * self.broker.cash)
                    self.size = round((amount_to_invest / self.dataclose[0]), 3)
                    self.log(f"(1) SIGNAL NOTICE: Sell {self.size} shares of {self.params.symbol} at {self.data.close[0]}")
                    self.sell(size=self.size)
                    self.wallet = self.broker.getvalue()

        else:
            if self.position.size > 0:
                if self.datahigh[0] >= self.executed_price * (1 + self.params.takeprofit):
                    self.close()
                    self.log(f'(3) CLOSE LONG position at {self.executed_price * (1 + self.params.takeprofit)}')
                    self.profit_loss = "profit"
                if self.datalow[0] <= self.executed_price * (1 - self.params.stoploss):
                    self.close()
                    self.log(f'(3) CLOSE LONG position at {self.executed_price * (1 - self.params.stoploss)}')
                    self.profit_loss = "loss"

            if self.params.short_positions:
                if self.position.size < 0:
                    if self.datalow[0] <= self.executed_price * (1 - self.params.takeprofit):
                        self.close()
                        self.log(f'(3) CLOSE SHORT position at {self.executed_price * (1 - self.params.takeprofit)}')
                        self.profit_loss = "profit"
                    if self.datahigh[0] >= self.executed_price * (1 + self.params.stoploss):
                        self.close()
                        self.log(f'(3) CLOSE SHORT position at {self.executed_price * (1 + self.params.stoploss)}')
                        self.profit_loss = "loss"
    def stop(self):
            self.log(f'OPTIMIZATION RESULTS : \n* stoploss : {self.p.stoploss}\n* takeprofit : {self.p.takeprofit} \n* short_positions : {self.p.short_positions} {self.broker.getvalue()-self.starting_cash}', doprint=True)