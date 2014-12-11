'''
Program to compute Bollinger bands for a given stock
Uses the QSTK Python module
Assuming that the QSTK module is installed in:
usr/local/lib/python2.7/site-packages/QSTK/
Then, the stock data should be in:  /usr/local/lib/python2.7/site-packages/QSTK/QSData/Yahoo/
to create these stock data, run: /usr/local/lib/python2.7/site-packages/QSTK/qstktools/YahooDataPull.py
after creating a file symbols.txt in the directory you currently are
then move the created .csv files into the QSData/Yahoo/ directory

The output of the program is in the Bollinger.png figure (only for the 1st stock requested)
The code also prints the Bollinger values for the requested sticks
at the requested dates
'''

# QSTK Imports
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da
# Third Party Imports
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import math

def moving_average(a, n=3):
    ret = np.cumsum(a, dtype=float)
    ret[n:] -= ret[:-n]
    return ret[n - 1:] / n

def simulate(startdate,enddate,ls_symbols):

    timeofday = dt.timedelta(hours=16)
    tradingdays = du.getNYSEdays(startdate,enddate,timeofday)
    dataobj = da.DataAccess('Yahoo',cachestalltime=0)
    df_data = dataobj.get_data(tradingdays,ls_symbols,"close")
    df_data = df_data.fillna(method='ffill')
    df_data = df_data.fillna(method='bfill')
    df_data = df_data.fillna(1.0)
    fDev  = pd.rolling_std(df_data,20,min_periods=20)
    fMean = pd.rolling_mean(df_data,20,min_periods=20)
    Bollinger=(df_data-fMean)/fDev
    
    for ntime in np.arange(len(tradingdays)):
        print Bollinger.index[ntime],Bollinger.values[ntime]
    
    return (Bollinger,df_data)


def main():
    ''' Main Function'''

    # List of symbols
    ls_symbols = ['AAPL','GOOG','IBM','MSFT']
    # Start and End date of the charts
    startdate = dt.datetime(2010,1,1)
    enddate = dt.datetime(2010,12,31)
    
    Bollinger,df_data = simulate(startdate,enddate,ls_symbols)

    #print Bollinger['AAPL'].values

    # Plot the prices
    plt.clf()

    symtoplot = 'AAPL'
    plt.xlim([df_data.index[20],df_data.index[-1]])
    plt.plot(df_data.index,df_data[symtoplot].values,label=symtoplot,color='b')
    plt.plot(df_data.index,df_data[symtoplot].values+Bollinger[symtoplot],label='bollingerp',color='r')
    plt.plot(df_data.index,df_data[symtoplot].values-Bollinger[symtoplot],label='bollingerm',color='r')
    #plt.plot(Bollinger.index,Bollinger[symtoplot].values)
    plt.legend([symtoplot,'Bollinger Bands'])
    plt.ylabel('Adjusted Close')

    plt.savefig("Bollinger.png", format='png')


if __name__ == '__main__':
    main()
