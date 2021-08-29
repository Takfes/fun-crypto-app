from crypto_daily_create import DB_NAME
from tqdm import tqdm
import logging
import os, json, sys, requests, time, calendar
import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime
from helpers import get_ccxt_data, get_sorted_crypto
import config

# define constants
DB_NAME = config.DB_NAME
TABLE_NAME = config.DB_ASSET_TABLE_CRYPTO_DAILY
TICKERS = config.TICKERSXT
EXCHANGE = 'binance'
AGGREGATE = '1d'

# logging setup
current_file_name = os.path.basename(__file__)
dir_path = os.path.dirname(os.path.realpath(__file__))
filename = os.path.join(dir_path,f'logs/{current_file_name}.log')
os.chdir(dir_path)
logging.basicConfig(filename=filename,level=logging.WARNING,
                    format='%(asctime)s:%(filename)s:%(message)s')

if __name__ == '__main__':
    
    # download dataset 
    consolidated_data = get_ccxt_data(EXCHANGE,TICKERS,AGGREGATE)
    
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