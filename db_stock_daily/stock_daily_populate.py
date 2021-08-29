from tqdm import tqdm
import logging
import os, json, sys, requests, time, calendar
import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime
from helpers import get_ccxt_data, get_sorted_crypto
import yfinance as yf
import config

# define constants
DB_NAME = config.DB_NAME
TABLE_NAME = config.DB_ASSET_TABLE_STOCK_DAILY
TICKERS = config.STOCKSXT
AGGREGATE = '1d'
START_DATE = '2010-01-01'

# logging setup
current_file_name = os.path.basename(__file__)
dir_path = os.path.dirname(os.path.realpath(__file__))
filename = os.path.join(dir_path,f'logs/{current_file_name}.log')
os.chdir(dir_path)
logging.basicConfig(filename=filename,level=logging.WARNING,
                    format='%(asctime)s:%(filename)s:%(message)s')

if __name__ == '__main__':
        
    # start timer
    timer_start = time.time()
    # download data
    df = yf.download(TICKERS,start =START_DATE, interval=AGGREGATE)
    # process downloaded file ; wide to long
    consolidated_data = df.stack().rename_axis(['datetime','symbol']).reset_index()
    consolidated_data.columns = [x.lower().replace(" ","_") for x in consolidated_data.columns]
    # reorder columns
    columns_reordered = ['datetime','symbol','open','high','low','close','adj_close','volume']
    consolidated_data = consolidated_data[columns_reordered]
    # change datetime column's datatype
    consolidated_data = consolidated_data.assign(datetime = lambda x: x.datetime.astype(str))
    # end timer
    timer_end = time.time()

    # find dir path
    dir_path = os.path.dirname(os.path.realpath(__file__))
    
    # DB_FILE = dir_path + DB_NAME coming from config
    db_file = '/home/takis/Desktop/sckool/my-crypto-app/assets.db'
    db_file = os.path.join(dir_path,DB_NAME)
    print(f'db_file:{db_file}')
    
    # connect to db & execute queries
    con = sqlite3.connect(db_file)
    cursor = con.cursor()
    ttl_rows = 0
    for i,row in consolidated_data.iterrows():
        try:
            sql_insert_asset_table = 'INSERT INTO {} {} VALUES {}'.format(TABLE_NAME,tuple(dict(row).keys()),tuple(dict(row).values()))
            cursor.execute(sql_insert_asset_table)
            ttl_rows += 1
        except Exception as e:
            pass
    con.commit()
    con.close()
    logging.warning(f'{ttl_rows} new entries')