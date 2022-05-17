from json import JSONDecodeError
from matplotlib import markers
import pandas as pd
import numpy as np
import requests
import xlsxwriter
import math
from tqdm import tqdm

TOKEN = 'Tpk_059b97af715d417d9f49f50b51b1c448'
stocks = pd.read_csv('portfolio\sp_500_stocks.csv')

def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

columns = ['Ticker', 'Stock Price', 'Market Capitalization', 'Number of Shares to Buy']
final_dataframe = pd.DataFrame(columns = columns)

symbol_groups = list(chunks(stocks['Ticker'], 100))
symbol_strings = []
for i in range(0, len(symbol_groups)):
    symbol_strings.append(','.join(symbol_groups[i]))

for symbol_string in symbol_strings:
    batch_api_call_url = f'https://sandbox.iexapis.com/stable/stock/market/batch/?types=quote&symbols={symbol_string}&token={TOKEN}'
    data = requests.get(batch_api_call_url).json()
    try:
        for symbol in symbol_string.split(','):
            final_dataframe = final_dataframe.append(
                pd.Series([
                    symbol,
                    data[symbol]['quote']['latestPrice'],
                    data[symbol]['quote']['marketCap'],
                    'N/A'
                    ], index = columns),
                    ignore_index=True
        )
    except KeyError:
        pass
        
portfolio_size = int(input('Enter the value of your portfolio : '))