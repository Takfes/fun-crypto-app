
# ------------------ DB CONFIG ------------------ #

DB_NAME ='data/assets.db'

DB_ASSET_TABLE = 'assets'
DB_ASSET_TABLE_INDEX = 'time_symbol'

DB_ASSET_TABLE_CRYPTO = 'crypto'
DB_ASSET_TABLE_INDEX_CRYPTO = 'time_symbol_crypto'

DB_ASSET_TABLE_CRYPTO_DAILY = 'cryptodaily'
DB_ASSET_TABLE_CRYPTO_DAILY_INDEX = 'time_symbol_cryptodaily'

DB_ASSET_TABLE_STOCK_DAILY = 'stockdaily'
DB_ASSET_TABLE_STOCK_DAILY_INDEX = 'time_symbol_stockdaily'

DB_ASSET_TABLE_FUTURES_15 = 'futures15'
DB_ASSET_TABLE_FUTURES_15_INDEX = 'time_symbol_futures15'

DB_ASSET_TABLE_FUTURES_1 = 'futures1'
DB_ASSET_TABLE_FUTURES_1_INDEX = 'time_symbol_futures1'
DB_ASSET_TABLE_FUTURES_1_INDEX_TIME = 'time_futures1'
DB_ASSET_TABLE_FUTURES_1_INDEX_SYMBOL = 'symbol_futures1'

# ------------------ DATA ------------------ #

TICKERS = ['BTC','ETH','XRP','DOGE','DOT','LTC','ADA','VET','MATIC',         'BNB','LINK','UNI','SOL','TRX','EOS','ENJ','DASH',         'XTZ','XMR','XLM']

'''
HOW TICKERSXT IS DERIVED :
from helpers import get_sorted_crypto
tickers_by_conditions = get_sorted_crypto()
tickers_by_volume = tickers_by_conditions.query('type=="top_100_by_volume"').copy()
tickers_by_volume.symbol.unique().tolist()
manually remove : USDT, OKB, HT, MIOTA, BCD, WBTC, ONGAS
'''

TICKERSXT = [
    'BTC','ETH','BNB','XRP','DOGE','ADA',    'MATIC','BUSD','SOL','DOT','LTC',    'LINK','ETC','FIL','EOS','THETA','BCH',    'VET','TFUEL','KSM','UNI','TRX','XLM',    'DATA','USDC','GTO','NEO','BTT',    'ZEC','BSV','ICP','CRV','XMR','CAKE',    'ALGO','QTUM','OMG','XTZ','ATOM',    'RUNE','DASH','LUNA','SUSHI','CHZ','ZIL',    'JST','BTG','WAVES','AAVE','BAKE',    'FTT','HBAR','SXP','GRT','ONT','MANA',    'IOST','1INCH','ZRX','ENJ','COMP','AVAX','YFI',    'SC','SRM','ICX','FTM','KNC','NANO','DOCK',    'KEY','ZEN','RVN','XVS','ONE','MKR','MTL','BAT',    'SNX','TRB','DGB','XEM','KAVA',    'BAND','OGN','NEAR','HOT','INJ','XVG','LSK',    'WIN','MFT','NU']

'''
HOW TICKERSXT IS DERIVED :
from helpers import get_stocks_list
stock_list = get_stocks_list()
stock_list = stock_list.sort_values(by=['Market Cap'],ascending=False).head(100).Symbol.tolist()
stock_list
'''

STOCKSXT = ['AAPL', 'MSFT', 'AMZN', 'GOOG', 'GOOGL', 'FB', 'TSM', 'TSLA', 'BABA', 'JPM', 'V', 'JNJ', 'NVDA', 'WMT', 'UNH', 'BAC', 'MA', 'HD', 'PG', 'DIS', 'PYPL', 'ASML', 'CMCSA', 'XOM', 'ADBE', 'KO', 'TM', 'INTC', 'ORCL', 'CSCO', 'NFLX', 'CRM', 'PFE', 'NKE', 'T', 'ABT', 'PEP', 'CVX', 'ABBV', 'NVS', 'WFC', 'AVGO', 'MRK', 'LLY', 'BHP', 'UPS', 'TMO', 'DHR', 'NVO', 'ACN', 'TMUS', 'TXN', 'MCD', 'MDT', 'MS', 'COST', 'SAP', 'C', 'HON', 'UL', 'PDD', 'LIN', 'SHOP', 'BBL', 'QCOM', 'PM', 'BUD', 'UNP', 'AZN', 'RY', 'BMY', 'BA', 'NEE', 'CHTR', 'RIO', 'HDB', 'SCHW', 'LOW', 'AMGN', 'RTX', 'SBUX', 'BLK', 'SNY', 'SE', 'HSBC', 'CAT', 'TD', 'AXP', 'IBM', 'AMAT', 'GS', 'CSAN', 'SONY', 'GE', 'TOT', 'INTU', 'MMM', 'AMT', 'JD', 'CVS']

