; IDL program that computes some basic technical indicators for a
; series of stocks specified in the config.dat file
; requires to have GNU Wget installed on your machine
; requires to have legend.pro routine (from the astrolib) installed
; program written to run on linux
; NB: the output is a postscript file analysis.ps

PRO technicalAnalysis

; configuration file:
@config.dat

GET_DATE,DTE    ; get current date
date=STRSPLIT(DTE,'-',/EXTRACT)
day =date[2]    ; current day
year=date[0]    ; current year
month=date[1]-1 ;current month

; ticker symbols of stocks followed
nstocks=N_ELEMENTS(ticker) ; number of stocks followed

; spawn the wget command line to download the .csv files containing the
; historical prices of the stocks followed'
FOR i=0,nstocks-1 DO BEGIN
    string='"finance.yahoo.com/d/quotes.csv?s='+STRTRIM(ticker[i],1)+'&f=d1ohgl1vl1" -O temp'
    SPAWN,'wget '+string
    string='"ichart.finance.yahoo.com/table.csv?s='+STRTRIM(ticker[i],1)+'&d='+STRTRIM(STRING(month),1)+'&e='+STRING(day)+'&f='+STRING(year)+'&g=d&a=4&b=13&c=1996&ignore=.csv" -O temp2'
    table='table'+STRTRIM(STRING(i),1)+'.csv'
    SPAWN,'wget '+string
    string=' cat temp temp2 > '+STRTRIM(table,1)
    SPAWN,string
ENDFOR
filename=STRARR(nstocks)
FOR i=0,nstocks-1 DO filename[i]="table"+STRTRIM(STRING(i),1)+".csv"

NMAX=7000

SET_PLOT,'PS'
DEVICE,FILE='analysis.ps',xoffset=0,yoffset=0.5,xsize=22,ysize=23,/color,bits=24 ; setup graphics output
LOADCT,4

