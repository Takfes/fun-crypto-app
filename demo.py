from logging import raiseExceptions
from time import asctime
from binance_f.model.constant import CandlestickInterval
import pandas as pd
import json
import requests
import yfinance as yf
from yahoofinancials import YahooFinancials
import websocket
import finviz
from finviz.screener import Screener
from tradingview_ta import TA_Handler, Interval, Exchange
from datetime import datetime, timedelta
import pandas_datareader as pdr
import pandas_datareader.data as web
import ta
import talib
import mplfinance as mpf
import tulipy as ti
import ccxt
import config
from binance.client import Client
from config import *
import helpers
from tqdm import tqdm
import cryptocompare
from coinmarketcap import Market


# %% Custom Fibonacci Retracement Levels

# Custom Fibonacci Retracement Levels
fratios = [0.236,0.382,0.5,0.618,0.786]
minp, maxp = min(self.dataclose), max(self.dataclose)
rangep = maxp - minp
rangep_fratios = [rangep * r for r in fratios]

upward_trend_fib = [maxp - x for x in rangep_fratios]
upward_trend_fib.append(maxp)
upward_trend_fib.sort()
upward_trend_fib

downward_trend_fib = [minp + x for x in rangep_fratios]
downward_trend_fib.append(minp)
downward_trend_fib.sort()
downward_trend_fib

# %% https://www.cryptocompare.com/coins/list/all/USD/1 web page api

def get_sorted_crypto():
    urls = {
        'top_100_by_volume' : 'https://min-api.cryptocompare.com/data/top/totaltoptiervol?ascending=true&assetClass=all&extraParams=https:%2F%2Fwww.cryptocompare.com&limit=100&page=0&tsym=USD',
        'top_100_by_marketcap' : 'https://min-api.cryptocompare.com/data/top/mktcap?ascending=true&assetClass=all&extraParams=https:%2F%2Fwww.cryptocompare.com&limit=100&page=0&tsym=USD',
        'top_100_by_change' : 'https://min-api.cryptocompare.com/data/top/percent?ascending=true&assetClass=all&extraParams=https:%2F%2Fwww.cryptocompare.com&limit=100&page=0&tsym=USD'
    }
    df_list = []
    for k,v in urls.items():
        print(f'Fetching data : {k}')
        resp = requests.get(v).json().get('Data')        
        temp_list = tuple((x.get('CoinInfo').get('Name'),k) for x in resp)
        df_list.append(pd.DataFrame(temp_list,columns=['symbol','type']).reset_index())
    return pd.concat(df_list)

jj = get_sorted_crypto()
jj.head()
jj.tail()
jj.symbol.nunique()

jj.query('type!="top_100_by_change"').symbol.nunique()
jj.query('type=="top_100_by_marketcap"').symbol.nunique()
jj.query('type=="top_100_by_marketcap"').symbol.unique().tolist()


#%% coinmarketcap
coinmarketcap = Market()
coinmarketcap.ticker(start=0, limit=3, convert='EUR')

#%% cryptocompare package

jj = cryptocompare.get_coin_list(format=False)
type(jj)
jj.keys()
'MATIC' in jj.keys()
jj.get('MATIC')

tt = cryptocompare.get_historical_price_day('BTC', 'USDT', exchange='Binance')
pd.DataFrame(tt)


#%% CryptoCompare
from helpers import timestamp_to_datetime, CryptoCompare

url = 'https://min-api.cryptocompare.com/data/all/coinlist'
resp = requests.get(url)
type(resp.json())
resp.json().keys()
resp.json().get('Data')
pd.DataFrame(resp.json().get('Data'))

client = CryptoCompare()

df = client._get_ohlcv_day('BTC')
df.datetime.min()
df.shape

df = client.get_ohlcv_day('BTC')

dataframes_list = []
fsym = 'BTC'

while True:
    temp = client._get_ohlcv_day(fsym,toTs=toTs)
    if not isinstance(temp,pd.DataFrame):
        break
    if temp.empty:
        break
    toTs = temp.time.min() # use toTs to track min current timestamp which will be used for the next api call
    dataframes_list.append(temp)
    print(f'[{fsym}] {temp.shape[0]} rows, from {temp.datetime.min()} to {temp.datetime.max()}')
    
pd.concat(dataframes_list).datetime.min()


#%% binance api
client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)

dir(client)

client.get_asset_details()
client.get_account_snapshot(type='SPOT')
client.get_all_orders(symbol='VETUSDT')
client.get_my_trades(symbol='VETUSDT')
client.get_asset_balance(asset='DOT')

account_info = client.get_account()
account_info_balances = pd.DataFrame(account_info['balances'])
account_info_balances = account_info_balances.assign(free = lambda x : x.free.astype(float) )
account_info_active_asset = account_info_balances.query('free>0 and asset!="USDT"').asset.tolist()

