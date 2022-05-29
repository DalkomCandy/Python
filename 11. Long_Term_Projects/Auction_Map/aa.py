# Imports required for Explicit wait:
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium. webdriver. common. keys import Keys
import time
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains

options = Options()

driver = webdriver.Chrome(chrome_options=options, executable_path='../chromedriver.exe')
driver.get("https://koa.com/campgrounds/austin-east/reserve/step2/?res=kI2O68dJS8X6si949wGzFa68NxYqwyCBul7NzF70cO3rQJLWCoDqp38g67l9SA4BcZqoRAxVFUdFtWBLcjbhl55toq-KCG20N36F-ytOHhr3EKHiJ3_qxDvkUMId1flJiRSh-9X6BDSw3EJ_IVCTNjo0ax44UscxXmfNXAVc8WybZ2xp6tu6H9lvR_igbYAXMf2t2dyN_NM-8JDDtJEe1ofkmQmsl1QJPJsZqfNq-cMnDD2mTdNCJxsfUQwEUYrUY6QEsdj3bbLMWqSTRW5bSzEoVNjVNc_dbH4R11-nnZU0tt1uvWNZZH-3OmrZA7Of9BI2W-GO6r9fk2sa0l1AaiCX7yclG2kXAQgxwTTMOfqI6OgYtKDRvEAgHW71w2LycESK3xVuxTP8C_4OwhFEQBg-GYcq-juoe5qeZNBhiBJsWJxqqxpcPBJ4RgeL7l-emnlG9DHqFk-R3LRDnAi2RBXsr9UWmcVwa3vtlXLLHPcJp07uBDPKz4d-Mm2nKPcjlQVQhaN9ooT5Ccvr5LergYRv4XRMI-u6z0gDYMpZUwLSFvQt3wUEXmQyM0PaazwX1fKjUVF9oKnU8yH5BGpy87uR3_QxfE7UP864PWqdaDg6ni3o7qOLnhZGJ-K6Z0oVu9f48BKRPWWX8-pvHRhe7Is6XnxD1_XVWxjAfXeWAxD8R0URqU6v8JvCgKZXJvwP0vjsXLeXtSsEEd2VFyrGk5UHhHuG1cc7YFGTXJBDMPW7E88LI7pkbsecM-Va5X4IrtoHLppMBOeihBj3Cxz9nHLF5X6fkIMRE7BWKh8TQxRTyNhvdNg-zlMAep2boMwQmBbFpyCH8VN_UxroErjaAixJsEdJyphoYPuIkyHOHfvxREsu5A5IR8aowrQMv1Kc04_bMU-BacYCTCAB8jeRv-I3CtuqetXls4DzC49crLDFyewmwIUdUkkWJS79ml_L3vh82vqjJfHnYs5GHYmqdGLlFPBD19hIjcrAcuOTNXFH5et8ShMfMaa1TRSJCTqeDmonbdH2Uv-_u1RAu_SMHDik2N2NCfEi4E-GvN6vw_kvce_yrLyzeVRCseHo0JmgWxpc4C9nwcLsxa7qN16Q6Gh9aa8RP3Od80tDN8SOOLeVStjcKopJU91ui1rSIdv4pncKWImnwOm7xBG2srVefDb7twP--WYZWeX5PyumDLw9-Nb_QN-LpET3ELxsF0eY6GmFYLFWdt38Aosc4hNFzDFQEkZ5KDnbLdvfMeKqXKDGdV9e5OaaynLyQNmvp4ZlLEVdD3LUraSw_TB-JClxIiw9AIYdhn1vlmilk2CsDIbyfF4n2WsxoVs0k0_RsiAcqaL6jEx31_shLwpGidHXgVUYrNaQ3URMf2Y_KUqB9RPIh0e8_aGoFxbthoxKQmyLMRtLutwvwmqQXx5sCEAfwQ2")

wait = WebDriverWait(driver,30)

# Options available on the page
options = driver.find_elements_by_xpath("//div[@id='reserve-container']//div[@id='site-types']")

# Get details of the 1st option.
viewdetails = options[0].find_element_by_xpath(".//div[contains(@class,'reserve-sitetype-main-row')]//a")
viewdetails.click()

# Get the heading
heading = wait.until(EC.visibility_of_element_located((By.XPATH,"//div[@class='fancybox-stage']//h3")))
print(heading.text)

# Get the details under the heading
details = driver.find_elements_by_xpath("//div[@class='fancybox-stage']//h3//parent::div//following-sibling::div//li")

for detail in details:
    print(detail.get_attribute("innerText"))

# Close the pop-up window
driver.find_element_by_xpath("//div[@class='fancybox-stage']//button[contains(@class,'wts-details-close')]").click()