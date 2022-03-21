import time
import pandas as pd
from selenium import webdriver as wd

def sakura():
    
    keyword = input("Type Item : ")
    url = 'https://sakurajapan.co.kr/hey/search?keyword={keyword}&type=buy'.format(keyword = keyword)
    
    driver = wd.Chrome(
        r"C:\Users\Administrator\Desktop\Coding\Python\Scrap\여행지 상품 크롤링\chromedriver.exe")
    driver.get(url)
        
    time.sleep(2)
    
    for i in range(20):
        name = driver.find_elements_by_css_selector('#title_{i}'.format(i=i))
        print(i, name[0].text)
    print('end')
        
        