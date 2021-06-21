import math
import backtrader as bt

class TripleFoo(bt.Strategy):
    
    params = (('risk',0.25),('ticker','ETH'),('period',-20),('multiplier',1.15))
        
    def __init__(self):
        self.dataclose = self.datas[0].close
        self.stoc = bt.indicators.Stochastic(self.data)
        self.rsi = bt.indicators.RSI_SMA(self.data,upperband=50.0,lowerband=50.0)
        self.macd = bt.indicators.MACD(self.data)
        self.crossover = bt.indicators.CrossOver(self.macd.macd,self.macd.signal)
        self.atr = bt.indicators.ATR(self.data)
        
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
                self.take_profit = order.executed.price + self.params.multiplier * (order.executed.price - self.swing_low)
            elif order.issell():
                self.log(f'SELL EXECUTED : {order.executed.price}')
                self.take_profit = order.executed.price - self.params.multiplier * (self.swing_high - order.executed.price)
            self.bar_executed = len(self)
        self.order = None
                
    def next(self):
        self.log('Close, %.5f' % self.datas[0].close[0])
    
        self.swing_low = min([self.datas[0].close[x] for x in range(0,self.params.period,-1)])
        self.swing_high = max([self.datas[0].close[x] for x in range(0,self.params.period,-1)])
               
        if not self.position:
            if (self.stoc < 50) & (self.rsi > 50) & (self.macd.macd > self.macd.signal):
                amount_to_invest = (self.params.risk * self.broker.cash)
                # self.size = round(amount_to_invest/self.data.close,0)
                self.size = math.floor(amount_to_invest/self.dataclose[0])
                print(f'Buy {self.size} shares of {self.params.ticker} at {self.data.close[0]}')
                print(f'>>> Low : {self.swing_low} - High : {self.swing_high}')
                self.buy(size=self.size)
        else:
            
            if (self.datas[0].close[0] <= self.swing_low) | (self.datas[0].close[0] >= self.take_profit):
                self.log(f'CLOSE POSITION for {self.params.ticker} @ {self.dataclose[0]}')
                self.order = self.close()                
            
            # if len(self) >= (self.bar_executed+5):
            #     self.log(f'CLOSE POSITION for {self.params.ticker} @ {self.dataclose[0]}')
            #     self.order = self.close()