import time
import pandas as pd
from tqdm import tqdm
from datetime import datetime
from binance_f import RequestClient
from binance_f.model import CandlestickInterval
from binance_f.base.printobject import PrintMix
from contextlib import contextmanager
import sys, os
import sqlite3
import pandas as pd

# Load files from parent directory
sys.path.append('../')
import config
import apikeys

@contextmanager
def suppress_stdout():
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:  
            yield
        finally:
            sys.stdout = old_stdout

def timestamp_to_datetime(x):
    return datetime.utcfromtimestamp(int(str(x)[:10])).strftime("%Y-%m-%d, %H:%M:%S")

def binance_candles_to_df(candledata,symbol):

    pr = [
        (
        x.open,x.high,x.low,x.close,x.volume
        ,x.openTime,x.closeTime,x.numTrades,x.quoteAssetVolume
        ,x.takerBuyBaseAssetVolume,x.takerBuyQuoteAssetVolume
        )
        for x in candledata
    ]

    df = pd.DataFrame(pr,columns=['open','high','low','close','volume',
                                'openTimets','closeTimets','numTrades','quoteAssetVolume',
                                'takerBuyBaseAssetVolume','takerBuyQuoteAssetVolume'])

    df['openTime'] = pd.to_datetime(df['openTimets'].apply(lambda x : timestamp_to_datetime(x)))
    df['closeTime'] = pd.to_datetime(df['closeTimets'].apply(lambda x : timestamp_to_datetime(x)))
    df['symbol'] = symbol

    column_select = ['symbol','openTimets','closeTimets','openTime','closeTime',\
        'open','high','low','close','volume','numTrades','quoteAssetVolume',\
            'takerBuyBaseAssetVolume','takerBuyQuoteAssetVolume'
            ]

    return df[column_select]

def get_maxts_per_symbol(db_file,verbose=True):
    start = time.time()
    try:
        con = sqlite3.connect(db_file)
    except Exception as e:
        print(e)
        print('Did not connect to the database')
        
    sql_query = '''
                SELECT symbol,MAX(closeTimets) maxclosetimets
                FROM futures1
                GROUP BY 1
                ORDER BY 1;
                '''
    print(f'Querying the db...')
    df = pd.read_sql(sql_query, con)
    end = time.time()
    if verbose:
        print(f'Took {end-start} to fetch data from the db')
    con.close()
    return df

if __name__=="__main__":
    
    # define objects
    db_file = '../'+config.DB_NAME
    INTERVAL = CandlestickInterval.MIN1
    bclient = RequestClient(api_key=apikeys.BINANCE_API_KEY, secret_key=apikeys.BINANCE_API_SECRET)
    dflist = []
    
    # connect to db and fetch data
    dbdata = get_maxts_per_symbol(db_file)
    
    # start request timer
    start = time.time()

    for sym in tqdm(dbdata.symbol.unique().tolist()):

        print(f'parsing : {sym}')
        
        end_time = None
        end_time_symbol = None
        while_condition = True
        max_existing_symbol_closetime = dbdata.query('symbol==@sym').maxclosetimets.squeeze()

        while while_condition:

            with suppress_stdout():
                if end_time:
                    results = bclient.get_candlestick_data(symbol=sym,interval=INTERVAL,endTime=end_time,limit=1000);
                else:
                    results = bclient.get_candlestick_data(symbol=sym,interval=INTERVAL,endTime=None,limit=1000);

            df = binance_candles_to_df(results,sym)
            end_time = df.openTimets.min()
            dflist.append(df)

            if not end_time_symbol:
                end_time_symbol = str(end_time) + sym
            else:
                if end_time_symbol != str(end_time) + sym:
                    if max_existing_symbol_closetime not in df.closeTimets.tolist():
                        end_time_symbol = str(end_time) + sym
                    else:
                        while_condition = False
                else:
                    while_condition = False

    end=time.time()

    dt = pd.concat(dflist,ignore_index=True)
    qq = dt.drop_duplicates(subset=['symbol','openTimets'])
    report = qq.groupby(['symbol'])['openTime'].agg(['size','min','max']).reset_index()
    filename = f'{datetime.now().strftime("%Y%m%d_%H%M%S")}_{qq.symbol.nunique()}'
    
    print(f'Process took {int(end-start)} seconds to download {len(dflist)} objects for a total of {qq.shape[0]} rows')
    qq.to_pickle(filename+'.pkl')
    report.to_csv(filename+'_report.csv',index=False)

