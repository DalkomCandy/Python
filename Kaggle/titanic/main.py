import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

from sklearn.ensemble import RandomForestClassifier

def generate_data(csvfile):
    LOCATE = f'./{csvfile}'
    train_df = pd.read_csv(LOCATE)

    X_train, X_test = train_test_split(train_df, test_size = 0.2, random_state = 1)

    y_train = X_train[['PassengerId', 'Survived']]
    X_train = X_train.drop(columns='Survived')

    y_test = X_test[['PassengerId', 'Survived']]
    X_test = X_test.drop(columns='Survived')
    
    return X_train, X_test, y_train, y_test

csvfile = "train.csv"
X_train, X_test, y_train, y_test = generate_data(csvfile)

def train_set():
    y = y_train['Survived']
    features = ["Sex"]
    X = pd.get_dummies(X_train[features])
    test = pd.get_dummies(X_test[features])

    model = RandomForestClassifier(n_estimators = 200, max_depth = 7, random_state = 2)
    model.fit(X,y)
    predictions = model.predict(test)

    print(model.score(X,y))
    
train_set()