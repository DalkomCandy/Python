First_URL = "https://www.google.com/search?q=%s&tbm=nws" %keyword
Second_URL = "https://summariz3.herokuapp.com/"
Third_URL = 'https://www.tyle.io/create'

def news():
    url_data = []
    keyword = input('Keyword : ')
    driver = 
    driver.get(First_URL)

    body = driver.find_element_by_tag_name("body")

    while True:

        # id = '#message' 에 해당하는 값을 가져옴.
        # 유튜브에서는 id = '#message'는 scoll을 맨 끝까지 내렸을 때 나타나는 값임.
        items = driver.find_elements_by_css_selector('#message')

        # scroll을 끝까지 내렸다면 반복문 탈출
        if(len(items)):
            break
        body.send_keys(Keys.PAGE_DOWN)

        # 로딩 시간 기다림
        time.sleep(0.1)

    print('End of main page')
    print('Start stealing URL')

    # 동영상 제목, url을 가지고 있는 class를 가져옴.
    items = driver.find_elements_by_css_selector('#video-title')

    # 한글 깨짐 방지
    for idx in items:
        if(idx.get_attribute('href') is not None):
            text = idx.text
            
            for i in range(len(text)):
                if not ((0 <= ord(text[i]) < 128) or (0xac00 <= ord(text[i]) <= 0xd7af)):
                    text = text.replace(text[i], ' ')
            url_data.append([text, idx.get_attribute('href')])

    driver.close()

    print('Finish previous working')
    print('The data is being written to the csv file.')

    # csv 파일에 저장 [동영상 제목, 동영상 url]
    dataframe = pd.DataFrame(url_data, columns=["title", "url"])
    dataframe.to_csv(
        r'C:\Users\user\Desktop\Machine\Scrap\data\youtube_url.csv', encoding='cp949')

    print('Finish working')

def video_comment_crawling():
    number = 100
    com_data = []
    df = pd.read_csv(
        r'C:\Users\user\Desktop\Machine\Scrap\data\youtube_url.csv', encoding='cp949')

    driver = wd.Chrome(
        r'C:\Users\user\Desktop\Machine\Scrap\crawler\chromedriver.exe')

    storage = 1
    for i in range(len(df.index)):
        title = df['title'][i]
        link = df['url'][i]

        print(f'Start comment crawling : title = {title}')

        driver.get(link)
        time.sleep(2)

        count = 0
        body = driver.find_element_by_tag_name("body")

        print('The scrolling starts moving to the bottom of the comment page.')

        # 댓글 데이터를 가져옴
        last = driver.find_elements_by_css_selector('#content-text')

        while True:
            body.send_keys(Keys.PAGE_DOWN)
            time.sleep(0.4)
            new = driver.find_elements_by_css_selector('#content-text')

            if new == last:
                if count == 10:
                    break
                count += 1

            else:
                count = 0

            last = new

        print('Arrived at the end of the comment page')

        for idx in new:
            # 한글 깨짐 방지
            text = idx.text

            for idx in range(len(text)):
                if not ((0 <= ord(text[idx]) < 128) or (0xac00 <= ord(text[idx]) <= 0xd7af)):
                    text = text.replace(text[idx], ' ')

            com_data.append([title, text])

        if storage == number:
            dataframe = pd.DataFrame(com_data, columns=["title", "content"])
            dataframe.to_csv(r'C:\Users\user\Desktop\Machine\Scrap\data\youtube_comment.csv',
                             mode='a', encoding='cp949')
            com_data = []

        storage += 1

    driver.close()
    
    print('Finish comment crawling')
    print('The data is being written to the csv file.')

    # 댓글 정보를 csv 파일에 저장
    dataframe = pd.DataFrame(com_data, columns=["title", "content"])
    dataframe.to_csv(
        r'C:\Users\user\Desktop\Machine\Scrap\data\youtube_{keyword}.csv', mode='a', encoding='cp949')

    print('Finish working')
