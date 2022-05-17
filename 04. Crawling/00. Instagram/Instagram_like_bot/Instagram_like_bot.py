from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from time import sleep

'''
You Should download chromedriver.exe
'''

def set_chrome_driver():
    chrome_options = webdriver.ChromeOptions()
    driver = webdriver.Chrome()
    return driver

insta_id = input("__Your Instagram ID__ : ")
insta_password = input("__Your Instagram Password__ : ")
keyword = input("Keyword : ")
print("If Time exceeds maximum page that instagram have, It will not work")
Times = int(input("Repeating Time : "))

url = "https://www.instagram.com"
driver = set_chrome_driver()
driver.get(url=url)
sleep(2)

id = driver.find_element(By.NAME, 'username')
id.send_keys(insta_id)
sleep(1.1)

password = driver.find_element(By.NAME, 'password')
password.send_keys(insta_password)
sleep(1.1)

password.submit()
driver.implicitly_wait(time_to_wait=5)

keyword = '커피'
search_btn = driver.find_element(By.XPATH, '//*[@id="react-root"]/section/nav/div[2]/div/div/div[2]/input')
search_btn.send_keys(keyword)
sleep(3)
target = driver.find_element(By.XPATH, '//*[@id="react-root"]/section/nav/div[2]/div/div/div[2]/div[3]/div/div[2]/div/div[1]/a/div')
target.click()
driver.implicitly_wait(time_to_wait=5)

# 두 번째 그림 클릭
first = driver.find_element(By.XPATH, '//*[@id="react-root"]/section/main/article/div[1]/div/div/div[1]/div[2]/a/div/div[2]')
first.click()

driver.implicitly_wait(time_to_wait=5)
for _ in range(Times):
    like_btn = driver.find_element(By.CSS_SELECTOR, 'body > div._2dDPU.QPGbb.CkGkG > div._32yJO > div > article > div > div.HP0qD > div > div > div.eo2As > section.ltpMr.Slqrh > span.fr66n > button')
    like_btn.click()
    driver.implicitly_wait(time_to_wait=10)
    sleep(1.8)
    nxt_btn = driver.find_element(By.XPATH, '/html/body/div[6]/div[1]/div/div/div[2]/button')
    nxt_btn.click()
    driver.implicitly_wait(time_to_wait=10)
    sleep(2.1)

driver.quit()
