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
1. check why datasize period = 5000 breaks
### TODOs PREKS
1. extend params to search (stoploss, takeprofit), run for data period = 30.000 and measure time
2. TripleH strategy : enable funcitonalities similar to those of Dictum