import os
import random

import pygame

from config.config_manager import ConfigManager

config_manager = ConfigManager(__file__)
json = config_manager.settings

# json.clear()

# 1. 초기 설정
pygame.init()

dino = json['dino']
# dino["SCREEN_WIDTH"] = 1200
# dino["SCREEN_HEIGHT"] = 800
# dino['background'] = "./game/images/ddong/background.jpg"
# dino['mans'] = ["./game/images/ddong/man_img1.png","./game/images/ddong/man_img2.png","./game/images/ddong/man_img3.png"]
# dino['mans'].append('./game/images/ddong/man_img4.png')
# dino['mans'].append('./game/images/ddong/man_img5.png')
# dino['mans'].append('./game/images/ddong/man_img6.png')

# json["dino"] = dino

# SCREEN_WIDTH = 1200
# SCREEN_HEIGHT = 800

screen = pygame.display.set_mode((dino["SCREEN_WIDTH"], dino["SCREEN_HEIGHT"]))
pygame.display.set_caption("떨어지는 운석 피하기 게임")

clock = pygame.time.Clock()

bg_img = pygame.image.load(dino['background']) #"./game/images/ddong/background.jpg")
bg_img = pygame.transform.scale(bg_img, (dino["SCREEN_WIDTH"], dino["SCREEN_HEIGHT"]))

# 캐릭터 애니메이션 리스트 생성
dino_right = []
for i in range(1,6):
    # img = pygame.image.load(f"./game/images/ddong/man_img{i}.png").convert_alpha()
    img = pygame.image.load(dino['mans'][i]).convert_alpha()
    # 이미지 크기를 절반(0.5)으로 부드럽게 줄입니다.
    img = pygame.transform.rotozoom(img, 0, 0.5)
    dino_right.append(img)

# 왼쪽 바향 애니메이션 이미지 생성(오른쪽 이미지를 좌우 반전)
dino_left = [pygame.transform.flip(img, True, False) for img in dino_right]

# 애니메이션 제어 변수
dino_image = dino_right

# 공룡 이미지 위치 설정
dino_rect = dino_right[0].get_rect()
dino_rect.x = (dino["SCREEN_WIDTH"] - dino_rect.width) // 2
dino_rect.y = dino["SCREEN_HEIGHT"] - dino_rect.height
dino_speed = 0

# 운석 이미지 로드
# dino['rock'] = ["./game/images/ddong/watermelon1.png"]
# dino['rock'].append("./game/images/ddong/watermelon2.png")
# dino['rock'].append("./game/images/ddong/watermelon3.png")
# dino['rock'].append("./game/images/ddong/watermelon4.png")
# dino['rock'].append("./game/images/ddong/watermelon5.png")
# rock = pygame.image.load("./game/images/ddong/watermelon1.png").convert_alpha()
rock = pygame.image.load(dino['rock'][0]).convert_alpha()

# 운석 초기 위치 설정
rock_rect = rock.get_rect()
rock_rect.x = random.randint(0, dino["SCREEN_WIDTH"] - rock_rect.width)
rock_rect.y = 0
rock_speed = 10

frame_index = 0  # 실수형 인텍스 (속도 조절용)
animation_speed = 0.4 # 숫자가 작을수록 천천히 움직입니다.
stop = True  # 캐릭터가 멈춰있는 상태를 나타내는 변수 (초기값은 True로 설정)

# config_manager.save()

score = 0
font = pygame.font.SysFont('Sans', 30)

# 4. 게임 루프
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                running = False
            
            if event.key == pygame.K_LEFT:
                stop = False
                dino_image = dino_left
                dino_speed = -10
            
            elif event.key == pygame.K_RIGHT:
                stop = False
                dino_image = dino_right
                dino_speed = 10

        if event.type == pygame.KEYUP:
            if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                stop = True
                dino_speed = 0
                frame_index = 0

    # 캐릭터 이동 및 경계 처리
    dino_rect.x += dino_speed
    if dino_rect.left < 0: dino_rect.left = 0
    if dino_rect.right > dino["SCREEN_WIDTH"]: dino_rect.right = dino["SCREEN_HEIGHT"]
    
    # 애니메이션 프레임 업데이트
    if not stop:
        frame_index += animation_speed
        if frame_index >= len(dino_image):
            frame_index = 0

    # 운석 이동 및 리셋
    rock_rect.y += rock_speed
    if rock_rect.y > dino["SCREEN_HEIGHT"]:
        score += 10
        rock_speed += 0.3
        rock_rect.y = 0
        rock_rect.x = random.randint(0, dino["SCREEN_WIDTH"] - rock_rect.width)

    # 충돌 처리
    if dino_rect.colliderect(rock_rect):
        running = False

    # 그리기
    screen.blit(bg_img, (0, 0))

    # 애니메이션 출력
    screen.blit(dino_image[int(frame_index)], (dino_rect.x, dino_rect.y))

    screen.blit(rock, (rock_rect.x, rock_rect.y))
    score_text = font.render(f"Score : {score}", True, (0, 0, 255))
    screen.blit(score_text, (20, 20))

    pygame.display.update()
    clock.tick(60)

pygame.quit()
