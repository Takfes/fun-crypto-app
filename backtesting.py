import os, sys, argparse
import config
import sqlite3
import pandas as pd
import backtrader as bt
from backtrader import Cerebro
from backtesting_settings import strategy_settings_dictionary
import pprint

from strategies.GoldenCross import GoldenCross
from strategies.BuyHold import BuyHold
from strategies.MACDCross import MACDCross
from strategies.Stochastic import Stochastic
from strategies.TripleFoo import TripleFoo
from strategies.BuyDip import BuyDip
from strategies.BearX import BearX
from strategies.Dictum import Dictum
from strategies.TripleH import TripleH

strategies = {
    'ma':GoldenCross,
    'macd':MACDCross,
    'bnh':BuyHold,
    'stoc':Stochastic,
    'triple':TripleFoo,
    'dip':BuyDip,
    'bearx':BearX,
    'dic':Dictum,
    '3h':TripleH
}

def parse_user_input():
    parser = argparse.ArgumentParser()
    parser.add_argument('type',help="what kind of asset : ['stock','crypto','crypto15','futures15']",type=str)
    parser.add_argument('symbol',help='which symbol to test',type=str)
    parser.add_argument('strategy',help=f'which strategy to test : {list(strategies.keys())}',type=str)
    parser.add_argument('cash',help='set cash amount',type=str)
    parser.add_argument('risk',help='percentage of budget to risk',type=float)
    args = parser.parse_args()
    return args

def get_price_series(type, symbol, con):
    
    if type == 'stock':
        sql_string = f"SELECT * FROM stockdaily WHERE symbol = '{symbol}' ORDER BY datetime"
    elif type == 'crypto':
        sql_string = f"SELECT * FROM cryptodaily WHERE symbol = '{symbol}' ORDER BY datetime"
    elif type == 'crypto15':
        sql_string = f"SELECT * FROM crypto WHERE symbol = '{symbol}' ORDER BY datetime"
    elif type == 'futures15':
        sql_string = f"SELECT * FROM futures15 WHERE symbol = '{symbol}' and openTime >= '2021-07-01' and openTime < '2021-08-13 15:30:00' ORDER BY openTimets"
    if type != 'futures15':
        price_series = pd.read_sql(sql_string,con).assign(datetime = lambda x : pd.to_datetime(x.datetime)).set_index('datetime')
    else:
        price_series = pd.read_sql(sql_string,con).assign(openTime = lambda x : pd.to_datetime(x.openTime)).set_index('openTime')

    return price_series

if __name__ == '__main__':

    args = parse_user_input()
    
    if args.strategy not in strategies.keys():
        print(f'Invalid strategy. Must be one of {list(strategies.keys())}') 
        sys.exit()
    else:
        strategy_settings = strategy_settings_dictionary[args.strategy]
        
        strategy_settings['symbol'] =  args.symbol
        strategy_settings['cash'] =  args.cash
        strategy_settings['risk'] =  args.risk
        
        print()
        print(f'===========>> Settings <<===========')
        for k,v in strategy_settings.items():
            print(f'* {k} : {v}')
        print(f'====================================')
        print()



    try :
        
        con = sqlite3.connect(config.DB_NAME)
        price_series = get_price_series(args.type,args.symbol,con)
        print(f'> backtesting.py : fetched {price_series.shape[0]} rows for {args.symbol}')

        if isinstance(price_series,pd.DataFrame):
            if not price_series.empty:

                cerebro = bt.Cerebro()
                cerebro.broker.setcash(int(args.cash))
                start_portfolio_value = cerebro.broker.getvalue()
                
                # Add Dataset
                feed = bt.feeds.PandasData(dataname=price_series)
                cerebro.adddata(feed)

                # Add Strategy
                cerebro.addstrategy(strategies[args.strategy],params = strategy_settings)
                # cerebro.addstrategy(strategies[args.strategy],ticker = args.symbol, risk=args.risk, percentage_change = args.percentage_change, short = bool(args.short))
                # cerebro.addstrategy(GoldenCross, fast=20, slow=100)
                # cerebro.addstrategy(strategies[args.strategy],ticker = args.symbol)

                # Add Analyzer
                cerebro.addanalyzer(bt.analyzers.DrawDown, _name='mydrawdown')
                cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='mysharpe')

                # cerebro.addanalyzer(bt.analyzers.PositionsValue, _name='mypositionsvalue')
                # cerebro.addanalyzer(bt.analyzers.PyFolio, _name='mypyfolio')
                # cerebro.addanalyzer(bt.analyzers.PeriodStats, _name='myperiodstats')
                # cerebro.addanalyzer(bt.analyzers.SQN, _name='mysqn')
                # cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='mytradeanalyzer')
                # cerebro.addanalyzer(bt.analyzers.Transactions, _name='mytransactions')

                # Run
                R = cerebro.run()
                H = R[0]

                
                # Basic Results
                end_portfolio_value = cerebro.broker.getvalue()
                pnl = end_portfolio_value - start_portfolio_value
                print(f'Starting Portfolio Value: {start_portfolio_value:2f}')
                print(f'Final Portfolio Value: {end_portfolio_value:2f}')
                print(f'PnL: {pnl:.2f}')

                # Analyzer Results
                print('Sharpe Ratio:', H.analyzers.mysharpe.get_analysis())
                print('Draw Down:', H.analyzers.mydrawdown.get_analysis())

                # Plot Results
                cerebro.plot()
                # figure.savefig('example.png')
                # cerebro.plot(savefig=True, figfilename='backtrader-plot.png')
                
            else :
                print('Invalid symbol')
            
    except Exception as e:
        print(e)