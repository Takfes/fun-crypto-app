import os
import sqlite3
from sqlite3 import Error
from sqlite3.dbapi2 import connect
import config
# from helpers import create_connection

DB_NAME = config.DB_NAME
TABLE_NAME = config.DB_ASSET_TABLE_CRYPTO_DAILY
INDEX_NAME = config.DB_ASSET_TABLE_CRYPTO_DAILY_INDEX

sql_create_asset_table = """CREATE TABLE IF NOT EXISTS {} (	
                            time TEXT NOT NULL,
                            datetime TEXT NOT NULL,
                            symbol TEXT NOT NULL,
                            exchange TEXT NOT NULL,
                            frequency TEXT NOT NULL,
                            open REAL NOT NULL,
                            high REAL NOT NULL,
                            low REAL NOT NULL,
                            close REAL NOT NULL,
                            volume REAL NOT NULL,
                            UNIQUE(time,symbol,exchange)
                        );""".format(TABLE_NAME)
                        
sql_create_asset_table_index = """CREATE INDEX {} ON {} (time,symbol);""".format(INDEX_NAME,TABLE_NAME)

if __name__ == '__main__':
    
    # find dir path
    dir_path = os.path.dirname(os.path.realpath(__file__))
    
    # DB_FILE = dir_path + DB_NAME coming from config
    # db_file = '/home/takis/Desktop/sckool/my-crypto-app/assets.db'
    db_file = os.path.join(dir_path,DB_NAME)
    print(f'db_file:{db_file}')
    
    # connect to db & execute queries
    con = sqlite3.connect(db_file)
    cursor = con.cursor()
    cursor.execute(sql_create_asset_table)
    cursor.execute(sql_create_asset_table_index)
    con.commit()
    con.close()