

# TODO :
# fix more accurate signals
#
# add kpi combinination of the following two
# add kpi logged close value to denote returns i.e. pct change ; macd pct change
# add kpi multiple level of lags (for close time, and kpis) and emas
#
# join dataframes of the same frequency from multiple stocks to see if this can benefit prediction ; rename columns with prefix
# use granger causality analysis to determine if a symbol-series is carries predictive info for another series
# examine correlation between series
#
# explore optimal portfolio strategy
# sharp ratio etc.

# hammers (inverted hammers) :
# idanika no shadow sth mia pleyra
# to allo shadow einai 2 fores to close - open
# future direction is determined based on the color of the candle

# doji's :
# open & close very close

# ichimoku
# conversion-line : minor support or resistance
# base-line : confirmation line - trailing support level
# lagging span :
# kumo cloud : span A - span B

# ==============================================
# LIBRARIES
# ==============================================

import os, time
os.chdir(r'C:\Users\Takis\Google Drive\_projects_\cryptocurrency\cryptowat-api')

from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

desired_width=320
pd.set_option('display.width', desired_width)
pd.set_option('display.max_columns',10)

# visualization libraries
import plotly.graph_objs as go
from plotly.offline import plot
from plotly import tools

# technical analysis libraries
import ta
from pyti.smoothed_moving_average import smoothed_moving_average as sma

# API to download cryptocurrency ohlc
from cryptowatch_client import Client

# enable emailing capabilities

# ==============================================
# DECLARATIONS
# ==============================================

def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            print(f'FUNCTION : {method.__name__} took {(te - ts) * 1000} to run')
        return result
    return timed

