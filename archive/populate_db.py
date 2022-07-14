from tqdm import tqdm
import os, json, sys, requests, time, calendar
import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime
from helpers import timestamp_to_datetime, CryptoCompare
import config

MINUTE_AGGREGATE = 5

if __name__ == '__main__':
            
    # TODO
    # enable max_existing_ts check
    
    client = CryptoCompare()
    
    # tickers = ['BTC','ETH']
    tickers = config.TICKERS

    start = time.time()
    dataframes_list = []
    for ticker in tqdm(tickers):
        print(f'Processing {ticker}')
        temp = client.get_ohlcv_minute(ticker,aggregate=MINUTE_AGGREGATE)
        dataframes_list.append(temp)
    consolidated_data = pd.concat(dataframes_list)
    print(f'Download took {time.time()-start}')
    
    print(consolidated_data.shape)
    print(consolidated_data.symbol.unique().tolist())
    
    # find dir path
    dir_path = os.path.dirname(os.path.realpath(__file__))
    
    # DB_FILE = dir_path + DB_NAME coming from config
    # db_file = '/home/takis/Desktop/sckool/my-crypto-app/assets.db'
    db_file = os.path.join(dir_path,config.DB_NAME)
    print(f'db_file:{db_file}')
    
    # connect to db & execute queries
    con = sqlite3.connect(db_file)
    cursor = con.cursor()
    for i,row in consolidated_data.iterrows():
        try:
            sql_insert_asset_table = 'INSERT INTO assets {} VALUES {}'.format(tuple(dict(row).keys()),tuple(dict(row).values()))
            cursor.execute(sql_insert_asset_table)
        except Exception as e:
            pass
    con.commit()
    con.close()