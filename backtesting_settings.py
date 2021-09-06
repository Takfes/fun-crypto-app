import numpy as np

strategy_settings_dictionary = {
    
    'ma' : {
        'fast' : [15,25],
        'slow' : 30
    },

    'macd':{},
    
    'bnh':{},
    
    'stoc':{},
    
    'triple':{},
    
    'dip':{},
    
    'bearx':{},
    
    'dic':{
        'wma_period' : 300,
        'stoploss' : [0.025,0.035,0.04],#list(np.round(np.arange(0.01,0.06,0.01),3)),
        'takeprofit' : [0.001,0.00115,0.015,0.02,0.025,0.035,0.04],#list(np.round(np.arange(0.01,0.06,0.01),3)),
        'short_positions' : [0,1],#[0,1],
        'period' : 110,
        'factor' : 0.618,
        'multiplier' : 3,
        'printlog' : False,
        'datasize' : 100000
    },
    
    '3h':{
        'stoploss' : 0.025,#list(np.round(np.arange(0.01,0.06,0.01),3)),
        'takeprofit' : 0.025,#list(np.round(np.arange(0.01,0.06,0.01),3)),
        'short_positions' : 1,#[0,1],
        'factor' : 6.5,
        'atr_period' : 170,
        'pivot_period' : 24
    }
}

strategy_analyzers = ['drawdown','returns','tradeanalyzer']