FOR stock=0,nstocks-1 DO BEGIN

   PRINT,'STOCK NUMBER ',stock
   OPENR,1,filename[stock]
   str=''
   READF,1,str
   ntime=0
   price=FLTARR(NMAX)
   volume=price
   low=price
   high=price
   open=price
   res=STRSPLIT(str,',',/extract)
   lasttradedate=res[0]
   lastday=STRSPLIT(lasttradedate,'/',/extract)
   lastday=UINT(lastday[1])
   price[ntime]=FLOAT(res[4]) ; close price, NOT adjusted close
   volume[ntime]=FLOAT(res[5])
   low[ntime]=FLOAT(res[3])
   high[ntime]=FLOAT(res[2])
   open[ntime]=FLOAT(res[1])
   ntime+=1
   READF,1,str
   WHILE ~ EOF(1) DO BEGIN
    READF,1,str
    res=STRSPLIT(str,',',/extract)
    price[ntime]=FLOAT(res[4])
    volume[ntime]=FLOAT(res[5])
    low[ntime]=FLOAT(res[3])
    high[ntime]=FLOAT(res[2])
    open[ntime]=FLOAT(res[1])
    IF(ntime EQ 1) THEN lastdate=res[0]
    ntime+=1
   ENDWHILE
   CLOSE,1
   
   price=price[0:ntime-1]
   price=REVERSE(price)
   volume=volume[0:ntime-1]
   volume=REVERSE(volume)
   low=low[0:ntime-1]
   low=REVERSE(low)
   high=high[0:ntime-1]
   high=REVERSE(high)
   open=open[0:ntime-1]
   open=REVERSE(open)
   
   ; read latest quote if it was obtained after markets closed:
   lastcloseday=STRSPLIT(lastdate,'-',/extract)
   lastcloseday=UINT(lastcloseday[2])
   IF lastcloseday EQ lastday THEN ntime=ntime-1
   price=price[0:ntime-1]
   volume=volume[0:ntime-1]
   low=low[0:ntime-1]
   high=high[0:ntime-1]
   open=open[0:ntime-1]
   
   dprice=price[1:ntime-1]-price[0:ntime-2]
   dprice=[0.0,dprice]
   up=dprice & a=WHERE(up LE 0.0) & up[a]=0.0
   down=-dprice & a=WHERE(down LE 0.0) & down[a]=0.0
   
   EMA=FLTARR(2,ntime)
   EMAup=FLTARR(ntime)
   EMAdown=EMAup
   EMAf=EMAup
   EMAs=EMAup
   MAup=EMAup
   MAdown=EMAup
   stdbol=EMAup
   meanbol=EMAup
   alpha0=2.d0/(N0+1.d0)
   alpha1=2.d0/(N1+1.d0)
   alpha2=2.d0/(N2+1.d0)
   alpharsi=2.d0/(Nrsi+1.d0)
   alphaf=2.d0/(Nfast+1.d0)
   alphas=2.d0/(Nslow+1.d0)
   EMA[0,0]=MEAN(price[0:N0-1])
   EMA[1,0]=MEAN(price[0:N1-1])
   EMA[0,1:N0-1]=EMA[0,0]
   EMA[1,1:N1-1]=EMA[1,0]
   EMAup[0]=MEAN(up[0:Nrsi-1])
   EMAup[1:Nrsi-1]=EMAup[0]
   EMAdown[0]=MEAN(down[0:Nrsi-1])
   EMAdown[1:Nrsi-1]=EMAdown[0]
   EMAf[0]=MEAN(price[0:Nfast-1])
   EMAs[0]=MEAN(price[0:Nslow-1])
   EMAf[1:Nfast-1]=EMAf[0]
   EMAs[1:Nslow-1]=EMAs[0]
   MAup[0]=MEAN(up[0:Nrsi-1])
   MAdown[0]=MEAN(down[0:Nrsi-1])
   MAup[1:Nrsi-1]=MAup[0]
   MAdown[1:Nrsi-1]=MAdown[0]
   meanbol[0:Nbol-1]=MEAN(price[0:Nbol-1])
   stdbol[0:Nbol-1]=STDDEV(price[0:Nbol-1])
   
   FOR i=N0,ntime-1 DO EMA[0,i]=EMA[0,i-1]+alpha0*(price[i]-EMA[0,i-1])
   FOR i=N1,ntime-1 DO EMA[1,i]=EMA[1,i-1]+alpha1*(price[i]-EMA[1,i-1])
   FOR i=Nrsi,ntime-1 DO BEGIN
       EMAup[i]=EMAup[i-1]+alpharsi*(up[i]-EMAup[i-1])
       EMAdown[i]=EMAdown[i-1]+alpharsi*(down[i]-EMAdown[i-1])
   ENDFOR
   FOR i=Nslow,ntime-1 DO EMAs[i]=EMAs[i-1]+alphas*(price[i]-EMAs[i-1])              ; exponential moving averages
   FOR i=Nfast,ntime-1 DO EMAf[i]=EMAf[i-1]+alphaf*(price[i]-EMAf[i-1])
   FOR i=Nrsi,ntime-1  DO MAup[i]=MAup[i-1]+up[i]/FLOAT(Nrsi)-up[i-Nrsi]/FLOAT(Nrsi) ; simple moving averages
   FOR i=Nrsi,ntime-1  DO MAdown[i]=MAdown[i-1]+down[i]/FLOAT(Nrsi)-down[i-Nrsi]/FLOAT(Nrsi)
   FOR i=Nbol,ntime-1  DO meanbol[i]=MEAN(price[i-Nbol+1:i])                         ; simple moving averages 
   FOR i=Nbol,ntime-1  DO stdbol[i]=STDDEV(price[i-Nbol+1:i]) 
   
   
   RS=EMAup/EMAdown
   RSI=100.d0-100.d0/(1.d0+RS) ; Wilder's RSI
   a=WHERE(finite(RSI) EQ 0,na)
   IF(a[0] NE -1) THEN RSI[a]=100.d0
   
   RS=MAup/MAdown
   RSI2=100.d0-100.d0/(1.d0+RS) ; Cutler's RSI
   a=WHERE(finite(RSI2) EQ 0,na)
   IF(a[0] NE -1) THEN RSI2[a]=100.d0
   
   MACD=REFORM(EMA[0,*]-EMA[1,*]) ; moving-average convergence-divergence
   signal=FLTARR(ntime)
   signal[0]=MEAN(MACD[0:N2-1])
   signal[1:N2-1]=signal[0]
   FOR i=N2,ntime-1 DO signal[i]=signal[i-1]+alpha2*(MACD[i]-signal[i-1])
   divergence=MACD-signal
   
   OBV=FLTARR(ntime) ;on-balance volume
   OBV[0]=MEAN(volume)
   sign=FLTARR(ntime)+1.0
   FOR i=1,ntime-1 DO IF (price[i]-price[i-1]) LT 0 THEN sign[i]=-1.0
   FOR i=1,ntime-1 DO IF  price[i] EQ price[i-1] THEN sign[i]= 0.0
   FOR i=1,ntime-1 DO OBV[i]=OBV[i-1]+volume[i]*sign[i]
   
   ; PLOT RESULTS
   !P.MULTI=[0,2,2]
   interv=INDGEN(ndays)+(ntime-ndays)
   interv2=INDGEN(ndays)-ndays+1
   
   mini=MIN([price[interv],EMAs[interv],EMAf[interv]])
   maxi=MAX([price[interv],EMAs[interv],EMAf[interv]])
   PLOT,interv2,price[interv],xst=1,yst=1,yrange=[mini*0.98,maxi*1.02],tit='!17'+ticker[stock],xtit='Time (in trading days)',ytit='Close price (in USD)',charsize=1.25,thick=2
   a=WHERE(RSI[interv] LE 30.d0)
   IF(a[0] NE -1) THEN OPLOT,interv2[a],price[interv[a]],col=180,thick=3,psym=4
   a=WHERE(RSI[interv] GE 70.d0)
   IF(a[0] NE -1) THEN OPLOT,interv2[a],price[interv[a]],thick=3,psym=4
   a=WHERE(divergence[interv] GT 0.d0,na)
   IF(a[0] NE -1) THEN FOR i=1,na-1 DO IF(a[i]-a[i-1] EQ 1) THEN OPLOT,[interv2[a[i-1]],interv2[a[i]]],[price[interv[a[i-1]]],price[interv[a[i]]]],thick=2,col=180
   mini=MIN([MIN(MACD[interv]),MIN(MACD[interv]-signal[interv])])
   maxi=MAX([MAX(MACD[interv]),MAX(MACD[interv]-signal[interv])])
   OPLOT,interv2,EMAf[interv],linestyle=2,thick=2
   OPLOT,interv2,EMAs[interv],linestyle=3,thick=2
   OPLOT,interv2,meanbol[interv]+2.0*stdbol[interv],thick=2,col=80
   OPLOT,interv2,meanbol[interv]-2.0*stdbol[interv],thick=2,col=80
   LEGEND,["Buy","Sell","Oversold","Overbought",'EMA'+STRING(Nfast),'EMA'+STRING(Nslow)],linestyle=[0,0,0,0,2,3],psym=[0,0,4,4,0,0],color=[180,0,180,0,0,0],thick=[2,2,3,3,2,2],box=0,charsize=0.6
   PLOT,interv2,MACD[interv],yrange=[mini,maxi],yst=1,xst=1,tit='!17',xtit='Time (in trading days)',ytit='MACD',charsize=1.25,thick=2
   OPLOT,interv2,signal[interv],col=180,thick=2
   OPLOT,[-NMAX,NMAX],[0,0],thick=2
   OPLOT,interv2,divergence[interv],psym=10,thick=3,linestyle=2
   LEGEND,["MACD","Signal","Divergence"],linestyle=[0,0,2],psym=[0,0,0],color=[0,180,0],thick=[2,2,2],box=0,charsize=0.6
   PLOT,interv2,RSI[interv],tit='!17',xtit='Time (in trading days)',ytit='RSI',xst=1,yst=1,thick=2,charsize=1.25,yrange=[0,100]
   OPLOT,interv2,RSI2[interv],thick=2,col=180
   OPLOT,[-NMAX,NMAX],[50,50],linestyle=2,thick=2
   OPLOT,[-NMAX,NMAX],[30,30],linestyle=2,thick=2
   OPLOT,[-NMAX,NMAX],[70,70],linestyle=2,thick=2
   LEGEND,["Wilder RSI","Cutler RSI"],linestyle=[0,0],color=[0,180],thick=[2,2],charsize=0.6,box=0
   XYOUTS,-ndays*0.33,250,SYSTIME(),charsize=1.5
   mini=MIN([volume[interv]/MAX(volume),OBV[interv]/MAX(ABS(OBV[interv]))])
   maxi=MAX([volume[interv]/MAX(volume),OBV[interv]/MAX(ABS(OBV[interv]))])
   PLOT,interv2,volume[interv]/MAX(volume),yst=1,xst=1,tit='!17',xtit='Time (in trading days)',ytit='Volume (norm. by MAX)',charsize=1.25,thick=2,psym=10,yrange=[mini,maxi]
   OPLOT,interv2,OBV[interv]/MAX(ABS(OBV[interv])),col=180,thick=2
   LEGEND,["Volume","on-balance volume"],linestyle=[0,0],color=[0,180],thick=[2,2],charsize=0.6,box=0
   
ENDFOR

DEVICE,/CLOSE
SET_PLOT,'X'
!P.MULTI=0

END
