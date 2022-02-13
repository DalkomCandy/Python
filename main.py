import pandas as pd
import numpy as np
from sklearn.model_selection import *

df = pd.read_csv('ETFs_main.csv')

# Rolling = 이동평균

# 이동평균
def moving_average(df, n):
    MA = pd.Series(df['CLOSE_SPY'].rolling(n, min_periods = n).mean(), name = "MA_" + str(n))
    df = df.join(MA)
    return df

# 거래량 이동 평균
def volume_moving_average(df, n):
    VMA = pd.Series(df['VOLUME'].rolling(n, min_periods = n).mean(), name = 'VMA_' + str(n))
    df = df.join(VMA)
    return df


# 시장 강도 지수
def relative_strength_index(df, n):
    i = 0
    UPI = [0]
    DOI = [0]
    
    while i + 1 <= df.index[-1]:
        UpMove = df.loc[i+1, 'HIGH'] - df.loc[i, 'HIGH']
        DoMove  = df.loc[i, 'LOW'] - df.loc[i+1, 'LOW']
        if UpMove > DoMove and UpMove > 0:
            UPD = UpMove
        else:
            UPD = 0
        UPI.append(UPD)
        
        if DoMove > UpMove and DoMove > 0:
            DOD = DoMove
        else:
            DOD = 0
        DOI.append(DOD)
        i += 1
    UPI = pd.Series(UPI)
    DOI = pd.Series(DOI)
    PosDI = pd.Series(UPI.ewm(span=n, min_periods=n).mean())
    NegDI = pd.Series(DOI.ewm(span=n, min_periods=n).mean())
    
    RSI = pd.Series(PosDI / (PosDI + NegDI), name = 'RSI_' + str(n))
    df = df.join(RSI)
    return df        
    
def run(df):
    # 실제 경과 일수는 60일이지만 영업일 기준인 45일로 작성
    df = moving_average(df, 45)
    df = volume_moving_average(df, 45)
    df = relative_strength_index(df, 14) # 시장 강도 지수로는 14일 or 21일을 자주 사용함.

    df = df.set_index('Dates')
    df = df.dropna()

    # 일별 수익률
    df['target'] = df['CLOSE_SPY'].pct_change()
    df['target'] = np.where(df['target'] > 0, 1, -1) # 수익률이 0보다 크면 1, 0보다 작으면 -1

    df['target'] = df['target'].shift(-1)
    df = df.dropna()
    df['target'] = df['target'].astype(np.int64)

    # 레이블 변수
    y_var = df['target']

    # 설명 변수
    x_var = df.drop(['target', 'OPEN', 'HIGH', 'LOW', 'VOLUME', 'CLOSE_SPY'], axis = 1)

    up = df[df['target'] == 1].target.count()
    total = df.target.count()
    print('up/down ratio : {0:.2f}'.format(up/total))
    
run(df)

# 머신 러닝 준비
x_train, x_test, y_train, y_test = train_test_split(x_var, y_var, test_size=0.3, shuffle=False, random_state=3)
# test_size : 0.3를 test-set으로 지정(Default = 0.25)
# shuffle : split을 해주기 이전에 섞을건지 여부(Default = True)
# stratify : stratify = traget일 경우 각각의 class 비율을 train / validation에 유지해줌.
# random_state : 세트를 섞을 때 해당 int 값을 참조하고 섞는다.