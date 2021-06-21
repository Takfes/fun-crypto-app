import pandas as pd
import ccxt
import talib
import patterns
import tulipy
import ta
from ta import add_all_ta_features
from ta.volatility import BollingerBands,AverageTrueRange
from ta.trend import SMAIndicator, EMAIndicator, WMAIndicator, MACD, macd_signal
from ta.momentum import RSIIndicator
import plotly.graph_objs as go
from plotly.offline import plot
from plotly import tools
import plotly.express as px
import plotly.io as pio
import mplfinance as mpf
from tqdm import tqdm
import sqlite3
import streamlit as st
import streamlit.components.v1 as components
import config
import helpers
from binance.client import Client

st.set_page_config(layout='wide')

# GP FUNCTIONS
def resample(df,period):
    # https://stackoverflow.com/questions/17001389/pandas-resample-documentation
    return df.resample(period).agg({'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'})  # to five-minute bar

@st.cache(allow_output_mutation=True,suppress_st_warning=True)
def get_data():
    st.write('get_data was triggered!!!')
    con = sqlite3.connect('assets.db')
    sql_string = "SELECT * FROM crypto"
    data = pd.read_sql(sql_string,con)
    con.close()
    return data

@st.cache(allow_output_mutation=True,suppress_st_warning=True)
def get_signals_data():
    data = pd.read_csv('data/signals.csv')
    return data

# APP STRUCTURE

data = get_data()
signals = get_signals_data()
symbols = data.symbol.unique().tolist()
current_page = st.sidebar.selectbox('Select Page',['Main','Screener','Binance'],1)
if current_page in ['Main','Screener']:
    user_symbol =  st.sidebar.selectbox('Select Symbol',symbols)

