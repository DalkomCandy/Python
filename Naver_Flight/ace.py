import csv
import json
import pandas as pd

def csv_to_json(DATE):
    df_csv = pd.read_csv(f'{DATE}.csv', encoding="utf-8")
    df_csv.drop(['Unnamed: 0'], axis = 1, inplace = True)
    print(df_csv.head())
csv_to_json(20220211)