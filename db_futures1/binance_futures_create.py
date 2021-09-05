import os
import sqlite3
from sqlite3 import Error
from sqlite3.dbapi2 import connect
import config

sql_create_asset_table = """CREATE TABLE IF NOT EXISTS {} (	
                            symbol TEXT NOT NULL,
                            openTimets INTEGER NOT NULL,
                            closeTimets INTEGER NOT NULL,
                            openTime TEXT NOT NULL,
                            closeTime TEXT NOT NULL,
                            open REAL NOT NULL,
                            high REAL NOT NULL,
                            low REAL NOT NULL,
                            close REAL NOT NULL,
                            volume INTEGER NOT NULL,
                            numTrades INTEGER NOT NULL,
                            quoteAssetVolume REAL NOT NULL,
                            takerBuyBaseAssetVolume INTEGER NOT NULL,
                            takerBuyQuoteAssetVolume REAL NOT NULL,
                            UNIQUE(openTimets,symbol)
                        );""".format(config.DB_ASSET_TABLE_FUTURES_1)
                        
sql_create_asset_table_index = """CREATE INDEX {} ON {} (openTimets,symbol);""".format(config.DB_ASSET_TABLE_FUTURES_1_INDEX,config.DB_ASSET_TABLE_FUTURES_1)

if __name__ == '__main__':
    
    # find dir path
    dir_path = os.path.dirname(os.path.realpath(__file__))
    
    # DB_FILE = dir_path + DB_NAME coming from config
    # db_file = '/home/takis/Desktop/sckool/my-crypto-app/data/assets.db'
    db_file = os.path.join(dir_path,config.DB_NAME)
    print(f'db_file:{db_file}')
    
    # connect to db & execute queries
    con = sqlite3.connect(db_file)
    cursor = con.cursor()
    cursor.execute(sql_create_asset_table)
    cursor.execute(sql_create_asset_table_index)
    con.commit()
    con.close()