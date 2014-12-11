'''code to price derivatives on securities and fixed income assets (options, futures, swaps, caplets, floorlets, etc...) using binomial model
    with calibration performed by Black Scholes model
'''

import numpy as np
import math

#compute stock prices tree
def stock_price_lattice(u,d,N,S0):
    #S0 is initial price of security
    #N is the number of periods in the binomial model
    #u is the factor by which the short rate goes up
    #d is the facto by which the sort rate goes down
    stkval = np.zeros((N+1,N+1)) #stock value
    stkval[0,0] = S0
    for i in range(1,N+1):
        stkval[i,0] = stkval[i-1,0]*u
        for j in range(1,N+1):
            stkval[i,j] = stkval[i-1,j-1]*d
    return stkval


#compute futures lattice:
def futures_price_lattice(u,d,N,T,r,c,stkval):
    #S0 is initial price of security
    #r is risk free interest rate
    #N is number of periods
    #T is time
    #c is dividend yield
    #stkval is price lattice of underlying asset (stock)

    futval = np.zeros((N+1,N+1)) #futures contract value
    deltaT = T/float(N)
    a = np.exp((r-c) * deltaT) #dividend is subtracted from rate
    q = (a-d)/(u-d)

    for j in range(N+1):
        futval[N,j]=stkval[N,j]
    for i in range(N-1,-1,-1):
        for j in range(i+1):
            futval[i,j]=(q*futval[i+1,j]+(1-q)*futval[i+1,j+1])

    return futval

#compute option prices tree
def option_price_lattice(u,d,N,T,r,c,cp,am,stkval,K):
    #r is risk free interest rate
    #N is number of periods
    #T is time
    #c is dividend yield
    #stkval is price lattice of underlying asset (stock)
    #N is the number of periods in the binomial model
    #u is the factor by which the short rate goes up
    #d is the facto by which the sort rate goes down
    #cp: 1 for call, -1 for put
    #am: True for American option, False for European
    #K=strike price
    
    optval = np.zeros((N+1,N+1)) #option on stock value
    deltaT = T/float(N)
    a = np.exp((r-c) * deltaT) #dividend is subtracted from rate
    q = (a-d)/(u-d)

    for j in range(N+1):
        optval[N,j]=max(0,cp*(stkval[N,j]-K))
    for i in range(N-1,-1,-1):
        for j in range(i+1):
            optval[i,j]=(q*optval[i+1,j]+(1-q)*optval[i+1,j+1])/np.exp(r*deltaT)
            if am:
                if(cp*(stkval[i,j]-K) >= optval[i,j]):
                    print 'option on stock optimal to exercise at t=',i,' option price=',optval[i,j],'payoff=',cp*(stkval[i,j]-K)
                optval[i,j] = max(optval[i,j],cp*(stkval[i,j]-K))

    return optval

#compute option prices tree with short-rate lattice
def option_price_lattice2(u,d,N,T,shrval,c,cp,am,stkval,K):
    #shrval is the short-rate lattice
    #N is number of periods
    #T is time
    #c is dividend yield
    #stkval is price lattice of underlying asset (stock)
    #N is the number of periods in the binomial model
    #u is the factor by which the short rate goes up
    #d is the facto by which the sort rate goes down
    #cp: 1 for call, -1 for put
    #am: True for American option, False for European
    #K=strike price
    
    optval = np.zeros((N+1,N+1)) #option on stock value
    q = 0.5
    
    for j in range(N+1):
        optval[N,j]=max(0,cp*(stkval[N,j]-K))
    for i in range(N-1,-1,-1):
        for j in range(i+1):
            optval[i,j]=(q*optval[i+1,j]+(1-q)*optval[i+1,j+1])/(1+shrval[i,j])
            if am:
                if(cp*(stkval[i,j]-K) >= optval[i,j]):
                    print 'option on stock optimal to exercise at t=',i,' option price=',optval[i,j],'payoff=',cp*(stkval[i,j]-K)
                optval[i,j] = max(optval[i,j],cp*(stkval[i,j]-K))
    
    return optval