account_hist_orders_list = []
for s in account_info_active_asset:
    sym = s + 'USDT'
    print(sym)
    current_order = client.get_all_orders(symbol=sym)
    current_order_df = pd.DataFrame(current_order)
    account_hist_orders_list.append(current_order_df)

account_hist_orders = pd.concat(account_hist_orders_list).reset_index(drop=True)

mycolumns = ['symbol','price','time','status']

account_hist_orders_cleaned = account_hist_orders[mycolumns].\
    assign(
        time = account_hist_orders.time.apply(helpers.timestamp_to_datetime)
    ).query('status != "CANCELED"').sort_values(by=['symbol','time'],ascending=[True,False]).reset_index(drop=True)

account_hist_orders_cleaned

all_tickers_data = pd.DataFrame(client.get_all_tickers())

orders_evaluation = account_hist_orders_cleaned.\
    merge(all_tickers_data,how='left',
          left_on='symbol',right_on='symbol',suffixes=('_bought', '_now')).\
              assign(
                  price_bought = lambda x : x.price_bought.astype(float),
                  price_now = lambda x : x.price_now.astype(float),
                  price_diff = lambda x : x.price_now - x.price_bought
                  )

orders_evaluation

#%% cctx
dir(ccxt)

timeframe = '15m'
pairs = config.TICKERS
gg = helpers.get_ccxt_data('binance', pairs[:3],'15m')
gg.shape


exchange_id = 'binance'
exchange_class = getattr(ccxt, exchange_id)
exchange_ = exchange_class({
    'apiKey': config.BINANCE_API_KEY,
    'secret': config.BINANCE_API_SECRET,
})


for x in dir(exchange_):
    if 'trades' in x.lower():
        print(x)

print(ccxt.exchanges) # print a list of all available exchange classes
exchange = ccxt.binance()

dir(exchange)
exchange.load_markets()
exchange.market('BTC/USDT')
exchange.fetchCurrencies()
exchange.quote_currencies
exchange.public_get_exchangeinfo()

dir(exchange_)
exchange_.fetch_balance()
exchange_.fetch_my_trades('DOT/USDT')
exchange

PAIR = 'DOT/USDT'
ticker = exchange.fetch_ticker(PAIR)

markets = exchange.load_markets()
list(markets.keys())
markets[PAIR]

crypto_usdt_pairs = [x for x in markets.keys() if x.endswith('/USDT')]
len(crypto_usdt_pairs)

PAIR = 'BTC/USDT'
TIMEFRAME = '1d'
column_names = ['time','open','high','low','close','volume']
# _since = int(datetime.timestamp(pd.to_datetime('2021-05-31')))

ohlc = exchange.fetch_ohlcv(PAIR,timeframe = TIMEFRAME, limit=2000)
df = pd.DataFrame(ohlc,columns=column_names).assign(datetime = lambda x : pd.to_datetime(x.time,unit='ms'))
df.shape
df.datetime.min()

df.shape
df.tail(20)
df.datetime.min() # Timestamp('2021-05-22 00:30:00')
df.datetime.max() # Timestamp('2021-06-01 10:15:00')

#%% mplfinance
# https://pypi.org/project/mplfinance/
mpf.plot(df.set_index('datetime').tail(100),type='candle')
mpf.plot(df.set_index('datetime').tail(50),type='candle',mav=(3,7,14,20))
mpf.plot(df.set_index('datetime').tail(50),type='candle',mav=(3,7,14,20),volume=True)


#%% ta
# ta library indicators
dfta = ta.add_all_ta_features(df, open="open", high="high", low="low", close="close", volume="volume")
# dfta.columns

# ta add indicators manuadfy
indicator_bb = BollingerBands(close=df["close"], window=20, window_dev=2)

dir(indicator_bb)
df['bb_bbh'] = indicator_bb.bollinger_hband()
df['bb_bbl'] = indicator_bb.bollinger_lband()
df['bb_bbm'] = indicator_bb.bollinger_mavg()


#%% yfinance

'''
-----------------------------------------------------------
interval=4h is not supported.
Valid intervals:
[1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo]
-----------------------------------------------------------
- BTC-USD: 1h data not available for 
startTime=1410908400 and endTime=1622246851. 
The requested range must be within the last 730 days.
-----------------------------------------------------------
'''

tsla = yf.download('TSLA', start='2019-01-01', progress=False)
tsla['Adj Close'].plot()

aapl = yf.download('AAPL', start='2015-01-01', progress=False)
aapl.index.min()


dir(yf)

ticker = yf.Ticker('ETH')
ticker.history(period="max")
dir(ticker)
ticker.sustainability
ticker.info
ticker.balancesheet
ticker.balance_sheet
ticker.financials

tickers_list = ['TSLA', 'FB', 'MSFT']
tickers = yf.download(tickers_list, start='2010-01-01', progress=False)
qq = tickers.stack().reset_index()
qq.Date.min()
qq.shape
qq.groupby(['level_1'])['Date'].min()
qq.groupby(['level_1'])['Date'].max()