# PREXTICKS = [
#     '1000SHIBUSDT'
#     ,'1INCHUSDT'
#     ,'AAVEUSDT'
#     ,'ADAUSDT'
#     ,'AKROUSDT'
#     ,'ALGOUSDT'
#     ,'ALICEUSDT'
#     ,'ALPHAUSDT'
#     ,'ANKRUSDT'
#     ,'ATOMUSDT'
#     ,'AVAXUSDT'
#     ,'AXSUSDT'
#     ,'BAKEUSDT'
#     ,'BALUSDT'
#     ,'BANDUSDT'
#     ,'BATUSDT'
#     ,'BCHUSDT'
#     ,'BELUSDT'
#     ,'BLZUSDT'

#     ,'BNBUSDT'
#     ,'BTCUSDT'
#     ,'BTSUSDT'
#     ,'BTTUSDT'
#     ,'BZRXUSDT'
#     ,'CELRUSDT'
#     ,'CHRUSDT'
#     ,'COMPUSDT'
#     ,'COTIUSDT'
#     ,'CRVUSDT'
#     ,'CTKUSDT'
#     ,'CVCUSDT'
#     ,'DASHUSDT'
#     ,'DENTUSDT'
#     ,'DODOUSDT'
#     ,'DOGEUSDT'
#     ,'DOTUSDT'
#     ,'EGLDUSDT'
#     ,'ENJUSDT'

#     ,'EOSUSDT'
#     ,'ETCUSDT'
#     ,'ETHUSDT'
#     ,'FILUSDT'
#     ,'FLMUSDT'
#     ,'FTMUSDT'
#     ,'GRTUSDT'
#     ,'GTCUSDT'
#     ,'HBARUSDT'
#     ,'HNTUSDT'
#     ,'HOTUSDT'
#     ,'ICPUSDT'
#     ,'ICXUSDT'
#     ,'KAVAUSDT'
#     ,'KEEPUSDT'
#     ,'KNCUSDT'
#     ,'KSMUSDT'
#     ,'LINAUSDT'
#     ,'LINKUSDT'

#     ,'LITUSDT'
#     ,'LRCUSDT'
#     ,'LTCUSDT'
#     ,'LUNAUSDT'
#     ,'MANAUSDT'
#     ,'MATICUSDT'
#     ,'MKRUSDT'
#     ,'MTLUSDT'
#     ,'NEARUSDT'
#     ,'NEOUSDT'
#     ,'NKNUSDT'
#     ,'OCEANUSDT'
#     ,'OGNUSDT'
#     ,'OMGUSDT'
#     ,'ONEUSDT'
#     ,'ONTUSDT'
#     ,'QTUMUSDT'
#     ,'REEFUSDT'
#     ,'RENUSDT'

#     ,'RLCUSDT'
#     ,'RSRUSDT'
#     ,'RUNEUSDT'
#     ,'RVNUSDT'
#     ,'SANDUSDT'
#     ,'SCUSDT'
#     ,'SFPUSDT'
#     ,'SKLUSDT'
#     ,'SNXUSDT'
#     ,'SOLUSDT'
#     ,'SRMUSDT'
#     ,'STMXUSDT'
#     ,'STORJUSDT'
#     ,'SUSHIUSDT'
#     ,'SXPUSDT'
#     ,'THETAUSDT'
#     ,'TLMUSDT'
#     ,'TOMOUSDT'
#     ,'TRBUSDT'

#     ,'TRXUSDT'
#     ,'UNFIUSDT'
#     ,'UNIUSDT'
#     ,'VETUSDT'
#     ,'WAVESUSDT'
#     ,'XEMUSDT'
#     ,'XLMUSDT'
#     ,'XMRUSDT'
#     ,'XRPUSDT'
#     ,'XTZUSDT'
#     ,'YFIIUSDT'
#     ,'YFIUSDT'
#     ,'ZECUSDT'
#     ,'ZENUSDT'
#     ,'ZILUSDT'
#     ,'ZRXUSDT'
# ]

PREXTICKS = [
    'TRXUSDT'
    ,'UNFIUSDT'
    ,'UNIUSDT'
    ,'VETUSDT'
    ,'WAVESUSDT'
    ,'XEMUSDT'
    ,'XLMUSDT'
    ,'XMRUSDT'
    ,'XRPUSDT'
    ,'XTZUSDT'
    ,'YFIIUSDT'
    ,'YFIUSDT'
    ,'ZECUSDT'
    ,'ZENUSDT'
    ,'ZILUSDT'
    ,'ZRXUSDT'
    ]