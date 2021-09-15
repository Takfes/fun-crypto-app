import requests, time, calendar, os
from datetime import datetime
import pandas as pd
from tqdm import tqdm
import ccxt
import time


def parse_cerebro(cerebro_results,strategy,optreturn=True):
        
    # IS OPTIMIZER RESULTS
    if isinstance(cerebro_results[0],list):
        
        # GATHER OPTRETURN ITEMS
        contents = list(vars(cerebro_results[0][0]).keys())
        
        # IF OPTRETURN
        if (len(contents)==4) | optreturn :
            
            if strategy == 'dic':
        
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
                        ,r[0].params.emergency_exit
                        ,r[0].params.rsi_value
                        ,r[0].params.stoploss
                        ,r[0].params.takeprofit
                        ,r[0].params.trstop
                        ,r[0].params.trstop_percent
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
                    for r in cerebro_results]
                
                columns = [
                    'symbol','starting_cash','risk',
                    'factor','multiplier','wma_period','period','short_positions','emergency_exit','rsi_value','stoploss','takeprofit','trstop','trstop_percent',
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
                
                dfr.insert(3, "indicative_position_size", (dfr['risk'] * dfr['starting_cash'].astype(int))/dfr['stoploss'].astype(float))
                dfr.insert(4, "stake_in_usd", (dfr['risk'] * dfr['starting_cash'].astype(int)))
                dfr.insert(5, "accuracy", dfr['td_won_total']/dfr['td_total_total'])
                dfr.insert(6, "total_signals", dfr['td_total_total'])
                dfr.insert(7, "gross_profit_pct", dfr['td_pnl_gross_total']/dfr['starting_cash'].astype(int))
                dfr.insert(8, "net_profit_pct", dfr['td_pnl_net_total']/dfr['starting_cash'].astype(int))
            
            
            if strategy == '3h':

                results = [
                    [
                        r[0].params.symbol
                        , r[0].params.cash
                        , r[0].params.risk
                        , r[0].params.factor
                        , r[0].params.atr_period
                        , r[0].params.pivot_period
                        , r[0].params.short_positions
                        , r[0].params.stoploss
                        , r[0].params.takeprofit
                        , r[0].params.trstop
                        , r[0].params.trstop_percent
                        # tradeanalyzer
                        , r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['total']['total']
                        , r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['total']['open']
                        , r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['total']['closed']
                        , r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['streak']['won']['longest']
                        , r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['streak']['lost']['longest']
                        , r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['pnl']['gross']['total']
                        , r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['pnl']['gross']['average']
                        , r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['pnl']['net']['total']
                        , r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['pnl']['net']['average']
                        , r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['won']['total']
                        , r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['won']['pnl']['total']
                        , r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['won']['pnl']['average']
                        , r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['won']['pnl']['max']
                        , r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['lost']['total']
                        , r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['lost']['pnl']['total']
                        , r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['lost']['pnl']['average']
                        , r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['lost']['pnl']['max']
                        , r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['long']['total']
                        , r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['long']['pnl']['total']
                        , r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['long']['pnl']['average']
                        , r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['long']['pnl']['won']['total']
                        , r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['long']['pnl']['won']['average']
                        , r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['long']['pnl']['won']['max']
                        , r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['long']['pnl']['lost']['total']
                        , r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['long']['pnl']['lost']['average']
                        , r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['long']['pnl']['lost']['max']
                        , r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['short']['total']
                        , r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['short']['pnl']['total']
                        , r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['short']['pnl']['average']
                        , r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['short']['pnl']['won']['total']
                        , r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['short']['pnl']['won']['average']
                        , r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['short']['pnl']['won']['max']
                        , r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['short']['pnl']['lost']['total']
                        , r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['short']['pnl']['lost']['average']
                        , r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['short']['pnl']['lost']['max']
                        # drawdown analyzer
                        , r[0].analyzers.getbyname('drawdown').get_analysis()['drawdown']
                        , r[0].analyzers.getbyname('drawdown').get_analysis()['moneydown']
                        , r[0].analyzers.getbyname('drawdown').get_analysis()['max']['drawdown']
                        , r[0].analyzers.getbyname('drawdown').get_analysis()['max']['moneydown']
                        # returns
                        , r[0].analyzers.getbyname('returns').get_analysis()['rtot']
                        , r[0].analyzers.getbyname('returns').get_analysis()['ravg']
                        , r[0].analyzers.getbyname('returns').get_analysis()['rnorm']
                        , r[0].analyzers.getbyname('returns').get_analysis()['rnorm100']
                    ]
                    for r in cerebro_results]

                columns = [
                    'symbol', 'starting_cash', 'risk',
                    'factor', 'atr_period', 'pivot_period', 'short_positions', 'stoploss', 'takeprofit', 'trstop', 'trstop_percent',
                    'td_total_total', 'td_total_open', 'td_total_closed',
                    'td_streak_won_longest', 'td_streak_lost_longest', 'td_pnl_gross_total', 'td_pnl_gross_average',
                    'td_pnl_net_total', 'td_pnl_net_average',
                    'td_won_total', 'td_won_pnl_total', 'td_won_pnl_average', 'td_won_pnl_max',
                    'td_lost_total', 'td_lost_pnl_total', 'td_lost_pnl_average', 'td_lost_pnl_max',
                    'td_long_total', 'td_long_pnl_total', 'td_long_pnl_average', 'td_long_pnl_won_total',
                    'td_long_pnl_won_average', 'td_long_pnl_won_max',
                    'td_long_pnl_lost_total', 'td_long_pnl_lost_average', 'td_long_pnl_lost_max',
                    'td_short_total', 'td_short_pnl_total', 'td_short_pnl_average', 'td_short_pnl_won_total',
                    'td_short_pnl_won_average', 'td_short_pnl_won_max',
                    'td_short_pnl_lost_total', 'td_short_pnl_lost_average', 'td_short_pnl_lost_max',
                    'dd_dd', 'dd_md', 'dd_max_dd', 'dd_max_md',
                    'rt_rtot', 'rt_ravg', 'rt_rnorm', 'rt_rnorm100']

                dfr = pd.DataFrame(results, columns=columns).sort_values(by=['td_pnl_gross_total'], ascending=False)

                dfr.insert(3, "indicative_position_size",
                           (dfr['risk'] * dfr['starting_cash'].astype(int)) / dfr['stoploss'].astype(float))
                dfr.insert(4, "stake_in_usd", (dfr['risk'] * dfr['starting_cash'].astype(int)))
                dfr.insert(5, "accuracy", dfr['td_won_total'] / dfr['td_total_total'])
                dfr.insert(6, "total_signals", dfr['td_total_total'])
                dfr.insert(7, "gross_profit_pct", dfr['td_pnl_gross_total'] / dfr['starting_cash'].astype(int))
                dfr.insert(8, "net_profit_pct", dfr['td_pnl_net_total'] / dfr['starting_cash'].astype(int))

            else:

                print(f'No parsing method has been set')

        # IF OPTRETURN FALSE    
        else:
            
            if strategy == 'dic':
                
                results = [
                    [
                    r[0].params.symbol
                    ,r[0].params.cash
                    ,r[0].starting_cash
                    ,r[0].pnl
                    ,r[0].total_signals
                    ,r[0].accuracy_rate
                    ,r[0].params.wma_period
                    ,r[0].params.stoploss
                    ,r[0].params.takeprofit
                    ,r[0].params.trstop
                    ,r[0].params.trstop_percent
                    ,r[0].params.short_positions
                    ,r[0].params.emergency_exit
                    ,r[0].params.rsi_value
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
                    for r in cerebro_results]

                columns = [
                    'risk','symbol',
                    'starting_cash','pnl','total_signals','accuracy_rate',
                    'p_wma_period','p_stoploss','p_takeprofit','p_trstop','p_trstop_percent','p_short_positions','emergency_exit','rsi_value','p_period','p_factor','p_multiplier',
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
                
                dfr.insert(3, "indicative_position_size", (dfr['risk'] * dfr['starting_cash'].astype(int))/dfr['stoploss'].astype(float))
                dfr.insert(4, "stake_in_usd", (dfr['risk'] * dfr['starting_cash'].astype(int)))
                dfr.insert(5, "accuracy", dfr['td_won_total']/dfr['td_total_total'])
                dfr.insert(6, "total_signals", dfr['td_total_total'])
                dfr.insert(7, "gross_profit_pct", dfr['td_pnl_gross_total']/dfr['starting_cash'].astype(int))
                dfr.insert(8, "net_profit_pct", dfr['td_pnl_net_total']/dfr['starting_cash'].astype(int))
            
            if strategy == '3h':

                results = [
                    [
                        r[0].params.symbol
                        , r[0].params.cash
                        , r[0].starting_cash
                        , r[0].pnl
                        , r[0].total_signals
                        , r[0].accuracy_rate
                        , r[0].params.atr_period
                        , r[0].params.stoploss
                        , r[0].params.takeprofit
                        , r[0].params.trstop
                        , r[0].params.trstop_percent
                        , r[0].params.short_positions
                        , r[0].params.pivot_period
                        , r[0].params.factor
                        # tradeanalyzer
                        , r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['total']['total']
                        , r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['total']['open']
                        , r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['total']['closed']
                        , r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['streak']['won']['longest']
                        , r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['streak']['lost']['longest']
                        , r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['pnl']['gross']['total']
                        , r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['pnl']['gross']['average']
                        , r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['pnl']['net']['total']
                        , r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['pnl']['net']['average']
                        , r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['won']['total']
                        , r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['won']['pnl']['total']
                        , r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['won']['pnl']['average']
                        , r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['won']['pnl']['max']
                        , r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['lost']['total']
                        , r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['lost']['pnl']['total']
                        , r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['lost']['pnl']['average']
                        , r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['lost']['pnl']['max']
                        , r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['long']['total']
                        , r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['long']['pnl']['total']
                        , r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['long']['pnl']['average']
                        , r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['long']['pnl']['won']['total']
                        , r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['long']['pnl']['won']['average']
                        , r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['long']['pnl']['won']['max']
                        , r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['long']['pnl']['lost']['total']
                        , r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['long']['pnl']['lost']['average']
                        , r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['long']['pnl']['lost']['max']
                        , r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['short']['total']
                        , r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['short']['pnl']['total']
                        , r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['short']['pnl']['average']
                        , r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['short']['pnl']['won']['total']
                        , r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['short']['pnl']['won']['average']
                        , r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['short']['pnl']['won']['max']
                        , r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['short']['pnl']['lost']['total']
                        , r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['short']['pnl']['lost']['average']
                        , r[0].analyzers.getbyname('tradeanalyzer').get_analysis()['short']['pnl']['lost']['max']
                        # drawdown analyzer
                        , r[0].analyzers.getbyname('drawdown').get_analysis()['drawdown']
                        , r[0].analyzers.getbyname('drawdown').get_analysis()['moneydown']
                        , r[0].analyzers.getbyname('drawdown').get_analysis()['max']['drawdown']
                        , r[0].analyzers.getbyname('drawdown').get_analysis()['max']['moneydown']
                        # returns
                        , r[0].analyzers.getbyname('returns').get_analysis()['rtot']
                        , r[0].analyzers.getbyname('returns').get_analysis()['ravg']
                        , r[0].analyzers.getbyname('returns').get_analysis()['rnorm']
                        , r[0].analyzers.getbyname('returns').get_analysis()['rnorm100']]
                    for r in cerebro_results]

                columns = [
                    'risk', 'symbol',
                    'starting_cash', 'pnl', 'total_signals', 'accuracy_rate',
                    'p_atr_period', 'p_stoploss', 'p_takeprofit', 'p_trstop', 'p_trstop_percent', 'p_short_positions', 'p_pivot_period', 'p_factor',
                    'td_total_total', 'td_total_open', 'td_total_closed',
                    'td_streak_won_longest', 'td_streak_lost_longest', 'td_pnl_gross_total', 'td_pnl_gross_average',
                    'td_pnl_net_total', 'td_pnl_net_average',
                    'td_won_total', 'td_won_pnl_total', 'td_won_pnl_average', 'td_won_pnl_max',
                    'td_lost_total', 'td_lost_pnl_total', 'td_lost_pnl_average', 'td_lost_pnl_max',
                    'td_long_total', 'td_long_pnl_total', 'td_long_pnl_average', 'td_long_pnl_won_total',
                    'td_long_pnl_won_average', 'td_long_pnl_won_max',
                    'td_long_pnl_lost_total', 'td_long_pnl_lost_average', 'td_long_pnl_lost_max',
                    'td_short_total', 'td_short_pnl_total', 'td_short_pnl_average', 'td_short_pnl_won_total',
                    'td_short_pnl_won_average', 'td_short_pnl_won_max',
                    'td_short_pnl_lost_total', 'td_short_pnl_lost_average', 'td_short_pnl_lost_max',
                    'dd_dd', 'dd_md', 'dd_max_dd', 'dd_max_md',
                    'rt_rtot', 'rt_ravg', 'rt_rnorm', 'rt_rnorm100']

                dfr = pd.DataFrame(results, columns=columns).sort_values(by=['td_pnl_gross_total'], ascending=False)

                dfr.insert(3, "indicative_position_size",
                           (dfr['risk'] * dfr['starting_cash'].astype(int)) / dfr['stoploss'].astype(float))
                dfr.insert(4, "stake_in_usd", (dfr['risk'] * dfr['starting_cash'].astype(int)))
                dfr.insert(5, "accuracy", dfr['td_won_total'] / dfr['td_total_total'])
                dfr.insert(6, "total_signals", dfr['td_total_total'])
                dfr.insert(7, "gross_profit_pct", dfr['td_pnl_gross_total'] / dfr['starting_cash'].astype(int))
                dfr.insert(8, "net_profit_pct", dfr['td_pnl_net_total'] / dfr['starting_cash'].astype(int))

            else:

                print(f'No parsing method has been set')
    
    # NOT OPTIMIZER RESULTS       
    else:
        
        if strategy=='dic':
            
            results = [
                    [
                    r.params.symbol
                    ,r.params.cash
                    ,r.params.risk
                    ,r.params.factor
                    ,r.params.multiplier
                    ,r.params.wma_period
                    ,r.params.period
                    ,r.params.short_positions
                    ,r.params.emergency_exit
                    ,r.params.rsi_value
                    ,r.params.stoploss
                    ,r.params.takeprofit
                    ,r.params.trstop
                    ,r.params.trstop_percent
                    # tradeanalyzer
                    ,r.analyzers.getbyname('tradeanalyzer').get_analysis()['total']['total']
                    ,r.analyzers.getbyname('tradeanalyzer').get_analysis()['total']['open']
                    ,r.analyzers.getbyname('tradeanalyzer').get_analysis()['total']['closed']
                    ,r.analyzers.getbyname('tradeanalyzer').get_analysis()['streak']['won']['longest']
                    ,r.analyzers.getbyname('tradeanalyzer').get_analysis()['streak']['lost']['longest']
                    ,r.analyzers.getbyname('tradeanalyzer').get_analysis()['pnl']['gross']['total']
                    ,r.analyzers.getbyname('tradeanalyzer').get_analysis()['pnl']['gross']['average']
                    ,r.analyzers.getbyname('tradeanalyzer').get_analysis()['pnl']['net']['total']
                    ,r.analyzers.getbyname('tradeanalyzer').get_analysis()['pnl']['net']['average']
                    ,r.analyzers.getbyname('tradeanalyzer').get_analysis()['won']['total']
                    ,r.analyzers.getbyname('tradeanalyzer').get_analysis()['won']['pnl']['total']
                    ,r.analyzers.getbyname('tradeanalyzer').get_analysis()['won']['pnl']['average']
                    ,r.analyzers.getbyname('tradeanalyzer').get_analysis()['won']['pnl']['max']
                    ,r.analyzers.getbyname('tradeanalyzer').get_analysis()['lost']['total']
                    ,r.analyzers.getbyname('tradeanalyzer').get_analysis()['lost']['pnl']['total']
                    ,r.analyzers.getbyname('tradeanalyzer').get_analysis()['lost']['pnl']['average']
                    ,r.analyzers.getbyname('tradeanalyzer').get_analysis()['lost']['pnl']['max']
                    ,r.analyzers.getbyname('tradeanalyzer').get_analysis()['long']['total']
                    ,r.analyzers.getbyname('tradeanalyzer').get_analysis()['long']['pnl']['total']
                    ,r.analyzers.getbyname('tradeanalyzer').get_analysis()['long']['pnl']['average']
                    ,r.analyzers.getbyname('tradeanalyzer').get_analysis()['long']['pnl']['won']['total']
                    ,r.analyzers.getbyname('tradeanalyzer').get_analysis()['long']['pnl']['won']['average']
                    ,r.analyzers.getbyname('tradeanalyzer').get_analysis()['long']['pnl']['won']['max']
                    ,r.analyzers.getbyname('tradeanalyzer').get_analysis()['long']['pnl']['lost']['total']
                    ,r.analyzers.getbyname('tradeanalyzer').get_analysis()['long']['pnl']['lost']['average']
                    ,r.analyzers.getbyname('tradeanalyzer').get_analysis()['long']['pnl']['lost']['max']
                    ,r.analyzers.getbyname('tradeanalyzer').get_analysis()['short']['total']
                    ,r.analyzers.getbyname('tradeanalyzer').get_analysis()['short']['pnl']['total']
                    ,r.analyzers.getbyname('tradeanalyzer').get_analysis()['short']['pnl']['average']
                    ,r.analyzers.getbyname('tradeanalyzer').get_analysis()['short']['pnl']['won']['total']
                    ,r.analyzers.getbyname('tradeanalyzer').get_analysis()['short']['pnl']['won']['average']
                    ,r.analyzers.getbyname('tradeanalyzer').get_analysis()['short']['pnl']['won']['max']
                    ,r.analyzers.getbyname('tradeanalyzer').get_analysis()['short']['pnl']['lost']['total']
                    ,r.analyzers.getbyname('tradeanalyzer').get_analysis()['short']['pnl']['lost']['average']
                    ,r.analyzers.getbyname('tradeanalyzer').get_analysis()['short']['pnl']['lost']['max']
                    # drawdown analyzer
                    ,r.analyzers.getbyname('drawdown').get_analysis()['drawdown']
                    ,r.analyzers.getbyname('drawdown').get_analysis()['moneydown']
                    ,r.analyzers.getbyname('drawdown').get_analysis()['max']['drawdown']
                    ,r.analyzers.getbyname('drawdown').get_analysis()['max']['moneydown']
                    # returns
                    ,r.analyzers.getbyname('returns').get_analysis()['rtot']
                    ,r.analyzers.getbyname('returns').get_analysis()['ravg']
                    ,r.analyzers.getbyname('returns').get_analysis()['rnorm']
                    ,r.analyzers.getbyname('returns').get_analysis()['rnorm100']
                    ]
                    for r in cerebro_results]
                
            columns = [
                'symbol','starting_cash','risk',
                'factor','multiplier','wma_period','period','short_positions','emergency_exit','rsi_value','stoploss','takeprofit','trstop','trstop_percent',
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
            
            dfr.insert(3, "indicative_position_size", (dfr['risk'] * dfr['starting_cash'].astype(int))/dfr['stoploss'].astype(float))
            dfr.insert(4, "stake_in_usd", (dfr['risk'] * dfr['starting_cash'].astype(int)))
            dfr.insert(5, "accuracy", dfr['td_won_total']/dfr['td_total_total'])
            dfr.insert(6, "total_signals", dfr['td_total_total'])
            dfr.insert(7, "gross_profit_pct", dfr['td_pnl_gross_total']/dfr['starting_cash'].astype(int))
            dfr.insert(8, "net_profit_pct", dfr['td_pnl_net_total']/dfr['starting_cash'].astype(int))

        if strategy == '3h':

            results = [
                [
                    r.params.symbol
                    , r.params.cash
                    , r.params.risk
                    , r.params.factor
                    , r.params.atr_period
                    , r.params.pivot_period
                    , r.params.short_positions
                    , r.params.stoploss
                    , r.params.takeprofit
                    , r.params.trstop
                    , r.params.trstop_percent
                    # tradeanalyzer
                    , r.analyzers.getbyname('tradeanalyzer').get_analysis()['total']['total']
                    , r.analyzers.getbyname('tradeanalyzer').get_analysis()['total']['open']
                    , r.analyzers.getbyname('tradeanalyzer').get_analysis()['total']['closed']
                    , r.analyzers.getbyname('tradeanalyzer').get_analysis()['streak']['won']['longest']
                    , r.analyzers.getbyname('tradeanalyzer').get_analysis()['streak']['lost']['longest']
                    , r.analyzers.getbyname('tradeanalyzer').get_analysis()['pnl']['gross']['total']
                    , r.analyzers.getbyname('tradeanalyzer').get_analysis()['pnl']['gross']['average']
                    , r.analyzers.getbyname('tradeanalyzer').get_analysis()['pnl']['net']['total']
                    , r.analyzers.getbyname('tradeanalyzer').get_analysis()['pnl']['net']['average']
                    , r.analyzers.getbyname('tradeanalyzer').get_analysis()['won']['total']
                    , r.analyzers.getbyname('tradeanalyzer').get_analysis()['won']['pnl']['total']
                    , r.analyzers.getbyname('tradeanalyzer').get_analysis()['won']['pnl']['average']
                    , r.analyzers.getbyname('tradeanalyzer').get_analysis()['won']['pnl']['max']
                    , r.analyzers.getbyname('tradeanalyzer').get_analysis()['lost']['total']
                    , r.analyzers.getbyname('tradeanalyzer').get_analysis()['lost']['pnl']['total']
                    , r.analyzers.getbyname('tradeanalyzer').get_analysis()['lost']['pnl']['average']
                    , r.analyzers.getbyname('tradeanalyzer').get_analysis()['lost']['pnl']['max']
                    , r.analyzers.getbyname('tradeanalyzer').get_analysis()['long']['total']
                    , r.analyzers.getbyname('tradeanalyzer').get_analysis()['long']['pnl']['total']
                    , r.analyzers.getbyname('tradeanalyzer').get_analysis()['long']['pnl']['average']
                    , r.analyzers.getbyname('tradeanalyzer').get_analysis()['long']['pnl']['won']['total']
                    , r.analyzers.getbyname('tradeanalyzer').get_analysis()['long']['pnl']['won']['average']
                    , r.analyzers.getbyname('tradeanalyzer').get_analysis()['long']['pnl']['won']['max']
                    , r.analyzers.getbyname('tradeanalyzer').get_analysis()['long']['pnl']['lost']['total']
                    , r.analyzers.getbyname('tradeanalyzer').get_analysis()['long']['pnl']['lost']['average']
                    , r.analyzers.getbyname('tradeanalyzer').get_analysis()['long']['pnl']['lost']['max']
                    , r.analyzers.getbyname('tradeanalyzer').get_analysis()['short']['total']
                    , r.analyzers.getbyname('tradeanalyzer').get_analysis()['short']['pnl']['total']
                    , r.analyzers.getbyname('tradeanalyzer').get_analysis()['short']['pnl']['average']
                    , r.analyzers.getbyname('tradeanalyzer').get_analysis()['short']['pnl']['won']['total']
                    , r.analyzers.getbyname('tradeanalyzer').get_analysis()['short']['pnl']['won']['average']
                    , r.analyzers.getbyname('tradeanalyzer').get_analysis()['short']['pnl']['won']['max']
                    , r.analyzers.getbyname('tradeanalyzer').get_analysis()['short']['pnl']['lost']['total']
                    , r.analyzers.getbyname('tradeanalyzer').get_analysis()['short']['pnl']['lost']['average']
                    , r.analyzers.getbyname('tradeanalyzer').get_analysis()['short']['pnl']['lost']['max']
                    # drawdown analyzer
                    , r.analyzers.getbyname('drawdown').get_analysis()['drawdown']
                    , r.analyzers.getbyname('drawdown').get_analysis()['moneydown']
                    , r.analyzers.getbyname('drawdown').get_analysis()['max']['drawdown']
                    , r.analyzers.getbyname('drawdown').get_analysis()['max']['moneydown']
                    # returns
                    , r.analyzers.getbyname('returns').get_analysis()['rtot']
                    , r.analyzers.getbyname('returns').get_analysis()['ravg']
                    , r.analyzers.getbyname('returns').get_analysis()['rnorm']
                    , r.analyzers.getbyname('returns').get_analysis()['rnorm100']
                ]
                for r in cerebro_results]

            columns = [
                'symbol', 'starting_cash', 'risk',
                'factor', 'atr_period', 'pivot_period', 'short_positions', 'stoploss', 'takeprofit', 'trstop', 'trstop_percent',
                'td_total_total', 'td_total_open', 'td_total_closed',
                'td_streak_won_longest', 'td_streak_lost_longest', 'td_pnl_gross_total', 'td_pnl_gross_average',
                'td_pnl_net_total', 'td_pnl_net_average',
                'td_won_total', 'td_won_pnl_total', 'td_won_pnl_average', 'td_won_pnl_max',
                'td_lost_total', 'td_lost_pnl_total', 'td_lost_pnl_average', 'td_lost_pnl_max',
                'td_long_total', 'td_long_pnl_total', 'td_long_pnl_average', 'td_long_pnl_won_total',
                'td_long_pnl_won_average', 'td_long_pnl_won_max',
                'td_long_pnl_lost_total', 'td_long_pnl_lost_average', 'td_long_pnl_lost_max',
                'td_short_total', 'td_short_pnl_total', 'td_short_pnl_average', 'td_short_pnl_won_total',
                'td_short_pnl_won_average', 'td_short_pnl_won_max',
                'td_short_pnl_lost_total', 'td_short_pnl_lost_average', 'td_short_pnl_lost_max',
                'dd_dd', 'dd_md', 'dd_max_dd', 'dd_max_md',
                'rt_rtot', 'rt_ravg', 'rt_rnorm', 'rt_rnorm100']

            dfr = pd.DataFrame(results, columns=columns).sort_values(by=['td_pnl_gross_total'], ascending=False)

            dfr.insert(3, "indicative_position_size",
                       (dfr['risk'] * dfr['starting_cash'].astype(int)) / dfr['stoploss'].astype(float))
            dfr.insert(4, "stake_in_usd", (dfr['risk'] * dfr['starting_cash'].astype(int)))
            dfr.insert(5, "accuracy", dfr['td_won_total'] / dfr['td_total_total'])
            dfr.insert(6, "total_signals", dfr['td_total_total'])
            dfr.insert(7, "gross_profit_pct", dfr['td_pnl_gross_total'] / dfr['starting_cash'].astype(int))
            dfr.insert(8, "net_profit_pct", dfr['td_pnl_net_total'] / dfr['starting_cash'].astype(int))

        else:

            print(f'No parsing method has been set')

    return dfr
    

def get_stocks_list():
    stock_list_files = [x for x in os.listdir('./data') if x.startswith('nasdaq_screener_')]
    stock_symbols = pd.concat(pd.read_csv(os.path.join('./data',x)) for x in stock_list_files)
    return stock_symbols

def get_sorted_crypto():
    urls = {
        'top_100_by_volume' : 'https://min-api.cryptocompare.com/data/top/totaltoptiervol?ascending=true&assetClass=all&extraParams=https:%2F%2Fwww.cryptocompare.com&limit=100&page=0&tsym=USD',
        'top_100_by_marketcap' : 'https://min-api.cryptocompare.com/data/top/mktcap?ascending=true&assetClass=all&extraParams=https:%2F%2Fwww.cryptocompare.com&limit=100&page=0&tsym=USD',
        'top_100_by_change' : 'https://min-api.cryptocompare.com/data/top/percent?ascending=true&assetClass=all&extraParams=https:%2F%2Fwww.cryptocompare.com&limit=100&page=0&tsym=USD'
    }
    df_list = []
    for k,v in urls.items():
        print(f'Fetching data : {k}')
        resp = requests.get(v).json().get('Data')        
        temp_list = tuple((x.get('CoinInfo').get('Name'),k) for x in resp)
        df_list.append(pd.DataFrame(temp_list,columns=['symbol','type']).reset_index())
    return pd.concat(df_list)

def resample_ohlcv(df,resample_period):
    
    # https://tcoil.info/aggregate-daily-ohlc-stock-price-data-to-weekly-python-and-pandas/
    # https://stackoverflow.com/questions/34597926/converting-daily-stock-data-to-weekly-based-via-pandas-in-python

    try :
        agg_dict = {
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'adj_close': 'last',
            'volume': 'sum'
            }
        
        adj_col_names = [x.lower().replace(" ","_") for x in df.columns]
        adj_col_names = [x for x in adj_col_names if x in agg_dict.keys()]
        df.columns = adj_col_names

        # resampled dataframe
        # 'W' means weekly aggregation
        r_df = df.resample('W').agg(agg_dict)

    except Exception as e:
        print(e)
        print(f'1.column names must be one of {agg_dict.keys()}')
        print(f'2.resample_period should be in accordance to : https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases')

def timestamp_to_datetime(x):
    return datetime.utcfromtimestamp(int(str(x)[:10])).strftime("%Y-%m-%d, %H:%M:%S")

def datetime_to_timestamp(x,local=False):
    from_timestamp_local = int(time.mktime(datetime.strptime(x, "%Y-%m-%d").timetuple()))
    from_timestamp_utc = calendar.timegm(time.strptime(x, "%Y-%m-%d"))
    return from_timestamp_local if local else from_timestamp_utc

def timestring_to_unix(timestring):
    # timestring = '2019-01-01 00:00:00'
    d = pd.to_datetime(timestring)
    unixtime = int(datetime.timestamp(d)*1000)
    return unixtime

def get_ccxt_data(exchange, pairs, timeframe):
    
    if not isinstance(pairs,list):
        raise Exception(f'Expected list type for pairs. Instead received {type(pairs)}')
    
    exchange_id = exchange
    exchange_class = getattr(ccxt, exchange_id)
    column_names = ['time','open','high','low','close','volume']
    reorder_columns = ['time','datetime','symbol','exchange','frequency','open','high','low','close','volume']
    list_pairs_df = []
    
    for pair in tqdm(pairs):
        # print(f'Now processing : {pair}')
        try:
            ohlc = exchange_class().fetch_ohlcv(pair+'/USDT',timeframe, limit=1000)
            df = pd.DataFrame(ohlc,columns=column_names).assign(
                datetime = lambda x : x.time.apply(timestamp_to_datetime),
                symbol = pair,
                exchange = exchange_id,
                frequency = timeframe
                )[reorder_columns]
            list_pairs_df.append(df)
        except Exception as e:
            print(e)
            print(f'failed to download data for {pair}')    
    
    return pd.concat(list_pairs_df) if list_pairs_df else []


class CryptoCompare:
    
    def __init__(self):
        self.exchanges_url = 'https://min-api.cryptocompare.com/data/exchanges/general'
        self.coins_url = 'https://min-api.cryptocompare.com/data/all/coinlist'
        self.tsym = 'USDT'
        self.limit = 2000
        self.exchange = 'Binance'
        self.aggregate = 1
 
    def get_exchanges(self):
        response = requests.get(self.exchanges_url)
        self.exchanges = pd.DataFrame(response.json().get('Data')).T.Name.unique().tolist()
        return self.exchanges
 
    def get_coins(self):
        response = requests.get(self.coins_url)
        self.coins = pd.DataFrame(response.json()['Data']).T
        return self.coins
    
    def _get_ohlcv_minute(self,fsym,tsym=None,limit=None,exchange=None,aggregate=None,toTs=None):
        """Function to retrieve minute data

        Args:
            fsym ([str]): [description]
            tsym ([str], optional): [description]. Defaults to None.
            limit ([int], optional): [description]. Defaults to None.
            exchange ([type], optional): [description]. Defaults to None.
            aggregate ([type], optional): [description]. Defaults to None.
            toTs ([type], optional): [description]. Defaults to None.

        Returns:
            [dataframe]: [returns data from a single request]
        """
        if tsym is None:
            tsym = self.tsym
        if limit is None:
            limit = self.limit
        if exchange is None:
            exchange = self.exchange
        if aggregate is None:
            aggregate = self.aggregate
        if toTs is None:
            toTs = calendar.timegm(time.gmtime())

        self.minute_url = f'https://min-api.cryptocompare.com/data/v2/histominute?fsym={fsym}&tsym={tsym}&limit={limit}&e={exchange}&aggregate={aggregate}&toTs={toTs}'
        
        try:
            response = requests.get(self.minute_url)
            # add datetime, symbol and exchange columns
            temp = pd.DataFrame(response.json().get('Data').get('Data')).\
            assign(
                datetime = lambda x : x.time.apply(timestamp_to_datetime),
                symbol = fsym,
                exchange = exchange
                )
            # select and reorder columns to output
            column_selection = ['datetime', 'time', 'symbol', 'exchange',
                                'open', 'high', 'low', 'close', 
                                'volumefrom', 'volumeto']
            return temp[column_selection]
        except Exception as e:
            pass
    
    def get_ohlcv_minute(self,fsym,tsym=None,limit=None,exchange=None,aggregate=None,toTs=None,max_existing_ts=None):
        """Function to retrieve consequtive minute dataframes;
        Builds on top of _get_ohlcv_minute ;
        wraps _get_ohlcv_minute in an iteration process

        Args:
            fsym ([type]): [description]
            tsym ([type], optional): [description]. Defaults to None.
            limit ([type], optional): [description]. Defaults to None.
            exchange ([type], optional): [description]. Defaults to None.
            aggregate ([type], optional): [description]. Defaults to None.
            toTs ([type], optional): [description]. Defaults to None.
            max_existing_ts ([type], optional): when this ts is found in the downloaded dataset, iteration stops. Defaults to None.

        Returns:
            [dataframe]: [returns concatenated data from a multiple request]
        """
        dataframes_list = []
        try:
            while True:
                temp = self._get_ohlcv_minute(fsym,tsym,limit,exchange,aggregate,toTs)
                if not isinstance(temp,pd.DataFrame):
                    break
                if temp.empty:
                    break
                toTs = temp.time.min() # use toTs to track min current timestamp which will be used for the next api call
                dataframes_list.append(temp)
                print(f'[{fsym}] {temp.shape[0]} rows, from {temp.datetime.min()} to {temp.datetime.max()}')
                if max_existing_ts: # if argument is provided
                    if max_existing_ts in temp.time.unique().tolist(): # if max existing ts was found in the downloaded data
                        break
        except Exception as e:
            print(f'iterations for {fsym} finished')
        finally:
            consolidated_data = pd.concat(dataframes_list).drop_duplicates(subset='time')
            return consolidated_data.query('time>@max_existing_ts') if max_existing_ts else consolidated_data
            
    def _get_ohlcv_day(self,fsym,tsym=None,limit=None,exchange=None,aggregate=None,toTs=None):
        """Function to retrieve minute data

        Args:
            fsym ([str]): [description]
            tsym ([str], optional): [description]. Defaults to None.
            limit ([int], optional): [description]. Defaults to None.
            exchange ([type], optional): [description]. Defaults to None.
            aggregate ([type], optional): [description]. Defaults to None.
            toTs ([type], optional): [description]. Defaults to None.

        Returns:
            [dataframe]: [returns data from a single request]
        """
        if tsym is None:
            tsym = self.tsym
        if limit is None:
            limit = self.limit
        if exchange is None:
            exchange = self.exchange
        if aggregate is None:
            aggregate = self.aggregate
        if toTs is None:
            toTs = calendar.timegm(time.gmtime())

        self.day_url = f'https://min-api.cryptocompare.com/data/v2/histoday?fsym={fsym}&tsym={tsym}&limit={limit}&e={exchange}&aggregate={aggregate}&toTs={toTs}'
        
        try:
            response = requests.get(self.day_url)
            # add datetime, symbol and exchange columns
            temp = pd.DataFrame(response.json().get('Data').get('Data')).\
            assign(
                datetime = lambda x : x.time.apply(timestamp_to_datetime),
                symbol = fsym,
                exchange = exchange
                )
            # select and reorder columns to output
            column_selection = ['datetime', 'time', 'symbol', 'exchange',
                                'open', 'high', 'low', 'close', 
                                'volumefrom', 'volumeto']
            return temp[column_selection]
        except Exception as e:
            pass
    
    def get_ohlcv_day(self,fsym,tsym=None,limit=None,exchange=None,aggregate=None,toTs=None,max_existing_ts=None):
        """Function to retrieve consequtive minute dataframes;
        Builds on top of _get_ohlcv_minute ;
        wraps _get_ohlcv_minute in an iteration process

        Args:
            fsym ([type]): [description]
            tsym ([type], optional): [description]. Defaults to None.
            limit ([type], optional): [description]. Defaults to None.
            exchange ([type], optional): [description]. Defaults to None.
            aggregate ([type], optional): [description]. Defaults to None.
            toTs ([type], optional): [description]. Defaults to None.
            max_existing_ts ([type], optional): when this ts is found in the downloaded dataset, iteration stops. Defaults to None.

        Returns:
            [dataframe]: [returns concatenated data from a multiple request]
        """
        dataframes_list = []
        try:
            while True:
                temp = self._get_ohlcv_day(fsym,tsym,limit,exchange,aggregate,toTs)
                if not isinstance(temp,pd.DataFrame):
                    break
                if temp.empty:
                    break
                toTs = temp.time.min() # use toTs to track min current timestamp which will be used for the next api call
                dataframes_list.append(temp)
                print(f'[{fsym}] {temp.shape[0]} rows, from {temp.datetime.min()} to {temp.datetime.max()}')
                if max_existing_ts: # if argument is provided
                    if max_existing_ts in temp.time.unique().tolist(): # if max existing ts was found in the downloaded data
                        break
        except Exception as e:
            print(f'iterations for {fsym} finished')
        finally:
            consolidated_data = pd.concat(dataframes_list).drop_duplicates(subset='time')
            return consolidated_data.query('time>@max_existing_ts') if max_existing_ts else consolidated_data
            
    
    