
from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

desired_width=320
pd.set_option('display.width', desired_width)
pd.set_option('display.max_columns',10)

import plotly.graph_objs as go
from plotly.offline import plot
from plotly import tools

import ta
from pyti.smoothed_moving_average import smoothed_moving_average as sma

from cryptowatch_client import Client

# Value Label
# 60 1m
# 180 3m
# 300 5m
# 900 15m
# 1800 30m
# 3600 1h
# 7200 2h
# 14400 4h
# 21600 6h
# 43200 12h
# 86400 1d
# 259200 3d
# 604800 1w

class CWClient:

    def __init__(self, frequency=180, exchange='kraken', symbol='btcusd'):
        self.client = Client(timeout=30)
        self.frequency = frequency
        self.exchange = exchange
        self.symbol = symbol
        self.colnames = ['CloseTime', 'Open', 'High', 'Low', 'Close', 'Volume', 'QuoteVolume']

        aa = self.client.get_exchanges().json()
        self.exchanges = pd.DataFrame(aa.get('result'))

        bb = self.client.get_markets().json()
        self.markets = pd.DataFrame(bb.get('result'))

    def set_params(self, exchange, symbol, frequency):
        self.exchange = exchange
        self.symbol = symbol
        self.frequency = frequency

    def summary(self):
        print(f'exchange : {self.exchange}\npair : {self.symbol}\nfrequency : {self.frequency}')

    def resample(self, frequency):
        # resample data
        dd = pd.DataFrame(self.data.get('result').get(str(frequency)), columns=self.colnames)
        # add basic features
        dd['OpenDateTime'] = dd['CloseTime'].apply(lambda x: datetime.fromtimestamp(x - frequency))
        dd['CloseDateTime'] = dd['CloseTime'].apply(lambda x: datetime.fromtimestamp(x))
        dd['Meta'] = f"{self.exchange}_{self.symbol}_{str(frequency)}"
        # tudor - basic indicators
        dd['fast_sma'] = sma(dd['Close'].tolist(), 10)
        dd['slow_sma'] = sma(dd['Close'].tolist(), 30)
        # bukosabino - ta
        df = ta.add_all_ta_features(dd, open="Open", high="High", low="Low", close="Close", volume="Volume")
        self.df = df
        return df

    def pull_data(self):
        self.data = self.client.get_markets_ohlc(exchange=self.exchange, pair=self.symbol).json()
        return self.resample(self.frequency)

    def plot(self):

        ll = self.df

        candle = go.Candlestick(
            x=ll['OpenDateTime'],
            open=ll['Open'],
            close=ll['Close'],
            high=ll['High'],
            low=ll['Low'],
            name="Candlesticks")

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


        fig = tools.make_subplots(rows = 3,
                                  cols = 1,
                                  subplot_titles = ('ticker','rsi', 'macd'),
                                  shared_xaxes = True)

        fig.append_trace(candle, 1, 1)
        fig.append_trace(bbh, 1, 1)
        fig.append_trace(bbm, 1, 1)
        fig.append_trace(bbl, 1, 1)
        fig.append_trace(rsi, 2, 1)
        fig.append_trace(rsi_30, 2, 1)
        fig.append_trace(rsi_70, 2, 1)
        fig.append_trace(trend_macd_signal, 3, 1)
        fig.append_trace(trend_macd, 3, 1)
        fig.layout.update(title=self.symbol)
        plot(fig, filename=self.symbol)

        # ONE MAIN PLOT OPTION ; NO SUBPLOTS
        # data = [candle, ssma, fsma, trend_psar]
        # layout = go.Layout(title=self.symbol)
        # fig = go.Figure(data=data, layout=layout)
        # plot(fig, filename=self.symbol)



ee = CWClient(frequency=60, exchange='binance', symbol='btcusdt')

# ee.exchanges
# ee.markets
# ee.markets.query("exchange == 'binance'").symbol.to_clipboard()

# ee.frequency = 60
# ee.symbol = 'btcusdt' # 'btcusd' , 'ltcusd', 'etcusd'
# ee.exchange = 'binance' # 'kraken'
# ee.summary()
#
# ll = ee.pull_data()
# ll.shape
# ll.to_clipboard()
# ee.plot()


import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go



app = dash.Dash('crypto-data')

app.layout = html.Div([
                html.Div([html.H2('Crypto Data')]),
                html.Div(children=html.Div(id='graphs'), className='row'),
                dcc.Interval(
                    id='graph-update',
                    interval=1000*60),
                    ],
                className="container",
                style={'width':'98%','margin-left':10,'margin-right':10,'max-width':50000}
                    )

@app.callback(Output('graphs','children'))
def update_graph():
    ll = ee.pull_data()
    graphs = []

    candle = go.Candlestick(
        x=ll['OpenDateTime'],
        open=ll['Open'],
        close=ll['Close'],
        high=ll['High'],
        low=ll['Low'],
        name="Candlesticks")

    # plot BB
    bbh = go.Scatter(
        x=ll['OpenDateTime'],
        y=ll['volatility_bbh'],
        name="volatility_bbh",
        line=dict(color=('rgba(21, 162, 117, 50)'), width=1, dash='dash'))

    bbm = go.Scatter(
        x=ll['OpenDateTime'],
        y=ll['volatility_bbm'],
        name="volatility_bbm",
        line=dict(color=('rgba(207, 21, 80, 50)'), width=1))

    bbl = go.Scatter(
        x=ll['OpenDateTime'],
        y=ll['volatility_bbl'],
        name="volatility_bbl",
        line=dict(color=('rgba(21, 162, 117, 50)'), width=1, dash='dash'))

    data = [candle,bbh,bbm,bbl]

    graphs.append(html.Div(dcc.Graph(
        id='ticker',
        animate=True,
        figure={'data': [data], 'layout': go.Layout(xaxis=dict(range=[min(ll['OpenDateTime']), max(ll['OpenDateTime'])]),
                                                    yaxis=dict(
                                                        range=[min(ll['volatility_bbl']), max(ll['volatility_bbh'])]),
                                                    margin={'l': 50, 'r': 1, 't': 45, 'b': 1},
                                                    title='tickers live')}
    )))

    return graphs




external_css = ["https://cdnjs.cloudflare.com/ajax/libs/materialize/0.100.2/css/materialize.min.css"]
for css in external_css:
    app.css.append_css({"external_url": css})

external_js = ['https://cdnjs.cloudflare.com/ajax/libs/materialize/0.100.2/js/materialize.min.js']
for js in external_css:
    app.scripts.append_script({'external_url': js})


if __name__ == '__main__':
    app.run_server(debug=True)