
import time
import config
import helpers
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import minimize

df = pd.read_csv('stocks.csv')

df.shape
df.columns
df.dtypes
df['datetime'] = pd.to_datetime(df.datetime, utc=True)
df.dtypes
    
# resample
agg_dict = {
    'open': 'first',
    'high': 'max',
    'low': 'min',
    'close': 'last',
    'adj_close': 'last',
    'volume': 'sum'
    }

# resampled dataframe
r_df = df.set_index('datetime').groupby(['symbol']).resample('D').agg(agg_dict).reset_index().dropna()
r_df.isnull().sum()

r_df.query('symbol=="AAPL"').head(20).to_clipboard()
df.query('symbol=="AAPL"').head(200).to_clipboard()

# pivot dataframe to enable returns
pivoted_data = pd.pivot_table(df,index='datetime',columns='symbol')
pivoted_data = pd.pivot_table(r_df,index='datetime',columns='symbol')
pivoted_data.columns

# custom functions
def get_risk(prices):
    return (prices / prices.shift(1) - 1).dropna().std().values

def get_return(prices):
    return ((prices / prices.shift(1) - 1).dropna().mean() * np.sqrt(250)).values

# optimize portfolio
# https://towardsdatascience.com/efficient-frontier-optimize-portfolio-with-scipy-57456428323e
risks = get_risk(pivoted_data.adj_close)
returns = get_return(pivoted_data.adj_close)
pivoted_symbol_columns = pivoted_data.adj_close.columns
popt = pd.DataFrame({'symbol':pivoted_symbol_columns,'risks':risks,'returns':returns})
popt.to_clipboard()

fig, ax = plt.subplots()
ax.scatter(x=popt.risks, y=popt.returns, alpha=0.5)
ax.set(title='Return and Risk', xlabel='Risk', ylabel='Return')

for i, symbol in enumerate(popt.symbol.unique().tolist()):
    ax.annotate(symbol, (popt.query('symbol==@symbol').risks.values, popt.query('symbol==@symbol').returns.values))
plt.show()

# df.groupby(['symbol'])['adj_close'].apply(get_return)
# df.groupby(['symbol'])['adj_close'].apply(get_risk)
