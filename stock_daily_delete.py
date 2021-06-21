import os
import sqlite3
from sqlite3 import Error
from sqlite3.dbapi2 import connect
import config

DB_NAME = config.DB_NAME
TABLE_NAME = config.DB_ASSET_TABLE_STOCK_DAILY
INDEX_NAME = config.DB_ASSET_TABLE_STOCK_DAILY_INDEX

sql_drop_assets_table = """DROP TABLE IF EXISTS {};""".format(TABLE_NAME)
                        
sql_create_asset_table_index = """DROP INDEX IF EXISTS {};""".format(INDEX_NAME)

if __name__ == '__main__':
    
    # find dir path
    dir_path = os.path.dirname(os.path.realpath(__file__))
    
    # DB_FILE = dir_path + DB_NAME coming from config
    # db_file = '/home/takis/Desktop/sckool/my-crypto-app/assets.db'
    db_file = os.path.join(dir_path,config.DB_NAME)
    print(f'db_file:{db_file}')

    # connect to db & execute queries    
    con = sqlite3.connect(db_file)
    cursor = con.cursor()
    cursor.execute(sql_create_asset_table_index)
    cursor.execute(sql_drop_assets_table)
    con.commit()