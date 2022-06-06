import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from fqtoolkit import dgToDf as dtd
import statsmodels.api as sm

from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import classification_report

assets, liability, sale, income, price = [item[1] for item in dtd("data2.xlsx", "Sheet1", 5).items()]

# 자산과 부채의 경우,
# 해당 값이 아닌 변화랑을 사용하기 위해 pct_change() 사용.
assets0 = assets.pct_change()
liability0 = liability.pct_change()

# asset, liability value는 12개월간 변하지 않으므로, 
# 가장 최근 주어진 변화율로 0을 채움.
assets0 = assets0.where(assets0 != 0, np.nan)
assets0 = assets0.fillna(method="ffill")

liability0 = liability0.where(liability0 != 0, np.nan)
liability0 = liability0.fillna(method="ffill")

#shift를 통해 정보를 실제로 얻는 시점까지 미룸

assets0 = assets0.shift(12+6)
liability0 = liability0.shift(12+6)
sale = sale.shift(12+6)
income = income.shift(12+6)

returns = price.pct_change()
returns = price.shift(0).pct_change()
returns0 = price.shift(0).pct_change()



def find_max_depth():
    results = {}
    r2 = []
    Max_Depth = 0
    Depth = 0
    Rolling_period = 0
    
    for k in range(5,201,5):
    
        for maxD in range(1,20):
            for col in returns.columns:
                reSeries = {}
                for n in range(1, returns.shape[0]-152):
                    #n부터 n+1**까지의 롤링 데이터 준비
                    temp = pd.DataFrame({"asset":assets0[col].iloc[n:n+151], #n시점의 총자산 변화율
                                        "liability":liability0[col].iloc[n:n+151], #n시점의 총부채 변화율
                                        "sale":sale[col].iloc[n:n+151], #n시점의 매출액
                                        "income":income[col].iloc[n:n+151], #n시점의 영업이익
                                        "re0": returns[col].iloc[n-1:n+150], #n-1시점의 종목 수익률
                                        "re": returns[col].iloc[n:n+151]}) #n시점의 종목 수익률

                    temp = temp.dropna() # 데이터 결측치 제거
                    
                    if temp.shape[0] < 50: #만약 결측치를 제거하였을 때도 길이가 50보다 작을 경우, signal 생성을 하지 않음
                        continue

                    model = DecisionTreeRegressor(max_depth=maxD, random_state=10)
                    model.fit(temp.drop("re", axis=1).iloc[:-1,:], temp["re"].iloc[:-1]) #현재 수익률 추정 모형 fitting
                    r = model.predict(temp.drop("re", axis=1).iloc[[-1], :]) #현재 시점의 추정 수익률 계산
                    reSeries[temp.index[-1]] = temp["re"].iloc[-1]-r[0] #현재 시점의 추정오차 저장

                    if len(reSeries) > 0: #추정오차 데이터가 있는 경우만 signal 저장
                        results[col] = pd.Series(reSeries) 


            results = pd.DataFrame(results) #시그널 데이터프레임화
            signal = (results).mean(axis=1) #종목별 시그널 통합

            temp = pd.DataFrame({"returns":returns.shift(-1).mean(axis=1), "result":signal}).dropna() #성능 측정용 데이터 준비
            test = temp.iloc[int(temp.shape[0]/4):2*int(temp.shape[0]/4), :] #validation set
            test0 = temp.iloc[2*int(temp.shape[0]/4):, :] #test set

            mu = temp.result.iloc[:int(temp.shape[0]/4)].mean() #training set에서의 signal 평균
            sd = temp.result.iloc[:int(temp.shape[0]/4)].std() #training set에서의 signal 표준편차

            test.result = (test.result-mu)/sd #training set 평균 표준편차를 이용한 정규화
            test0.result = (test0.result-mu)/sd #training set 평균 표준편차를 이용한 정규화
            
            r2_score = np.corrcoef(test.returns, -test.result)[1,0 ] ** 2 * 100
            
            if r2_score > Max_Depth:
                Max_r2_score = r2_score
                Depth = maxD
                Rolling_period = k

            # signal과 미래 수익률 간의 R Squared 측정
            r2.append(np.corrcoef(test.returns, -test.result)[1,0 ] ** 2 )
        
    return Rolling_period, Depth, round(Max_r2_score*100,4), r2

Rolling_period, max_depth, r2_score,r2 = find_max_depth()
print(Rolling_period, max_depth, r2_score)
