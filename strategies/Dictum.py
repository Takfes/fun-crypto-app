import math
import backtrader as bt
import numpy as np
import sys

debug = False

# TODO check quicknotify, cheat-on-open for entry and exit in the same bar
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
        ('multiplier', 3.0),
        ('leverage',10)
        )

    def __init__(self):

        self.params.printlog = True
        self.dataopen = self.datas[0].open
        self.dataclose = self.datas[0].close
        self.datalow = self.datas[0].low
        self.datahigh = self.datas[0].high
        self.starting_cash = self.broker.getvalue()
        self.accuracy_rate = 0
        self.total_signals = 0
        self.wma = bt.indicators.WeightedMovingAverage(self.data, period=self.params.wma_period)
        dick = self.dick = DICK(self.data)
        dick.plotinfo.subplot = False
        
    def log(self, txt, dt=None, doprint=False):
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.datetime(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def sizer(self):
        
        # TAKIS
        # amount_to_invest = (self.params.risk * self.broker.cash)
        # self.size = round((amount_to_invest / self.datas[0].close), 3)
        
        # PREKS
        amount_to_invest = (self.params.risk * self.starting_cash)/self.params.stoploss # ALMOST FIXED AMOUNT OF LOSS
        # amount_to_invest = (self.params.risk * self.broker.cash)/self.params.stoploss # AMOUNT OF LOSS CHANGES OVER TIME ACCORDING TO CURRENT CASH
        self.size = round((amount_to_invest / self.datas[0].close), 3)

    def notify_trade(self, trade):
            if not trade.isclosed:
                return
            self.log('(7) OPERATION PROFIT, GROSS %.2f, NET %.2f' %
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
                        self.accuracy_rate += 1
                        self.total_signals += 1
                        self.log(f"(6) ACCURACY RATE {self.accuracy_rate}/{self.total_signals} or {(self.accuracy_rate/self.total_signals)*100:.2f}%")
                    elif self.profit_loss == "loss":
                        self.log(f'(4) BUY EXECUTED : {order.executed.price}. LOSS: {self.broker.getvalue() - self.wallet}')
                        self.log(f"(5) CURRENT WALLET : {self.broker.getvalue()}")
                        self.total_signals += 1
                        self.log(f"(6) ACCURACY RATE {self.accuracy_rate}/{self.total_signals} or {(self.accuracy_rate/self.total_signals)*100:.2f}%")
            elif order.issell():
                self.executed_price = order.executed.price
                if self.position:
                    self.entry_price = order.executed.price
                    self.log(f'(2) SELL EXECUTED : {order.executed.price}')
                else:
                    if self.profit_loss == "profit":
                        self.log(f'(4) SELL EXECUTED : {order.executed.price}. PROFIT: {self.broker.getvalue() - self.wallet}')
                        self.log(f"(5) CURRENT WALLET : {self.broker.getvalue()}")
                        self.accuracy_rate += 1
                        self.total_signals += 1
                        self.log(f"(6) ACCURACY RATE {self.accuracy_rate}/{self.total_signals} or {(self.accuracy_rate/self.total_signals)*100:.2f}%")
                    elif self.profit_loss == "loss":
                        self.log(f'(4) SELL EXECUTED : {order.executed.price}. LOSS: {self.broker.getvalue() - self.wallet}')
                        self.log(f"(5) CURRENT WALLET : {self.broker.getvalue()}")
                        self.total_signals += 1
                        self.log(f"(6) ACCURACY RATE {self.accuracy_rate}/{self.total_signals} or {(self.accuracy_rate/self.total_signals)*100:.2f}%")
            self.bar_executed = len(self)
        self.order = None

    def next(self):

        if not self.position:

            # OPEN POSITIONS
            # OPEN LONG
            if (self.dataclose[0] > self.dick.lines.bbt) and (self.dataclose[0] > self.wma):
                self.sizer()
                self.log(f"(1) SIGNAL NOTICE: Buy {self.size} shares of {self.params.symbol} at {self.data.close[0]}")
                # self.buy(size=self.size)
                self.currency_format = str(self.data.close[0])[::-1].find('.')
                self.buy(exectype=bt.Order.Market, size=self.size)
                self.wallet = self.broker.getvalue()

            # OPEN SHORT
            if self.params.short_positions:
                if (self.dataclose[0] < self.dick.lines.bbb) and (self.dataclose[0] < self.wma):
                    self.sizer()
                    self.log(f"(1) SIGNAL NOTICE: Sell {self.size} shares of {self.params.symbol} at {self.data.close[0]}")
                    # self.sell(size=self.size)
                    self.currency_format = str(self.data.close[0])[::-1].find('.')
                    self.sell(exectype=bt.Order.Market, size=self.size)
                    self.wallet = self.broker.getvalue()

        else:
            # CLOSE POSITIONS
            # CLOSE LONG
            if self.position.size > 0:
                # TAKE PROFIT
                if self.datahigh[0] >= self.executed_price * (1 + self.params.takeprofit):
                    # self.close()
                    self.sell(exectype=bt.Order.Limit, size=self.size, price=self.executed_price * (1 + self.params.takeprofit))
                    self.log(f'(3) CLOSE LONG position at {self.executed_price * (1 + self.params.takeprofit)}')
                    self.profit_loss = "profit"
                # STOP LOSS
                if self.datalow[0] <= self.executed_price * (1 - self.params.stoploss):
                    self.close()
                    # self.sell(exectype=bt.Order.Market, size=self.size)
                    self.log(f'(3) CLOSE LONG position at {self.executed_price * (1 - self.params.stoploss)}')
                    self.profit_loss = "loss"

            # CLOSE SHORT
            if self.params.short_positions:
                if self.position.size < 0:
                    # TAKE PROFIT
                    if self.datalow[0] <= self.executed_price * (1 - self.params.takeprofit):
                        # self.close()
                        self.buy(exectype=bt.Order.Limit, size=self.size, price=self.executed_price * (1 - self.params.takeprofit))
                        self.log(f'(3) CLOSE SHORT position at {self.executed_price * (1 - self.params.takeprofit)}')
                        self.profit_loss = "profit"
                    # STOP LOSS
                    if self.datahigh[0] >= self.executed_price * (1 + self.params.stoploss):
                        self.close()
                        # self.buy(exectype=bt.Order.Market, size=self.size)
                        self.log(f'(3) CLOSE SHORT position at {self.executed_price * (1 + self.params.stoploss)}')
                        self.profit_loss = "loss"
    def stop(self):
            self.log(f'\n{50*"+"}\n')
            self.log(f'STOP RESULTS : \n\n* stoploss : {self.p.stoploss}\n* takeprofit : {self.p.takeprofit} \n* short_positions : {self.p.short_positions} {self.broker.getvalue()-self.starting_cash}', doprint=True)
            self.log(f'\n{50*"+"}\n')