def Main():
    
    # user_symbol =  st.sidebar.selectbox('Select Symbol',symbols)
    # user_theme = st.sidebar.selectbox('Select Theme',[theme for theme in pio.templates])
    # user_frequency = st.sidebar.selectbox('Select Resample Frequency',['5M','15M','30M','1H','4H','1D','7D','1M','All'])
    user_indicators = st.sidebar.multiselect('Select Indicators',
                                             ['SMA','Bollinger Bands','RSI','MACD','ATR'], 
                                             default=['RSI','Bollinger Bands','MACD'])
    
    st.write(user_symbol)
    user_time = st.sidebar.slider('Select Time Window', min_value=0, max_value=100, value=5)
    
    df = data.query('symbol == @user_symbol')
    df = df.tail(int(user_time/100 * df.shape[0]))
    
    # SMA
    df['sma_3'] = SMAIndicator(close=df["close"],window=3).sma_indicator()
    df['sma_5'] = SMAIndicator(close=df["close"],window=5).sma_indicator()
    df['sma_7'] = SMAIndicator(close=df["close"],window=7).sma_indicator()
    df['sma_14'] = SMAIndicator(close=df["close"],window=14).sma_indicator()
    df['sma_21'] = SMAIndicator(close=df["close"],window=21).sma_indicator()
    
    # Bollinger Bands
    indicator_bb = BollingerBands(close=df["close"], window=20, window_dev=2)
    df['bb_bbh'] = indicator_bb.bollinger_hband()
    df['bb_bbl'] = indicator_bb.bollinger_lband()
    df['bb_bbm'] = indicator_bb.bollinger_mavg()
    
    # RSI
    indicator_rsi = RSIIndicator(close=df["close"])
    df['rsi'] = indicator_rsi.rsi()
    df['rsi_30'] = 30
    df['rsi_70'] = 70
    
    # ATR
    indicator_atr = AverageTrueRange(high=df['high'],low=df['low'],close=df['close'],window=5)
    df['atr_5'] = AverageTrueRange(high=df['high'],low=df['low'],close=df['close'],window=5).average_true_range()
    df['atr_10'] = AverageTrueRange(high=df['high'],low=df['low'],close=df['close'],window=10).average_true_range()
    
    # MACD
    inicator_macd = MACD(close=df["close"])
    df['macd'] = inicator_macd.macd()
    df['macd_diff'] = inicator_macd.macd_diff()
    df['macd_signal'] = inicator_macd.macd_signal()

    # Plotting Components
    candle = go.Candlestick(
                x=df['datetime'],
                open=df['open'],
                close=df['close'],
                high=df['high'],
                low=df['low'],
                name="Candlesticks")
    
    close = go.Scatter(
        x=df['datetime'],
        y=df['close'],
        name="close",
        line=dict(color=('#ff4545'),width=1.5))
    
    sma_14 = go.Scatter(
        x=df['datetime'],
        y=df['sma_14'],
        name="sma_14",
        line=dict(color=('#80cfa9'),width=1.5))
    
    sma_21 = go.Scatter(
        x=df['datetime'],
        y=df['sma_21'],
        name="sma_21",
        line=dict(color=('#4c6663'),width=1.5))
    
    bbh = go.Scatter(
        x=df['datetime'],
        y=df['bb_bbh'],
        name="bb_bbh",
        line=dict(color=('#c1ff45'),width=1.5,dash='dash'))

    bbm = go.Scatter(
        x=df['datetime'],
        y=df['bb_bbm'],
        name="bb_bbm",
        line=dict(color=('#d8a6f5'),width=1.5,dash='dash'))

    bbl = go.Scatter(
        x=df['datetime'],
        y=df['bb_bbl'],
        name="bb_bbl",
        line=dict(color=('#ff4567'),width=1.5,dash='dash')) #dash='dash'

    rsi = go.Scatter(
        x=df['datetime'],
        y=df['rsi'],
        name="rsi",
        line=dict(color=('rgba(146, 17, 141, 50)')))

    rsi_30 = go.Scatter(
        x=df['datetime'],
        y=df['rsi_30'],
        name="rsi_30",
        line=dict(color=('#ffffff'),width=1, dash='dash'))

    rsi_70 = go.Scatter(
        x=df['datetime'],
        y=df['rsi_70'],
        name="rsi_70",
        line=dict(color=('#ffffff'),width=1, dash='dash'))

    atr_5 = go.Scatter(
            x=df['datetime'],
            y=df['atr_5'],
            name="atr_5",
            line=dict(color=('#d8a6f5'),width=1))

    macd = go.Scatter(
        x=df['datetime'],
        y=df['macd'],
        name="macd",
        line=dict(color=('#4583ff'),width=1, dash='dash'))

    macd_signal = go.Scatter(
            x=df['datetime'],
            y=df['macd_signal'],
            name="macd_signal",
            line=dict(color=('#ffab45'),width=1))

    # Customize Layout
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
    
    if 'Bollinger Bands' in user_indicators:
        fig.add_trace(bbh)
        fig.add_trace(bbm)
        fig.add_trace(bbl)

    if 'SMA' in user_indicators:
        fig.add_trace(sma_14)
        fig.add_trace(sma_21)

    st.write(f'Candles for {user_symbol}')
    st.plotly_chart(fig)

    if 'RSI' in user_indicators:
        fig2 = go.Figure(layout=layout)
        fig2.layout.template = 'plotly_dark'
        fig2.update_xaxes(showticklabels=False)
        fig2.update_layout(
            autosize=False,width=800,height=150,
            margin=dict(l=0, r=20, t=0, b=20),
            legend=dict(yanchor="top",y=0.99,xanchor="left",x=0.01),
            xaxis={'fixedrange': True, 'rangeslider': {'visible': False}}
            )
        fig2.add_trace(rsi_30)
        fig2.add_trace(rsi_70)
        fig2.add_trace(rsi)
        st.write(f'RSI for {user_symbol}')
        st.plotly_chart(fig2)
        
    if 'ATR' in user_indicators:
        fig3 = go.Figure(layout=layout)
        fig3.layout.template = 'plotly_dark'
        fig3.update_xaxes(showticklabels=False)
        fig3.update_layout(
            autosize=False,width=800,height=150,
            margin=dict(l=0, r=20, t=0, b=20),
            legend=dict(yanchor="top",y=0.99,xanchor="left",x=0.01),
            xaxis={'fixedrange': True, 'rangeslider': {'visible': False}}
            )
        fig3.add_trace(atr_5)
        st.write(f'ATR for {user_symbol}')
        st.plotly_chart(fig3)

    if 'MACD' in user_indicators:
        fig4 = go.Figure(layout=layout)
        fig4.layout.template = 'plotly_dark'
        fig4.update_xaxes(showticklabels=False)
        fig4.update_layout(
            autosize=False,width=800,height=150,
            margin=dict(l=0, r=20, t=0, b=20),
            legend=dict(yanchor="top",y=0.99,xanchor="left",x=0.01),
            xaxis={'fixedrange': True, 'rangeslider': {'visible': False}}
            )
        fig4.add_trace(macd)
        fig4.add_trace(macd_signal)
        # fig4.add_trace(close)
        st.write(f'MACD for {user_symbol}')
        st.plotly_chart(fig4)