class CWClient:

    def __init__(self, exchange='binance'):

        self.client = Client(timeout=30)

        self.exchange = exchange
        self.colnames = ['CloseTime', 'Open', 'High', 'Low', 'Close', 'Volume', 'QuoteVolume']

        self.params = {'rsi_low' : 30,
                       'rsi_high' : 70}

        self.frequency_dict = {
            '1m': 60,
            '3m': 180,
            '5m': 300,
            '15m': 900,
            '30m': 1800,
            '1h': 3600,
            '2h': 7200,
            '4h': 14400,
            '6h': 21600,
            '12h': 43200,
            '1d': 86400,
            '3d': 259200,
            '1w': 604800
        }

    @property
    def get_exchanges(self):
        aa = self.client.get_exchanges().json()
        return pd.DataFrame(aa.get('result'))

    @property
    def get_markets(self):
        bb = self.client.get_markets().json()
        return pd.DataFrame(bb.get('result'))

    def _frequency(self, frequency):
        self.freq_int = self.frequency_dict.get(frequency)
        self.freq_str = frequency

    @property
    def get_frequencies(self):
        for s,i in self.frequency_dict.items():
            print(f'{s} :: {i} seconds')

    @property
    def summary(self):
        print(f'EXCHANGE::{self.exchange}-SYMBOL::{self.symbol}')

    @timeit
    def pull_data(self, symbol):
        self.symbol = symbol
        self.data = self.client.get_markets_ohlc(exchange=self.exchange, pair=symbol).json()
        print(f'DATA FETCH SUCCESSFUL')
        self.summary

    @timeit
    def resample(self, frequency):
        self._frequency(frequency)
        self.dataframe = pd.DataFrame(self.data.get('result').get(str(self.freq_int)), columns=self.colnames)

    @property
    @timeit
    def add_features(self):

        df = self.dataframe

        df['OpenDateTime'] = df['CloseTime'].apply(lambda x: datetime.fromtimestamp(x - self.freq_int))
        df['CloseDateTime'] = df['CloseTime'].apply(lambda x: datetime.fromtimestamp(x))
        df['Meta'] = f"{self.exchange}_{self.symbol}_{str(self.freq_str)}"

        # expontential moving averages
        df['ema_08'] = df.Close.ewm(span=8, adjust=False).mean()
        df['ema_13'] = df.Close.ewm(span=13, adjust=False).mean()
        df['ema_21'] = df.Close.ewm(span=21, adjust=False).mean()
        df['ema_55'] = df.Close.ewm(span=55, adjust=False).mean()

        # rsi limits
        df['rsi_'+str(self.params['rsi_low'])] = self.params['rsi_low']
        df['rsi_'+str(self.params['rsi_high'])] = self.params['rsi_high']

        # tudor - basic indicators
        df['fast_sma'] = sma(df['Close'].tolist(), 10)
        df['slow_sma'] = sma(df['Close'].tolist(), 30)

        # bukosabino - ta
        df = ta.add_all_ta_features(df, open="Open", high="High", low="Low", close="Close", volume="Volume")

        # ichimoku
        # Tenkan-sen (Conversion Line): (9-period high + 9-period low)/2))
        df['ichi_period20_high'] = df['Close'].rolling(window=20).max()
        df['ichi_period20_low'] = df['Close'].rolling(window=20).min()
        df['ichi_tenkan_sen'] = (df['ichi_period20_high'] + df['ichi_period20_low']) / 2

        # Kijun-sen (Base Line): (26-period high + 26-period low)/2))
        df['ichi_period60_high'] = df['Close'].rolling(window=60).max()
        df['ichi_period60_low'] = df['Close'].rolling(window=60).min()
        df['ichi_kijun_sen'] = (df['ichi_period60_high'] + df['ichi_period60_low']) / 2

        # Senkou Span A (Leading Span A): (Conversion Line + Base Line)/2))
        df['ichi_senkou_span_a'] = ((df['ichi_tenkan_sen'] + df['ichi_kijun_sen']) / 2).shift(60)

        # Senkou Span B (Leading Span B): (52-period high + 52-period low)/2))
        df['ichi_period120_high'] = df['Close'].rolling(window=120).max()
        df['ichi_period120_low'] = df['Close'].rolling(window=120).min()
        df['ichi_senkou_span_b'] = ((df['ichi_period120_high'] + df['ichi_period120_low']) / 2).shift(60)

        # The most current closing price plotted 22 time periods behind (optional)
        df['ichi_chikou_span'] = df.Close.shift(-30)  # 22 according to investopedia

        # fill nas
        df.fillna(0, inplace=True)

        self.dataframe = df

    @property
    @timeit
    def add_signals(self):

        df = self.dataframe

        # EMA INDICATORS
        df['buy_ema']  = df[['ema_08', 'ema_55']].apply(lambda x: 1 if x['ema_08'] >= 1.05 * x['ema_55'] and x['ema_08'] <= 1.3 * x['ema_55'] else 0, axis = 1)
        df['sell_ema'] = df[['ema_08', 'ema_55']].apply(lambda x: 1 if x['ema_55'] >= 1.05 * x['ema_08'] and x['ema_55'] <= 1.3 * x['ema_08'] else 0, axis = 1)

        # RSI
        df['buy_rsi'] = df['momentum_rsi'].apply(lambda x: 1 if x >= 25 and x <= 40 else 0)
        df['sell_rsi'] = df['momentum_rsi'].apply(lambda x: 1 if x >= 70 and x <= 85  else 0)

        # BB
        df['buy_bb'] = df[['Close', 'volatility_bbl']].apply(lambda x: 1 if x['Close'] <= 1.2 * x['volatility_bbl'] else 0 , axis=1)
        df['sell_bb'] = df[['Close', 'volatility_bbh']].apply(lambda x: 1 if x['volatility_bbh'] <= 1.2 * x['Close']else 0, axis=1)

        # MACD
        df['buy_macd'] = df[['trend_macd', 'trend_macd_signal']].apply(lambda x: 1 if x['trend_macd'] > x['trend_macd_signal'] else 0, axis=1)
        df['sell_macd'] = df[['trend_macd', 'trend_macd_signal']].apply(lambda x: 1 if x['trend_macd_signal'] / x['trend_macd'] else 0, axis=1)

        # ichimoku indicator
        df['buy_ichi'] = df[['ichi_tenkan_sen', 'ichi_kijun_sen', 'Close', 'Open', 'ichi_senkou_span_a', 'ichi_senkou_span_b']].apply(lambda x: 1 if (x['ichi_tenkan_sen'] > x['ichi_kijun_sen']) and (min(x['Close'], x['Open']) > max(x['ichi_senkou_span_b'], x['ichi_senkou_span_a'])) else 0, axis=1)
        df['sell_ichi'] = df[['ichi_tenkan_sen', 'ichi_kijun_sen', 'Close', 'Open', 'ichi_senkou_span_a', 'ichi_senkou_span_b']].apply(lambda x: 1 if (x['ichi_tenkan_sen'] < x['ichi_kijun_sen']) and (max(x['Close'], x['Open']) < min(x['ichi_senkou_span_b'], x['ichi_senkou_span_a'])) else 0, axis=1)

        # count signals
        df['buy_signals'] = df['buy_ema'] + df['buy_rsi'] + df['buy_bb'] + df['buy_macd'] + df['buy_ichi']
        df['sell_signals'] = df['sell_ema'] + df['sell_rsi'] + df['sell_bb'] + df['sell_macd'] + df['sell_ichi']


        self.dataframe = df

    def make_dataframe(self, frequency):
        self.resample(frequency)
        self.add_features
        self.add_signals

        return self.dataframe

    @timeit
    def write_output(self, specs, save_csv = False):

        symbolslist = specs['symbolslist']
        timeframes = specs['timeframes']

        columns_selection = ['CloseTime', 'Open', 'High', 'Low', 'Close',
                             'Volume', 'QuoteVolume', 'OpenDateTime', 'CloseDateTime',
                             'Meta', 'ema_08', 'ema_13', 'ema_21', 'ema_55', 'rsi_30', 'rsi_70',
                             'volatility_bbm', 'volatility_bbh', 'volatility_bbl',
                             'trend_macd', 'trend_macd_signal', 'momentum_rsi',

                             # 'ichi_period9_high', 'ichi_period9_low', 'ichi_tenkan_sen',
                             # 'ichi_period26_high', 'ichi_period26_low',
                             # 'ichi_kijun_sen',
                             # 'ichi_senkou_span_a',
                             # 'ichi_period52_high', 'ichi_period52_low', 'ichi_senkou_span_b',
                             # 'ichi_chikou_span',

                             'buy_ema','sell_ema',
                             'buy_rsi','sell_rsi',
                             'buy_bb','sell_bb',
                             'buy_macd','sell_macd',
                             # 'buy_ichi','sell_ichi'
                             'buy_signals','sell_signals'
                             ]

        start = time.time()
        df_list = []
        for ticker in symbolslist:
            ee.pull_data(ticker)

            for f in timeframes:
                temp = ee.make_dataframe(f)
                filename = f'csvdata/{ee.exchange}_{ee.symbol}_{ee.freq_str}_{datetime.now().strftime("%Y_%m_%d_%H_%M_%S")}.csv'
                # temp.to_csv(filename, index=False)
                df_list.append(temp)

        df = pd.concat(df_list)

        if save_csv:
            df[columns_selection].sort_values(by=['Meta', 'CloseTime'], ascending=False).to_csv('csvdata/total.csv',index=False)

        self.analysis = df

        end = time.time()

        print(f'Duration : {end-start}')
        print(f'Output : {filename}')

    def seek_tips(self, last_frames=2, min_signals=2, output = False):

        cols = ['Meta', 'CloseTime',
                'OpenDateTime', 'CloseDateTime',
                'buy_signals', 'sell_signals']

        group_obj = self.analysis[cols].sort_values(by=['Meta', 'CloseTime'], ascending=False).groupby('Meta')

        meta_list = []
        data_list = []

        for group, data in group_obj:
            temp = data.head(last_frames)
            if temp.sell_signals.max() > min_signals or temp.buy_signals.max() > min_signals:
                meta_list.append(group)
                data_list.append(temp)

        self.tips, self.tipsdata = meta_list, pd.concat(data_list)

        if output:
            return self.tips, self.tipsdata

    def send_email(self, user, pwd, recipients, subject = ''):

        try:
            df_html = self.tipsdata.to_html()
            dfPart = MIMEText(df_html, 'html')

            msg = MIMEMultipart('alternative')

            subj = subject + ",".join(self.tips)

            msg['Subject'] = subj
            msg['From'] = user

            # if isinstance(recipients, list):
            #     recs = ",".join(recipients)
            # elif isinstance(recipients, str):
            #     recs = recipients



            msg.attach(dfPart)

            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(user, pwd)

            if isinstance(recipients, list):
                for recs in recipients:
                    msg['To'] = recs
                    server.sendmail(user, recs, msg.as_string())
                    print(f'Email was sent to {recs}!')
            elif isinstance(recipients, str):
                recs = recipients
                msg['To'] = recs
                server.sendmail(user, recs, msg.as_string())
                print(f'Email was sent to {recs}!')

            server.close()



        except Exception as e:
            print(str(e))
            print('Failed to sent the email')

    def plot(self):
        self.pull_data()
        ll = self.df

        candle = go.Candlestick(
            x=ll['OpenDateTime'],
            open=ll['Open'],
            close=ll['Close'],
            high=ll['High'],
            low=ll['Low'],
            name="Candlesticks")

        close = go.Scatter(
            x=ll['OpenDateTime'],
            y=ll['Close'],
            name="Close",
            line=dict(color=('rgba(255, 20, 20, 50)')))

        # plot EMA 8/13/21/55
        ema08 = go.Scatter(
            x=ll['OpenDateTime'],
            y=ll['ema_08'],
            name="ema08",
            line=dict(color=('rgba(48, 23, 208, 50)')))

        ema13 = go.Scatter(
            x=ll['OpenDateTime'],
            y=ll['ema_13'],
            name="ema13",
            line=dict(color=('rgba(25, 215, 65, 50)')))

        ema21 = go.Scatter(
            x=ll['OpenDateTime'],
            y=ll['ema_21'],
            name="ema21",
            line=dict(color=('rgba(218, 223, 276, 50)')))

        ema55 = go.Scatter(
            x=ll['OpenDateTime'],
            y=ll['ema_55'],
            name="ema55",
            line=dict(color=('rgba(149, 62, 44, 50)')))

        # plot MAs
        fsma = go.Scatter(
            x=ll['OpenDateTime'],
            y=ll['fast_sma'],
            name="Fast SMA",
            line=dict(color=('rgba(102, 207, 255, 50)')))

        ssma = go.Scatter(
            x=ll['OpenDateTime'],
            y=ll['slow_sma'],
            name="Slow SMA",
            line=dict(color=('rgba(255, 207, 102, 50)')))

        # plot BB
        bbh = go.Scatter(
            x=ll['OpenDateTime'],
            y=ll['volatility_bbh'],
            name="volatility_bbh",
            line=dict(color=('rgba(21, 162, 117, 50)'),width=1,dash='dash'))

        bbm = go.Scatter(
            x=ll['OpenDateTime'],
            y=ll['volatility_bbm'],
            name="volatility_bbm",
            line=dict(color=('rgba(207, 21, 80, 50)'),width=1))

        bbl = go.Scatter(
            x=ll['OpenDateTime'],
            y=ll['volatility_bbl'],
            name="volatility_bbl",
            line=dict(color=('rgba(21, 162, 117, 50)'),width=1,dash='dash'))

        # plot RSI
        rsi = go.Scatter(
            x=ll['OpenDateTime'],
            y=ll['momentum_rsi'],
            name="momentum_rsi",
            line=dict(color=('rgba(146, 17, 141, 50)')))

        rsi_30 = go.Scatter(
            x=ll['OpenDateTime'],
            y=pd.Series([30 for x in range(ll.shape[0])]),
            name="momentum_rsi_30",
            line=dict(color=('rgba(146, 17, 141, 50)'),width=0.5, dash='dash'))

        rsi_70 = go.Scatter(
            x=ll['OpenDateTime'],
            y=pd.Series([70 for x in range(ll.shape[0])]),
            name="momentum_rsi_70",
            line=dict(color=('rgba(146, 17, 141, 50)'),width=0.5, dash='dash'))

        # plot MACD
        trend_macd = go.Scatter(
            x=ll['OpenDateTime'],
            y=ll['trend_macd'],
            name="trend_macd",
            line=dict(color=('rgba(15, 100, 203, 50)')))

        trend_macd_signal = go.Scatter(
            x=ll['OpenDateTime'],
            y=ll['trend_macd_signal'],
            name="trend_macd_signal",
            line=dict(color=('rgba(239, 164, 51, 50)')))

        trend_macd_diff = go.Scatter(
            x=ll['OpenDateTime'],
            y=ll['trend_macd_diff'],
            name="trend_macd_diff",
            line=dict(color=('rgba(239, 145, 30, 50)')))


        fig = tools.make_subplots(rows = 4,
                                  cols = 1,
                                  subplot_titles = ('ticker','rsi', 'macd'),
                                  shared_xaxes = True)

        fig.append_trace(candle, 1, 1)

        fig.append_trace(bbh, 1, 1)
        fig.append_trace(bbm, 1, 1)
        fig.append_trace(bbl, 1, 1)

        fig.append_trace(close, 2, 1)
        fig.append_trace(ema08, 2, 1)
        fig.append_trace(ema13, 2, 1)
        fig.append_trace(ema21, 2, 1)
        fig.append_trace(ema55, 2, 1)

        fig.append_trace(rsi, 3, 1)
        fig.append_trace(rsi_30, 3, 1)
        fig.append_trace(rsi_70, 3, 1)

        fig.append_trace(trend_macd_signal, 4, 1)
        fig.append_trace(trend_macd, 4, 1)

        fig.layout.update(title=self.symbol)
        plot(fig, filename=self.symbol)

        # ONE MAIN PLOT OPTION ; NO SUBPLOTS
        # data = [candle, ssma, fsma, trend_psar]
        # layout = go.Layout(title=self.symbol)
        # fig = go.Figure(data=data, layout=layout)
        # plot(fig, filename=self.symbol)



