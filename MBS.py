''' program to price pass-through mortgage-backed securities '''

import numpy as np
import math

initial_balance = 417000. #initial mortgage balance  (USD)
mortgage_rate = 4.75      #annualized mortgage rate in %
passthrough_rate = 4.75   #annualized pass-through rate in %
seasoning=0               #how old is the mortgage pool (in months)
terms=360                 #term of loan in months
multiplier=100            #multiplier for PSA prepayment model (in percent)
PSA_parameter_time=[1,30,240]
PSA_parameter_rate=[0.2,6.,6.] #CPR (constant prepayment rate) in percent


mortgage_rate /= 100.
passthrough_rate /= 100.
multiplier /= 100.
for i in range(3):
    PSA_parameter_rate[i] /= 100.

month=np.zeros(terms)
CPR=np.zeros(terms)
SMM=np.zeros(terms)
beginning_balance=np.zeros(terms)
monthly_payment=np.zeros(terms)
monthly_interest_paid=np.zeros(terms)
monthly_interest_passed=np.zeros(terms)
scheduled_principal_repayment=np.zeros(terms)
prepayment=np.zeros(terms)
total_principal_repayment=np.zeros(terms)
ending_balance=np.zeros(terms)

initial_monthly_payment = initial_balance*(mortgage_rate/12.)/(1.0-(1.0+(mortgage_rate/12.0))**(-(terms-seasoning)))
r=3.5     #risk free interest rate in percent
r /=100.
PV_PO=0.0 #present value of principal only MBS based on this passthrough mortgage
PV_IO=0.0 #present value of interest only

average_life =0.0
average_IO_life = 0.0

for i in range(terms):

    month[i]=i+1
    if i+seasoning < PSA_parameter_time[1]:
        CPR[i]=PSA_parameter_rate[0]+(month[i]+seasoning-PSA_parameter_time[0])*(PSA_parameter_rate[1]-PSA_parameter_rate[0])/(PSA_parameter_time[1]-PSA_parameter_time[0])
    else:
        CPR[i]=PSA_parameter_rate[1]+(month[i]+seasoning-PSA_parameter_time[1])*(PSA_parameter_rate[2]-PSA_parameter_rate[1])/(PSA_parameter_time[2]-PSA_parameter_time[1])
    CPR[i] *= multiplier
    SMM[i] = (1.0-(1.0-CPR[i])**(1./12.))

    if i>0:
        beginning_balance[i]=ending_balance[i-1]
        monthly_payment[i]=ending_balance[i-1]*(mortgage_rate/12.)/(1.0-(1.0+(mortgage_rate/12.0))**(-(terms-seasoning-month[i]+1.0)))
        monthly_interest_paid[i]=mortgage_rate*beginning_balance[i]/12.
    else:
        beginning_balance[i]=initial_balance
        monthly_payment[i]=initial_monthly_payment
        monthly_interest_paid[i]=mortgage_rate*initial_balance/12.

    monthly_interest_passed[i]=monthly_interest_paid[i]*passthrough_rate/mortgage_rate
    scheduled_principal_repayment[i]=monthly_payment[i]-monthly_interest_paid[i]
    prepayment[i]=(beginning_balance[i]-scheduled_principal_repayment[i])*(1.0-(1.0-CPR[i])**(1./12.))
    total_principal_repayment[i]=scheduled_principal_repayment[i]+prepayment[i]
    ending_balance[i]=beginning_balance[i]-total_principal_repayment[i]

TP=0.0 #total principal amount
TI=0.0 #total interest amount
for i in range(terms):
    TP += total_principal_repayment[i]
    TI += monthly_interest_passed[i]

for i in range(terms):
    average_life += month[i]*total_principal_repayment[i]/12./TP
    PV_PO += total_principal_repayment[i]/(1.0+r/12.0)**month[i]
    PV_IO += monthly_interest_passed[i]/(1.0+r/12.0)**month[i]
    average_IO_life += month[i]*monthly_interest_passed[i]/12./TI

for i in range(terms):
   #print month[i],CPR[i]*100.,SMM[i]*100.,beginning_balance[i],monthly_payment[i],monthly_interest_paid[i],monthly_interest_passed[i],scheduled_principal_repayment[i],prepayment[i],total_principal_repayment[i],ending_balance[i]
    print month[i],monthly_payment[i],monthly_interest_paid[i],scheduled_principal_repayment[i],ending_balance[i]


print 'average MBS life',average_life
print 'Present value of PO (principal only) MBS:',PV_PO
print 'Present value of IO (interest only) MBS:',PV_IO
print 'average IO life',average_IO_life
