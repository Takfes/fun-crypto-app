import json, sys, requests, time, calendar, os
from datetime import datetime
import pandas as pd
import sqlite3
from sqlite3 import Error
from tqdm import tqdm
import ccxt
import time

def get_stocks_list():
    stock_list_files = [x for x in os.listdir('./data') if x.startswith('nasdaq_screener_')]
    stock_symbols = pd.concat(pd.read_csv(os.path.join('./data',x)) for x in stock_list_files)
    return stock_symbols

def get_sorted_crypto():
    urls = {
        'top_100_by_volume' : 'https://min-api.cryptocompare.com/data/top/totaltoptiervol?ascending=true&assetClass=all&extraParams=https:%2F%2Fwww.cryptocompare.com&limit=100&page=0&tsym=USD',
        'top_100_by_marketcap' : 'https://min-api.cryptocompare.com/data/top/mktcap?ascending=true&assetClass=all&extraParams=https:%2F%2Fwww.cryptocompare.com&limit=100&page=0&tsym=USD',
        'top_100_by_change' : 'https://min-api.cryptocompare.com/data/top/percent?ascending=true&assetClass=all&extraParams=https:%2F%2Fwww.cryptocompare.com&limit=100&page=0&tsym=USD'
    }
    df_list = []
    for k,v in urls.items():
        print(f'Fetching data : {k}')
        resp = requests.get(v).json().get('Data')        
        temp_list = tuple((x.get('CoinInfo').get('Name'),k) for x in resp)
        df_list.append(pd.DataFrame(temp_list,columns=['symbol','type']).reset_index())
    return pd.concat(df_list)

def resample_ohlcv(df,resample_period):
    
    # https://tcoil.info/aggregate-daily-ohlc-stock-price-data-to-weekly-python-and-pandas/
    # https://stackoverflow.com/questions/34597926/converting-daily-stock-data-to-weekly-based-via-pandas-in-python

    try :
        agg_dict = {
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'adj_close': 'last',
            'volume': 'sum'
            }
        
        adj_col_names = [x.lower().replace(" ","_") for x in df.columns]
        adj_col_names = [x for x in adj_col_names if x in agg_dict.keys()]
        df.columns = adj_col_names

        # resampled dataframe
        # 'W' means weekly aggregation
        r_df = df.resample('W').agg(agg_dict)

    except Exception as e:
        print(e)
        print(f'1.column names must be one of {agg_dict.keys()}')
        print(f'2.resample_period should be in accordance to : https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases')

def timestamp_to_datetime(x):
    return datetime.utcfromtimestamp(int(str(x)[:10])).strftime("%Y-%m-%d, %H:%M:%S")

def datetime_to_timestamp(x,local=False):
    from_timestamp_local = int(time.mktime(datetime.strptime(x, "%Y-%m-%d").timetuple()))
    from_timestamp_utc = calendar.timegm(time.strptime(x, "%Y-%m-%d"))
    return from_timestamp_local if local else from_timestamp_utc

def timestring_to_unix(timestring):
    # timestring = '2019-01-01 00:00:00'
    d = pd.to_datetime(timestring)
    unixtime = int(datetime.timestamp(d)*1000)
    return unixtime

def get_ccxt_data(exchange, pairs, timeframe):
    
    if not isinstance(pairs,list):
        raise Exception(f'Expected list type for pairs. Instead received {type(pairs)}')
    
    exchange_id = exchange
    exchange_class = getattr(ccxt, exchange_id)
    column_names = ['time','open','high','low','close','volume']
    reorder_columns = ['time','datetime','symbol','exchange','frequency','open','high','low','close','volume']
    list_pairs_df = []
    
    for pair in tqdm(pairs):
        # print(f'Now processing : {pair}')
        try:
            ohlc = exchange_class().fetch_ohlcv(pair+'/USDT',timeframe, limit=1000)
            df = pd.DataFrame(ohlc,columns=column_names).assign(
                datetime = lambda x : x.time.apply(timestamp_to_datetime),
                symbol = pair,
                exchange = exchange_id,
                frequency = timeframe
                )[reorder_columns]
            list_pairs_df.append(df)
        except Exception as e:
            print(e)
            print(f'failed to download data for {pair}')    
    
    return pd.concat(list_pairs_df) if list_pairs_df else []


