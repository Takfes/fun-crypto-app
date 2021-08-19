import math
import backtrader as bt

class Stochastic(bt.Strategy):
    
    params = (('order_percentage',0.1),('ticker','ETH'))
        
    def __init__(self):
        self.stoc = bt.indicators.Stochastic(self.data)
       
    def next(self):
        
        # if not self.position:
        if self.stoc < 30 :
            amount_to_invest = (self.params.order_percentage * self.broker.cash)
            # self.size = round(amount_to_invest/self.data.close,0)
            self.size = math.floor(amount_to_invest/self.data.close)
            print(f'Buy {self.size} shares of {self.params.ticker} at {self.data.close[0]}')
            self.buy(size=self.size)
        
        if self.stoc > 70 :
            print(f'Sell {self.size} shares of {self.params.ticker} at {self.data.close[0]}')
            self.close()