def Binance():
    st.write('This is Binance Orders page')
    
    client = Client(config.BINANCE_API_KEY, config.BINANCE_API_SECRET)

    # Get balance information ; derive active cryptos
    account_info = client.get_account()
    account_info_balances = pd.DataFrame(account_info['balances'])
    account_info_balances = account_info_balances.assign(free = lambda x : x.free.astype(float) )
    account_info_active_asset = account_info_balances.query('free>0 and asset!="USDT"').asset.tolist()

    # for each active crypto, Get Spot Orders thoughout history
    account_hist_orders_list = []
    for s in account_info_active_asset:
        sym = s + 'USDT'
        # print(sym)
        current_order = client.get_all_orders(symbol=sym)
        current_order_df = pd.DataFrame(current_order)
        account_hist_orders_list.append(current_order_df)
    account_hist_orders = pd.concat(account_hist_orders_list)

    # Data manipulation
    mycolumns = ['symbol','price','time','status']
    account_hist_orders_cleaned = account_hist_orders[mycolumns].\
        assign(
            time = account_hist_orders.time.apply(helpers.timestamp_to_datetime)
        ).query('status != "CANCELED"').sort_values(by=['symbol','time'],ascending=[True,False]).reset_index(drop=True)
    # Bring current price info
    all_tickers_data = pd.DataFrame(client.get_all_tickers())
    
    # Consolidate price bought vs current price
    orders_evaluation = account_hist_orders_cleaned.\
        merge(all_tickers_data,how='left',
            left_on='symbol',right_on='symbol',suffixes=('_bought', '_now')).\
                assign(
                    price_bought = lambda x : x.price_bought.astype(float),
                    price_now = lambda x : x.price_now.astype(float),
                    price_diff = lambda x : x.price_now - x.price_bought,
                    price_diff_pct = lambda x : round(100 * (x.price_now - x.price_bought)/x.price_bought,2),
                    )

    st.dataframe(orders_evaluation)
    st.markdown(f'For more details, visit [Binance Orders](https://www.binance.com/en/my/orders/exchange/tradeorder)')

def Screener():
    
    # user_pattern = st.sidebar.selectbox('Select Pattern',[x for x in patterns.patterns.keys()])
    symbol_list = signals.symbol.unique().tolist()
    # user_symbol = st.sidebar.selectbox('Select Symbol',symbol_list)
    # TODO enable dynamic PATTERN PERIOD ; provided a dynamic script for adding pattern indicators
    st.write(f'You have selected {user_symbol}')
    st.write(f'https://www.binance.com/en/trade/{user_symbol}_USDT?type=spot')
    # st.write(f'total dataframe shape : {signals.shape}')
    # st.write('Last 3 rows per symbol')
    # st.dataframe(signals.groupby(['symbol']).head(3))
    
    pattern_columns = [col for col in signals.columns if col.startswith('pattern_')]
    # signals.groupby(['symbol']).agg({'symbol':'nunique'})
    # signals.groupby(['symbol'])['symbol','temp_indicator_3'].head(3).groupby(['symbol']).sum().sort_values(by='temp_indicator_3')
    # signals.tail(3).datetime
    # signals.columns
    
    indicator_sum_per_symbol = signals.groupby(['symbol'])['symbol','temp_indicator_3'].head(3).groupby(['symbol']).sum().sort_values(by='temp_indicator_3')
    st.write('indicator_sum_per_symbol')
    st.dataframe(indicator_sum_per_symbol)
    
    # signals.query('symbol=="XTZ"').tail(3)[pattern_columns].sum()[signals.query('symbol=="XTZ"').tail(3)[pattern_columns].sum()!=0]
    dict_with_pattern_dfs = {}
    for s in symbols:
        print(s)
        temp_sdf = signals.query('symbol==@s').tail(3)
        temp_signal_columns = temp_sdf[pattern_columns].sum()[temp_sdf[pattern_columns].sum()!=0].index.tolist()
        temp_final_columns = ['symbol','datetime'] + temp_signal_columns
        dict_with_pattern_dfs[s] = temp_sdf.tail(3)[temp_final_columns]
    
    st.write(f'dict_with_pattern_dfs for {user_symbol}')
    st.dataframe(dict_with_pattern_dfs[user_symbol])
    # dict_with_pattern_dfs.keys()

    list_of_relevant_patterns = dict_with_pattern_dfs[user_symbol].columns.tolist()[2:]
    user_pattern = st.sidebar.selectbox('Select Pattern',list_of_relevant_patterns)
    list_of_relevant_patterns_adj = [l.lower().replace('pattern_','').replace('_','-') for l in list_of_relevant_patterns]
    {k:f'https://www.investopedia.com/terms/{k[0]}/{k}.asp' for k in list_of_relevant_patterns_adj}
    for l in list_of_relevant_patterns_adj:
        st.sidebar.markdown(f'[{l}](https://www.investopedia.com/terms/{l[0]}/{l}.asp)')
        # st.sidebar.markdown(f'<p style="font-size:10px">https://www.investopedia.com/terms/{l[0]}/{l}.asp</p>',unsafe_allow_html=True)
        # st.sidebar.markdown(f'<p style="font-size:10px"><a href=https://www.investopedia.com/terms/{l[0]}/{l}.asp></p>',unsafe_allow_html=True)
        
if current_page == "Main":
    Main()
elif current_page == "Binance":
    Binance()
elif current_page == "Screener":
    Screener()
    
