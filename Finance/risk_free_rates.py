# 1. Free Entity Exists(미국 국채 사용)
# 2. No Default - Free Entity

import pandas as pd
import numpy as np
from pandas_datareader import data as pdr
import matplotlib.pyplot as plt

import yfinance as yf
from datetime import datetime as dt
yf.pdr_override()

import warnings
warnings.filterwarnings("ignore")

# 1. Free Entity Exists(미국 국채 사용)
def find_risk_free_by_treasury(stock_code = '^FVX'):
    # 미국채 5년물 채권 symbol  : ^FVX
    # 미국채 10년물 채권 symbol : ^TNX
    # 미국채 30년물 채권 symbol : ^TYX
    today = dt.strftime(dt.today(),"%Y-%m-%d")
    risk_free = pdr.get_data_yahoo(stock_code, start = today, end = today)
    
    return risk_free['Close'][0]

# 2. No Default - Free Entity

# 2.1 Local currency government bond

# 2.2 Build up approach

# 2.3 Derivatives markets
def find_data_by_derivatives(F, S, rf, T):
    # 달러 선물의 이론 가격 공식
    # r = Domestic Risk rate
    r = (F/S)**(1/T)+rf-1
    
    # rf = Foreign Risk rate
    # S = 현물 이자율
    # F = 선도 이자율
    return r