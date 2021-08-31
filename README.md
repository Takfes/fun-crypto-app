### How to run strategy
> python backtesting.py futures15 ETHUSDT dic 10000 0.5

### Strategy Options
* futures15 -> table name
* ETHUSDT -> pair
* dic -> strategy to test
> other options : 'ma','macd','bnh','stoc','triple','dip','bearx','dic','3h'
* 10000 -> total budget
* 0.5 -> risk percentage (applied on total budget)

### Additional Strategy Parameters in 
> backtesting_strategies.py

### TODO : 
- print(f"Buy {self.size} shares of {self.params.get('ticker')} at {self.data.close[0]}") -> self.executed_price should be shown instead of self.data.close[0]
- if self.dataclose[0] >= self.executed_price * (1 + self.params.get('takeprofit')) or self.dataclose[0] < self.executed_price * (1 + self.params.get('stoploss')):
  - this condition should be reconstructed to check if takeprofit/stoploss are between high and low, instead of comparison with self.dataclose[0]. Furthermore, for more accurate results we need to check if in the same candle it first satisfied the takeprofit or the stoploss price...