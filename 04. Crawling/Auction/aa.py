import yfinance as yf
yf.pdr_override()
import matplotlib.pyplot as plt

import pandas as pd
import numpy as np
from pandas_datareader import data as pdr
import statsmodels.api as sm

import warnings
warnings.filterwarnings('ignore')

import math

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def CAPM(CODE):
    if CODE.endswith('.KS'): # 한국 기업이면 코스피 사용
        KOSPI_CODE = '^KS11'
        RF = 3.119
        ERP = 5.36
    else:
        KOSPI_CODE = '^IXIC' # 다른 나라 기업이면 일단은 미국 기업으로 산정
        RF = 2.8741
        ERP = 4.24

    FIRST = '2017-05-08'
    TODAY = '2022-05-06' #dt.strftime(dt.today(),"%Y-%m-%d")
    INTERVAL ='1wk'

    price = yf.download(CODE, start = FIRST, end = TODAY, interval=INTERVAL, progress=False)
    kospi = yf.download(KOSPI_CODE, start = FIRST, end = TODAY, interval=INTERVAL, progress=False)

    df_stock = pd.concat([price['Close'], round(price['Close'].pct_change()*100,2)], axis=1)
    df_kospi = pd.concat([kospi['Close'], round(kospi['Close'].pct_change()*100,2)], axis=1)

    df_stock.columns = ['stock_price', 'stock_pct']
    df_stock = df_stock.dropna()

    df_kospi.columns = ['kospi_price', 'kospi_pct']
    df_kospi = df_kospi.dropna()

    df = pd.concat([df_kospi, df_stock], axis=1, join='inner',)

    y = df['stock_pct'].values
    X = df['kospi_pct'].values

    X = X.reshape(-1,1)
    y = y.reshape(-1,1)

    results = sm.OLS(y, sm.add_constant(X)).fit()
    BETA = results.params[1]

    print('Rf :',RF)
    print('ERP :', ERP)
    print("Beta :", BETA)

    rm = RF + BETA*ERP
    print('E(r) :',rm)
    print('')
    
def ROE(CODE):
    df_stock = yf.Ticker(CODE)
    ROE = df_stock.financials.loc['Net Income'] / df_stock.balancesheet.loc['Total Stockholder Equity'] 
    return ROE.drop('2018-12-31').values

def NET_INCOME(CODE):
    df_stock = yf.Ticker(CODE)
    df0 = df_stock.financials.loc['Net Income'].drop('2018-12-31').values
    df1 = list(math.floor(i/1000) for i in df0)
    return df1

def CHANGE_IN_WORKING_CAPITAL(CODE):
    df_stock = yf.Ticker(CODE)
    df1 = df_stock.balancesheet.loc['Total Current Assets'] - df_stock.balancesheet.loc['Total Current Liabilities']
    df2 = []
    for i in range(len(df1.values)-1):
        df2.append(math.floor((df1.values[i]-df1.values[i+1])/1000))
    return df2

def CHANGE_IN_DEBT(CODE):
    options = Options()
    options.add_argument('headless')
    driver = webdriver.Chrome(chrome_options=options, executable_path='./chromedriver.exe')

    wait = WebDriverWait(driver, 10)
    driver.get(f'https://finance.yahoo.com/quote/{CODE}/cash-flow?p={CODE}')
    wait

    li = []
    for i in range(3,7):
        a = driver.find_element(By.XPATH, f'//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[6]/div[1]/div[{i}]/span')
        b = driver.find_element(By.XPATH, f'//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[7]/div[1]/div[{i}]/span')

        a = a.text.replace(',','')
        b = b.text.replace(',','')

        li.append(int(a) + int(b))
    driver.quit()
    return li[:3]

def NET_CAPEX(CODE):    
    options = Options()
    options.add_argument('headless')
    driver = webdriver.Chrome(chrome_options=options, executable_path='./chromedriver.exe')

    wait = WebDriverWait(driver, 20)
    driver.get(f'https://finance.yahoo.com/quote/{CODE}/balance-sheet?p={CODE}')
    wait
    
    click = driver.find_element(By.XPATH,'//*[@id="Col1-1-Financials-Proxy"]/section/div[2]/button/div/span')
    click = click.text
    wait
    
    if click == 'Expand All':
        driver.find_element(By.XPATH,'//*[@id="Col1-1-Financials-Proxy"]/section/div[2]/button/div/span').click()

    wait
    li = []
    for i in range(2,6):
        a = driver.find_element(By.XPATH, f'//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[1]/div[2]/div[2]/div[2]/div[1]/div[2]/div[2]/div[1]/div[{i}]/span')
        a = a.text.replace(',','')

        li.append(int(a))
    driver.quit()
    
    df_stock = yf.Ticker(CODE)
    
    li2 = []
    for i in range(len(li)-1):
        li2.append(li[i+1] - li[i])
        
    a = (df_stock.balancesheet.loc['Total Assets'] - df_stock.balancesheet.loc['Total Current Assets'])/1000
    b = li2
    
    a1 = []
    for i in range(len(a)-1):
        a1.append(a[i] - a[i+1])

    li5 = []
    for i,j in zip(a1,b):
        li5.append(math.floor(i+j))
        
    return li5

def HIGH_GROWTH_MODEL(CODE):
    df = pd.DataFrame(columns=['Net CAPEX','Change In Working Capital', 'change in debt', 'Net Income', 'b', 'ROE', 'Equity RIR'],
                     index = ['2021','2020','2019'])
    # Net CAPEX
    #print('Net Capex')
    df['Net CAPEX'] = NET_CAPEX(CODE)
    
    # Change In Working Capital
    #print("Change in working Capital")
    df['Change In Working Capital'] = CHANGE_IN_WORKING_CAPITAL(CODE)
    
    # Change In Debt
    #print("Change in Debt")
    df['change in debt'] = CHANGE_IN_DEBT(CODE)
    
    # Net Inocme
    #print("Net Income")
    df['Net Income'] = NET_INCOME(CODE)
    
    # b
    #print("b")
    df['b'] = (df['Net CAPEX'] + df['Change In Working Capital'] - df['change in debt'])/df['Net Income']
    
    # ROE
    #print("ROE")
    df['ROE'] = ROE(CODE)

    return df

df_stock = yf.Ticker('VZ')
print(df_stock.cashflow)

