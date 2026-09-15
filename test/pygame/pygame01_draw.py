""" 
[예제] 여러가지 도형 그리기  (pygame003.py)
"""

import pygame

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
pygame.display.set_caption("도형 그리기")

clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 여러가지 도형 그리기
    screen.fill('white')  # 배경색 (WHITE) 지정

    # ===== 1. 여기에 코드를 작성해주세요 =====
    # 자유롭게 여러가지 도형을 그려보세요.

    # 사각형 그리기
    pygame.draw.rect(screen, 'blue', [50, 50, 100, 100], 0)
    pygame.draw.rect(screen, 'green', [450, 50, 100, 100], 5)

    # 원 그리기
    pygame.draw.circle(screen, 'red', [400, 200], 50, 5)
    pygame.draw.ellipse(screen, 'red', (50, 400, 140, 60))

    # 선
    pygame.draw.line(screen, 'black', [0, 280], [700, 280], 5)
    pygame.draw.line(screen, 'blue', [300, 230], [380, 500], 10)

    # 다각형
    pygame.draw.polygon(screen, 'blue', [[250, 50], [350, 50], [300, 150]], 5)

    pygame.display.update()   # 변경 내용 화면에 적용
    clock.tick(60)
pygame.quit()
