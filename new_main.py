import pandas as pd
from rpy2.robjects.packages import importr,isinstalled
from rpy2.robjects import pandas2ri, default_converter, r
from rpy2.robjects.conversion import localconverter, rpy2py
import socket
packages = ["xlsx","leaps","locfit","fBasics","forecast","TSA","FinTS","rugarch"]
utils = importr("utils")
utils.chooseCRANmirror(ind=15)
for p in packages:
    if not isinstalled(p):
        if p == "TSA":
            utils.install_packages("TSA_1.2.1.tar.gz")
            continue
        utils.install_packages(p)


r("source('Code_Garch.r')")
price = None
with localconverter(default_converter + pandas2ri.converter):
    price = rpy2py(r["price\n"])
print("Fim Code_Garch.r")
print(price)
r("while (1){               \n"  
      "    if (dev.cur()==1){   \n"
      "        break            \n"
      "    }                    \n"
      "}                        \n")