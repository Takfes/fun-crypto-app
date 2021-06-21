import os
import time
import requests
import argparse
import sqlite3
import logging
import pandas as pd
from tqdm import tqdm
from datetime import datetime
from binance.client import Client
from config import *

def timestamp_to_datetime(x):
    return datetime.utcfromtimestamp(int(str(x)[:10])).strftime("%Y-%m-%d, %H:%M:%S")

def get_historical_data(tickers,start_period):
    
    # binance klines column names
    colnames = [
        'OpenTime','Open','High','Low','Close','Volume','CloseTime','QuoteAssetvolume',
        'NoTrades','BaseAssetVolume','BuyAssetVolume','Ignore'
        ]

    # list to hold downloaded data
    list_hist_data = []

    for ticker in tqdm(tickers):    

        start = time.time()
        klines = client.get_historical_klines(ticker, Client.KLINE_INTERVAL_30MINUTE, start_period)
        end = time.time()
        print(f'Data for {ticker} took {end-start}\n')

        df = pd.DataFrame(klines,columns=colnames).\
            assign(
                OpenTime = lambda x: x.OpenTime.apply(lambda y : timestamp_to_datetime(y)),
                CloseTime = lambda x: x.CloseTime.apply(lambda y : timestamp_to_datetime(y)),
                Symbol = ticker
                )
        
        list_hist_data.append(df)
    
    return pd.concat(list_hist_data)  
        
if __name__ == "__main__":

    # Instantiate Binance Client
    client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)

    # Define Constants
    DB_NAME = 'assets.db'
    SAFETY_DAYS = 1
    con = sqlite3.connect(DB_NAME)

    # Handle db
    if DB_NAME in os.listdir():
        query = "SELECT Symbol, MAX(OpenTime) as OpenTime FROM stocks GROUP BY Symbol;"
        metadata = pd.read_sql(query,con)
        MAX_DB_DATE = metadata.OpenTime.min()    
        UPDATE_FROM = ( pd.to_datetime(MAX_DB_DATE) - pd.DateOffset(SAFETY_DAYS)).strftime('%d %B, %Y')
    else :
        UDPATE_FROM = '1 Jan, 2010'

    # Tickers of Interest
    tickers = ['BTCUSDT','ETHUSDT','XRPUSDT','DOGEUSDT','DOTUSDT','LTCUSDT','ADAUSDT','VETUSDT','MATICUSDT']
    
    # Get Data
    df = get_historical_data(tickers,UDPATE_FROM)
    
    # MAX_COMMON_OPENTIME = df.groupby(['OpenTime']).size().sort_index()[df.groupby(['OpenTime']).size()==df.groupby(['OpenTime']).size().max()].index[-1]
    # df = df.query("OpenTime <= @MAX_COMMON_OPENTIME").copy()
    
    df.to_sql('stocks',con, if_exists='append')

    df.sample(100)
    df.dtypes
    
    # # QA section
    # df.OpenTime.min(),df.OpenTime.max()
    # df.CloseTime.min(),df.CloseTime.max()
    # df.Symbol.unique()
    # df.groupby(['Symbol']).size()
    # df.groupby(['CloseTime']).size()
    
    # for ticker in tickers:
    #     _from = df.query('Symbol==@ticker').OpenTime.min()
    #     _to = df.query('Symbol==@ticker').OpenTime.max()
    #     print(f'{ticker} {_from}-{_to}')
    #     # print(50*"=")
        
    # query = '''SELECT COUNT(*) FROM stocks;'''
    # query = '''SELECT symbol,COUNT(*) FROM stocks GROUP BY symbol;'''
    