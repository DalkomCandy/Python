# Imports
import numpy as np
import pandas as pd

from pandas_datareader import data as pdr
import riskfolio as rp
import yfinance as yf
yf.pdr_override()

import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")

def price(assets, start, end):
    df = pd.DataFrame()
    for i in assets:
        raw = pdr.get_data_yahoo(i, start=start, end=end)['Adj Close']
        raw.name = i
        
        df = pd.concat([df, raw], axis = 1)
    return df
    
# 회사 요약 정보
def info(ticker_df):
    df_info = ticker_df.info
    return df_info

# 회사 배당, 분할 정보
def action(ticker_df):
    df_data = ticker_df.actions
    return df_data
    
# 회사 재무제표
def financials(ticker_df):
    df_finance = ticker_df.financials
    return df_finance
    
# 주주정보
def holders(ticker_df):
    df_holder = ticker_df.major_holders
    return df_holder

# 대차 대조표
def balance(ticker_df):
    df_balance = ticker_df.balance_sheet
    return df_balance

# 현금흐름표
def cashflow(ticker_df):
    df_cashflow = ticker_df.cashflow
    return df_cashflow

# 기업실적
def earnings(ticker_df):
    df_earnings = ticker_df.earnings
    return df_earnings

def portfolio():
    df = price()
    Y = df[assets].pct_change().dropna()