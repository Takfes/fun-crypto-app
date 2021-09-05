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

### TODOs TAKIS
1. optresults - output - analyzers - paraller execution
2. add writer to opt results
3. find out how to test multiple strategies on a single datafeed
4. find out how to test and optimize one strategy over multiple datafees
5. resample

### TODOs PREKS
1. stoploss risk leverage
   - In general you can use one of the 3 scenarios when entering a signal:
     - cash * (risk/stoploss)*
     - starting cash * (risk/stoploss)*
     - cash**
     - *That means that stoploss percentage should be bigger than risk percentage, otherwise you need to use leverage
     - **That means that you enter with 100% of your cash every time, risking the stoploss percentage of your wallet 
     for every signal, that's why it's safe to use 1% risk if you don't use leverage
2. arguments between strategies - what is per strategy what is across strategies
   - The arguments per strategy are defined in backtesting settings
   - Across strategies we use cash and risk only
3. consistency between arguments - stoploss vs risk input
   - You need to use leverage x10-x15 in order to avoid problems when risk percentage is almost equal to stoploss 
   percentage 
4. cheat on close - quicknotify
   - Both seem to not have any effect currently :(
5. what can mits check