import warnings
warnings.filterwarnings('ignore')

import pandas as pd
from sklearn.decomposition import randomized_svd
from sklearn.model_selection import train_test_split

from learntools.core import binder
binder.bind(globals())
from learntools.ml_intermediate.ex2 import *
print("Setup Complete")

# Read Data
X_full = pd.read_csv('Projects\\Housing_price\\train.csv', index_col="Id")
X_test_full = pd.read_csv('Projects\\Housing_price\\test.csv', index_col="Id")

X_full.dropna(axis=0, subset=['SalePrice'], inplace=True)
y = X_full.SalePrice
X_full.drop(['SalePrice'], axis=1, inplace=True)

X = X_full.select_dtypes(exclude = ['object'])
X_test = X_test_full.select_dtypes(exclude=['object'])

X_train, X_valid, y_train, y_valid = train_test_split(X, y, train_size=0.8, test_size=0.2, random_state = 0)

print(X_train.shape)

missing_val_count_by_column = (X_train.isnull().sum())
print(missing_val_count_by_column[missing_val_count_by_column > 0])

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

def model_score(X_train = X_train, X_valid = X_valid, y_train = y_train, y_valid = y_valid):
    model = RandomForestRegressor(n_estimators=100, random_state=0)
    model.fit(X_train, y_train)
    preds = model.predict(X_valid)
    return mean_absolute_error(y_valid, preds)

# Drop columns with missing values
cols_have_null = [col for col in X_train.columns if X_train[col].isnull().any()]

reduced_X_train = X_train.drop(cols_have_null, axis = 1)
reduced_X_valid = X_valid.drop(cols_have_null, axis = 1)
step_2.check()

print("MAE (Drop columns with missing values):")
print(model_score(reduced_X_train, reduced_X_valid, y_train, y_valid))

from sklearn.impute import SimpleImputer
my_imputer = SimpleImputer()
imputed_X_train = pd.DataFrame(my_imputer.fit_transform(X_train))
imputed_X_valid = pd.DataFrame(my_imputer.transform(X_valid))

imputed_X_train.columns = X_train.columns
imputed_X_valid.columns = X_valid.columns

step_3.a.check()
print('MAE (Imputation):')
print(model_score(imputed_X_train, imputed_X_valid, y_train, y_valid))

final_X_train = X_train.drop(cols_have_null, axis = 1)
final_X_valid = X_valid.drop(cols_have_null, axis = 1)

# 앙상블 분석
model_1 = RandomForestRegressor(n_estimators=50, random_state=0)
model_2 = RandomForestRegressor(n_estimators=100, random_state=0)
model_3 = RandomForestRegressor(n_estimators=100, random_state=0) # criterion : Split의 품질을 측정하는 기능(mse : mean squared error, mae : mean absolute error)
model_4 = RandomForestRegressor(n_estimators=100, random_state=0, max_depth=7) # 덴드로그램처럼 K를 정하는 느낌.
model_5 = RandomForestRegressor(n_estimators=200, random_state=0, min_samples_split=20) # 셈플이 나눠지기 위한 최소의 셈플 수

models = [model_1,model_2,model_3,model_4,model_5]

def new_model_score(model, X_train = X_train, X_valid = X_valid, y_train = y_train, y_valid = y_valid):
    model.fit(X_train, y_train)
    preds = model.predict(X_valid)
    return mean_absolute_error(y_valid, preds)

epoch = 0
dict_mae = {}
for i in models:
    epoch += 1
    mae = new_model_score(i, X_train = final_X_train, X_valid = final_X_valid)
    dict_mae[i] = mae

print((i for dict_mae.values in dict_mae))