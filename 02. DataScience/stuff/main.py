import warnings
warnings.filterwarnings('ignore')
import pandas as pd
import numpy as np
from sklearn.metrics import *
from sklearn.model_selection import *
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from xgboost import XGBClassifier

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
    
    return x_var, y_var
    
x_var, y_var = run(df)

# 머신 러닝 준비
# test_size : 0.3를 test-set으로 지정(Default = 0.25)
# shuffle : split을 해주기 이전에 섞을건지 여부(Default = True)
# stratify : stratify = traget일 경우 각각의 class 비율을 train / validation에 유지해줌.
# random_state : 세트를 섞을 때 해당 int 값을 참조하고 섞는다.
x_train, x_test, y_train, y_test = train_test_split(x_var, y_var, test_size=0.3, shuffle=False, random_state=3)
train_count = y_train.count()
test_count = y_test.count()

print('Train Set Label Ratio')
print(y_train.value_counts()/train_count)
print('Test Set Label Ratio')
print(y_test.value_counts()/test_count)

# ROC-AUC 점수
def get_confusion_matrix(y_test, pred):
    confusion = confusion_matrix(y_test, pred)
    accuracy = accuracy_score(y_test, pred)
    precision = precision_score(y_test, pred)
    recall = recall_score(y_test, pred)
    f1 = f1_score(y_test, pred)
    roc_score = roc_auc_score(y_test, pred)
    print('Confusion Matrix')
    print('accuracy:{0:.4f}, precision : {1:.4f}, recall : {2:.4f}, F1 : {3:.4f}, ROC_AUC_SCORE = {4:.4f}'.format(accuracy, precision, recall, f1, roc_score))
    
# XGBoost 분류기
def XGBoost(x_train = x_train, y_train = y_train, x_test = x_test, y_test = y_test):
    xgb_dis = XGBClassifier(n_estimators = 400, learning_rate = 0.1, max_depth = 3)
    xgb_dis.fit(x_train, y_train)
    gbrt = GradientBoostingClassifier(random_state = 0)
    xgb_pred = xgb_dis.predict(x_test)
    print('xgb_dis_score : ', xgb_dis.score(x_train, y_train))
    get_confusion_matrix(y_test, xgb_pred)
    
    gbrt.fit(x_train, y_train)
    gbrt_pred = gbrt.predict(x_test)
    print('gbrt_score : ', gbrt.score(x_train, y_train))
    get_confusion_matrix(y_test, gbrt_pred)

XGBoost()
n_estimator = range(10, 200, 10)
params = {
    'bootstrap' : [True],
    'n_estimator': n_estimator,
    'max_depth' : [4,6,8,10,12],
    'min-samples_leaf' : [2,3,4,5],
    'min_samples_split': [2,4,6,8,10],
    'max_features' : [4]
}
my_cv = TimeSeriesSplit(n_splits = 5).split(x_train)
clf = GridSearchCV(RandomForestClassifier(), params, cv = my_cv, n_jobs = -1)
clf.fit(x_train, y_train)