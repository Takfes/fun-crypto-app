### How to run strategy
> python backtesting.py futures1 ETHUSDT dic 10000 0.01

### Strategy Options
1. futures15 : table name
2. ETHUSDT : pair
3. dic : strategy to test
4. 10000 : total budget
5. 0.01 : risk percentage (applied on total budget)

### Additional Strategy Parameters in 
> backtesting_strategies.py

### Backtrader Links (end to start)
https://www.one-tab.com/page/Kb8lsK4LSqOzardwGMNAeg

### TODOs TAKIS
1. find out how to test multiple strategies on a single datafeed
2. start end dates as parameters
3. find out how to test multiple datafeeds
4. leverage as a parameter

### TODOs PREKS
1. stoploss risk leverage
   - In general you can use one of the 3 scenarios when entering a signal:
   - cash * (risk/stoploss)
   - starting cash * (risk/stoploss)
   - *That means that stoploss percentage should be bigger than risk percentage, otherwise you need to use leverage
2. arguments across strategies COIN, STRATEGY, (CASH, RISK)
3. consistency between arguments - stoploss vs risk input
   - You need to use leverage x10-x15 in order to avoid problems when risk percentage is almost equal to stoploss 
   percentage 
4. what can mits check