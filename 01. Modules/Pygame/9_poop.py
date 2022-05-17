import pygame
import random
import time

pygame.init()

screen_width = 480
screen_height = 640 
screen = pygame.display.set_mode((screen_width, screen_height))

pygame.display.set_caption("POOP!")

clock = pygame.time.Clock()

# 배경 만들기
background = pygame.image.load(r"C:\Users\Administrator\Desktop\Coding\Python\Pygame_basic\background.png")

# 캐릭터 만들기
character = pygame.image.load(r"C:\Users\Administrator\Desktop\Coding\Python\Pygame_basic\character.png")
character_size = character.get_rect().size
character_width = character_size[0]
character_height = character_size[1]
character_x_pos = (screen_width / 2) - (character_width / 2)
character_y_pos = screen_height - character_height
character_speed = 0.6

# 적 만들기
enemy = pygame.image.load(r"C:\Users\Administrator\Desktop\Coding\Python\Pygame_basic\ddong.png")
enemy_size = enemy.get_rect().size
enemy_width = enemy_size[0]
enemy_height = enemy_size[1]
enemy_x_pos = random.randint(0, screen_width - enemy_width)
enemy_y_pos = 0
enemy_speed = 7

# 좌표 설정
to_x = 0

#폰트 정의
game_font = pygame.font.Font(None, 40)

#시작 시간
start_ticks = pygame.time.get_ticks()
print(start_ticks)
#########################################################################

#이벤트 루프
running = True #게임이 진행중인가?

while running:
    dt = clock.tick(200) #게임화면의 초당 프레임 수를 설정

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                to_x -= character_speed
            elif event.key == pygame.K_RIGHT:
                to_x += character_speed
            
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                to_x = 0

    # 3. 캐릭터 위치 정의            
    character_x_pos += to_x * dt

    if character_x_pos < 0:
        character_x_pos = 0
    elif character_x_pos > screen_width - character_width:
        character_x_pos = screen_width - character_width

    enemy_y_pos += enemy_speed

    if enemy_y_pos > screen_height:
        enemy_y_pos = 0
        enemy_x_pos = random.randint(0, screen_width - enemy_width)

#   4. 충돌 처리
    character_rect = character.get_rect()
    character_rect.left = character_x_pos
    character_rect.top = character_y_pos

    enemy_rect = enemy.get_rect()
    enemy_rect.left = enemy_x_pos
    enemy_rect.top = enemy_y_pos

    if character_rect.colliderect(enemy_rect):
        print("You Fail")
        running = False

#   5. 화면에 그리기
    screen.blit(background, (0,0))
    screen.blit(character, (character_x_pos, character_y_pos))
    screen.blit(enemy, (enemy_x_pos, enemy_y_pos))
    
    pygame.display.update() #게임화면 다시 그리기

pygame.quit()