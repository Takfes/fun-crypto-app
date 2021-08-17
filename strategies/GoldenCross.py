import math
import backtrader as bt

class GoldenCross(bt.Strategy):

    params = (('fast',50),('slow',200),('order_percentage',0.95),('ticker','ETH'))
        
    def __init__(self):
        
        self.fast_ma = bt.indicators.SMA(
            self.data.close,period=self.params.fast,plotname=f'{self.params.fast} moving average'
        )
        self.slow_ma = bt.indicators.SMA(
            self.data.close,period=self.params.slow,plotname=f'{self.params.slow} moving average'
        )
        self.crossover = bt.indicators.CrossOver(self.fast_ma,self.slow_ma)
                
    def next(self):
        
        if self.position.size == 0:
            if self.crossover > 0 :
                amount_to_invest = (self.params.order_percentage * self.broker.cash)
                # self.size = math.floor(amount_to_invest/self.data.close)
                self.size = round(amount_to_invest/self.data.close,0)
                # print(f'Buy {self.size} shares of {self.params.ticker} at {self.data.close[0]}')
                self.buy(size=self.size)
        
        if self.crossover < 0 :
            # print(f'Sell {self.size} shares of {self.params.ticker} at {self.data.close[0]}')
            self.close()