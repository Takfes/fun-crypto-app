from tqdm import tqdm
import os, time
import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime
import config

# define constants
DB_NAME = config.DB_NAME
TABLE_NAME = config.DB_ASSET_TABLE_FUTURES_15

if __name__ == '__main__':
    
    # load dataset 
    consolidated_data = pd.read_pickle('data/20210813_185853_111.pkl').assign(
            openTime = lambda x: x.openTime.astype(str),
            closeTime = lambda x: x.closeTime.astype(str))
    print(f'file read successfully {consolidated_data.shape[0]} rows')

    # find dir path
    dir_path = os.path.dirname(os.path.realpath(__file__))
    
    # DB_FILE = dir_path + DB_NAME coming from config
    # db_file = r'/Users/takis/Desktop/sckool/my-crypto-app/data/assets.db'
    db_file = os.path.join(dir_path,DB_NAME)
    print(f'db_file:{db_file}')
    
    # connect to db & execute queries
    con = sqlite3.connect(db_file)
    cursor = con.cursor()
    ttl_rows = 0
    start = time.time()
    for i,row in tqdm(consolidated_data.iterrows()):
        try:
            sql_insert_asset_table = 'INSERT INTO {} {} VALUES {}'.format(TABLE_NAME,tuple(dict(row).keys()),tuple(dict(row).values()))
            cursor.execute(sql_insert_asset_table)
            ttl_rows += 1
        except Exception as e:
            print(e)
    con.commit()
    con.close()
    end = time.time()
    print(f'Inserted {ttl_rows} entries in {int(end-start)} seconds')