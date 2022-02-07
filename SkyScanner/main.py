# Imports
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import pandas as pd
import datetime
# Basic Settings
options = Options()
options.add_experimental_option("detach", True)

driver = webdriver.Chrome('chromedriver.exe', options=options)
driver.implicitly_wait(5)

for i in range(1,20):
    time.sleep(3.8)
    FROM = 'GMP'
    TO = 'CJU'
    today = datetime.datetime.now() 
    DATE = str(today.year) + str(today.month).zfill(2) + str(today.day + i).zfill(2)
    URL = f'https://m-flight.naver.com/flights/domestic/{FROM}-{TO}-{DATE}?adult=1&fareType=YC'

    driver.get(url = URL)

    time.sleep(20)
    driver.find_element(By.CLASS_NAME, 'domestic_current__nsjAG').click()
    time.sleep(1)
    driver.find_element(By.XPATH, '//*[@id="__next"]/div/div[1]/div[5]/div/div[1]/div/div/div/button[1]').click()
    time.sleep(1)
    #-----------------------------------------------------------------------------------------------------
    columns = ['검색 날짜', '출발 날짜', '항공사', '출발시간', '가격']
    df = pd.DataFrame(columns = columns)
    airline = driver.find_elements(By.CLASS_NAME, 'airline')
    departure = driver.find_elements(By.CLASS_NAME, 'time')
    price = driver.find_elements(By.CLASS_NAME, 'domestic_num__2roTW')

    for a,b,c in zip(airline, departure, price):
        df = df.append({'검색 날짜' : today.strftime('%Y%m%d'),'출발 날짜': DATE, '항공사' : a.text , '출발시간' : b.text, '가격' : c.text} , ignore_index=True)
    
    time.sleep(2)
    driver.quit()

print(len(df))
print(df)
        