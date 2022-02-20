import pandas as pd
import numpy as np

import json
import ujson
import os
import csv

fname = ['20220208.csv','20220211.csv','20220213.csv','20220215.csv','20220216.csv',
         '20220217.csv','20220218.csv', '20220219.csv', '20220220.csv']

columns = ['Departure_Date', 'Airline', 'Departure_time', 'price']
df = []
for f in fname:
    raw_df = pd.read_csv(f'csv_data/{f}')
    df.append(raw_df)
df = pd.concat(df)
print(df.head())
print(type(df))