if __name__ == '__main__':

    ee = CWClient()

    specs = {'symbolslist' : ['btcusdt', 'ltcusdt', 'ethusdt', 'xrpusdt', 'vetusdt', 'hotusdt', 'bchusdt', 'xlmusdt',
                           'bsvusdt', 'eosusdt', 'bnbusdt', 'trxusdt', 'xmrusdt', 'dashusdt', 'xtzusdt'],
             'timeframes' : ['4h', '12h', '1d']}

    ee.write_output(specs, save_csv = True)
    dfa = ee.analysis

    tips, tipsdata = ee.seek_tips(output=True)

    subject = nowstr = datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + " : "
    recipients = ['johnprek@gmail.com','pan.fessas@gmail.com','isfinias@gmail.com']
    pwd = "T28!1990akis"
    user = 'pan.fessas@gmail.com'

    if tipsdata.shape[0]!=0:
        ee.send_email(user, pwd, recipients, subject)
    else :
        print('No tips found. No email sent')


dfa.shape
dfa.to_clipboard()

# ichimoku indicator
# dfa['buy_ichi'] = dfa[['ichi_tenkan_sen', 'ichi_kijun_sen', 'Close', 'Open', 'ichi_senkou_span_a', 'ichi_senkou_span_b']].apply(lambda x: 1 if (x['ichi_tenkan_sen'] > x['ichi_kijun_sen']) and (min(x['Close'], x['Open']) > max(x['ichi_senkou_span_b'], x['ichi_senkou_span_a'])) else 0, axis=1)
# dfa['sell_ichi'] = dfa[['ichi_tenkan_sen', 'ichi_kijun_sen', 'Close', 'Open', 'ichi_senkou_span_a', 'ichi_senkou_span_b']].apply(lambda x: 1 if (x['ichi_tenkan_sen'] < x['ichi_kijun_sen']) and (max(x['Close'], x['Open']) < min(x['ichi_senkou_span_b'], x['ichi_senkou_span_a'])) else 0, axis=1)
#
# dfa['buy_ichi_meta'] = dfa['buy_ichi'].rolling(window=4).sum().apply(lambda x : 0 if x == 4 else x)

# dfa['buy_testichi'] = dfa['buy_ichi'].shift(-1)
# dfa['sell_testichi'] = dfa['sell_ichi'].shift(-1)
#
# dfa['buy_ichi'] = dfa[['ichi_tenkan_sen', 'ichi_kijun_sen', 'Close', 'Open', 'ichi_senkou_span_a', 'ichi_senkou_span_b']].apply(lambda x: 1 if (x['ichi_tenkan_sen'] > x['ichi_kijun_sen']) and (min(x['Close'], x['Open']) > max(x['ichi_senkou_span_b'], x['ichi_senkou_span_a'])) and dfa[] else 0, axis=1)
