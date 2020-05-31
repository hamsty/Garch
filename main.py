import pandas as pd
from rpy2.robjects.packages import importr, isinstalled
from rpy2.robjects import default_converter, pandas2ri, r, numpy2ri, NULL, globalenv
from rpy2.robjects.conversion import localconverter
import rpy2.rinterface
import numpy as np
import asyncio


async def main():
    base = importr("base")
    rprint = rpy2.rinterface.baseenv['print']
    utils = importr("utils")
    graphics = importr("graphics")
    grDevices = importr("grDevices")
    stats = importr("stats")
    utils.chooseCRANmirror(ind=15)
    data = pd.read_excel("Dolar_Futuro.xlsx")
    data.columns = ["Date", "Close"]
    grDevices.x11()
    graphics.par(mar=r.c(1, 1, 1, 1))
    with localconverter(default_converter + pandas2ri.converter + numpy2ri.converter) as cv:
        r.plot(data, main="Futures price series", xlab="Date")

        if not isinstalled("TSA"):
            utils.install_packages("leaps")
            utils.install_packages("locfit")
            utils.install_packages("TSA_1.2.1.tar.gz")
        TSA = importr("TSA")

        if not isinstalled("forecast"):
            utils.install_packages("forecast")
        forecast = importr("forecast")

        if not isinstalled("fBasics"):
            utils.install_packages("fBasics")
        fBasics = importr("fBasics")
        dlog = np.log(data.Close)
        ests = fBasics.basicStats(dlog)
        ests.columns = [""]
        print(ests)
        r.hist(dlog, breaks=100)
        r.tsdisplay(dlog)

        bp1 = stats.Box_test(dlog, type="Ljung", lag=10)
        print(bp1)
        bp2 = stats.Box_test(dlog ** 2, lag=15, type='Ljung')
        print(bp2)

        if not isinstalled("FinTS"):
            utils.install_packages("FinTS")
        FinTS = importr("FinTS")
        pF = FinTS.ArchTest(dlog ** 2, lag=15)
        print(pF)

        if not isinstalled("rugarch"):
            utils.install_packages("rugarch")
        rugarch = importr("rugarch")
        model = rugarch.ugarchspec(variance_model=r.list(model="sGARCH", garchOrder=r.c(1, 1)),
                                   mean_model=r.list(armaOrder=r.c(1, 1), include_mean=True), distribution_model="norm")
        modelfit = rugarch.ugarchfit(spec=model, data=dlog)
        modelfitfind = lambda x, y: x[int(np.where(x.names == y)[0][0])]
        print(modelfitfind(modelfit.slots["fit"], "coef"))
        rugarch.coef(modelfit)
        rugarch.coef(modelfit)[0]
        print(modelfitfind(modelfit.slots["fit"], "fitted.values"))
        r.plot(modelfit, which="all")
        print(modelfit)
        time = list(range(0, dlog.shape[0]))
        h_rugarch = base.as_numeric(rugarch.sigma(modelfit) ** 2)
        graphics.par(mfrow=r.c(1, 2))
        r.plot(time, dlog, type="l", col=2)
        r.plot(time, h_rugarch, type="l", col=3)
        resid_rugarch = base.as_numeric(rugarch.residuals(modelfit, standardize=True))
        r.plot(resid_rugarch, type="l", col=2)

        graphics.par(mfrow=r.c(1, 2))
        forecast.Acf(resid_rugarch)
        forecast.Pacf(resid_rugarch)

        bp3 = stats.Box_test(resid_rugarch, lag=1, type="Ljung-Box", fitdf=0)
        print(bp3)
        bp4 = stats.Box_test(resid_rugarch, lag=10, type="Ljung-Box", fitdf=0)
        print(bp4)
        bp5 = stats.Box_test(resid_rugarch, lag=30, type="Ljung-Box", fitdf=0)
        print(bp5)

        stats.qqnorm(resid_rugarch, col=2)
        stats.qqline(resid_rugarch, col=1)

        TSA.kurtosis(resid_rugarch)

        graphics.par(mfrow=r.c(1, 2))
        forecast.Acf(resid_rugarch ** 2)
        forecast.Pacf(resid_rugarch ** 2)
        bp6 = stats.Box_test(resid_rugarch ** 2, lag=1, type="Ljung-Box", fitdf=0)
        print(bp6)
        bp7 = stats.Box_test(resid_rugarch ** 2, lag=10, type="Ljung-Box", fitdf=0)
        print(bp7)
        bp8 = stats.Box_test(resid_rugarch ** 2, lag=30, type="Ljung-Box", fitdf=0)
        print(bp8)

        modelfit2 = rugarch.ugarchfit(spec=model, data=dlog, out_sample=50)
        forecast2 = rugarch.ugarchforecast(modelfit2, n_ahead=50)

        rugarch.fpm(forecast2)

        forecast = rugarch.ugarchforecast(modelfit, data=NULL, n_ahead=60, n_roll=0, out_sample=0)
        rugarch.fitted(forecast)
        rugarch.sigma(forecast)

        r.plot(modelfitfind(forecast.slots["forecast"], "seriesFor"))

        price = list()
        price.append(
            base.exp(
                modelfitfind(forecast.slots["forecast"], "seriesFor")[0] + np.log(data.Close.loc[0])))
        for i in range(1, 60):
            price.append(base.exp(modelfitfind(forecast.slots["forecast"], "seriesFor")[0] + np.log(price[i - 1])))
        price = pd.DataFrame(data={"price_forecast": price})
        r("source('Code_GARCH.r')")
        await asyncio.sleep(1)
        price = price.assign(price2=r["price"]["price"])
        print(price)


if __name__ == '__main__':
    asyncio.run(main())
    r("while (1){               \n"
      "    if (dev.cur()==1){   \n"
      "        break            \n"
      "    }                    \n"
      "}                        \n")