data = yf.download('BTC-USD', start='2009-01-12')
data.head()
data.index.min()

now = datetime.now()
current_date = now.strftime("%Y-%m-%d")
last_week_date = (now - timedelta(days=729)).strftime("%Y-%m-%d")
start = pd.to_datetime(last_week_date)
end = pd.to_datetime(current_date)

df = yf.download('BTC-USD',interval="1h")
df = yf.download('BTC-USD',start =last_week_date, interval="1h")
df.shape
df.index.min(),df.index.max()

ticker.history(period="max",interval='1h',start =last_week_date)
# mpf.plot(df,type='candle',mav=(3,6,9),volume=True)

df2 = df.resample('5T').agg({'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'})  # to five-minute bar
df2.shape
mpf.plot(df2,type='candle',mav=(3,6,9),volume=True)

#%% pandas_datareader

f = web.DataReader(["USD/JPY", "BTC/CNY"], "av-forex")

now = datetime.now()
current_date = now.strftime("%Y-%m-%d")
last_year_date = (now - timedelta(days=365)).strftime("%Y-%m-%d")
last_year_date = (now - timedelta(days=365*13)).strftime("%Y-%m-%d")

start = pd.to_datetime(last_year_date)
end = pd.to_datetime(current_date)

CURRENCY = 'USD'
cryptocurrency = 'BTC'

data = pdr.get_data_yahoo(f'{cryptocurrency}-{CURRENCY}', start, end)

data.shape
data.columns
data.index.min()
data.head()

#%% FinViz
dir(finviz)

aapl = finviz.get_stock('AAPL')
finviz.get_all_news()
finviz.get_analyst_price_targets('MSFT')
ins = finviz.get_insider('TSLA')
pd.DataFrame(ins)

filters = ['exch_nasd', 'idx_sp500']  # Shows companies in NASDAQ which are in the S&P500
stock_list = Screener(filters=filters, table='Performance', order='price')  # Get the performance table and sort it by price ascending

dir(stock_list)
stock_list.data
stock_list.get_charts()

# Get chart from finviz
stock = 'AAPL'
stock_chart_url = f'https://finviz.com/chart.ashx?t={stock}&ty=c&ta=1&p=d&s=l'
stock_chart_url

crypto = 'ETHUSD'
crypto_chart_url = f'https://finviz.com/crypto_charts.ashx?t={crypto}&tf=d1'
crypto_chart_url


#%% TradingView
# https://python-tradingview-ta.readthedocs.io/en/latest/usage.html
dir(Interval)

# TSLA
tsla = TA_Handler(
    symbol="TSLA",
    screener="america",
    exchange="NASDAQ",
    interval=Interval.INTERVAL_1_DAY
)

tsla_analysis = tsla.get_analysis()
tsla_analysis.summary
tsla_analysis.indicators
tsla_analysis.oscillators
tsla_analysis.moving_averages

# MATICs
matic = TA_Handler(
    symbol="MATICUSDT",
    screener="crypto",
    exchange="binance",
    interval=Interval.INTERVAL_1_DAY
)

matic_analysis = matic.get_analysis()
dir(matic_analysis)
matic_analysis.summary
matic_analysis.indicators
matic_analysis.oscillators
matic_analysis.moving_averages

#%% yahoofinancials
ticker = 'AAPL'
yahoo_financials = YahooFinancials(ticker)

balance_sheet_data_qt = yahoo_financials.get_financial_stmts('quarterly', 'balance')
income_statement_data_qt = yahoo_financials.get_financial_stmts('quarterly', 'income')
all_statement_data_qt = yahoo_financials.get_financial_stmts('quarterly', ['income', 'cash', 'balance'])
apple_earnings_data = yahoo_financials.get_stock_earnings_data()
apple_net_income = yahoo_financials.get_net_income()
historical_stock_prices = yahoo_financials.get_historical_price_data('2008-09-15', '2018-09-15', 'weekly')

cryptocurrencies = ['BTC-USD', 'ETH-USD', 'XRP-USD']
yahoo_financials_cryptocurrencies = YahooFinancials(cryptocurrencies)
yahoo_financials_cryptocurrencies.get_stock_price_data()
daily_crypto_prices = yahoo_financials_cryptocurrencies.get_historical_price_data('2008-09-15', '2018-09-15', 'daily')

#%% websocket

# https://www.youtube.com/watch?v=z2ePTq-KTzQ
# https://pypi.org/project/websocket-client/

sy = 'btcusd'
interval = '1m'
socket = f'wss://stream.binance.com:9443/ws/{sy}t@kline_{interval}'

def on_message(ws, message):
    print(message)

def on_close(ws):
    print("### closed ###")

ws = websocket.WebSocketApp(socket,on_close = on_close,on_message = on_message)

ws.run_forever()

#%% crypto
resp = requests.get('https://api.cryptowat.ch/exchanges')
resp.content
resp.json()