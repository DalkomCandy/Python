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
from tqdm import tqdm

def sw_option():
    options = Options()
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    # options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return options

    
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=sw_option())
li = []

driver.implicitly_wait(5)

TAG = "제주도"
URL = f'https://www.instagram.com/explore/tags/{TAG}/?hl=ko'
driver.get(url = URL)

time.sleep(1)

driver.find_element(By.XPATH, '//*[@id="loginForm"]/div/div[1]/div/label/input').send_keys('gyumin0815@gmail.com')
time.sleep(1)

driver.find_element(By.XPATH, '//*[@id="loginForm"]/div/div[2]/div/label/input').send_keys('qkrrbals!1')
time.sleep(1)


# driver.find_element(By.CLASS_NAME, '_9AhH0').click()

# for _ in tqdm(range(20)):
#     try:
#         tag = driver.find_elements(By.CLASS_NAME, ' xil3i')
#         li.append(tag)
#         print(tag)
#     except:
#         pass
#     finally:
#         time.sleep(1)
#         driver.find_element(By.CLASS_NAME, 'wpO6b  ').click()
# print(li)        


# #  driver.quit()