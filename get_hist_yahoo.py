import pandas as pd
import time
import json
import requests
import yfinance as yf
from yahoofinancials import YahooFinancials
from datetime import datetime, timedelta
import pandas_datareader as pdr
import pandas_datareader.data as web
import config
import helpers
import os

def get_stocks_list():
    stock_list_files = [x for x in os.listdir('./data') if x.startswith('nasdaq_screener_')]
    stock_symbols = pd.concat(pd.read_csv(os.path.join('./data',x)) for x in stock_list_files)
    return stock_symbols

# stock_symbols.Symbol.value_counts()
# stock_symbols.groupby(['Symbol']).size().sort_values()

def main():
    
    INTERVAL = '1d'
    OUTPUT_FILE_NAME = 'stocks.csv'
    TOP_X_STOCKS = 100
    
    timer_start = time.time()
    now = datetime.now()
    current_date = now.strftime("%Y-%m-%d")
    last_week_date = (now - timedelta(days=729)).strftime("%Y-%m-%d")
    # start = pd.to_datetime(last_week_date)
    # end = pd.to_datetime(current_date)
    start_date = '2010-01-01'

    stock_symbols = get_stocks_list()
    # tickers_list = ['TSLA', 'FB', 'MSFT']
    tickers_list = stock_symbols.sort_values(by=['Market Cap'],ascending=False).head(TOP_X_STOCKS).Symbol.tolist()
    # df = yf.download(tickers_list,start =last_week_date, interval=INTERVAL)
    df = yf.download(tickers_list,start =start_date, interval=INTERVAL)
    
    # process downloaded file ; wide to long
    final_df = df.stack().rename_axis(['datetime','symbol']).reset_index()
    final_df.columns = [x.lower().replace(" ","_") for x in final_df.columns]
    timer_end = time.time()
    final_df.to_csv(OUTPUT_FILE_NAME,index=False)
    
    final_df.groupby(['symbol'])['datetime'].min()
    
    # process info
    print()
    print(f'Process Summary :\n* number of stocks : {len(tickers_list)}\n* rows : {final_df.shape[0]}\n* interval : {INTERVAL}\n* from : {str(final_df.datetime.min())}\n* to : {str(final_df.datetime.max())}\n* time : {timer_end-timer_start}')
    print(f'Success Summary :\n* {final_df.symbol.nunique()}/{len(tickers_list)} or ({final_df.symbol.nunique()/len(tickers_list)*100}%)')
    print(f'file saved in the current directory : {OUTPUT_FILE_NAME}')
    
    return final_df

if __name__ == '__main__':
    df = main()