class CryptoCompare:
    
    def __init__(self):
        self.exchanges_url = 'https://min-api.cryptocompare.com/data/exchanges/general'
        self.coins_url = 'https://min-api.cryptocompare.com/data/all/coinlist'
        self.tsym = 'USDT'
        self.limit = 2000
        self.exchange = 'Binance'
        self.aggregate = 1
 
    def get_exchanges(self):
        response = requests.get(self.exchanges_url)
        self.exchanges = pd.DataFrame(response.json().get('Data')).T.Name.unique().tolist()
        return self.exchanges
 
    def get_coins(self):
        response = requests.get(self.coins_url)
        self.coins = pd.DataFrame(response.json()['Data']).T
        return self.coins
    
    def _get_ohlcv_minute(self,fsym,tsym=None,limit=None,exchange=None,aggregate=None,toTs=None):
        """Function to retrieve minute data

        Args:
            fsym ([str]): [description]
            tsym ([str], optional): [description]. Defaults to None.
            limit ([int], optional): [description]. Defaults to None.
            exchange ([type], optional): [description]. Defaults to None.
            aggregate ([type], optional): [description]. Defaults to None.
            toTs ([type], optional): [description]. Defaults to None.

        Returns:
            [dataframe]: [returns data from a single request]
        """
        if tsym is None:
            tsym = self.tsym
        if limit is None:
            limit = self.limit
        if exchange is None:
            exchange = self.exchange
        if aggregate is None:
            aggregate = self.aggregate
        if toTs is None:
            toTs = calendar.timegm(time.gmtime())

        self.minute_url = f'https://min-api.cryptocompare.com/data/v2/histominute?fsym={fsym}&tsym={tsym}&limit={limit}&e={exchange}&aggregate={aggregate}&toTs={toTs}'
        
        try:
            response = requests.get(self.minute_url)
            # add datetime, symbol and exchange columns
            temp = pd.DataFrame(response.json().get('Data').get('Data')).\
            assign(
                datetime = lambda x : x.time.apply(timestamp_to_datetime),
                symbol = fsym,
                exchange = exchange
                )
            # select and reorder columns to output
            column_selection = ['datetime', 'time', 'symbol', 'exchange',
                                'open', 'high', 'low', 'close', 
                                'volumefrom', 'volumeto']
            return temp[column_selection]
        except Exception as e:
            pass
    
    def get_ohlcv_minute(self,fsym,tsym=None,limit=None,exchange=None,aggregate=None,toTs=None,max_existing_ts=None):
        """Function to retrieve consequtive minute dataframes;
        Builds on top of _get_ohlcv_minute ;
        wraps _get_ohlcv_minute in an iteration process

        Args:
            fsym ([type]): [description]
            tsym ([type], optional): [description]. Defaults to None.
            limit ([type], optional): [description]. Defaults to None.
            exchange ([type], optional): [description]. Defaults to None.
            aggregate ([type], optional): [description]. Defaults to None.
            toTs ([type], optional): [description]. Defaults to None.
            max_existing_ts ([type], optional): when this ts is found in the downloaded dataset, iteration stops. Defaults to None.

        Returns:
            [dataframe]: [returns concatenated data from a multiple request]
        """
        dataframes_list = []
        try:
            while True:
                temp = self._get_ohlcv_minute(fsym,tsym,limit,exchange,aggregate,toTs)
                if not isinstance(temp,pd.DataFrame):
                    break
                if temp.empty:
                    break
                toTs = temp.time.min() # use toTs to track min current timestamp which will be used for the next api call
                dataframes_list.append(temp)
                print(f'[{fsym}] {temp.shape[0]} rows, from {temp.datetime.min()} to {temp.datetime.max()}')
                if max_existing_ts: # if argument is provided
                    if max_existing_ts in temp.time.unique().tolist(): # if max existing ts was found in the downloaded data
                        break
        except Exception as e:
            print(f'iterations for {fsym} finished')
        finally:
            consolidated_data = pd.concat(dataframes_list).drop_duplicates(subset='time')
            return consolidated_data.query('time>@max_existing_ts') if max_existing_ts else consolidated_data
            
    def _get_ohlcv_day(self,fsym,tsym=None,limit=None,exchange=None,aggregate=None,toTs=None):
        """Function to retrieve minute data

        Args:
            fsym ([str]): [description]
            tsym ([str], optional): [description]. Defaults to None.
            limit ([int], optional): [description]. Defaults to None.
            exchange ([type], optional): [description]. Defaults to None.
            aggregate ([type], optional): [description]. Defaults to None.
            toTs ([type], optional): [description]. Defaults to None.

        Returns:
            [dataframe]: [returns data from a single request]
        """
        if tsym is None:
            tsym = self.tsym
        if limit is None:
            limit = self.limit
        if exchange is None:
            exchange = self.exchange
        if aggregate is None:
            aggregate = self.aggregate
        if toTs is None:
            toTs = calendar.timegm(time.gmtime())

        self.day_url = f'https://min-api.cryptocompare.com/data/v2/histoday?fsym={fsym}&tsym={tsym}&limit={limit}&e={exchange}&aggregate={aggregate}&toTs={toTs}'
        
        try:
            response = requests.get(self.day_url)
            # add datetime, symbol and exchange columns
            temp = pd.DataFrame(response.json().get('Data').get('Data')).\
            assign(
                datetime = lambda x : x.time.apply(timestamp_to_datetime),
                symbol = fsym,
                exchange = exchange
                )
            # select and reorder columns to output
            column_selection = ['datetime', 'time', 'symbol', 'exchange',
                                'open', 'high', 'low', 'close', 
                                'volumefrom', 'volumeto']
            return temp[column_selection]
        except Exception as e:
            pass
    
    def get_ohlcv_day(self,fsym,tsym=None,limit=None,exchange=None,aggregate=None,toTs=None,max_existing_ts=None):
        """Function to retrieve consequtive minute dataframes;
        Builds on top of _get_ohlcv_minute ;
        wraps _get_ohlcv_minute in an iteration process

        Args:
            fsym ([type]): [description]
            tsym ([type], optional): [description]. Defaults to None.
            limit ([type], optional): [description]. Defaults to None.
            exchange ([type], optional): [description]. Defaults to None.
            aggregate ([type], optional): [description]. Defaults to None.
            toTs ([type], optional): [description]. Defaults to None.
            max_existing_ts ([type], optional): when this ts is found in the downloaded dataset, iteration stops. Defaults to None.

        Returns:
            [dataframe]: [returns concatenated data from a multiple request]
        """
        dataframes_list = []
        try:
            while True:
                temp = self._get_ohlcv_day(fsym,tsym,limit,exchange,aggregate,toTs)
                if not isinstance(temp,pd.DataFrame):
                    break
                if temp.empty:
                    break
                toTs = temp.time.min() # use toTs to track min current timestamp which will be used for the next api call
                dataframes_list.append(temp)
                print(f'[{fsym}] {temp.shape[0]} rows, from {temp.datetime.min()} to {temp.datetime.max()}')
                if max_existing_ts: # if argument is provided
                    if max_existing_ts in temp.time.unique().tolist(): # if max existing ts was found in the downloaded data
                        break
        except Exception as e:
            print(f'iterations for {fsym} finished')
        finally:
            consolidated_data = pd.concat(dataframes_list).drop_duplicates(subset='time')
            return consolidated_data.query('time>@max_existing_ts') if max_existing_ts else consolidated_data
            
    
    