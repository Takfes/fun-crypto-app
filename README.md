TODO :

* scetch streamlit app.py
* enable hourly and daily requests
* enable requests to get historical stock price
* test patterns & ta indicators for different resampling frequencies
* work around resampling for entire dataframe
* enable trading view indicator gauges across different time frames
* code different strategies
* test with backtrader
* add indicator_flag(s) for ta columns
* check ta indicator signals ; consider correlation/granger?
* plot buy sell signal in candle plots 
* portfolio optimization script
* rethink db design to hold different granularity leves of data
* setup cronjob
* enable max_existing_ts in populate_db.py

NOTES : 

* type(cerebro.datas)
* cerebro.datas[0]
* dir(cerebro.datas[0])
* cerebro.datas[0].datafields

* oscillators vs trend
* rsi vs stochastic
* parabolic sar
* supertrend
* aligator
* ichimoku
* fibonacci retracement indicator
* atr
* chandelier stop
* overbought vs oversold indicator

RESOURCES :

* [get list of all stocks](https://www.nasdaq.com/market-activity/stocks/screener?exchange=amex&letter=0&render=download)
* https://www.youtube.com/watch?v=nSw96qUbK9o
* https://medium.com/@u.praneel.nihar/building-multi-page-web-app-using-streamlit-7a40d55fa5b4
* https://www.youtube.com/watch?v=510G39RXuPE