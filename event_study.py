'''
Program to perform an event study (e.g. stock returns following a daily drop by X% in the
stock price).
This program uses the QSTK Python module.
The data for the study should be located in the QSData/Yahoo/ directory,
e.g.: /usr/local/lib/python2.7/site-packages/QSTK/QSData/Yahoo/
assuming this path is correct, to add data for the event study, 
run: /usr/local/lib/python2.7/site-packages/QSTK/qstktools/YahooDataPull.py
after creating a file symbols.txt in the directory you currently are
then move the created .csv files into the QSData/Yahoo/ directory
'''

import pandas as pd, numpy as np
import math, copy
import QSTK.qstkutil.qsdateutil as du
import datetime as dt
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkstudy.EventProfiler as ep

def find_events(ls_symbols, d_data):
    ''' Finding the event dataframe '''
    df_close = d_data['close']
    ts_market = df_close['SPY']
    
    print "Finding Events"
    
    # Creating an empty dataframe
    df_events = copy.deepcopy(df_close)
    df_events = df_events * np.NAN
    
    # Time stamps for the event range
    ldt_timestamps = df_close.index
    
    for s_sym in ls_symbols:
        count = 0
        for i in range(1, len(ldt_timestamps)):
            # Calculating the returns for this timestamp
            f_symprice_today = df_close[s_sym].ix[ldt_timestamps[i]]
            f_symprice_yest = df_close[s_sym].ix[ldt_timestamps[i - 1]]
            f_marketprice_today = ts_market.ix[ldt_timestamps[i]]
            f_marketprice_yest = ts_market.ix[ldt_timestamps[i - 1]]
            f_symreturn_today = (f_symprice_today / f_symprice_yest) - 1
            f_marketreturn_today = (f_marketprice_today / f_marketprice_yest) - 1
            
            # Event is found if the symbol is down more then 5% while the
            # market is up more then 2%
            if f_symreturn_today < -0.05 and f_marketreturn_today >= 0.02:
                df_events[s_sym].ix[ldt_timestamps[i]] = 1
                count += 1
                print("event %d found for symbol %s at time %s" % (count,s_sym,ldt_timestamps[i]))
    
    return df_events


if __name__ == '__main__':
    dt_start = dt.datetime(1997, 1, 1)
    dt_end = dt.datetime(2013,10,1)
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))
    
    #grab local copy of Yahoo data
    dataobj = da.DataAccess('Yahoo',cachestalltime=0)
    ls_symbols = dataobj.get_symbols_from_list('sp5002012')
   #ls_symbols=['BAC','C','WFC','JPM','GS','MS','BK','USB','HBC','PNC','COF','TD']
    ls_symbols.append('SPY')
    
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data = dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))
    
    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)
    
    df_events = find_events(ls_symbols, d_data)
    print "Creating Study"
    ep.eventprofiler(df_events, d_data, i_lookback=60, i_lookforward=60,
                     s_filename='EventStudy.png', b_market_neutral=True, b_errorbars=False,
                     s_market_sym='SPY')
