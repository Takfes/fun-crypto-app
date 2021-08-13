import time
import config
import pandas as pd
from tqdm import tqdm
from datetime import datetime
from binance_f import RequestClient
from binance_f.model import CandlestickInterval
from binance_f.base.printobject import PrintMix

from contextlib import contextmanager
import sys, os

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

if __name__=="__main__":

    start = time.time()
    INTERVAL = CandlestickInterval.MIN15
    symbols = config.PREXTICKS
    bclient = RequestClient(api_key=config.BINANCE_API_KEY, secret_key=config.BINANCE_API_SECRET)
    dflist = []

    for sym in tqdm(symbols):

        print(f'parsing : {sym}')
        
        end_time = None
        end_time_symbol = None
        while_condition = True

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
                    end_time_symbol = str(end_time) + sym
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

    