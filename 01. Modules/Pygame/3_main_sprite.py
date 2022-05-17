import pygame

pygame.init() #초기화

screen_width = 480 # 가로
screen_height = 640 # 세로
screen = pygame.display.set_mode((screen_width, screen_height))

pygame.display.set_caption("MR.Gyu")

background = pygame.image.load("C:/Users/user/Desktop/VsCode/Pygame_basic/background.png")

#캐릭터 불러오기
character = pygame.image.load("C:/Users/user/Desktop/VsCode/Pygame_basic/character.png")
character_size = character.get_rect().size #이미지의 크기를 구해옴
character_width = character_size[0] #캐릭터 가로 크기
character_height = character_size[1] # 캐릭터 세로 크기
character_x_pos = (screen_width /2) - (character_width/2) #화면 가로의 절반 크기에 해당하는 곳에 위치
character_y_pos = screen_height - character_height #화면 세로 크기 가장 아래에 위치



#이벤트 루프
running = True #게임이 진행중인가?
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.blit(background, (0,0)) #배경그리기

    screen.blit(character, (character_x_pos, character_y_pos))

    pygame.display.update() #게임화면 다시 그리기

pygame.quit()