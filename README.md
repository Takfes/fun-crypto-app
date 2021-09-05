### How to run strategy
> python backtesting.py futures15 ETHUSDT dic 10000 0.5

### Strategy Options
1. futures15 : table name
2. ETHUSDT : pair
3. dic : strategy to test
4. 10000 : total budget
5. 0.5 : risk percentage (applied on total budget)

### Additional Strategy Parameters in 
> backtesting_strategies.py

### TODOs
1. optresults - output - analyzers - paraller execution
2. add writer to opt results
3. find out how to test multiple strategies on a single datafeed
4. find out how to test and optimize one strategy over multiple datafees