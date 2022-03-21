from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import pandas as pd
from tqdm import tqdm

def sw_option():
    options = Options()
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    # options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return options
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=sw_option())
column = ['code']
df = pd.read_csv('list.csv', names = column)
data = df.code.to_list()

for i in data:
    driver.implicitly_wait(5)
    print(i)

    URL = f'https://finance.yahoo.com/quote/{i}/history?p={i}'
    driver.get(url = URL)
    time.sleep(7)

    driver.find_element(By.XPATH, '//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[1]/div[1]/div[1]/div/div').click()
    time.sleep(1)
    driver.find_element(By.XPATH, '//*[@id="dropdown-menu"]/div/ul[2]/li[3]/button').click()
    time.sleep(1)
    driver.find_element(By.XPATH, '//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[1]/div[1]/button').click()
    time.sleep(1)
    driver.find_element(By.XPATH, '//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[1]/div[2]/span[2]/a').click()
    time.sleep(1)
