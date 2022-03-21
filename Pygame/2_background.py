import pygame

pygame.init()

screen_width = 480
screen_height = 640
screen = pygame.display.set_mode((screen_width, screen_height))

pygame.display.set_caption("MR.Gyu")

background = pygame.image.load("C:/Users/user/Desktop/VsCode/Pygame_basic/background.png")

#이벤트 루프
running = True #게임이 진행중인가?
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.blit(background, (0,0)) #배경그리기

    pygame.display.update() #게임화면 다시 그리기

pygame.quit()