#compute option price on futures tree
def option_on_future_price_lattice(u,d,N,T,r,c,cp,am,N2,futval,K):
    optfutval = np.zeros((N2+1,N2+1)) #options on futures contract value
    deltaT = T/float(N)
    a = np.exp((r-c) * deltaT) #dividend is subtracted from rate
    q = (a-d)/(u-d)

    for j in range(N2+1):
        optfutval[N2,j]=max(0,cp*(futval[N2,j]-K))
    for i in range(N2-1,-1,-1):
        for j in range(i+1):
            optfutval[i,j]=(q*optfutval[i+1,j]+(1-q)*optfutval[i+1,j+1])/np.exp(r*deltaT)
            if am:
                if(cp*(futval[i,j]-K) > optfutval[i,j]):
                    print 'option on futures optimal to exercise at t=',i,' option price=',optfutval[i,j],'payoff=',cp*(futval[i,j]-K)
                optfutval[i,j] = max(optfutval[i,j],cp*(futval[i,j]-K))

    return optfutval


def short_rate_lattice(u,d,N,r0):
    #N is the number of periods of the lattice
    #u is the factor by which the short rate goes up
    #d is the facto by which the sort rate goes down
    #r0 is the short rate at t=0
    shrval = np.zeros((N+1,N+1)) #short rate value
    shrval[0,0]=r0
    #compute short-rate lattice
    for i in range(1,N+1):
        shrval[i,0] = shrval[i-1,0]*u
        for j in range(1,N+1):
            shrval[i,j] = shrval[i-1,j-1]*d

    return shrval

#lattice for zero-coupn bond
def ZCB_lattice(N,face,shrval):
    zcbval = np.zeros((N+1,N+1)) #zero-coupon bond value
    q=0.5
    for j in range(N+1):
        zcbval[N,j]=face #face value of coupon at maturity
    for i in range(N-1,-1,-1):
        for j in range(i+1):
            zcbval[i,j]=(q*zcbval[i+1,j]+(1-q)*zcbval[i+1,j+1])/(1.0+shrval[i,j])

    return zcbval

#lattice for coupon-bearing bond
def CB_lattice(N,face,shrval,c):
    #c is the coupon
    #face is the face value of the bond
    #N is the time to maturity
    #shrval is the short-rate lattice in the N-period binomial model
    
    cbval = np.zeros((N+1,N+1)) #coupon-bearing bond value
    q=0.5
    for j in range(N+1):
        cbval[N,j]=face*(1.0+c) #face value of coupon at maturity+coupon
    for i in range(N-1,-1,-1):
        for j in range(i+1):
            cbval[i,j]=face*c+(q*(cbval[i+1,j])+(1-q)*(cbval[i+1,j+1]))/(1.0+shrval[i,j])
    
    return cbval


#price of the forward contract on a coupon-bearing bond (when delivery occurs AFTER a coupon has been paid)
def forward_on_bond(N,face,Nb,c,u,d,r0):
    #Nb is the time to maturity of the bond
    #face is the face value of the bond
    #c is the coupon of the bond
    #N is the period at which we take delivery of the underlying asset in the forward contract
    #u is the factor by which the short rate goes up
    #d is the facto by which the sort rate goes down
    #r0 is the short rate at t=0

    #compute short-rate lattices
    shrval=short_rate_lattice(u,d,N,r0)
    shrval2=short_rate_lattice(u,d,Nb,r0)
    #zcbval is the value of a zero coupon bond maturing at t=N
    zcbval=ZCB_lattice(N,1.0,shrval)
    #cbval2 is the value of a coupon-bearing bond maturing at t=Nb (1 coupon paid at each period)
    cbval2=CB_lattice(Nb,face,shrval2,c)
    
    bexcouponval = np.zeros((N+1,N+1)) #value of bond ex-coupon
    q=0.5
    for j in range(N+1):
        bexcouponval[N,j]=cbval2[N,j]-face*c #we assume we take delivery of asset underlying the forward just AFTER a coupon has been paid
    for i in range(N-1,-1,-1):
        for j in range(i+1):
            bexcouponval[i,j]=(q*bexcouponval[i+1,j]+(1-q)*bexcouponval[i+1,j+1])/(1.0+shrval[i,j])
    
    forbonval=bexcouponval[0,0]/zcbval[0,0] #value at t=0 of forward contract on coupon-bearing bond
    
    return forbonval

