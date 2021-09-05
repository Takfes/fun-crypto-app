import math
import backtrader as bt
from backtrader.indicators.pivotpoint import PivotPoint
import numpy as np
import sys

debug = False

class PAT(bt.Indicator):

    # global vwma_list, bbt_list, bbb_list
    # vwma_list = bbt_list = bbb_list = []

    # lines = ('pp',)  # output lines (array)
    lines = ('ph','pl')  # output lines (array)
    # lines = ('ph','pl','r1','r2','pp','s1','s2')  # output lines (array)
    params = (
        ('pivot_period', 24),
    )

    def __init__(self):
        # indicate min period ; i.e. buffering period
        self.buffering_period = (self.p.pivot_period * 2) + 1
        self.addminperiod(self.buffering_period)

    def next(self):

        # calculate pivot points
        highp = np.array(self.data.high.get(size=self.buffering_period))
        lowp = np.array(self.data.low.get(size=self.buffering_period))
        closep = np.array(self.data.close.get(size=self.buffering_period))

        high = np.mean(highp)
        low = np.mean(lowp)
        close = np.mean(closep)
        hlc = (high+low+close)/3.0

        self.lines.ph[0] = ph = np.max(highp)
        self.lines.pl[0] = pl = np.min(lowp)
        
        # self.lines.r1[0] = r1 = (hlc * 2) - low
        # self.lines.r2[0] = r2 = hlc + (high - low)
        # self.lines.s1[0] = s1 = (hlc * 2) - high
        # self.lines.s2[0] = s2 = hlc - (high - low)
        # self.lines.pp[0] = pp = hlc

        if debug :
            pass
            # print('> highp : ','\n',type(highp),'\n',highp,'\n')
            # print('> lowp : ','\n',type(lowp),'\n',lowp,'\n')
            # print('> closep : ','\n',type(closep),'\n',closep,'\n')
            # print('> hlcp : ','\n',type(hlcp),'\n',hlcp,'\n')

            # print('> high : ','\n',type(high),'\n',high,'\n')
            # print('> low : ','\n',type(low),'\n',low,'\n')
            # print('> close : ','\n',type(close),'\n',close,'\n')
            # print('> hlcp : ','\n',type(hlc),'\n',hlc,'\n')
            
            # print('> r1 : ','\n',type(r1),'\n',r1,'\n')
            # print('> r2 : ','\n',type(r2),'\n',r2,'\n')
            # print('> s1 : ','\n',type(s1),'\n',s1,'\n')
            # print('> s2 : ','\n',type(s2),'\n',s2,'\n')
            # print('> pp : ','\n',type(pp),'\n',pp,'\n')

            # print('> ph : ','\n',type(ph),'\n',ph,'\n')
            # print('> pl : ','\n',type(pl),'\n',pl,'\n')
            


class TripleH(bt.Strategy):
    
    params = (('symbol', 'unknown'),
              ('cash', 1000),
              ('risk', 0.25),
              ('factor', 6.5),
              ('atr_period', 170),
              ('pivot_period', 24),
              ('stoploss', 0.01),
              ('takeprofit', 0.01),
              ('short_positions', 0))
        
    def __init__(self):

        self.dataclose = self.datas[0].close
        self.ATR = bt.indicators.ATR(self.data, period=self.p.atr_period)a
        # pat = self.pat = PAT(self.data)
        # pat.plotinfo.subplot = False


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
        print(self.ATR)
        print(dir(self.ATR))
        print(self.ATR * 1)
        print(self.ATR * self.p.factor)
        print(50*'=')
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