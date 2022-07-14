import pandas as pd
import talib
import ta
import sqlite3
import patterns
import config

def main():
    
    PATTERN_TIME_EFFECT = 1
    list_dfs_with_patterns = []
    con = sqlite3.connect(config.DB_NAME)
    sql_sting = f"SELECT * FROM {config.DB_ASSET_TABLE_CRYPTO};"
    dfsql = pd.read_sql(sql_sting,con)
    df = dfsql.copy()
    
    for s in df.sort_values(by=['symbol']).symbol.unique().tolist():
        
        # subset for a particular symbol
        temp_df = df.query('symbol==@s').copy()
        
        # add pattern columns (talib)
        for k,v in patterns.patterns.items():
            temp_col_name = v.replace(" ","_").replace("-","_")
            temp_pattern_function = getattr(talib,k)
            temp_df['pattern_'+temp_col_name] = temp_pattern_function(temp_df['open'],temp_df['high'],temp_df['low'],temp_df['close'])
        
        # pattern column names
        pattern_cols =[col for col in temp_df.columns if col.startswith('pattern_')]
    
        # add flag to symbol if a pattern was triggered during the last PATTERN_TIME_EFFECT time steps
        # pattern_indicator : binary used for flagging purposes
        pattern_indicator = temp_df[pattern_cols].tail(PATTERN_TIME_EFFECT).sum().sum()
        temp_df['pattern_indicator'] = int(pattern_indicator)
        list_dfs_with_patterns.append(temp_df)
        
    qq = pd.concat(list_dfs_with_patterns)
    print(qq.groupby(['pattern_indicator']).agg({'symbol':'nunique'}))
    qq.query('pattern_indicator!=0').groupby(['symbol'])['symbol','pattern_indicator'].tail(1).sort_values(by=['pattern_indicator','symbol'],ascending=[False,True])
    qq.to_csv('data/signals.csv',index=False)

if __name__ == '__main__':
    main()