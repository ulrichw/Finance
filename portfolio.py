'''
program to analyze a stock portfolio over a period of one year
and compare it with the S&P 500
uses the pandas module
this program plots the portfolio value, cumulative returns, and computes
the Sharpe ratio, Jensen's alpha, beta, and R-squared values.
'''

import numpy as np, pandas as pd, pandas.io.data as web, matplotlib.pyplot as plt, datetime as dt
from pandas.stats.api import ols

def scatterplot(d1,d2,res):
    fig = plt.figure()
    
    #create axis and scatterplot our data
    ax = fig.add_subplot(111)
    ax.scatter(d1*100., d2*100.)
    #prevent matplotlib from automatically changing axis ranges
    ax.autoscale(False)
    #add x = 0 and y = 0 lines
    ax.vlines(0,-10,10)
    ax.hlines(0,-10,10)
    #add y = x and linear regression result
    ax.plot((-10,10),(-10,10),label='y=x')
    ax.plot((-10,10),(-10*res.beta['x']+100.*res.beta['intercept'],10*res.beta['x']+100.*res.beta['intercept']), color='r',label='linear regression')
    ax.set_xlabel("S&P 500 Daily Returns (in %)")
    ax.set_ylabel("Portfolio Daily Returns (in %)")
    ax.legend()

    plt.show()


def main():

	# dictionary of stocks (stocks tickers and share numbers): this is just an example, not my actual portfolio :-)
    tickers= { 'MBT':742,'T':326,'C':205,'BAC':781,'SAN':1409,'SCGLY':1320,'LFRGY':693,'CRRFY':1814,'MTNOY':505,'BACHY':914,'BCS':821,'SRGHY':738,'VCISY':758,'VIV':532}
    
    end  = dt.date.today() #today's date
    start= end-dt.timedelta(days=365)
    
    # create a pandas dataframe by reading data from the internet
    stock={} #create a dictionary
    tickers_names=tickers.keys()

    for i in np.arange(len(tickers)):
        temp=web.DataReader(tickers_names[i],data_source='yahoo',start=start,end=end)
        stock[tickers_names[i]]=temp['Close']*tickers[tickers_names[i]]

    SPX=web.DataReader('^GSPC',data_source='yahoo',start=start,end=end)
    SPX=SPX['Close']

	#convert my dictionary into a pandas dataframe:
    stocks=pd.DataFrame(stock)
    #compute the porfolio daily values
    stocks=stocks.sum(axis=1)

    stocks_dchange=stocks.pct_change()           #daily returns (price_today-price_yesterday)/price_yesterday

    stocks_change=(stocks_dchange+1).cumprod()-1 #multiple period returns (cumulative returns)
    SPX_dchange=SPX.pct_change()
    SPX_change=(SPX_dchange+1).cumprod()-1

    #plot cumulative returns
    plt.clf()
    plt.subplot(211)
    plt.title('Portfolio')
    plt.ylabel('cumulative daily returns (%)')
    plt.xlabel('Date')
    plt.plot(stocks.index,stocks_change*100.,label='Portfolio')
    plt.plot(SPX.index,SPX_change*100.,label='S&P 500')
    plt.legend()
    plt.subplot(212)
    plt.ylabel('Portfolio daily value (USD)')
    plt.xlabel('Date')
    plt.plot(stocks.index,stocks,label='Portfolio')
    plt.show()
    
    #run a linear regression with ordinary least-squares
    Rf=(1.+0.0025)**(1./252.)-1. #daily risk-free rate, from the 1-year treasury rate of 0.25%
    print 'daily risk-free rate (in percentage)=%f' % (Rf*100.)
    #linear regression from the risk-adjusted returns
    res = ols(y=stocks_dchange-Rf, x=SPX_dchange-Rf)
    #Sharpe ratio:
    sharpe=(stocks_dchange-Rf).mean()/(stocks_dchange-Rf).std()
    # returns the Jensen's alpha and beta (from daily returns)
    print '---------------------------------------------------------------------'
    print 'Jensen annualized alpha (in percentage)= %f' % (((1.+res.beta['intercept'])**252-1.)*100.)
    print 'portfolio beta= %f'          % res.beta['x']
    print 'portfolio R-squared= %f'     % res.r2
    print 'adjusted R-squared= %f'      % res.r2_adj
    print 'Sharpe ratio= %f'            % (sharpe*np.sqrt(252))  # annualized Sharpe ratio
    print 'Maximum portfolio value= %f' % stocks.max()
    print 'Minimum portfolio value= %f' % stocks.min()
    print '---------------------------------------------------------------------'

    #scatter pot of daily returns
    scatterplot(SPX_dchange,stocks_dchange,res)



if __name__ == "__main__":
	main()