#price of the futures contract on a coupon-bearing bond (when dleivery occurs AFTER a coupon has been paid)
def futures_on_bond(N,face,Nb,c,u,d,r0):
    #Nb is the time to maturity of the bond
    #face is the face value of the bond
    #c is the coupon of the bond
    #N is the period at which we take delivery of the underlying asset in the forward contract
    #u is the factor by which the short rate goes up
    #d is the facto by which the sort rate goes down
    #r0 is the short rate at t=0
    
    #compute short-rate lattices
    shrval=short_rate_lattice(u,d,N,r0)
    shrval2=short_rate_lattice(u,d,Nb,r0)
    #zcbval is the value of a zero coupon bond maturing at t=N
    zcbval=ZCB_lattice(N,1.0,shrval)
    #cbval2 is the value of a coupon-bearing bond maturing at t=Nb (1 coupon paid at each period)
    cbval2=CB_lattice(Nb,face,shrval2,c)
    
    bexcouponval = np.zeros((N+1,N+1)) #value of bond ex-coupon
    q=0.5
    for j in range(N+1):
        bexcouponval[N,j]=cbval2[N,j]-face*c #we assume we take delivery of asset underlying the forward just AFTER a coupon has been paid
    for i in range(N-1,-1,-1):
        for j in range(i+1):
            bexcouponval[i,j]=(q*bexcouponval[i+1,j]+(1-q)*bexcouponval[i+1,j+1])
    
    futbonval=bexcouponval[0,0] #value at t=0 of futures contract on coupon-bearing bond
    
    return futbonval

#value of a swap (starts at t=1, expires a t=N+1. We pay fixed, receiving floating. N is the number of payments made)
def swap(fixed,N,shrval):
    #fixed is the fixed rate
    #N is the expiration of the swap in periods
    #shrval is the short-rate lattice
    swapval = np.zeros((N+1,N+1)) #zero-coupon bond value
    q=0.5
    for j in range(N+1):
        swapval[N,j]=(shrval[N,j]-fixed)/(1+shrval[N,j])
    for i in range(N-1,-1,-1):
        for j in range(i+1):
            swapval[i,j]=((shrval[i,j]-fixed)+q*swapval[i+1,j]+(1-q)*swapval[i+1,j+1])/(1+shrval[i,j])
 
    return swapval

#value of a forward-starting swap (starts at t=2, expires a t=N+2. We pay fixed, receiving floating)
#forward-starting swap is like normal swap except thre is no cash flow for the first few periods!
#but we still receive cash-flow after that in arrears (with 1 period delay)
def forswap(fixed,N,shrval):
    #fixed is the fixed rate
    #N is the expiration of the swap in periods
    #shrval is the short-rate lattice
    forswapval = np.zeros((N+1,N+1)) #zero-coupon bond value
    q=0.5
    for j in range(N+1):
        forswapval[N,j]=(shrval[N,j]-fixed)/(1+shrval[N,j])
    for i in range(N-1,0,-1):
        for j in range(i+1):
            forswapval[i,j]=((shrval[i,j]-fixed)+q*forswapval[i+1,j]+(1-q)*forswapval[i+1,j+1])/(1+shrval[i,j])
    forswapval[0,0]=(q*forswapval[1,0]+(1-q)*forswapval[1,1])/(1+shrval[0,0])

    return forswapval

#swaption value for strike=0
def swaption(N,swapval,shrval):
    swaptionval = np.zeros((N+1,N+1)) #zero-coupon bond value
    q=0.5
    for j in range(N+1):
        swaptionval[N,j]=max(swapval[N,j],0)
    for i in range(N-1,-1,-1):
        for j in range(i+1):
            swaptionval[i,j]=(q*swaptionval[i+1,j]+(1-q)*swaptionval[i+1,j+1])/(1+shrval[i,j])

    return swaptionval

