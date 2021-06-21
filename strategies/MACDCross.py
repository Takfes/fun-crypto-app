import backtrader as bt

class MACDCross(bt.Strategy):
    
    params = (('order_percentage',0.95),('ticker','ETH'))
    
    def __init__(self):
        
        # self.macd = bt.talib.MACD(self.data, plotname='TA_MACD')
        # self.talibmacdhist = bt.indicators.MACDHisto(self.data)
        self.macd = bt.indicators.MACD(self.data)
        self.crossover = bt.indicators.CrossOver(self.macd.macd,self.macd.signal)
        
    def next(self):
        
        if self.position.size == 0:
            if self.crossover > 0 :
                amount_to_invest = (self.params.order_percentage * self.broker.cash)
                # self.size = math.floor(amount_to_invest/self.data.close)
                self.size = round(amount_to_invest/self.data.close,0)
                print(f'Buy {self.size} shares of {self.params.ticker} at {self.data.close[0]}')
                self.buy(size=self.size)
        
        if self.crossover < 0 :
            print(f'Sell {self.size} shares of {self.params.ticker} at {self.data.close[0]}')
            self.close()
        