""" 
[예제] 화면 정중앙에 고양이 이미지 띄우기 (pygame010.py)
"""
import pygame
pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("이미지 출력하기")

clock = pygame.time.Clock() 

# ===== 1. 여기에 코드를 작성해주세요 =====
#  "cat.png" 파일을 불러와 투명도를 유지하도록 설정한 뒤, imgsurface 변수에 저장하세요.
imgsurface = pygame.image.load("./game/images/jigsaw/[ㄴ일]9151.mkv_002650870.png").convert_alpha()

# 이미지 위치 중앙으로 계산
x = (SCREEN_WIDTH - imgsurface.get_width()) // 2
y = (SCREEN_HEIGHT - imgsurface.get_height()) // 2

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill("skyblue") # 배경 색상 채우기
    # ===== 2. 여기에 코드를 작성해주세요 =====
    # 불러온 고양이 이미지(img)를 계산된 (x, y) 좌표에 그려주세요.
    screen.blit(imgsurface, (x + 300, y - 50))


    pygame.display.update() # 화면 업데이트

    clock.tick(60) 
pygame.quit()