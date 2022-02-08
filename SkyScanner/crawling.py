# Imports
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import pandas as pd
from datetime import timedelta, datetime


def crawling(FROM, TO):
    print(datetime.now().strftime("%Y년 %m월 %d일" + "크롤링을 시작합니다."))
    # Basic Settings
    def sw_option():
        options = Options()
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        return options
        
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=sw_option())
    columns = ['검색 날짜', '출발 날짜', '항공사', '출발시간', '가격']
    df = pd.DataFrame(columns = columns)

    for i in range(1,20):
        driver.implicitly_wait(5)
        
        DATE = datetime.now() + timedelta(days=i)
        DATE = DATE.strftime("%Y%m%d")
        URL = f'https://m-flight.naver.com/flights/domestic/{FROM}-{TO}-{DATE}?adult=1&fareType=YC'
        driver.get(url = URL)

        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, 'domestic_current__nsjAG')))
        time.sleep(1)
        
        driver.find_element(By.CLASS_NAME, 'domestic_current__nsjAG').click()
        time.sleep(1)
        driver.find_element(By.XPATH, '//*[@id="__next"]/div/div[1]/div[5]/div/div[1]/div/div/div/button[1]').click()
        time.sleep(1)
        #-----------------------------------------------------------------------------------------------------
        airline = driver.find_elements(By.CLASS_NAME, 'airline')
        departure = driver.find_elements(By.CLASS_NAME, 'time')
        price = driver.find_elements(By.CLASS_NAME, 'domestic_num__2roTW')

        for a,b,c in zip(airline, departure, price):
            df = df.append({'출발 날짜': DATE, '항공사' : a.text , '출발시간' : b.text, '가격' : c.text} , ignore_index=True)
        
        time.sleep(2)
        
    return df

          