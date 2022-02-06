# Imports
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd

# Basic Settings
URL = 'https://www.skyscanner.co.kr/'
FROM = '서울'
TO = '제주'
DATE = None

def ChromeOptions():
    global driver
    options = Options()
    options.add_experimental_option("detach", True)

    driver = webdriver.Chrome('chromedriver.exe', options=options)
    driver.implicitly_wait(5)
    driver.get(url = URL)
    
ChromeOptions()
    
from_location = driver.find_element_by_name('fsc-origin-search')
from_location.send_keys(Keys.BACK_SPACE)
time.sleep(0.5)
from_location.send_keys(FROM)
time.sleep(1)

driver.find_element_by_name('fsc-destination-search').send_keys(TO)
time.sleep(1)

search_btn = driver.find_elements_by_xpath('//*[@id="flights-search-controls-root"]/div/div/form/div[3]/button')

driver.execute_script("arguments[0].click();", search_btn)
time.sleep(1)

columns = ['from_time', 'to_time', 'airline', 'way']
df = pd.DataFrame(columns = columns)

time.sleep(10)
#----------------------------------------------------------------------------------------
driver.find_element_by_xpath('//*[@id="app-root"]/div[1]/div/div[2]/div[2]/div[1]/button').click()
time.sleep(2)

def scroll_down(whileSeconds):
    import datetime
    start = datetime.datetime.now()
    end = start + datetime.timedelta(seconds=whileSeconds)
    while True:
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        time.sleep(1)
        if datetime.datetime.now() > end:
            break
scroll_down()

from_time = driver.find_elements_by_class_name('BpkText_bpk-text__YWQwM BpkText_bpk-text--base__NDljN')
to_time = driver.find_elements_by_class_name('BpkText_bpk-text__YWQwM BpkText_bpk-text--base__NDljN')
airline = driver.find_elements_by_class_name('BpkText_bpk-text__YWQwM BpkText_bpk-text--xs__MWQxY')
way = driver.find_elements_by_class_name('BpkText_bpk-text__YWQwM BpkText_bpk-text--xs__MWQxY LegInfo_stopsLabelGreen__YWM4M')

for a,b,c,d in zip(from_time, to_time, airline, way):
    df = df.append(a,b,c,d)

print(df.head())
    
