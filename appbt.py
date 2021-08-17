
# Import Dependencies -----------------------------------------

import os
import re
import time
import numpy as np
import pandas as pd
import talib
from tqdm import tqdm
import sqlite3
import streamlit as st
import streamlit.components.v1 as components
import config
import helpers

import plotly.graph_objs as go
from plotly.offline import plot
from plotly import tools
import plotly.express as px
import plotly.io as pio

import backtrader as bt
from backtrader import Cerebro

from strategies.GoldenCross import GoldenCross
from strategies.BuyHold import BuyHold
from strategies.MACDCross import MACDCross
from strategies.Stochastic import Stochastic
from strategies.TripleFoo import TripleFoo
from strategies.BuyDip import BuyDip
from strategies.BearX import BearX

# Define Constants --------------------------------------------

STRATEGIES_PATH = 'strategies/'
DATABASE_PATH = 'data/assets.db'
st.set_page_config(layout='wide')

# Custom Functions --------------------------------------------

def make_candlesplot(df):
    candle = go.Candlestick(
                x=df['closeTime'],
                open=df['open'],
                close=df['close'],
                high=df['high'],
                low=df['low'],
                name="Candlesticks")

    layout = go.Layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)'
    )

    fig = go.Figure(layout=layout)
    fig.layout.template = 'plotly_dark'
    fig.update_xaxes(showticklabels=False)
    fig.update_layout(
        autosize=False,width=800,height=300,
        margin=dict(l=0, r=20, t=0, b=20),
        legend=dict(yanchor="top",y=0.99,xanchor="left",x=0.01),
        xaxis={'fixedrange': True, 'rangeslider': {'visible': False}}
        )
    fig.add_trace(candle)
    return fig

def backtest(df,strategy,symbol,cash=1000):
    strategies = {
                    'GoldenCross':GoldenCross,
                    'MACDCross':MACDCross,
                    'BuyHold':BuyHold,
                    'Stochastic':Stochastic,
                    'TripleFoo':TripleFoo,
                    'BuyDip':BuyDip,
                    'BearX':BearX
                }

    cerebro = bt.Cerebro()
    cerebro.broker.setcash(cash)
    start_portfolio_value = cerebro.broker.getvalue()
    
    feed = bt.feeds.PandasData(dataname=df)
    cerebro.adddata(feed)    
    cerebro.addstrategy(strategies[strategy],ticker = symbol)
    cerebro.run()
    
    end_portfolio_value = cerebro.broker.getvalue()
    pnl = end_portfolio_value - start_portfolio_value
    st.write(f'Starting Portfolio Value: {start_portfolio_value:2f}')
    st.write(f'Final Portfolio Value: {end_portfolio_value:2f}')
    st.write(f'PnL: {pnl:.2f}')
    
    return cerebro.plot()

def get_strategies():
    strategies_list = None
    if os.path.exists(STRATEGIES_PATH):
        strategies_list = [x for x in os.listdir(STRATEGIES_PATH) if x.endswith('.py')]
        strategies_list = [re.sub('\.py$', '', x) for x in strategies_list]
    else:
        st.write(f'{STRATEGIES_PATH} not found')
    return strategies_list

@st.cache(allow_output_mutation=True,suppress_st_warning=True)
def get_symbols():
    data = None
    if os.path.exists(DATABASE_PATH):
        start = time.time()
        con = sqlite3.connect(DATABASE_PATH)
        sql_string = "SELECT DISTINCT symbol FROM futures15;"
        data = pd.read_sql(sql_string,con)
        end = time.time()
        st.write(f'loaded {data.shape[0]} symbols from {DATABASE_PATH} in {int(end-start)} seconds')
        con.close()
    else:
        st.write(f'{DATABASE_PATH} not found')
    return data

# @st.cache(allow_output_mutation=True,suppress_st_warning=True)
def get_data(symbol):
    data = None
    if os.path.exists(DATABASE_PATH):
        start = time.time()
        con = sqlite3.connect(DATABASE_PATH)
        sql_string = f"SELECT * FROM futures15 where symbol = '{symbol}' ORDER BY openTimets"
        data = pd.read_sql(sql_string,con)
        end = time.time()
        con.close()
        data = data.assign(
                        openTime = lambda x : pd.to_datetime(x.openTime),
                        closeTime = lambda x : pd.to_datetime(x.closeTime)
                        ).set_index('openTime')
    else:
        st.write(f'{DATABASE_PATH} not found')
    return data

def get_strategy_params(strategy):
    return list(globals()[strategy].params._getkeys())

# App Structure -----------------------------------------------

current_page = st.sidebar.selectbox('Select Page',['Strategies','Main'],0)
symbols = get_symbols().symbol.tolist()

def Strategies():
    
    # Symbol Selection
    user_symbol =  st.sidebar.selectbox('Select Symbol',symbols,symbols.index('BTCUSDT'))

    st.sidebar.markdown(f'You have selected {user_symbol}')
    # if st.sidebar.button('Load symbol'):

    df = get_data(user_symbol)
    st.sidebar.success(f'Loaded {df.shape[0]} observations for {user_symbol}')
    st.subheader(f'{user_symbol} Analysis')
    st.plotly_chart(make_candlesplot(df))

    # Strategy Selection
    strategies = get_strategies()
    user_strategy =  st.sidebar.selectbox('Select Strategy',strategies,len(strategies)-1)
    st.sidebar.write(f'{user_strategy} parameters :')
    st.sidebar.write(get_strategy_params(user_strategy))

    # Run Strategy
    if st.sidebar.button(f'Run {user_strategy} for {user_symbol}'):
                
        if isinstance(df,pd.DataFrame):
            if not df.empty:
                pee = backtest(df,user_strategy,user_symbol,1000)
                st.pyplot(pee)
                      
def Main():
    st.write('this is the main page')

if current_page == "Strategies":
    Strategies()
elif current_page == "Main":
    Main()
    
