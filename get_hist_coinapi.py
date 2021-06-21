import requests
import pandas as pd
import config

# Get Assets
url = 'https://rest.coinapi.io/v1/assets'
headers = {'X-CoinAPI-Key' : config.COIN_API_KEY}
response = requests.get(url, headers=headers)

response.json()
type(response.json())
df = pd.DataFrame(response.json())
df.columns

df.type_is_crypto.value_counts()
df.query("type_is_crypto==0")
df.query("asset_id=='MATIC'")

# Get Exchanges
url = 'https://rest.coinapi.io/v1/exchanges'
headers = {'X-CoinAPI-Key' : config.COIN_API_KEY}
response = requests.get(url, headers=headers)

response.json()
type(response.json())
df = pd.DataFrame(response.json())
df.head()
df.columns

# Get Available Periods
url = 'https://rest.coinapi.io/v1/exchangerate/history/periods'
headers = {'X-CoinAPI-Key' : config.COIN_API_KEY}
response = requests.get(url, headers=headers)

response.json()
type(response.json())
periods = pd.DataFrame(response.json())
periods.shape
periods.head()
periods

# Get OHLCV
url = 'https://rest.coinapi.io/v1/ohlcv/BTC/USD/history?period_id=5MIN&time_start=2016-01-01T00:00:00'
headers = {'X-CoinAPI-Key' : config.COIN_API_KEY}
response = requests.get(url, headers=headers)

response.json()
type(response.json())
df = pd.DataFrame(response.json())
df.shape
df.tail()
df.columns

# Get OHLCV Parametrized
url = 'https://rest.coinapi.io/v1/ohlcv/BTC/USD/history?period_id=5MIN&limit=100000&time_end=2021-05-27T00:00:00'
headers = {'X-CoinAPI-Key' : config.COIN_API_KEY}
response = requests.get(url, headers=headers)

response.json()
type(response.json())
df = pd.DataFrame(response.json())
df.shape
df.head()
df.columns
