import os, sys, argparse
import config
import sqlite3
import pandas as pd
import backtrader as bt
from backtrader import Cerebro
from backtesting_settings import strategy_settings_dictionary

from strategies.GoldenCross import GoldenCross
from strategies.BuyHold import BuyHold
from strategies.BuyDip import BuyDip
from strategies.Dictum import Dictum
from strategies.TripleH import TripleH

strategies = {
    'ma':GoldenCross,
    'bnh':BuyHold,
    'dip':BuyDip,
    'dic':Dictum,
    '3h':TripleH
}

optimizer = False

def parse_user_input():
    parser = argparse.ArgumentParser()
    parser.add_argument('type',help="what kind of asset : ['stock','crypto','crypto15','futures15','futures1']",type=str)
    parser.add_argument('symbol',help='which symbol to test',type=str)
    parser.add_argument('strategy',help=f'which strategy to test : {list(strategies.keys())}',type=str)
    parser.add_argument('cash',help='set cash amount',type=str)
    parser.add_argument('risk',help='percentage of budget to risk',type=float)
    args = parser.parse_args()
    return args

def print_arguments(args):
    print(f'\n====================================\n')
    print(f'Command Line Arguments :')
    for k,v in args._get_kwargs():
        print(f'* {k} : {v}')
    print(f'\n====================================\n')
    
def get_price_series(type, symbol, con):
    if type == 'stock':
        sql_string = f"SELECT * FROM stockdaily WHERE symbol = '{symbol}' ORDER BY datetime"
        price_series = pd.read_sql(sql_string,con).assign(datetime = lambda x : pd.to_datetime(x.datetime)).set_index('datetime')
    elif type == 'crypto':
        sql_string = f"SELECT * FROM cryptodaily WHERE symbol = '{symbol}' ORDER BY datetime"
        price_series = pd.read_sql(sql_string,con).assign(datetime = lambda x : pd.to_datetime(x.datetime)).set_index('datetime')
    elif type == 'crypto15':
        sql_string = f"SELECT * FROM crypto WHERE symbol = '{symbol}' ORDER BY datetime"
        price_series = pd.read_sql(sql_string,con).assign(datetime = lambda x : pd.to_datetime(x.datetime)).set_index('datetime')
    elif type == 'futures15':
        sql_string = f"SELECT * FROM futures15 WHERE symbol = '{symbol}' and openTime >= '2021-08-01' and openTime < '2021-08-13 15:30:00' ORDER BY openTimets"
        price_series = pd.read_sql(sql_string,con).assign(openTime = lambda x : pd.to_datetime(x.openTime)).set_index('openTime')
    elif type == 'futures1':
        sql_string = f"SELECT * FROM futures1  WHERE symbol = '{symbol}' and openTime >= '2021-08-01' and openTime < '2021-08-13 15:30:00' ORDER BY openTimets"
        price_series = pd.read_sql(sql_string,con).assign(openTime = lambda x : pd.to_datetime(x.openTime)).set_index('openTime')
    return price_series


