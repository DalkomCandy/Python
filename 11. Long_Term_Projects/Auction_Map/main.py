from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium. webdriver. common. keys import Keys
import time
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains

class auction():
    def __init__(self):
        # 모든 하위 객체들은 self.id와 self.pwd를 입력받은 뒤 작동.
        self.id = ''
        self.pwd = ''
        
        # Driver는 ChromeDriver를 사용한다.
        self.driver = self.step1()
        
        # 크롤링의 매끄러운 작동을 위해 페이지 로딩이 완료될 때까지 기다린다.
        self.wait = WebDriverWait(self.driver, 10)
    
    # Selenium 사용을 편하게 할 기본 설정
    def step1(self):
        options = Options()
        options.add_argument('start-maximized')
        options.add_argument('disable-infobars')
        options.add_experimental_option("useAutomationExtension", False)
        options.add_experimental_option("excludeSwitches",["enable-automation"])
        driver = webdriver.Chrome(chrome_options=options, executable_path='./chromedriver.exe')
        
        return driver
    
    # 본격적인 크롤링 코드
    def step2(self):
        driver = self.driver
        driver.get('http://www.speedauction.co.kr/')
        
        # 스피드 옥션의 경우 특이하게 Frame 형태로 웹페이지가 구성되어있다.
        # 따라서 최초 크롤링 당시의 웹페이지를 부모 페이지로 설정하고, 
        # 각각의 장소 정보가 나오는 Frame을 자식 페이지로 설정한 뒤, 하나의 자식 페이지를 모두 크롤링하면 자식 페이지만을 닫고 다시 부모페이지로 돌아온다.
        iframe = driver.find_element(By.NAME, "bottomFrame")
        driver.switch_to.frame(iframe)
        
        #ID
        elem = driver.find_element(By.CLASS_NAME,"login_input")
        elem.clear()
        elem.send_keys(self.id)
        self.wait

        #PW
        elem = driver.find_element(By.CLASS_NAME, "login_input_black")
        elem.clear()
        elem.send_keys(self.pwd)
        elem.send_keys(Keys.RETURN)
        self.wait
        
        # 메인 페이지에서 경매검색에 hover
        target = driver.find_element(By.XPATH, '''/html/body/table/tbody/
                                     tr[2]/td/table/tbody/tr/td/table/tbody/
                                     tr/td[2]/table/tbody/tr[2]/td/table/tbody/tr[1]/td/table/tbody/tr[1]/td[1]''')
        ActionChains(driver).move_to_element(target).perform()
        self.wait

        # 종합검색 클릭
        driver.find_element(By.XPATH, '//*[@id="lyr_1"]/td/table/tbody/tr/td[1]/a').click()
        self.wait
        
        # 아파트 선택
        driver.find_element(By.XPATH, '//*[@id="trYongdo"]/td/table/tbody/tr[3]/td[2]/table/tbody/tr[1]/td[1]/input').click()
        self.wait
        
        #TODO 소재지, 매각기일 선택
        
        # 검색하기 클릭
        driver.find_element(By.XPATH, "/html/body/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr[2]/td/table/tbody/tr/td[3]/table/tbody/tr[2]/td/table/tbody/tr[3]/td/table/tbody/tr[2]/td/table/tbody/tr[3]/td/img").click()
        self.wait
        
    def crawling(self):
        driver = self.driver
        li = []
        while True:
            a = 1
            for i in range(50):
                main_window_handle = None
                while not main_window_handle:
                    main_window_handle = driver.current_window_handle
                    print(main_window_handle)
                driver.find_element(By.XPATH, f'/html/body/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr[2]/td/table/tbody/tr/td[3]/table/tbody/tr[1]/td/table/tbody/tr[12]/td/table/tbody/tr[{i+3}]/td[3]').click()
                self.wait
                signin_window_handle = None
                while not signin_window_handle:
                    for handle in driver.window_handles:
                        if handle != main_window_handle:
                            signin_window_handle = handle
                            print(signin_window_handle)
                            break
                driver.switch_to.window(signin_window_handle)
                location = driver.find_element(By.XPATH, '//*[@id="printArea"]/tbody/tr/td/table/tbody/tr[8]/td/table/tbody/tr[1]/td[2]/table/tbody/tr/td/font/b')
                li.append(location)
                print(location)
                driver.switch_to.window(main_window_handle)
            try:
                driver.find_element(By.XPATH, f'/html/body/table/tbody/tr[2]/td/table/tbody/tr/td/table/tbody/tr[2]/td/table/tbody/tr/td[3]/table/tbody/tr[1]/td/table/tbody/tr[15]/td/a[{a}]')
                
            except:
                return False
    
    def run(self):
        self.step2()
        self.crawling()
            
run = auction()
run.run()