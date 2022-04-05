import pandas as pd

from learntools.core import binder
binder.bind(globals())
from learntools.ml_intermediate.ex1 import *
print("Setup Complete")

from sklearn.decomposition import randomized_svd
from sklearn.model_selection import train_test_split

# Read Data
X_full = pd.read_csv('Projects\\Housing_price\\train.csv', index_col="Id")
X_test_full = pd.read_csv('Projects\\Housing_price\\test.csv', index_col="Id")

y = X_full.SalePrice

features = ['LotArea', 'YearBuilt', '1stFlrSF', '2ndFlrSF', 'FullBath', 'BedroomAbvGr', 'TotRmsAbvGrd']
X = X_full[features].copy()
X_test = X_test_full[features].copy()

X_train, X_valid, y_train, y_valid = train_test_split(X, y, train_size=0.8, test_size=0.2, random_state = 0)

# 앙상블 분석
from sklearn.ensemble import RandomForestRegressor

model_1 = RandomForestRegressor(n_estimators=50, random_state=0)
model_2 = RandomForestRegressor(n_estimators=100, random_state=0)
model_3 = RandomForestRegressor(n_estimators=100, random_state=0) # criterion : Split의 품질을 측정하는 기능(mse : mean squared error, mae : mean absolute error)
model_4 = RandomForestRegressor(n_estimators=100, random_state=0, max_depth=7) # 덴드로그램처럼 K를 정하는 느낌.
model_5 = RandomForestRegressor(n_estimators=200, random_state=0, min_samples_split=20) # 셈플이 나눠지기 위한 최소의 셈플 수

models = [model_1,model_2,model_3,model_4,model_5]

# 모델들 중 최고를 선정하기 위해 score_model() 메서드 이용.
from sklearn.metrics import mean_absolute_error
def model_score(model, X_t = X_train, X_v = X_valid, y_t = y_train, y_v = y_valid):
    model.fit(X,y)
    preds = model.predict(X_v)
    return mean_absolute_error(y_v, preds)

epoch = 0
for i in models:
    epoch += 1
    mae = model_score(i)
    print(f"Model{epoch} MAE : {mae}")

my_model = model_3
my_model.fit(X,y)

preds_test = my_model.predict(X_test)
output = pd.DataFrame({
    'id' : X_test.index,
    'SalesPrice' : preds_test
})

output.to_csv('submission.csv', index=False)
print(output)