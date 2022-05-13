# Imports
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.chrome.options import Options

# ID / Password
id = "gyumin1009"
pwd = "qkrrbals!1"

#Chromedriver을 사용할 경우 상단에 뜨는 'chrome이 자동화된 테스트 소프트웨어에 의해 제어되고 있습니다' 제거
#options = Options()
#options.add_argument('start-maximized')
#options.add_argument('disable-infobars')
#options.add_experimental_option("useAutomationExtension", False)
#options.add_experimental_option("excludeSwitches",["enable-automation"])
#driver = webdriver.Chrome(chrome_options=options, executable_path='C:/dev_python/Webdriver/chromedriver.exe')

# Driver
chromedriver = '../chromedriver.exe'
driver = webdriver.Chrome(chromedriver)
driver.get('http://www.speedauction.co.kr/')
iframe = driver.find_element(By.NAME, "bottomFrame") # id가 mainFrame이라는 요소를 찾아내고 -> iframe임
driver.switch_to.frame(iframe) # 이 iframe이라는 요소로 focus한다.
#ID
elem = driver.find_element(By.CLASS_NAME, "login_input")
elem.clear()
elem.send_keys(id)

#PW
#ID
elem = driver.find_element_by_class_name("login_input_black")
elem.clear()
elem.send_keys(pwd)
elem.send_keys(Keys.RETURN)

# Get parent window
parent_window = driver.current_window_handle

js_exe = driver.find_element(By.CSS_SELECTOR, "body > table > tbody > tr:nth-child(2) > td > table > tbody > tr > td > table > tbody > tr > td:nth-child(2) > table > tbody > tr:nth-child(3) > td > table > tbody > tr:nth-child(3) > td > table > tbody > tr:nth-child(1) > td > table > tbody > tr:nth-child(1) > td:nth-child(1) > table > tbody > tr:nth-child(2) > td > table > tbody > tr:nth-child(2) > td > table > tbody > tr > td:nth-child(7) > table > tbody > tr:nth-child(5) > td > a")
driver.execute_script("javascript:detail_view('E01','2021','63930','1', '33acfafa39eac28d4db8feacf9f0d229');") 
#a_href에 걸린 링크들 list로 모으고 하나씩 불러오면 될듯

# Get list of all windows currently opened (parent + child)
all_windows = driver.window_handles 
WebDriverWait(driver, 10)
# Get child window
child_window = [window for window in all_windows if window != parent_window][0]

print("parent", parent_window)
print("child", child_window)

WebDriverWait(driver, 10)
# Switch to child window
driver.switch_to.window(child_window)
WebDriverWait(driver, 10)
try:
    elem = driver.find_element(By.XPATH, '//*[@id="printArea"]/tbody/tr/td/table/tbody/tr[8]/td/table/tbody/tr[2]/td[2]')
    print(elem.text)
except Exception as e:
    import traceback
    import logging
    logging.error(traceback.format_exc())
    driver.quit()