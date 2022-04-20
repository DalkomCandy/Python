import pandas as pd
import numpy as np
from pandas_datareader import data as pdr
import matplotlib.pyplot as plt

import yfinance as yf
import datetime
yf.pdr_override()

import warnings
warnings.filterwarnings("ignore")

def find_data(start, end, stock_code):
    # start = '2000-01-04'
    # end = '2022-01-01'
    idx = pd.date_range(start, end)

    stock = pdr.get_data_yahoo(stock_code, start = start, end = end)
    return stock