#repository of 3 simple functions to compute confidence intervals
#for mean, standard deviation, and proportion
#simpler than using the stats package!

#for the mean: provide the sample x, and significance level alpha
#assumes we do not know the standard dev. of the population
#so we use the t-distribution rather than the z-distribution
CImean <- function(x,alpha=0.05) {
    
  dof = length(x)-1 #degrees of freddom for t-distribution 
  critical_t = qt(1-alpha/2,dof)  
  Error = critical_t*sd(x)/sqrt(length(x))
  Mean=mean(x)
  
  cat("The confidence interval is:",Mean-Error,"<",Mean,"<",Mean+Error,"\n")  
  
}

#for the standard deviation: provide the sample x, and significance level alpha
#we use the chi-square distribution
CIsd <- function(x,alpha=0.05) {
  
    dof = length(x)-1
    criticalL = qchisq(alpha/2,dof) #left-tail critical value for chi-square
    criticalR = qchisq(1-alpha/2,dof) #right-tail critical value for chi-square 
    Sd=sd(x)
    Var=var(x)
    ErrorL = sqrt(dof*Var/criticalL) 
    ErrorR = sqrt(dof*Var/criticalR)  
  
    cat("The confidence interval is:",ErrorR,"<",Sd,"<",ErrorL)
}

#for a proportion: provide the sample proportion p
#and the size of your sample n
#assumes that the sample proportion follows a normal distribution
#but for the standard deviation uses a binomial one
CIprop <- function(p,n,alpha=0.05){
  
    critical=qnorm(1-alpha/2)
    Error=critical*sqrt(p*(1-p)/n)
  
    cat("The confidence interval is:",p-Error,"<",p,"<",p+Error)
}

