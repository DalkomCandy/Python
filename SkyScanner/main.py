from tkinter import W
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

import time

URL = 'https://www.skyscanner.co.kr/'

def setting(URL):
    global driver
    
    options = Options()
    options.add_experimental_option("detach", True)
    
    driver = webdriver.Chrome('chromedriver.exe', options=options)
    driver.implicitly_wait(5)
    driver.get(url = URL)
    
    return driver

def login():
    
    from_location = driver.find_element_by_name('fsc-origin-search')
    from_location.send_keys(Keys.BACK_SPACE)
    from_location.send_keys("인천")
    time.sleep(1)
    
    driver.find_element_by_name('fsc-destination-search').send_keys("제주")
    time.sleep(1)
    
    search_btn = driver.find_elements_by_class_name('BpkButtonBase_bpk-button__NTM4Y BpkButtonBase_bpk-button--large__ZWQyM App_submit-button__NGFhZ App_submit-button-oneline__MmU3N')
    search_btn.click()
    time.sleep(1)
    
def scrap():
    for _ in range(10):
        from_time = driver.find_element_by_class_name('BpkText_bpk-text__YWQwM BpkText_bpk-text--base__NDljN')
        to_time = driver.find_element_by_class_name('BpkText_bpk-text__YWQwM BpkText_bpk-text--base__NDljN')
        airline = driver.find_element_by_class_name('BpkText_bpk-text__YWQwM BpkText_bpk-text--xs__MWQxY')
        way = driver.find_element_by_class_name('BpkText_bpk-text__YWQwM BpkText_bpk-text--xs__MWQxY LegInfo_stopsLabelGreen__YWM4M')
        print(from_time, to_time, airline, way)
    
setting(URL)
login()
time.sleep(10)

scrap()
