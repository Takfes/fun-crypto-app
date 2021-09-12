import math
import backtrader as bt
from backtrader.indicators.pivotpoint import PivotPoint
import numpy as np

debug = True

class PAT(bt.Indicator):

    lines = ('ph','pl')
    
    plotinfo = dict(plot=True, subplot=False, plotlinelabels=True)
    plotlines = dict(
        ph=dict(marker='$\u21E9$', markersize=6.0, color='green', fillstyle='full', ls=''),
        pl=dict(marker='$\u21E7$', markersize=6.0, color='red', fillstyle='full', ls='')
        )
    params = (
        ('barplot', False),  # plot above/below max/min for clarity in bar plot
        ('bardist', 0.055),  # distance to max/min in absolute perc
    )
    
    params = (
        ('atr_period', 170),
        ('pivot_period', 3),
        ('factor', 6.5),
        ('printlog',True)
    )

    def __init__(self):
        # indicate min period ; i.e. buffering period
        self.buffering_period = (self.p.pivot_period * 2) + 1
        self.addminperiod(self.buffering_period)
        self.ATR = bt.indicators.ATR(self.data, period=self.p.atr_period)

        self.center = 0
        self.lastpp = 0
        self.tup = 0
        self.tdn = 0
        self.trend = 1
        self.ph = self.pl = 0
        
    def log(self, txt, dt=None, doprint=False):
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.datetime(0)
            print('%s, %s' % (dt.isoformat(), txt))
        
    def next(self):

        # grab necessary info
        highp = np.array(self.data.high.get(size=self.buffering_period))
        lowp = np.array(self.data.low.get(size=self.buffering_period))
        closep = np.array(self.data.close.get(size=self.buffering_period))
        
        # get highest high or lowest low position
        highest_bar_position = highp.argmax()
        lowest_bar_position = lowp.argmin()
        
        # check for pivot high
        if highest_bar_position == 0:
            self.lines.ph[-(self.buffering_period)] = self.ph = np.max(highp)
            self.lastpp = np.max(highp)

        # check for pivot low
        if lowest_bar_position == 0:
            self.lines.pl[-(self.buffering_period)] = self.pl = np.min(lowp)
            self.lastpp = np.min(lowp)
        
        if self.lastpp != 0:
            
            # calculate center
            if self.center == 0:
                self.center = self.lastpp
            else:
                self.center = (self.center * 2 + self.lastpp)/3
            
            # calculate up and down
            self.up = self.center - (self.p.factor * self.ATR[0])
            self.dn = self.center + (self.p.factor * self.ATR[0])
            
            # calculate trend up
            if closep[-1] > self.tup:
                self.tup = max(self.tup,self.up)
            else:
                self.tup = self.up

            # calculate trend down
            if closep[-1] < self.tdn:
                self.tup = min(self.tdn,self.dn)
            else:
                self.tdn = self.dn

            # calculate trend
            if closep[0] > self.tdn:
                self.trend = 1
            elif closep[0] < self.tup:
                self.trend = -1
                
            # calculate trailing stoploss
            if self.trend == 1:
                self.tsl = self.tup
            else:
                self.tsl = self.tdn

        if debug :
            self.log(f'length : {len(self.datas[0])}')
            self.log(f'highp : {highp[0]}')
            self.log(highp)
            self.log(f'highest_bar_position : {highest_bar_position}')
            self.log(f'> ph : {self.ph}')
            self.log(f'> pl : {self.pl}')
            self.log(50*'=')
class TripleH(bt.Strategy):
    
    params = (('symbol', 'unknown'),
              ('cash', 1000),
              ('risk', 0.25),
              ('stoploss', 0.01),
              ('takeprofit', 0.01),
              ('short_positions', 0),
              ('atr_period', 170),
              ('pivot_period', 3),
              ('factor', 6.5),
              ('printlog',False),
              )
        
    def __init__(self):
        self.dataclose = self.datas[0].close
        self.ATR = bt.indicators.ATR(self.data, period=self.p.atr_period)
        pat = self.pat = PAT(self.data, atr_period = self.p.atr_period, pivot_period = self.p.pivot_period, factor = self.p.factor)
        pat.plotinfo.subplot = False

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        # print(f'{dt.isoformat()} {txt}') #Print date and close
            
    # def notify_order(self, order):
    #     # print("YOU ARE IN NOTIFY_ORDER")
    #     if order.status in [order.Submitted, order.Accepted]:
    #         return
    #     if order.status in [order.Completed]:
    #         if order.isbuy():
    #             # self.log(f'BUY EXECUTED : {order.executed.price}')
    #             self.take_profit = order.executed.price
    #         elif order.issell():
    #             # self.log(f'SELL EXECUTED : {order.executed.price}')
    #             self.take_profit = order.executed.price
    #         self.bar_executed = len(self)
    #     self.order = None
                
    def next(self):
        pass
        # print(len(self.data))
        
        # if not self.position:

        #     if (self.dataclose[0] > self.dick.lines.bbt) and (self.dataclose[0] > self.wma):
        #         amount_to_invest = (self.params.risk * self.broker.cash)
        #         self.size = math.floor(amount_to_invest/self.dataclose[0])
        #         print(f'Buy {self.size} shares of {self.params.symbol} at {self.data.close[0]}')
        #         self.buy(size=self.size)
            
        #     if self.p.short:
        #         if (self.dataclose[0] < self.dick.lines.bbb) and (self.dataclose[0] < self.wma):
        #             amount_to_invest = (self.params.risk * self.broker.cash)
        #             self.size = math.floor(amount_to_invest/self.dataclose[0])
        #             print(f'Sell {self.size} shares of {self.params.symbol} at {self.data.close[0]}')
        #             self.sell(size=self.size)
            
        # else:
            
        #     if self.position.size > 0:
        #         if self.dataclose[0] >= self.take_profit * (1 + self.p.percentage_change):
        #             self.close()
        #             print(f'> Close LONG position')#: {self.getposition()}')
            
        #     if self.p.short:
        #         if self.position.size < 0:
        #             if self.dataclose[0] <= self.take_profit * (1 - self.p.percentage_change):
        #                 self.close()
        #                 print(f'> Close SHORT position')#: {self.getposition()}')

        # stopLoss
        # takeProfit (target)
        # number of singals
        # accuracy (takeProfit/num of signals)
        # net profit