#defaultable zero-coupon bond with recovery
def defaultable_ZCB(shrval,F,R):
    #F is face value of coupon
    #shrval is short rate lattice
    #R is the recovery rate
    a=0.01
    b=1.01
    h=np.zeros((N+1,N+1)) #1-step hazard rates
    for i in range(N+1):
        for j in range(N+1):
            h[i,j]=a*b**(j-i/2.)

    zcbval=np.zeros((N+1,N+1)) #price of a bond maturing on date T at node (i,j) AFTER RECOVERY

    q=0.5
    for j in range(N+1):
        zcbval[N,j]=F #face value of coupon at maturity
    for i in range(N-1,-1,-1):
        for j in range(i+1):
            zcbval[i,j]=(q*(1-h[i,j])*zcbval[i+1,j]+(1-q)*(1-h[i,j])*zcbval[i+1,j+1]+q*h[i,j]*R*F+(1-q)*h[i,j]*R*F)/(1.0+shrval[i,j])

    return zcbval



#calibration by Black-Scholes model
T=0.50
sigma=0.20
N=10   #periods in binomial model over which the underlying security price is computed
u=math.exp(sigma*math.sqrt(T/float(N)))
d=1.0/u
print 'u=',u
print 'd=',d
stkval=stock_price_lattice(u,d,N,100.0)

r=0.02 #risk-free interest rate
K=100.0#strike price for derivative
c=0.01 #dividend yield of underlying security, or coupon of bond
cp=-1   #+1 for call options, -1 for put options
am=False#True for American option, False for European
optval=option_price_lattice(u,d,N,T,r,c,cp,am,stkval,K)
print 'option value on stock at t=0',optval[0,0]
futval=futures_price_lattice(u,d,N,T,r,c,stkval)
print 'futures value on stock at t=0',futval[0,0]

N2=10  #periods in binomial model over which the derivative is computed (e.g. the options on futures contract)
optfutval=option_on_future_price_lattice(u,d,N,T,r,c,cp,am,N2,futval,K)
print 'option value on futures at t=0',optfutval[0,0]
shrval=short_rate_lattice(1.1,0.9,10,0.05)
#shrval=short_rate_lattice(1.25,0.9,5,0.06)
#print 'short rate lattice:',shrval
zcbval=ZCB_lattice(10,100.0,shrval)
#zcbval=ZCB_lattice(4,100.0,shrval)
print 'ZCB value at time t=0',zcbval[0,0]
#swapval=swap(0.05,5,shrval) #NB: if swaps expires at t=6, then N=5 !!!! careful!
#print 'Swap value at t=0',swapval[0,0]
forswapval=forswap(0.045,10,shrval)
notional=1000000.0
print 'Forward-starting swap value at t=0',forswapval[0,0]*notional
swaptionval=swaption(5,forswapval,shrval)
print 'Swaption value at t=0',swaptionval[0,0]*notional
optonzcbval=option_price_lattice2(1.1,0.9,6,1,shrval,0.0,1,True,zcbval,80.0) #option on ZCB
#optonzcbval=option_price_lattice2(1.25,0.9,3,1,shrval,0.0,-1,True,zcbval,88.0) #option on ZCB
print 'option on ZCB at t=0',optonzcbval[0,0]
forbonval=forward_on_bond(4,100.,10,0.0,1.1,0.9,0.05)
print 'forward contract value on a coupon-bearing bond at t=0',forbonval
futbonval=futures_on_bond(4,100.,10,0.0,1.1,0.9,0.05)
print 'futures contract value on a coupon-bearing bond at t=0',futbonval

shrval=short_rate_lattice(1.1,0.9,10,0.05)
defaultZCBval=defaultable_ZCB(shrval,100.,0.2)
print 'price of a defaultable zero-coupon bond with recovery',defaultZCBval[0,0]


