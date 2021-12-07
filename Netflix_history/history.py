import FinanceDataReader as fdr
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

def Beta(Re, Rm):
    Cov = np.cov(Re,Rm)[0,1]
    var = np.var(Rm)
    try:
        k = Cov / var
        return k
    except RuntimeWarning:
        return 0

start_date = '2000-01-01'
end_date = '2021-12-01'

stock = fdr.DataReader('AMZN', '2010')
market = fdr.DataReader('US500', '2010')

close_stock = []
close_market = []
for i in tqdm(range(min(len(stock), len(market)) -1)):
    close_stock.append(((stock["Close"][i+1] / stock["Close"][i]) -1)*100)
    close_market.append(((market["Close"][i+1] / market["Close"][i]) -1)*100)

print(len(close_stock))
print(len(close_market))
for i,j in zip(close_stock, close_market):
    beta = []

print(beta)


'''
def CAFM():

    return expected_return'''