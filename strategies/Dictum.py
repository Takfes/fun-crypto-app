import math
import backtrader as bt
import numpy as np
import sys

debug = False

# Custom Indicator

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

# Strategy

class Dictum(bt.Strategy):
    
    # params = (
    #     ('ticker','unknown'),
    #     ('cash',1000),
    #     ('risk',0.1),
    #     ('wma_period',300),
    #     ('stoploss',0.01),
    #     ('takeprofit',0.01),
    #     ('short_positions',0),
    #     ('period', 110),
    #     ('factor', 0.618),
    #     ('multiplier', 3.0)
    #     )
        
    def __init__(self, params):

        self.params = params
        print('>> Dictum Strategy Params :')
        for k,v in self.params.items():
            print(f'{k} : {v}')
        print()
        self.dataclose = self.datas[0].close
        self.wma = bt.indicators.WeightedMovingAverage(self.data,period=self.params.get('wma_period'))
        dick = self.dick = DICK(self.data)
        dick.plotinfo.subplot = False
        
    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()} {txt}') #Print date and close
            
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status in [order.Completed]:
            if order.isbuy():
                # self.log(f'BUY EXECUTED : {order.executed.price}')
                self.executed_price = order.executed.price
            elif order.issell():
                # self.log(f'SELL EXECUTED : {order.executed.price}')
                self.executed_price = order.executed.price
            self.bar_executed = len(self)
        self.order = None
                
    def next(self):
        
        if not self.position:

            if (self.dataclose[0] > self.dick.lines.bbt) and (self.dataclose[0] > self.wma):
                amount_to_invest = (self.params.get('risk') * self.broker.cash)
                self.size = math.floor(amount_to_invest/self.dataclose[0])
                print(f"Buy {self.size} shares of {self.params.get('ticker')} at {self.data.close[0]}")
                self.buy(size=self.size)
            
            if self.params.get('short_positions'):
                if (self.dataclose[0] < self.dick.lines.bbb) and (self.dataclose[0] < self.wma):
                    amount_to_invest = (self.params.get('risk') * self.broker.cash)
                    self.size = math.floor(amount_to_invest/self.dataclose[0])
                    print(f"Sell {self.size} shares of {self.params.get('ticker')} at {self.data.close[0]}")
                    self.sell(size=self.size)
            
        else:
            
            if self.position.size > 0:
                if self.dataclose[0] >= self.executed_price * (1 + self.params.get('takeprofit')) or self.dataclose[0] < self.executed_price * (1 + self.params.get('stoploss')):
                    self.close()
                    print(f'> Close LONG position at {self.data.close[0]}')
                    diff = self.data.close[0] - self.executed_price
                    if diff > 0:
                        print(f'Profit!')
                    else:
                        print(f'Loss!')

            if self.params.get('short_positions'):
                if self.position.size < 0:
                    if self.dataclose[0] <= self.executed_price * (1 - self.params.get('stoploss')) or self.dataclose[0] > self.executed_price * (1 - self.params.get('takeprofit')):
                        self.close()
                        diff = self.data.close[0] - self.executed_price
                        if diff < 0:
                            print(f'Profit!')
                        else:
                            print(f'Loss!')

        # stopLoss
        # takeProfit (target)
        # number of singals
        # accuracy (takeProfit/num of signals)
        # net profit