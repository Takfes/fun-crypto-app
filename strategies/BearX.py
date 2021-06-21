import math
import backtrader as bt

class BearX(bt.Strategy):
    
    params = (('risk',0.25),('ticker','ETH'))
    
    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None
    
    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()} {txt}') #Print date and close
        
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED : {order.executed.price}')
            elif order.issell():
                self.log(f'SELL EXECUTED : {order.executed.price}')
            self.bar_executed = len(self)
        self.order = None
        
    def next(self):
        self.log('Close, %.4f' % self.datas[0].close[0])
        if not self.position:
            if self.dataclose[0] > self.dataclose[-1]:
                if self.dataclose[-1] > self.dataclose[-2]:
                    if self.dataclose[-2] > self.dataclose[-3]:
                        amount_to_invest = (self.params.risk * self.broker.cash)
                        self.size = math.floor(amount_to_invest/self.data.close)
                        self.log(f'SHORT CREATE for {self.params.ticker} @ {self.dataclose[0]}')
                        self.order = self.sell(size=self.size)
        else:
            if len(self) >= (self.bar_executed+5):
                self.log(f'CLOSE POSITION for {self.params.ticker} @ {self.dataclose[0]}')
                self.order = self.close()