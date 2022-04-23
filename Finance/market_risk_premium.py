import pandas as pd
import numpy as np
from pandas_datareader import data as pdr
import matplotlib.pyplot as plt
from regex import R

import yfinance as yf
from datetime import datetime as dt
yf.pdr_override()

import warnings
warnings.filterwarnings("ignore")

def historical(stock_code='042700.KS', start='2000-01-04', end='2022-04-22', interval='3mo'):
    price = pdr.get_data_yahoo(stock_code, start = start, end = end, interval=interval)
    stock = pd.concat([price['Close'], round(price['Close'].pct_change()*100,2)], axis=1)
    stock.columns = ['price', 'pct_change']
    stock = stock.dropna()
    
    # print('Arithmetic Average : '+str(round(stock['pct_change'].mean(),2))+'%') # 주 평균 0.46%
    # print('Geometric Average : ' +str(round(np.exp(np.log(stock['pct_change']).mean()),2))+'%')
    return round(np.exp(np.log(stock['pct_change']).mean()),2)