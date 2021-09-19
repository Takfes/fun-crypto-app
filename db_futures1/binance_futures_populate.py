from tqdm import tqdm
import os, time, sys
from pathlib import Path
import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime

sys.path.append('../')
import config

# define objects
TABLE_NAME = config.DB_ASSET_TABLE_FUTURES_1
ORIGIN_PATH = '..' / Path(config.DB_DIRECTORY)
DATABASE_PATH = '..' / Path(config.DB_DIRECTORY) / config.DB_NAME

if __name__ == '__main__':

    start_ttl = time.time()
    # dir_path = os.path.dirname(os.path.realpath(__file__))
    # db_file = os.path.join(dir_path, DB_NAME)
    print(f'db_file:{DATABASE_PATH}')

    # pickles = [x for x in os.listdir() if x.endswith('.pkl')]
    pickles = [x for x in os.listdir(ORIGIN_PATH) if x.endswith('.pkl')]

    con = sqlite3.connect(DATABASE_PATH)
    cursor = con.cursor()

    for pic in pickles:
        start = time.time()
        ttl_rows = 0
        pickle_path = ORIGIN_PATH / pic
        raw = pd.read_pickle(pickle_path)
        df = raw.copy()

        df["latest"] = df.groupby(["symbol"])["openTimets"].transform("max")
        df = df.query("openTimets != latest").drop("latest", axis = 1).assign(
                openTime = lambda x: x.openTime.astype(str),
                closeTime = lambda x: x.closeTime.astype(str))

        print(f'File read successfully {pic} with {df.shape[0]} rows')

        for i,row in tqdm(df.iterrows()):
            try:
                sql_insert_asset_table = 'INSERT INTO {} {} VALUES {}'.format(TABLE_NAME,tuple(dict(row).keys()),tuple(dict(row).values()))
                cursor.execute(sql_insert_asset_table)
                ttl_rows += 1
            except Exception as e:
                print(e)

        end = time.time()
        print(f'File {pic} inserted {ttl_rows} entries in {int(end - start)} seconds')
        con.commit()
    con.close()
    end_ttl = time.time()
    print(f'Total process lasted {int(end_ttl - start_ttl)} seconds')
