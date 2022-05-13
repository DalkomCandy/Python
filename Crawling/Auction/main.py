from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium. webdriver. common. keys import Keys
import time
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
import pandas as pd
import numpy as np

options = Options()
options.add_argument('disable-infobars')
options.add_experimental_option("useAutomationExtension", False)
options.add_experimental_option("excludeSwitches",["enable-automation"])
#options.add_argument('headless')
driver = webdriver.Chrome(chrome_options=options, executable_path='../chromedriver.exe')

id = "gyumin1009"
pwd = "qkrrbals!1"

wait = WebDriverWait(driver, 10)

driver.get('http://www.speedauction.co.kr/')

iframe = driver.find_element(By.NAME, "bottomFrame")
driver.switch_to.frame(iframe)

#ID
elem = driver.find_element(By.CLASS_NAME,"login_input")
elem.clear()
elem.send_keys(id)
wait

#PW
elem = driver.find_element(By.CLASS_NAME, "login_input_black")
elem.clear()
elem.send_keys(pwd)
elem.send_keys(Keys.RETURN)
wait
    
# 메인 페이지에서 경매검색에 hover
target = driver.find_element(By.XPATH, '/html/body/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr/td[2]/table/tbody/tr[2]/td/table/tbody/tr[1]/td/table/tbody/tr[1]/td[1]')
ActionChains(driver).move_to_element(target).perform()
wait

# 종합검색 클릭
driver.find_element(By.XPATH, '//*[@id="lyr_1"]/td/table/tbody/tr/td[1]/a').click()
wait

# 소재지

# 대분류
select_1 = Select(driver.find_element(By.NAME, 'region_code1'))
select_1.select_by_visible_text('서울')
time.sleep(1)

# 중분류
select_2 = Select(driver.find_element(By.NAME, 'region_code2'))
select_2.select_by_visible_text('강남구')
time.sleep(1)

# 소분류
select_3 = Select(driver.find_element(By.NAME, 'region_code3'))
select_3.select_by_visible_text('대치동')

# 매각기일
start_date = driver.find_element(By.NAME, "sell_yyyymmdd_ss")
start_date.clear()
start_date.send_keys('20200101')
wait

end_date = driver.find_element(By.NAME, "sell_yyyymmdd_ee")
end_date.clear()
end_date.send_keys('20220501')
wait

# 아파트 선택
driver.find_element(By.XPATH, '//*[@id="trYongdo"]/td/table/tbody/tr[3]/td[2]/table/tbody/tr[1]/td[1]/input').click()

# #TODO 소재지, 매각기일 선택

# 검색하기 클릭
driver.find_element(By.XPATH, "/html/body/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr[2]/td/table/tbody/tr/td[3]/table/tbody/tr[2]/td/table/tbody/tr[3]/td/table/tbody/tr[2]/td/table/tbody/tr[3]/td/img").click()
wait

df = pd.DataFrame(columns=['법원명', '사건번호', '소재지', '용도', '감정가', '최저가', '매각기일', '결과유출수', '조회수'])

table = driver.find_element(By.XPATH, '/html/body/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr[2]/td/table/tbody/tr/td[3]/table/tbody/tr[1]/td/table/tbody/tr[12]/td/table')

# tbody
tbody = table.find_element(By.TAG_NAME, "tbody")

# tbody > tr > td
for tr in tbody.find_elements(By.TAG_NAME, "tr"):
    for td in tr.find_elements(By.TAG_NAME,"td"):
        print(td.get_attribute("innerText"))
        
        

# def crawling(self):
#     driver = self.driver
#     li = []
#     while True:
#         a = 1
#         for i in range(50):
#             main_window_handle = None
#             while not main_window_handle:
#                 main_window_handle = driver.current_window_handle
#                 print(main_window_handle)
#             driver.find_element(By.XPATH, f'/html/body/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr[2]/td/table/tbody/tr/td[3]/table/tbody/tr[1]/td/table/tbody/tr[12]/td/table/tbody/tr[{i+3}]/td[3]').click()
#             self.wait
#             signin_window_handle = None
#             while not signin_window_handle:
#                 for handle in driver.window_handles:
#                     if handle != main_window_handle:
#                         signin_window_handle = handle
#                         print(signin_window_handle)
#                         break
#             driver.switch_to.window(signin_window_handle)
#             location = driver.find_element(By.XPATH, '//*[@id="printArea"]/tbody/tr/td/table/tbody/tr[8]/td/table/tbody/tr[1]/td[2]/table/tbody/tr/td/font/b')
#             li.append(location)
#             print(location)
#             driver.switch_to.window(main_window_handle)
#         try:
#             driver.find_element(By.XPATH, f'/html/body/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr[2]/td/table/tbody/tr/td[3]/table/tbody/tr[1]/td/table/tbody/tr[15]/td/a[{a}]')
            
#         except:
#             return False