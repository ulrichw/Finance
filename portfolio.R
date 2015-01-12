# R program to analyze a stock portfolio over a period of one year
# and compare it with the S&P 500
# uses the pandas module
# this program plots the portfolio value, cumulative returns, and computes
# the Sharpe ratio, Jensen's alpha, beta, and R-squared values.
# requires the tseries and zoo libraries

#import proper libraries (if installation needed, install.packages("tseries"))
library(tseries) #financial package
library(zoo)     #the prices will be returned as zoo series

#vector with the weights of each stock
tickers <- c(742,326,205,781,1409,1320,693,1814,505,914,821,738,758,532)
names(tickers)<-c("MBT","T","C","BAC","SAN","SCGLY","LFRGY","CRRFY","MTNOY","BACHY","BCS","SRGHY","VCISY","VIV")

end <- Sys.Date()
begin<- end - 365

temp <- get.hist.quote(names(tickers[1]), quote="Close", start=begin, end=end, provider="yahoo", retclass="zoo")

for(i in 2:length(tickers)){
  # Download Adjusted Price Series from Yahoo! Finance
  prices <- get.hist.quote(names(tickers[i]), quote="Close", start=begin, end=end, provider="yahoo", retclass="zoo")
  temp <- merge(temp,prices,all=FALSE) #intersection: only keeps the dates for which all the ticker symboles have data
}

#retrieve the S&P 500 prices
prices <- get.hist.quote("^GSPC", quote="Close", start=begin, end=end, provider="yahoo", retclass="zoo")
SP500 <- coredata(prices)

#convert temp into a matrix
#and compute the daily value of the portfolio
temp <- coredata(temp)
temp <- sweep(temp,MARGIN=2,tickers,FUN='*') #multiply each row of the price matrix by the number of shares
portfolio <- rowSums(temp)

#compute the daily stock returns
n<-length(portfolio)
returns <- diff(portfolio)/portfolio[1:n-1]
cumreturns <- cumprod(returns+1)-1
SPXreturns <- diff(SP500)/SP500[1:n-1]

#daily risk-free rate, from 1-year treasury yield of 0.25%
Rf <- (1+0.0025)^(1/252)-1 

#linear regression
returns <- returns - Rf
SPXreturns <- SPXreturns -Rf
res <- lm(returns ~ SPXreturns)
coeff<-res$coefficients

#annualized Sharpe ratio
sharpe <- mean(returns)/sd(returns)*sqrt(252)

cat("\n RESULTS: \n")
cat("Jensen annualized alpha (in percentage)=",(((1+coeff[1])^252-1)*100),"\n")
cat("portfolio beta=",coeff[2],"\n")
cat("portfolio R-squared=",summary(res)$r.squared,"\n")
cat("annualized Sharpe ratio=",sharpe,"\n")
cat("maximum value of portfolio=",max(portfolio),"\n")
cat("minimum value of portfolio=",min(portfolio),"\n")

#plot the result
par(mfrow=c(2,1)) #to plot 2 panels on 1 figure
plot(cumreturns,col="blue",type="o",xlab="days",ylab="cumulative returns")
plot(SPXreturns,returns,xlab="S&P 500 daily returns",ylab="Portfolio daily returns")
abline(res,col="red")


