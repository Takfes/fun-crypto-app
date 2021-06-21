import os
import time
import requests
import argparse
import sqlite3
import logging
import calendar
import pandas as pd
from tqdm import tqdm
from cryptowatch_client import Client
from datetime import datetime
import config

def timestamp_to_datetime(x):
    return datetime.utcfromtimestamp(int(str(x)[:10])).strftime("%Y-%m-%d, %H:%M:%S")

def datetime_to_timestamp(x,local=False):
    from_timestamp_local = int(time.mktime(datetime.strptime(x, "%Y-%m-%d").timetuple()))
    from_timestamp_utc = calendar.timegm(time.strptime(x, "%Y-%m-%d"))
    return from_timestamp_local if local else from_timestamp_utc

## Usage 
# x = '2015-01-01'
# datetime_to_timestamp(x,local=True)
    
if __name__ == "__main__":

    client = Client()
    dir(client)

    # Get Assets
    resp = client.get_assets()
    type(resp.json())
    resp.json().get('result')
    type(resp.json().get('result'))
    pd.DataFrame(resp.json().get('result')).query('symbol=="eth"')

    # Get Exchanges
    exchanges = client.get_exchanges() # GET /exchanges
    exchanges.json()

    # Indicative Periods
    periods = {
    '60': '1m',  # 1 Minute
    '180': '3m', # 3 Minutes
    '300': '5m',
    '900': '15m',
    '1800': '30m',
    '3600': '1h', # 1 Hour
    '7200': '2h',
    '14400': '4h',
    '21600': '6h',
    '43200': '12h',
    '86400': '1d', # 1 Day
    '259200': '3d',
    '604800': '1w', # 1 Week
    }

    # WAY A
    periods = '3600'
    resp = requests.get('https://api.cryptowat.ch/markets/bitfinex/btcusd/ohlc', params={
    'periods': periods})
    resp.json().keys()
    resp.json()['result']
    resp.json()['result']['3600']
    df = pd.DataFrame(resp.json()['result']['3600'],columns=['CloseTime', 'OpenPrice', 'HighPrice', 'LowPrice', 'ClosePrice', 'Volume', 'NA'])
    df.CloseTime.apply(timestamp_to_datetime).min()
    df.head()

    # WAY B
    url = f'https://api.cryptowat.ch/markets/binance/btcusdt/ohlc&after={after_date}&before={before_date}'
    resp = requests.get('https://api.cryptowat.ch/markets/binance/btcusdt/ohlc')
    resp.json()['result'].keys()

    for period in resp.json()['result'].keys():
        print(f'period{period}:{periods.get(period)}')
        _temp = pd.DataFrame(resp.json()['result'].get(period),columns=['CloseTime', 'OpenPrice', 'HighPrice', 'LowPrice', 'ClosePrice', 'Volume', 'NA']).\
            assign(CloseTimeR = lambda x : x.CloseTime.apply(lambda y:pd.to_datetime(y,unit='s')))
        print(_temp.CloseTimeR.min())
        print(_temp.CloseTimeR.max())
        print(_temp.shape)

    resp.json()['result']['900']

    # WAY C
    url = f'https://api.cryptowat.ch/markets/binance/btcusdt/ohlc?after={from_timestamp}'
    resp = requests.get(url)
    resp.json()['result'].keys()

    for period in resp.json()['result'].keys():
        print(f'period{period}:{periods.get(period)}')
        _temp = pd.DataFrame(resp.json()['result'].get(period),columns=['CloseTime', 'OpenPrice', 'HighPrice', 'LowPrice', 'ClosePrice', 'Volume', 'NA']).\
            assign(CloseTimeR = lambda x : x.CloseTime.apply(lambda y:pd.to_datetime(y,unit='s')))
        print(_temp.CloseTimeR.min())
        print(_temp.CloseTimeR.max())
        print(_temp.shape)

    # WAY D
    periods = '300'
    resp = requests.get(url,params={'periods': periods})
    resp.json().get('result').keys()
