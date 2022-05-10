import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import seaborn as sns

import statsmodels.api as sm
import statsmodels.formula.api as smf #TODO

import warnings
warnings.filterwarnings('ignore')
from statsmodels.stats.outliers_influence import variance_inflation_factor
from sklearn.model_selection import train_test_split
import wooldridge as woo

woo.data('wage1', description = True)
df = woo.dataWoo('wage1')

new_df = df[['wage', 'educ', 'exper', 'tenure', 'numdep', 'lwage', 'expersq', 'tenursq']]
y = new_df['wage']
X = new_df.copy().drop(['wage','lwage'], axis=1)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=True, random_state = 2000)
X_train = sm.add_constant(X_train)

variables =  X_train.columns.tolist()
        
# 전진선택법이기 때문에 처음에는 비어있는 리스트에서 시작하여 1개 -> 2개 -> ... 증가할 것이다.
forward_variables = []
PV = 0.05
start_step = 0.05
steps = []
adj_list = []
step = []

while len(variables) > 0: # 모든 변수를 조작했을 때까지
    remain = list(set(variables) - set(forward_variables)) # 조작을 위해 set으로 각각의 list 설정
    pvalue = pd.Series(index = remain)
    

    for i in remain:
        X = X_train[forward_variables+[i]]

        X = sm.add_constant(X)
        model = sm.OLS(y_train,X).fit()
        pvalue[i] = model.pvalues[i]
        
    
    # P-value가 가장 작은 feature부터 포함 여부를 확인한다. 이는 전진선택법의 특성이다.
    # 아래의 후진제거법에서는 모든 특성 변수들 중 P-value가 가장 큰 값부터 소거하는 방식으로 이루어지기 때문에 Max를 사용한다.
    if pvalue.idxmin() == 'const':
        sub_pvalue = pvalue.copy().drop(labels=['const'])
        min_pvalue = sub_pvalue.min()
    else:
        sub_pvalue = pvalue
        min_pvalue = pvalue.min()

    # 최소 p-value 값이 기준 값(0.05)보다 작으면 포함
    if min_pvalue < PV:
        forward_variables.append(sub_pvalue.idxmin())
        
        while len(forward_variables) > 0:
            selected_X = X_train[forward_variables]
            selected_X = sm.add_constant(selected_X)
            selected_pvalue = sm.OLS(y_train, selected_X).fit().pvalues

            max_pvalue = selected_pvalue.max()
            # p-value 값의 최댓값이 기준값보다 크가나 같으면 제외
            if max_pvalue >=  PV:
                removed_variable = selected_pvalue.idxmax()
                forward_variables.remove(removed_variable)
            else:
                break

        start_step += 1
        steps.append(start_step)
        adj_rsquare = sm.OLS(y_train, sm.add_constant(X_train[forward_variables])).fit().rsquared_adj
        adj_list.append(adj_rsquare)
        step.append(forward_variables.copy())
    else:
        break
print(step)