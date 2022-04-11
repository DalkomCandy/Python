import crawling
from csv_to_json import csv_to_json
from datetime import datetime as dt

FROM = 'GMP'
TO = 'CJU'
DATE = dt.now().strftime("%Y%m%d")

# 크롤링 실행
Start_Project = crawling.crawling(FROM, TO)

# 날짜.csv로 저장
Start_Project.to_csv(f'csv_data\{DATE}.csv', encoding='utf-8', index=False)

# 전체 data.json 관리
csv_to_json(DATE)

if __name__=="__main__":
    Start_Project
