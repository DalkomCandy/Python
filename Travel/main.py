import sys
import sakura

MAX_MENU = 1
SAKURA_CRAWLING = 1



def menu():
    print('Crawling Program >> Please select menu')
    print('=======================================')
    print('1. Sakura Crawling')
    print('=======================================')


if __name__ == "__main__":

    menu()
    try:
        menu_num = int(input('Menu : '))

    except:
        print('Please press valid menu number')
        sys.exit(1)
    if(not(1 <= menu_num <= MAX_MENU)):
        print('Please press valid menu number (1~3)')
        sys.exit(1)

    if(menu_num == SAKURA_CRAWLING):
        sakura.sakura()

'''
    elif(menu_num == YOUTUBE_CRAWLING):
        youtube_crawler.video_url_crawling()          # 유튜브에 있는 동영상 제목, url 전부 가져옴
        youtube_crawler.video_comment_crawling()     # 유튜브 각 동영상에 있는 댓글 전부 가져옴

    elif(menu_num == TWITTER_CRAWLING):
        twitter_crawler.crawling()
'''
