import math
import backtrader as bt
import numpy as np
import sys

debug = False

class DICK(bt.Indicator):

    # global vwma_list, bbt_list, bbb_list
    # vwma_list = bbt_list = bbb_list = []

    lines = ('vwma','bbt','bbb')  # output lines (array)
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
        hlcp = (highp + lowp + closep)/3.0
        sumprodp = hlcp * volumep
        vwma = sum(sumprodp)/sum(volumep)
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

        if debug :
            print('> highp : ','\n',type(highp),'\n',highp,'\n')
            print('> lowp : ','\n',type(lowp),'\n',lowp,'\n')
            print('> closep : ','\n',type(closep),'\n',closep,'\n')
            print('> volumep : ','\n',type(volumep),'\n',volumep,'\n')
            print('> hlcp : ','\n',type(hlcp),'\n',hlcp,'\n')
            print('> sumprodp : ','\n',type(sumprodp),'\n',sumprodp,'\n')
            print('> vwma : ','\n',type(vwma),'\n',vwma,'\n')
            print('> std(hlcp) : ','\n',type(std),'\n',std,'\n')
            # print('> vwma_list) : ','\n',vwma_list,'\n')
            # print('> bbt_list) : ','\n',bbt_list,'\n')
            # print('> bbb_list) : ','\n',bbb_list,'\n')


class Dictum(bt.Strategy):
    
    params = (('risk',0.25),('ticker','ETH'),
              ('wma_period',300),('percentage_change',0.01),
              ('short',False))
        
    def __init__(self):

        self.dataclose = self.datas[0].close
        self.wma = bt.indicators.WeightedMovingAverage(self.data,period=self.p.wma_period)
        dick = self.dick = DICK(self.data)
        dick.plotinfo.subplot = False

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()} {txt}') #Print date and close
            
    def notify_order(self, order):
        # print("YOU ARE IN NOTIFY_ORDER")
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status in [order.Completed]:
            if order.isbuy():
                # self.log(f'BUY EXECUTED : {order.executed.price}')
                self.take_profit = order.executed.price
            elif order.issell():
                # self.log(f'SELL EXECUTED : {order.executed.price}')
                self.take_profit = order.executed.price
            self.bar_executed = len(self)
        self.order = None
                
    def next(self):
        
        if not self.position:

            if (self.dataclose[0] > self.dick.lines.bbt) and (self.dataclose[0] > self.wma):
                amount_to_invest = (self.params.risk * self.broker.cash)
                self.size = math.floor(amount_to_invest/self.dataclose[0])
                print(f'Buy {self.size} shares of {self.params.ticker} at {self.data.close[0]}')
                self.buy(size=self.size)
            
            if self.p.short:
                if (self.dataclose[0] < self.dick.lines.bbb) and (self.dataclose[0] < self.wma):
                    amount_to_invest = (self.params.risk * self.broker.cash)
                    self.size = math.floor(amount_to_invest/self.dataclose[0])
                    print(f'Sell {self.size} shares of {self.params.ticker} at {self.data.close[0]}')
                    self.sell(size=self.size)
            
        else:
            
            if self.position.size > 0:
                if self.dataclose[0] >= self.take_profit * (1 + self.p.percentage_change):
                    self.close()
                    print(f'> Close LONG position')#: {self.getposition()}')
            
            if self.p.short:
                if self.position.size < 0:
                    if self.dataclose[0] <= self.take_profit * (1 - self.p.percentage_change):
                        self.close()
                        print(f'> Close SHORT position')#: {self.getposition()}')

        # stopLoss
        # takeProfit (target)
        # number of singals
        # accuracy (takeProfit/num of signals)
        # net profit