if __name__ == '__main__':

    args = parse_user_input()
    print_arguments(args)
    
    if args.strategy not in strategies.keys():
        print(f'Invalid strategy. Must be one of {list(strategies.keys())}') 
        sys.exit()
    else:
        # strategy_settings = strategy_settings_dictionary['dic']
        strategy_settings = strategy_settings_dictionary[args.strategy]
        # check whether any of the parameters passed is list
        # if so, enable cerebro.optstrategy instead of cerebro.addstrategy
        if any([isinstance(p,list) for p in strategy_settings.values()]):
            optimizer = True
            print(f'OPTIMIZER IS NOW OPEN')

    try:
        con = sqlite3.connect(config.DB_NAME)
        # price_series = get_price_series(type,symbol,con)
        price_series = get_price_series(args.type,args.symbol,con)
        print(f'> backtesting.py : fetched {price_series.shape[0]} rows for {args.symbol}')
        print(f'\n====================================\n')
    except Exception as e:
        print(f'DB CONNECTION ERROR')
        print(e)
        
        
    try:
        if not isinstance(price_series,pd.DataFrame):
            print('Expected Dataframe input ; EXITING ...')
            sys.exit()
        else:
            if price_series.empty:
                print('Received empty Dataframe ; EXITING ...')
                sys.exit()
            else:
                
                # initiate cerebro
                # TODO check quicknotify
                # cerebro = bt.Cerebro(quicknotify=True)
                # check cheat_on_open
                # cerebro = bt.Cerebro(cheat_on_open=True)
                cerebro = bt.Cerebro(cheat_on_open=True, quicknotify=True)
                # cerebro = bt.Cerebro()
                cerebro.broker.setcash(int(args.cash))
                start_portfolio_value = cerebro.broker.getvalue()
                
                # Add Dataset(s)
                feed = bt.feeds.PandasData(dataname=price_series)
                cerebro.adddata(feed)
                cerebro.broker.setcommission(commission=0.001, leverage=10)
                if args.type=='futures1':
                    cerebro.resampledata(feed, timeframe=bt.TimeFrame.Minutes, compression=15)
                    # TODO Resample also to 60 minutes for emergency exits
                    # cerebro.resampledata(feed, timeframe=bt.TimeFrame.Minutes, compression=60)

                # TODO make the optimizer run for lists of symbols and settings and return with results per combination
                # Add Strategy or Optimizer according to parameter input
                if not optimizer:
                    
                    if args.strategy == 'ma':
                        cerebro.addstrategy(
                            strategies[args.strategy],
                            symbol=args.symbol,
                            risk=args.risk,
                            cash=args.cash,
                            fast=strategy_settings.get('fast'),
                            slow=strategy_settings.get('slow')
                                            )
                    elif args.strategy == 'dic':
                        cerebro.addstrategy(
                            strategies[args.strategy],
                            symbol=args.symbol,
                            risk=args.risk,
                            cash=args.cash,
                            wma_period=strategy_settings.get('wma_period'),
                            stoploss=strategy_settings.get('stoploss'),
                            takeprofit=strategy_settings.get('takeprofit'),
                            short_positions=strategy_settings.get('short_positions'),
                            period=strategy_settings.get('period'),
                            factor=strategy_settings.get('factor'),
                            multiplier=strategy_settings.get('multiplier')
                            )
                                            
                else:
                        
                    # add output file
                    # cerebro.addwriter(bt.WriterFile, csv=True)
                    
                    if args.strategy == 'ma':
                        cerebro.optstrategy(
                            strategies[args.strategy],
                            symbol=args.symbol,
                            risk=args.risk,
                            cash=args.cash,
                            fast=strategy_settings.get('fast'),
                            slow=strategy_settings.get('slow')
                            )
                    elif args.strategy == 'dic':
                        cerebro.optstrategy(
                            strategies[args.strategy],
                            symbol=args.symbol,
                            risk=args.risk,
                            cash=args.cash,
                            wma_period=strategy_settings.get('wma_period'),
                            stoploss=strategy_settings.get('stoploss'),
                            takeprofit=strategy_settings.get('takeprofit'),
                            short_positions=strategy_settings.get('short_positions'),
                            period=strategy_settings.get('period'),
                            factor=strategy_settings.get('factor'),
                            multiplier=strategy_settings.get('multiplier')
                            )
                    
                    
                # Add Analyzer
                # cerebro.addanalyzer(bt.analyzers.DrawDown, _name='mydrawdown')
                # cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='mysharpe')
                # cerebro.addanalyzer(bt.analyzers.Returns, _name='myreturns')
                # cerebro.addanalyzer(bt.analyzers.PositionsValue, _name='mypositionsvalue')
                # cerebro.addanalyzer(bt.analyzers.PyFolio, _name='mypyfolio')
                # cerebro.addanalyzer(bt.analyzers.PeriodStats, _name='myperiodstats')
                # cerebro.addanalyzer(bt.analyzers.SQN, _name='mysqn')
                # cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='mytradeanalyzer')
                # cerebro.addanalyzer(bt.analyzers.Transactions, _name='mytransactions')

                # Run
                R = cerebro.run()
                H = R[0]
                
                # Analyzer Results
                # https://www.backtrader.com/docu/analyzers-reference/
                # print('Draw Down:', H.analyzers.mydrawdown.get_analysis())
                # print('Sharpe Ratio:', H.analyzers.mysharpe.get_analysis())
                # print('Returns:', H.analyzers.myreturns.get_analysis())
                # print('Position Value:', H.analyzers.mypositionsvalue.get_analysis())
                # print('PyFolio:', H.analyzers.mypyfolio.get_analysis())
                # print('Period Stats:', H.analyzers.myperiodstats.get_analysis())
                # print('SQN:', H.analyzers.mysqn.get_analysis())
                # print('Trade Analyzer:', H.analyzers.mytradeanalyzer.get_analysis())
                # print('Transactions:', H.analyzers.mytransactions.get_analysis())

                if not optimizer:
                    
                    # Basic Results
                    end_portfolio_value = cerebro.broker.getvalue()
                    pnl = end_portfolio_value - start_portfolio_value
                    print(f'\nStarting Portfolio Value: {start_portfolio_value:.2f}')
                    print(f'Final Portfolio Value: {end_portfolio_value:.2f}')
                    print(f'PnL: {pnl:.2f} - {(pnl/end_portfolio_value)*100:.2f}%')
                    # TODO print(f'Accuracy Rate: {accuracy_rate}/{total_signals} - {(accuracy_rate/total_signals)*100:.2f}%')
                    
                    # Plot Results
                    cerebro.plot()
    
    except Exception as e:
        print('Error in cerebro section ; EXITING ...')
        print(e)
        # sys.exit()
