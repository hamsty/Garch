### GARCH model to predict price of BMF futures contract - using rugarch
### April 07, 2017
### Thu Hoang

library(xlsx)
data<- read.xlsx("Dolar_Futuro.xlsx",1)
par(mar=c(1,1,1,1))
plot(data, main="Futures price series", xlab = "Date")

####### Descriptive statistics ######
library(fBasics)


# calculate log-return
library(TSA)
library(forecast)
dlog = diff(log(data$Close))
basicStats(dlog)
# N <- dim(data)[1]
# dlog2=log(data$Close[2:N])-log(data$Close[1:(N-1)]) # same as dlog
hist(dlog, breaks=100)
tsdisplay(dlog) #  ## There appears a stationary in mean.

###### Test ARCH effects #####
# If the volatility clustering is properly explained by the model,
# then there will be no autocorrelation in the squared standardized residuals.  
# It is common to do a Ljung-Box test to test for this autocorrelation.
Box.test(dlog,type='Ljung',lag=10)
Box.test(dlog^2,lag=15,type='Ljung')
library(FinTS)
ArchTest(dlog^2,lag=15) 

###### Fitting using rugarch ######
# the mean model is ARMA(1,1)
library(rugarch)
model=ugarchspec(variance.model = list(model = "sGARCH", garchOrder = c(1, 1)),
                 mean.model = list(armaOrder = c(1, 1), include.mean = TRUE),
                 distribution.model = "norm")

modelfit=ugarchfit(spec=model,data=dlog)
# to get the estimated parameters
modelfit@fit$coef
coef(modelfit)
coef(modelfit)["mu"] 
# to get the fitted values of in-sample
modelfit@fit$fitted.values
plot(modelfit,which="all")
print(modelfit)
# conditional variance
time <- 1:length(dlog)
h.rugarch <- as.numeric(sigma(modelfit)^2)
par(mfrow=c(1,2))
plot(time, dlog, type="l", col=2)
plot(time, h.rugarch, type="l", col=3)
# residuals
resid.rugarch <- as.numeric(residuals(modelfit, standardize=TRUE))
plot(resid.rugarch, type="l", col=2)

## Check Residuals
# Check White Noise: ok
par(mfrow=c(1,2))
Acf(resid.rugarch)
Pacf(resid.rugarch)

# Ljung-Box test
# the residuals are assumed to be "white noise," meaning that they are identically, independently distributed (from each other). 
# Thus, as we saw last week, the ideal ACF for residuals is that all autocorrelations are 0.
# A small p-value (for instance, p-value < .05) indicates the possibility of 
# non-zero autocorrelation within the first m lags.
Box.test(resid.rugarch, lag=1, type="Ljung-Box", fitdf=0)
Box.test(resid.rugarch, lag=10, type="Ljung-Box", fitdf=0)
Box.test(resid.rugarch, lag=30, type="Ljung-Box", fitdf=0)
# Interpretation: in our case we have a large p value -> zero autocorrelation betweent the residuals

# Check Gaussianity: ok
qqnorm(resid.rugarch, col=2)
qqline(resid.rugarch, col=1)

#N ormality Statistics
kurtosis(resid.rugarch) # excess kurtosis, 0 for Gaussian


## Check Squared Residuals
par(mfrow=c(1,2))
Acf(resid.rugarch^2)
Pacf(resid.rugarch^2)
Box.test(resid.rugarch^2, lag=1, type="Ljung-Box", fitdf=0)
Box.test(resid.rugarch^2, lag=10, type="Ljung-Box", fitdf=0)
Box.test(resid.rugarch^2, lag=30, type="Ljung-Box", fitdf=0)


# Measure the perfomance of the model
modelfit2 =ugarchfit(spec=model,data=dlog, out.sample = 50)
forecast2 =ugarchforecast(modelfit2, n.ahead = 50)
# this means that 50 data points are left from the end with which to
# make inference on the forecasts
fpm(forecast2)


# Prediction for the next two months
forecast=ugarchforecast(modelfit, data = NULL, n.ahead = 60, n.roll= 0, out.sample = 0)
# the forecast of the series
fitted(forecast)
# the sigma (the conditional standard deviation) 
sigma(forecast)
# plot the series forecast (series of return)
plot(forecast@forecast$seriesFor)

# Series of predicted price for the next two months
price <- NULL
price[1] <- exp(forecast@forecast$seriesFor[1] + log(data$Close[dim(data)[1]]))
for (i in (2:60)){
  price[i] <- exp(forecast@forecast$seriesFor[i] + log(price[i-1]))
}
price <- as.data.frame(price)

