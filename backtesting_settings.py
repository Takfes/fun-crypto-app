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
        'stoploss' : 0.025,#list(np.round(np.arange(0.01,0.06,0.01),3)),
        'takeprofit' : 0.025,#list(np.round(np.arange(0.01,0.06,0.01),3)),
        'short_positions' : 0,#[0,1],
        'period' : 110,
        'factor' : 0.618,
        'multiplier' : 3
    },
    
    '3h':{}
}