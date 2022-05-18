from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium. webdriver. common. keys import Keys
import time
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
import random
from time import sleep

'''
You Should download chromedriver.exe
'''

KEYWORD = '#커피'
INSTA_ID = input("__Your Instagram ID__ : ")
INSTA_PASSWORD = input("__Your Instagram Password__ : ")
TIMES = 10 # 반복횟수 

options = Options()
options.add_argument('disable-infobars')
options.add_experimental_option("useAutomationExtension", False)
options.add_experimental_option("excludeSwitches",["enable-automation"])
#options.add_argument('headless')
driver = webdriver.Chrome(chrome_options=options, executable_path='../chromedriver.exe')

url = "https://www.instagram.com"
driver.get(url=url)
sleep(2)

id = driver.find_element(By.NAME, 'username')
id.send_keys(INSTA_ID)
sleep(1.1)

password = driver.find_element(By.NAME, 'password')
password.send_keys(INSTA_PASSWORD)
sleep(1.1)

password.submit()
driver.implicitly_wait(time_to_wait=5)

search_btn = driver.find_element(By.XPATH, '//*[@id="react-root"]/section/nav/div[2]/div/div/div[2]/input')
search_btn.send_keys(KEYWORD)
sleep(3)
target = driver.find_element(By.XPATH, '//*[@id="react-root"]/section/nav/div[2]/div/div/div[2]/div[3]/div/div[2]/div/div[1]/a/div')
target.click()
driver.implicitly_wait(time_to_wait=5)

# 두 번째 그림 클릭
first = driver.find_element(By.XPATH, '//*[@id="react-root"]/section/main/article/div[1]/div/div/div[1]/div[2]/a/div/div[2]')
first.click()

driver.implicitly_wait(time_to_wait=5)
for _ in range(TIMES):
    like_btn = driver.find_element(By.CSS_SELECTOR, 'body > div._2dDPU.QPGbb.CkGkG > div._32yJO > div > article > div > div.HP0qD > div > div > div.eo2As > section.ltpMr.Slqrh > span.fr66n > button')
    like_btn.click()
    driver.implicitly_wait(time_to_wait=10)
    sleep(1.8)
    nxt_btn = driver.find_element(By.XPATH, '/html/body/div[6]/div[1]/div/div/div[2]/button')
    nxt_btn.click()
    driver.implicitly_wait(time_to_wait=10)
    sleep(2.1)

driver.quit()
