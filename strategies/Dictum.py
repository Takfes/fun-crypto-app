import math
import backtrader as bt

class Dictum(bt.Strategy):
    
    params = (('risk',0.25),('ticker','ETH'),('period',-20))
        
    def __init__(self):
        self.dataclose = self.datas[0].close
        self.bb = bt.indicators.BollingerBands(self.data,period=30)
        
    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()} {txt}') #Print date and close
            
    def notify_order(self, order):
        print("YOU ARE IN NOTIFY_ORDER")
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED : {order.executed.price}')
                self.take_profit = order.executed.price
            elif order.issell():
                self.log(f'SELL EXECUTED : {order.executed.price}')
                self.take_profit = order.executed.price
            self.bar_executed = len(self)
        self.order = None
                
    def next(self):
        self.log('Close, %.5f' % self.datas[0].close[0])
              
        if not self.position:
            if self.data.close < self.bb.lines.bot :
                amount_to_invest = (self.params.risk * self.broker.cash)
                # self.size = round(amount_to_invest/self.data.close,0)
                self.size = math.floor(amount_to_invest/self.dataclose[0])
                print(f'Buy {self.size} shares of {self.params.ticker} at {self.data.close[0]}')
                self.buy(size=self.size)
            
            # if self.data.close >= self.bb.lines.top:
            #     amount_to_invest = (self.params.risk * self.broker.cash)
            #     # self.size = round(amount_to_invest/self.data.close,0)
            #     self.size = math.floor(amount_to_invest/self.dataclose[0])
            #     print(f'Sell {self.size} shares of {self.params.ticker} at {self.data.close[0]}')
            #     self.sell(size=self.size)

        else:
            
            if self.data.close >= (self.bb.lines.top * 0.7):
                self.log(f'CLOSE POSITION for {self.params.ticker} @ {self.dataclose[0]}')
                self.order = self.close()
            # if self.data.close < (self.bb.lines.bot * 0.7):
            #     self.log(f'CLOSE POSITION for {self.params.ticker} @ {self.dataclose[0]}')
            #     self.order = self.close()