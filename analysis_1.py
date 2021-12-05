import numpy as np
import pandas as pd
import pprint
import FinanceDataReader as fdr
from itertools import groupby, chain


class Core():
    def __init__(self):
        self.annual = 252

    # 산술평균
    def average(self, returns):
        return returns.mean() * self.annual

    # 기하평균
    def cagr(self, returns):
        return (1+ returns).prod() ** (self.annual / len(returns)) -1

    # 표준편차
    def stdev(self, returns):
        return returns.std() * np.sqrt(self.annual)

    # 하방 표준편차 
    def downdev(self, returns, target= 0.0):
        returns = returns.copy()
        returns.loc[returns > target] = 0
        summation = (returns ** 2).sum()
        return np.sqrt(self.annual * summation / len(returns))

    # 상방 표준편차
    def updev(self, returns, target= 0.0):
        returns = returns.copy()
        returns.loc[returns < target] = 0
        summation = (returns ** 2).sum()
        return np.sqrt(self.annual * summation / len(returns))

    def covar(self, returns, benchmark):
        return returns.cov(benchmark) * self.annual

    def correl(self, returns, benchmark):
        return returns.corr(benchmark)

    def print_result(self, returns, benchmark, target = 0.0):
        average = self.average(returns)
        cagr = self.cagr(returns)
        stdev = self.downdev(returns, target)
        downdev = self.downdev(returns, target)
        updev = self.updev(returns, target)
        covar = self.covar(returns, benchmark)
        correl = self.correl(returns, benchmark)

        result = {
        "Arithmetric Return" : round(average,2), 
        "Compound Return" : round(cagr,2), 
        "Volatility" : round(stdev,2),
        "Downside Deviation" : round(downdev,2),
        "Upside Deviation" : round(updev,2),
        "Covariance" : round(covar,2),
        "Correlation" : round(correl,2)
        }

        return result

class Tail():
    # 왜도 : 수익률 분포의 비대칭 정도
    def skewness(self, returns):
        return returns.skew()

    # 첨도 : Fat-tail 정도를 측정
    def kurtosis(self, returns):
        return returns.kurtosis()
    
    '''    # 공왜도 : 밴치마크 대비 전략의 수익률 분포가 얼마나 왜도를 가지고 있는가?
    def coskewness(self, returns, benchmark):
        r_mean = returns.mean()
        b_mean = benchmark.mean()
        r_stdev = returns.std()
        b_stdev = benchmark.std()
        T = len(returns)
        summation = ((returns - r_mean) - ((benchmark - b_mean) ** 2) / (r_stdev * (b_stdev ** 2))).sum()
        return (T / ((T - 1) * (T - 2))) ** summation

    def cokurtosis(self, returns, benchmark):
        r_mean = returns.mean()
        b_mean = benchmark.mean()
        r_stdev = returns.std()
        b_stdev = benchmark.std()
        T = len(returns)
        summation = ((returns - r_mean) - ((benchmark - b_mean) ** 3) / (r_stdev * (b_stdev ** 3))).sum()
        return ((T * (T+1)) / ((T - 1) * (T - 2)*(T - 3))) * summation - (3 * (T - 1) ** 2) / ((T - 2) * (T - 3))'''

    def drawdown(self, returns):
        cumulative = (1 + returns).cumprod()
        highwatermark = cumulative.cummax()
        drawdown = (cumulative / highwatermark) - 1
        return drawdown

    # 최대 낙폭
    def maximum_drawdown(self, returns):
        return np.min(self.drawdown(returns))

    # 낙폭 기간
    def drawdown_duration(self, returns):
        drawdown = self.drawdown(returns)
        ddur = list(chain.from_iterable((np.arange(len(list(j))) + 1).tolist() if i == 1 else [0] * len(list(j)) for i,j in groupby(drawdown != 0)))
        ddur = pd.DataFrame(ddur)
        ddur.index = returns.index
        return ddur

    def maximum_drawdown_duration(self, returns):
        return self.drawdown_duration(returns).max()[0]

    # 최대예상손실액 (신뢰 수준 99%)
    def VaR(self, returns, percentile=99):
        return returns.quantile(1 - percentile / 100)
    
    def cVar(self, returns, percentile=99):
        return returns[returns < self.VaR(returns, percentile)].mean()

    def print_result(self, returns, benchmark, percentile=99):
        skew = self.skewness(returns)
        kurt = self.kurtosis(returns)
        '''coskew = self.coskewness(returns, benchmark)
        cokurt = self.cokurtosis(returns, benchmark)'''
        mdd = self.maximum_drawdown(returns)
        mddur = self.maximum_drawdown_duration(returns)
        vaR = self.VaR(returns, percentile)
        cvaR = self.cVar(returns, percentile) 

        result = {
            "Skewness" : round(skew, 2),
            "kurtosis" : round(kurt, 2),
            '''
            "Co-skewness" : round(coskew, 2),
            "Co-kurtosis" : round(cokurt, 2),
            '''
            "Maximum Drawdown" : round(mdd, 2),
            "Maximum Drawdown Duration" : round(mddur, 2),
            "99% VaR" : round(vaR,2),
            "99% CVaR" : round(cvaR,2)
        }
        return result

if __name__ == "__main__":

    start_date = '2000-01-01'
    end_date = '2020-12-31'

    Amazon = fdr.DataReader('AMZN', start_date, end_date)
    Nasdaq = fdr.DataReader('IXIC', start_date, end_date)

    Amazon_ret = Amazon['Close'].pct_change().dropna()
    Nasdaq_ret = Nasdaq['Close'].pct_change().dropna()
    
    core = Core()
    core_result = core.print_result(Amazon_ret, Nasdaq_ret)

    tail = Tail()
    tail_result = tail.print_result(Amazon_ret, Nasdaq_ret)
    
    pprint.pprint(core_result)
    pprint.pprint(tail_result)