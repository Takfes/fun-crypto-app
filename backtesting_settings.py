import numpy as np

strategy_settings_dictionary = {
    
    'ma' : {
        'fast' : [15,25],
        'slow' : 30
    },
    
    'dic':{
        'wma_period' : 300,
        'stoploss' : 0.025,
        'takeprofit' : 0.025,
        'short_positions' : 1,
        'period' : [100,200],
        'factor' : [0.618,0.5],
        'multiplier' : [3,4],
        'printlog' : False,
        'datasize' : 10000
    },
    
    '3h':{
        'stoploss' : 0.025,
        'takeprofit' : 0.025,
        'short_positions' : 1,
        'factor' : 6.5,
        'atr_period' : 170,
        'pivot_period' : 2,
        'printlog' : False,
        'datasize' : 1000
    }
}

strategy_analyzers = ['drawdown','returns','tradeanalyzer']