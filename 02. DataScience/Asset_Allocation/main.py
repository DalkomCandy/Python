# 1. Downloading the data
import numpy as np
import pandas as pd
import yfinance as yf # 야후 바이낸스의 차트의 주가 정보를 가져옴.
import warnings

import riskfolio as rp
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore") # 경고 메시지 무시
pd.options.display.float_format = '{:.4%}'.format # 실수 x를 받아 소수점 넷째자리까지만 표현

start = '2016-01-01'
end = '2019-12-30'

assets = ['JCI', 'TGT', 'CMCSA', 'CPB']
assets.sort()

data = yf.download(assets, start = start, end = end)
data = data.loc[:,('Adj Close', slice(None))]
data.columns = assets

Y = data[assets].pct_change().dropna()

model = 'Classic' # Model은 BL (Black Litterman) OR FM (Factor Model)
rm = 'MV' # Risk Measure가 사용됨 (지금은 분산 사용)
obj = 'Sharpe' # 샤프를 구하려고 함. MinRisk, MaxRet, Utility 가능
hist = True # 역사적 시나리오 사용
rf = 0 # Risk free rate은 0으로 가정
l = 0 # Risk aversion factor(Util일때만 사용 가능)

port = rp.Portfolio(returns = Y)

method_mu = 'hist' # Expected returns based on historical data.
method_cov = 'hist' # Covariance matrix based on historical data.

port.assets_stats(method_mu = method_mu, method_cov = method_cov, d = 0.94)

# 2. Estimation Mean Variance Portfolios
def maximize_ratio():
    w = port.optimization(model=model, rm=rm, obj=obj, rf=rf, l=l, hist=hist)
    print(w.T)
    
    ax0 = rp.plot_pie(w=w, title='Sharpe Mean Variance', others=0.05, nrow=25, cmap = "tab20",
                     height=6, width=10, ax=None)
    plt.show()
    
def effi_frontier():
    points = 50 # Frontier에 있는 포인트의 수
    frontier = port.efficient_frontier(model=model, rm=rm, points=points, rf=rf, hist=hist)    
    label = 'Max Risk Adjusted Return Portfolio'
    mu = port.mu
    cov = port.cov
    returns = port.returns
    
    ax1 = rp.plot_frontier(w_frontier=frontier, mu=mu, cov=cov, returns=returns, rm=rm,
                      rf=rf, alpha=0.05, cmap='viridis', w=w, label=label,
                      marker='*', s=16, c='r', height=6, width=10, ax=None)
    plt.show()

def Optimal_Portfolio():

    rms = ['MV', 'MAD', 'MSV', 'FLPM', 'SLPM', 'CVaR',
           'EVaR', 'WR', 'MDD', 'ADD', 'CDaR', 'UCI', 'EDaR']
    w_s = pd.DataFrame([])
    
    for i in rms:
        w = port.optimization(model=model, rm=i, obj=obj, rf=rf, l=l, hist=hist)
        w_s = pd.concat([w_s, w], axis=1)
    w_s.columns = rms
    w_s.style.format("{:.2%}").background_gradient(cmap='YlGn')
    
