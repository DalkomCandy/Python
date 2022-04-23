import pandas as pd
import numpy as np
from pandas_datareader import data as pdr
import matplotlib.pyplot as plt

import yfinance as yf
import datetime
yf.pdr_override()

import warnings
warnings.filterwarnings("ignore")

def find_market_risk_premium(stock_code, start = '2000-01-04', end = '2022-01-01'):
    start = '2000-01-01'
    end = '2022-01-01'
    price = pdr.get_data_yahoo(stock_code, start = start, end = end, interval='1wk')
    stock = pd.concat([price['Close'], round(price['Close'].pct_change()*100,2)], axis=1)
    stock = stock.dropna()
    return stock

k = find_data('042700.KS', '2000-01-04','2022-01-01')
print(k)
