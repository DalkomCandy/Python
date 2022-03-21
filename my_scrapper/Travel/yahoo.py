import requests
from bs4 import BeautifulSoup as bs
from selenium import webdriver as wd
import time
import re
import pymysql
from tqdm import tqdm

#DB연결
db = pymysql.connect(host='database-1.c6mk0lt68gxl.ap-northeast-2.rds.amazonaws.com', port=3306, user='admin',
                     passwd='hanium123', db='TRAVEL', charset='utf8')
cursor = db.cursor()

#rakuten 페이지 접근
res = requests.get('https://sakurajapan.co.kr/category?shop_id=rakuten')
soup = bs(res.content, 'html.parser')
categories = soup.select('div#main_navi div a')

#개행, tap제거
def no_space(text):
    text1 = re.sub('&nbsp; | &nbsp;| \n|\t|\r', '', text)
    text2 = re.sub('\n\n', '', text1)
    return text2

#get category
def get_category(category_link, category_name):
    res = requests.get(category_link)
    soup = bs(res.content, 'html.parser')
    sub_categories = soup.select('div#main_navi div a')
    for sub_category in sub_categories:
        page = 'https://sakurajapan.co.kr'+sub_category['href']
        get_items(page, category_name, sub_category.get_text())

#DB저장
def save_toDB(item_info):
  try:
    sql = """INSERT INTO test (main_category, sub_category, title, price) VALUES('""" + str(item_info['category_name']) + """',
    '""" + str(item_info['sub_category_name']) + """', 
    '""" + str(item_info['name']) + """', 
    '""" + item_info['price'] + """')"""
    cursor.execute(sql)
  except:
    pass

#상품정보 get
def get_items(page, category_name, sub_category_name):
    chromeDriver = r"C:\Users\Administrator\Desktop\Coding\Python\Scrap\여행지 상품 크롤링\chromedriver.exe"
    options = wd.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    driver = wd.Chrome(chromeDriver, options=options)
    driver.get(page)
    time.sleep(2)

    # for index, item in enumerate(driver.find_element_by_css_selector("div.twice ul")):
    name_css = driver.find_elements_by_css_selector("li.sana_txt a span")
    price_css = driver.find_elements_by_css_selector("li.sana_price")
    img_css = driver.find_elements_by_css_selector("li.sana_thumb")
    for item in tqdm(range(30)):
        data_dict = dict()
        
        name = name_css[item].text
        price = price_css[item].text.replace(',', '').replace('円', '')
        img = img_css[item].text
        
        data_dict['category_name'] = no_space(category_name)
        data_dict['sub_category_name'] = no_space(sub_category_name)

        data_dict['price'] = no_space(price).split(' ')[0]
        data_dict['name'] = name.replace("'",'')
        data_dict['img'] = img

        # print(data_dict)
        save_toDB(data_dict)

#모든 카테고리 탐색

for i in range(100):
    try:
        get_category("https://sakurajapan.co.kr" + categories[i]['href'], categories[i].get_text())
        print("{i}번째 Complete".format(i=i))
        db.commit()
    except:
        pass
        print("{i}번째 Failed".format(i=i))


#DB commit 및 DB연결 종료
db.close()