# Imports
import numpy as np
import pandas as pd

from pandas_datareader import data as pdr
import riskfolio as rp

import yfinance as yf # 야후 바이낸스의 차트의 주가 정보를 가져옴.
yf.pdr_override()

import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")

# 초기 세팅
start = '2001-01-01'
end = '2022-01-01'
stocks = ["005930.KS", "000270.KS", "000660.KS","035720.KS"]
bonds = ['122260.KS', '114260.KS']
# 122260.KS (1년물 채권)
# 114260.KS (3년물 채권)
# 397420.KS (5년물 채권)
assets = stocks + bonds

# 회사 주가
def price():
    df = pd.DataFrame()
    for i in assets:
        raw = pdr.get_data_yahoo(i, start=start, end=end)['Adj Close']
        raw.name = i
        # raw.name = info(yf.Ticker(i))['shortName']
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

    model = 'Classic' # Model은 BL (Black Litterman) OR FM (Factor Model)
    rm = 'MV' # Risk Measure가 사용됨 (지금은 분산 사용)
    obj = 'Sharpe' # 샤프를 구하려고 함. MinRisk, MaxRet, Utility 가능
    hist = True # 역사적 시나리오 사용
    rf = 0 # Risk free rate은 0으로 가정
    l = 0 # Risk aversion factor(Util일때만 사용 가능)

    port = rp.Portfolio(returns = Y)
    pd.options.display.float_format = '{:.4%}'.format    

    method_mu = 'hist' # Expected returns based on historical data.
    method_cov = 'hist' # Covariance matrix based on historical data.
    port.assets_stats(method_mu = method_mu, method_cov = method_cov, d = 0.94)

    w = port.optimization(model=model, rm=rm, obj=obj, rf=rf, l=l, hist=hist)
    print(w.T)

    ax = rp.plot_pie(w=w, title='Sharpe Mean Variance', others=0.05, nrow=25, cmap = "tab20",
                    height=6, width=10, ax=None)
    # plt.subplot(2,1,1)
    
    frontier = port.efficient_frontier(model=model, rm=rm, points=20, rf=rf, hist=hist)
    label = 'Max Risk Adjusted Return Portfolio'
    mu = port.mu
    cov = port.cov
    returns = port.returns

    bx = rp.plot_frontier(w_frontier=frontier, mu=mu, cov=cov, returns=returns, rm=rm,
                    rf=rf, alpha=0.05, cmap='viridis', w=w, label=label,
                    marker='*', s=16, c='r', height=6, width=10, bx=None)
    # plt.subplot(2,1,2)
    # plt.show()
        
portfolio()