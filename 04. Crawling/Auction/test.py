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
from selenium.common.exceptions import NoSuchElementException

def NET_CAPEX(CODE):    
    options = Options()
    #options.add_argument('headless')
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
    
    li = driver.find_element(By.XPATH("//div[@class='Va(m)']/span[@class='D(tbr) fi-row Bgc($hoverBgColor):h']"))
    print(li.text)
        
NET_CAPEX('VZ')