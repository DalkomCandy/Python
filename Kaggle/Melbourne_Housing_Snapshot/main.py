import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split

# Use informations to predict home price

raw_data = pd.read_csv(f'Melbourne_Housing_Snapshot\melb_data.csv')

X = raw_data.copy().drop(['Price'], axis=1)
X = X.select_dtypes(exclude = 'object')
y = raw_data['Price']

X_train, X_valid, y_train, y_valid = train_test_split(X,y, train_size=0.8, test_size=0.2, random_state=0)

# score dataset
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

def score_dataset(X_train, X_valid, y_train, y_valid):
    model = RandomForestRegressor(n_estimators=10, random_state=0)
    model.fit(X_train, y_train)
    preds = model.predict(X_valid)
    return mean_absolute_error(y_valid, preds)

# STEP 1

cols_have_null = [col for col in X_train.columns if X_train[col].isnull().any()]
# print(cols_have_null) ['Car', 'BuildingArea', 'YearBuilt']

# 결측치 있는 행 그냥 없애버리기
reduced_X_train = X_train.drop(cols_have_null, axis = 1)
reduced_X_valid = X_valid.drop(cols_have_null, axis = 1)

# Define Function to Measure Quality of Each Approach
print("MAE from Approach 1 (Drop column with missing values)")
print(score_dataset(reduced_X_train, reduced_X_valid, y_train, y_valid))

# STEP 2

# simpleImputer
from sklearn.impute import SimpleImputer
my_imputer = SimpleImputer()
imputed_X_train = pd.DataFrame(my_imputer.fit_transform(X_train))
imputed_X_valid = pd.DataFrame(my_imputer.transform(X_valid))

imputed_X_train.columns = X_train.columns
imputed_X_valid.columns = X_valid.columns

print("MAE from Approach 2 (Using simpleImputer)")
print(score_dataset(imputed_X_train, imputed_X_valid, y_train, y_valid)) # MAE가 simpleimputer를 사용했을 때 더 좋다는 것을 발견

# STEP 3

X_train_plus = X_train.copy()
X_valid_plus = X_valid.copy()

for col in cols_have_null:
    X_train_plus[col + '_was missing'] = X_train_plus[col].isnull()
    X_valid_plus[col + '_was missing'] = X_valid_plus[col].isnull()
    
# Imputation
my_imputer = SimpleImputer()
imputed_X_train_plus = pd.DataFrame(my_imputer.fit_transform(X_train_plus))
imputed_X_valid_plus = pd.DataFrame(my_imputer.transform(X_valid_plus))

imputed_X_train_plus.columns = X_train_plus.columns
imputed_X_valid_plus.columns = X_valid_plus.columns

print("MAE from Mixture of Approach 1 and Approach 2")
print(score_dataset(imputed_X_train_plus, imputed_X_valid_plus, y_train, y_valid))

print(X_train.shape)

missing_val_count_by_column = (X_train.isnull().sum())
print(missing_val_count_by_column[missing_val_count_by_column > 0])
print(reduced_X_train.shape)
print(imputed_X_train.shape)
print(imputed_X_train_plus.shape)