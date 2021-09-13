import os, sys, argparse, time
from datetime import datetime
import config
import sqlite3
import pandas as pd
import backtrader as bt
from backtrader import Cerebro
from backtesting_settings import strategy_settings_dictionary, strategy_analyzers

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
optreturn = True

# type = 'futures1'
# symbol = 'ETHUSDT'
# strategy = '3h'
# cash = 10000
# risk = 0.025
# datasize = 10000

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
    
def get_price_series(type, symbol, con, datasize):
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
        # sql_string = f"SELECT * FROM futures1  WHERE symbol = '{symbol}' and openTime >= '2020-09-01' and openTime < '2021-08-31 15:30:00' ORDER BY openTimets"
        sql_string = f"SELECT * FROM futures1  WHERE symbol = '{symbol}' ORDER BY openTimets DESC limit {datasize}"
        price_series = pd.read_sql(sql_string,con).assign(openTime = lambda x : pd.to_datetime(x.openTime)).sort_values(by=['openTime']).set_index('openTime')
    return price_series


if __name__ == '__main__':

    start = time.time()
    
    args = parse_user_input()
    print_arguments(args)
    
    if args.strategy not in strategies.keys():
        print(f'Invalid strategy. Must be one of {list(strategies.keys())}') 
        sys.exit()
    else:
        # strategy_settings = strategy_settings_dictionary['dic']
        # strategy_settings = strategy_settings_dictionary['3h']
        strategy_settings = strategy_settings_dictionary[args.strategy]
        datasize = strategy_settings['datasize']
        # check whether any of the parameters passed is list
        # if so, enable cerebro.optstrategy instead of cerebro.addstrategy
        if any([isinstance(p,list) for p in strategy_settings.values()]):
            optimizer = True
            print(f'OPTIMIZER IS NOW OPEN')

    try:
        con = sqlite3.connect(config.DB_NAME)
        # price_series = get_price_series(type,symbol,con,datasize)
        price_series = get_price_series(args.type,args.symbol,con,datasize)
        print(f'> backtesting.py : fetched latest {price_series.shape[0]} rows for {args.symbol}')
        print(f'> backtesting.py : period from {price_series.index.min()} to {price_series.index.max()}')
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
                cerebro = bt.Cerebro()
                # cerebro.broker.setcash(cash)
                cerebro.broker.setcash(int(args.cash))
                start_portfolio_value = cerebro.broker.getvalue()
                
                # Add Dataset(s)
                feed = bt.feeds.PandasData(dataname=price_series)
                cerebro.adddata(feed)
                cerebro.broker.setcommission(commission=0.00, leverage=1)
                if args.type=='futures1':
                    cerebro.resampledata(feed, timeframe=bt.TimeFrame.Minutes, compression=15)
                    
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
                            # strategies['dic'],
                            # symbol = symbol,
                            # risk = risk,
                            # cash = cash,
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
                            multiplier=strategy_settings.get('multiplier'),
                            printlog=strategy_settings.get('printlog')
                            )
                        
                    elif args.strategy == '3h':
                        cerebro.addstrategy(
                            # strategies['3h'],
                            # symbol = symbol,
                            # risk = risk,
                            # cash = cash,
                            strategies[args.strategy],
                            symbol=args.symbol,
                            risk=args.risk,
                            cash=args.cash,
                            stoploss=strategy_settings.get('stoploss'),
                            takeprofit=strategy_settings.get('takeprofit'),
                            short_positions=strategy_settings.get('short_positions'),
                            factor=strategy_settings.get('factor'),
                            atr_period=strategy_settings.get('atr_period'),
                            pivot_period=strategy_settings.get('pivot_period'),
                            printlog=strategy_settings.get('printlog')
                            )
                                            
                else:
                        
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
                            # strategies['dic'],
                            # symbol = symbol,
                            # risk = risk,
                            # cash = cash,
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
                            multiplier=strategy_settings.get('multiplier'),
                            printlog=strategy_settings.get('printlog')
                            )
                        
                    elif args.strategy == '3h':
                        cerebro.optstrategy(
                            # strategies['3h'],
                            # symbol = symbol,
                            # risk = risk,
                            # cash = cash,
                            strategies[args.strategy],
                            symbol=args.symbol,
                            risk=args.risk,
                            cash=args.cash,
                            stoploss=strategy_settings.get('stoploss'),
                            takeprofit=strategy_settings.get('takeprofit'),
                            short_positions=strategy_settings.get('short_positions'),
                            factor=strategy_settings.get('factor'),
                            atr_period=strategy_settings.get('atr_period'),
                            pivot_period=strategy_settings.get('pivot_period'),
                            printlog=strategy_settings.get('printlog')
                            )
                    
                    
                # Add Analyzer
                if 'drawdown' in strategy_analyzers:
                    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
                if 'sharpe' in strategy_analyzers:
                    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
                if 'returns' in strategy_analyzers:
                    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
                if 'periodstats' in strategy_analyzers:
                    cerebro.addanalyzer(bt.analyzers.PeriodStats, _name='periodstats')
                if 'tradeanalyzer' in strategy_analyzers:
                    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='tradeanalyzer')

                # cerebro.addanalyzer(bt.analyzers.PositionsValue, _name='mypositionsvalue')
                # cerebro.addanalyzer(bt.analyzers.PyFolio, _name='mypyfolio')
                # cerebro.addanalyzer(bt.analyzers.PeriodStats, _name='myperiodstats')
                # cerebro.addanalyzer(bt.analyzers.SQN, _name='mysqn')
                # cerebro.addanalyzer(bt.analyzers.Transactions, _name='mytransactions')
   
                # Cerebro Results
                # Optimizer Results
                if optimizer:
                    
                    # w/ optreturn  
                    if optreturn:
                        # Run
                        R = cerebro.run(stdstats=False)
                        print(f'>>> Cerebro finished {len(R)} trials !!! <<<')
                        # Collect results                        
                        results = [
                            [
                                r[0].params.symbol
                                ,r[0].params.cash
                                ,r[0].params.risk
                                ,r[0].params.factor
                                ,r[0].params.multiplier
                                ,r[0].params.wma_period
                                ,r[0].params.period
                                ,r[0].params.short_positions
                                ,r[0].params.stoploss
                                ,r[0].params.takeprofit
                                # tradeanalyzer
                                ,r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['total']['total']
                                ,r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['total']['open']
                                ,r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['total']['closed']
                                ,r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['streak']['won']['longest']
                                ,r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['streak']['lost']['longest']
                                ,r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['pnl']['gross']['total']
                                ,r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['pnl']['gross']['average']
                                ,r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['pnl']['net']['total']
                                ,r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['pnl']['net']['average']
                                ,r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['won']['total']
                                ,r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['won']['pnl']['total']
                                ,r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['won']['pnl']['average']
                                ,r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['won']['pnl']['max']
                                ,r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['lost']['total']
                                ,r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['lost']['pnl']['total']
                                ,r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['lost']['pnl']['average']
                                ,r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['lost']['pnl']['max']
                                ,r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['long']['total']
                                ,r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['long']['pnl']['total']
                                ,r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['long']['pnl']['average']
                                ,r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['long']['pnl']['won']['total']
                                ,r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['long']['pnl']['won']['average']
                                ,r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['long']['pnl']['won']['max']
                                ,r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['long']['pnl']['lost']['total']
                                ,r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['long']['pnl']['lost']['average']
                                ,r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['long']['pnl']['lost']['max']
                                ,r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['short']['total']
                                ,r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['short']['pnl']['total']
                                ,r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['short']['pnl']['average']
                                ,r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['short']['pnl']['won']['total']
                                ,r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['short']['pnl']['won']['average']
                                ,r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['short']['pnl']['won']['max']
                                ,r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['short']['pnl']['lost']['total']
                                ,r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['short']['pnl']['lost']['average']
                                ,r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['short']['pnl']['lost']['max']
                                # drawdown analyzer
                                ,r[0].analyzers.getbyname('drawdown').get_analysis()['drawdown']
                                ,r[0].analyzers.getbyname('drawdown').get_analysis()['moneydown']
                                ,r[0].analyzers.getbyname('drawdown').get_analysis()['max']['drawdown']
                                ,r[0].analyzers.getbyname('drawdown').get_analysis()['max']['moneydown']
                                # returns
                                ,r[0].analyzers.getbyname('returns').get_analysis()['rtot']
                                ,r[0].analyzers.getbyname('returns').get_analysis()['ravg']
                                ,r[0].analyzers.getbyname('returns').get_analysis()['rnorm']
                                ,r[0].analyzers.getbyname('returns').get_analysis()['rnorm100']
                                ]
                            for r in R]
                        
                        columns = [
                            'symbol','starting_cash','risk',
                            'factor','multiplier','wma_period','period','short_positions','stoploss','takeprofit',
                            'td_total_total','td_total_open','td_total_closed',
                            'td_streak_won_longest','td_streak_lost_longest','td_pnl_gross_total','td_pnl_gross_average','td_pnl_net_total','td_pnl_net_average',
                            'td_won_total','td_won_pnl_total','td_won_pnl_average','td_won_pnl_max',
                            'td_lost_total','td_lost_pnl_total','td_lost_pnl_average','td_lost_pnl_max',
                            'td_long_total','td_long_pnl_total','td_long_pnl_average','td_long_pnl_won_total','td_long_pnl_won_average','td_long_pnl_won_max',
                            'td_long_pnl_lost_total','td_long_pnl_lost_average','td_long_pnl_lost_max',
                            'td_short_total','td_short_pnl_total','td_short_pnl_average','td_short_pnl_won_total','td_short_pnl_won_average','td_short_pnl_won_max',
                            'td_short_pnl_lost_total','td_short_pnl_lost_average','td_short_pnl_lost_max',
                            'dd_dd','dd_md','dd_max_dd','dd_max_md',
                            'rt_rtot','rt_ravg','rt_rnorm','rt_rnorm100']
                
                        dfr = pd.DataFrame(results,columns = columns).sort_values(by=['td_pnl_gross_total'],ascending=False)
                        
                        dfr.insert(0, "strategy", args.strategy)
                        dfr.insert(4, "indicative_position_size", (dfr['risk'] * dfr['starting_cash'].astype(int))/dfr['stoploss'].astype(float))
                        dfr.insert(5, "stake_in_usd", (dfr['risk'] * dfr['starting_cash'].astype(int)))
                        dfr.insert(6, "accuracy", dfr['td_won_total']/dfr['td_total_total'])
                        dfr.insert(7, "total_signals", dfr['td_total_total'])
                        dfr.insert(8, "gross_profit_pct", dfr['td_pnl_gross_total']/dfr['starting_cash'].astype(int))
                        dfr.insert(9, "net_profit_pct", dfr['td_pnl_net_total']/dfr['starting_cash'].astype(int))
                        
                        timetag = datetime.now().strftime("%Y%m%d_%H%M%S")
                        dfr.to_csv(f'./optimization_results/{args.strategy}_{timetag}_{args.symbol}.csv', index=False)
                    
                    # w/o optreturn    
                    else:
                        
                        R = cerebro.run(stdstats=False,optreturn=False)
                        print(f'>>> Cerebro finished {len(R)} trials !!! <<<')
                        
                        results = [
                        [
                        args.risk
                        ,args.symbol
                        ,r[0].starting_cash
                        ,r[0].pnl
                        ,r[0].total_signals
                        ,r[0].accuracy_rate
                        ,r[0].params.wma_period
                        ,r[0].params.stoploss
                        ,r[0].params.takeprofit
                        ,r[0].params.short_positions
                        ,r[0].params.period
                        ,r[0].params.factor
                        ,r[0].params.multiplier
                        # tradeanalyzer
                        ,r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['total']['total']
                        ,r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['total']['open']
                        ,r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['total']['closed']
                        ,r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['streak']['won']['longest']
                        ,r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['streak']['lost']['longest']
                        ,r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['pnl']['gross']['total']
                        ,r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['pnl']['gross']['average']
                        ,r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['pnl']['net']['total']
                        ,r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['pnl']['net']['average']
                        ,r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['won']['total']
                        ,r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['won']['pnl']['total']
                        ,r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['won']['pnl']['average']
                        ,r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['won']['pnl']['max']
                        ,r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['lost']['total']
                        ,r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['lost']['pnl']['total']
                        ,r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['lost']['pnl']['average']
                        ,r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['lost']['pnl']['max']
                        ,r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['long']['total']
                        ,r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['long']['pnl']['total']
                        ,r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['long']['pnl']['average']
                        ,r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['long']['pnl']['won']['total']
                        ,r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['long']['pnl']['won']['average']
                        ,r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['long']['pnl']['won']['max']
                        ,r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['long']['pnl']['lost']['total']
                        ,r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['long']['pnl']['lost']['average']
                        ,r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['long']['pnl']['lost']['max']
                        ,r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['short']['total']
                        ,r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['short']['pnl']['total']
                        ,r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['short']['pnl']['average']
                        ,r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['short']['pnl']['won']['total']
                        ,r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['short']['pnl']['won']['average']
                        ,r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['short']['pnl']['won']['max']
                        ,r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['short']['pnl']['lost']['total']
                        ,r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['short']['pnl']['lost']['average']
                        ,r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['short']['pnl']['lost']['max']
                        # drawdown analyzer
                        ,r[0].analyzers.getbyname('drawdown').get_analysis()['drawdown']
                        ,r[0].analyzers.getbyname('drawdown').get_analysis()['moneydown']
                        ,r[0].analyzers.getbyname('drawdown').get_analysis()['max']['drawdown']
                        ,r[0].analyzers.getbyname('drawdown').get_analysis()['max']['moneydown']
                        # returns
                        ,r[0].analyzers.getbyname('returns').get_analysis()['rtot']
                        ,r[0].analyzers.getbyname('returns').get_analysis()['ravg']
                        ,r[0].analyzers.getbyname('returns').get_analysis()['rnorm']
                        ,r[0].analyzers.getbyname('returns').get_analysis()['rnorm100']]
                        for r in R]

                        columns = [
                            'risk','symbol',
                            'starting_cash','pnl','total_signals','accuracy_rate',
                            'p_wma_period','p_stoploss','p_takeprofit','p_short_positions','p_period','p_factor','p_multiplier',
                            'td_total_total','td_total_open','td_total_closed',
                            'td_streak_won_longest','td_streak_lost_longest','td_pnl_gross_total','td_pnl_gross_average','td_pnl_net_total','td_pnl_net_average',
                            'td_won_total','td_won_pnl_total','td_won_pnl_average','td_won_pnl_max',
                            'td_lost_total','td_lost_pnl_total','td_lost_pnl_average','td_lost_pnl_max',
                            'td_long_total','td_long_pnl_total','td_long_pnl_average','td_long_pnl_won_total','td_long_pnl_won_average','td_long_pnl_won_max',
                            'td_long_pnl_lost_total','td_long_pnl_lost_average','td_long_pnl_lost_max',
                            'td_short_total','td_short_pnl_total','td_short_pnl_average','td_short_pnl_won_total','td_short_pnl_won_average','td_short_pnl_won_max',
                            'td_short_pnl_lost_total','td_short_pnl_lost_average','td_short_pnl_lost_max',
                            'dd_dd','dd_md','dd_max_dd','dd_max_md',
                            'rt_rtot','rt_ravg','rt_rnorm','rt_rnorm100']
                
                        dfr = pd.DataFrame(results,columns = columns).sort_values(by=['td_pnl_gross_total'],ascending=False)
                        
                        dfr.insert(0, "strategy", args.strategy)
                        dfr.insert(3, "indicative_position_size", (dfr['risk'] * dfr['starting_cash'].astype(int))/dfr['stoploss'].astype(float))
                        dfr.insert(4, "stake_in_usd", (dfr['risk'] * dfr['starting_cash'].astype(int)))
                        dfr.insert(5, "accuracy", dfr['td_won_total']/dfr['td_total_total'])
                        dfr.insert(6, "total_signals", dfr['td_total_total'])
                        dfr.insert(7, "gross_profit_pct", dfr['td_pnl_gross_total']/dfr['starting_cash'].astype(int))
                        dfr.insert(8, "net_profit_pct", dfr['td_pnl_net_total']/dfr['starting_cash'].astype(int))
                        
                        timetag = datetime.now().strftime("%Y%m%d_%H%M%S")
                        dfr.to_csv(f'./optimization_results/{args.strategy}_{timetag}_{args.symbol}.csv', index=False)

                # Results w/o optimizer
                else:
                    
                    cerebro.run()
                    # Basic Results
                    end_portfolio_value = cerebro.broker.getvalue()
                    pnl = end_portfolio_value - start_portfolio_value
                    print(f'\nStarting Portfolio Value: {start_portfolio_value:.2f}')
                    print(f'Final Portfolio Value: {end_portfolio_value:.2f}')
                    print(f'PnL: {pnl:.2f} - {(pnl/end_portfolio_value)*100:.2f}%')
                    
                    # Analyzer Results
                    # https://www.backtrader.com/docu/analyzers-reference/
                    # print('Draw Down:', H.analyzers.mydrawdown.get_analysis())
                    # print('Sharpe Ratio:', H.analyzers.mysharpe.get_analysis())
                    # print('Returns:', H.analyzers.myreturns.get_analysis())
                    # print('Returns:', H.analyzers.myreturns.get_analysis())
                    # print('Position Value:', H.analyzers.mypositionsvalue.get_analysis())
                    # print('PyFolio:', H.analyzers.mypyfolio.get_analysis())
                    # print('Period Stats:', H.analyzers.myperiodstats.get_analysis())
                    # print('SQN:', H.analyzers.mysqn.get_analysis())
                    # print('Trade Analyzer:', H.analyzers.mytradeanalyzer.get_analysis())
                    # print('Transactions:', H.analyzers.mytransactions.get_analysis())
                    
                    # Plot Results
                    cerebro.plot()
    
    except Exception as e:
        print('Error in cerebro section ; EXITING ...')
        print(e)
        # sys.exit()

    end = time.time()
    print(f'Total execution time {end-start}')