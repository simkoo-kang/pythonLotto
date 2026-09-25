""" 
[예제] 벽에 닿으면 통통 튕기는 사각형 만들기 (pygame007.py)
"""
import pygame

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("도형 움직이기")

# 사각형의 시작 좌표 (화면 중앙)
rect_x = SCREEN_WIDTH // 2
rect_y = SCREEN_HEIGHT // 2

RECT_SIZE = 50 # 사각형 크기
x_speed = 5    # 사각형의 이동 속도

clock = pygame.time.Clock()
running = True

while running:
    # 이벤트 처리 (키보드, 마우스 입력 확인)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # x 좌표를 계속 변화시켜 사각형을 이동시킵니다.
    rect_x += x_speed

    # ===== 1. 여기에 코드를 작성해주세요 =====
    # [미션 1] 사각형의 '오른쪽 끝'이 화면 오른쪽 벽에 닿거나 넘었을 때
    if rect_x >= SCREEN_WIDTH - RECT_SIZE:
        # 1. 파묻힘 방지를 위해 위치를 오른쪽 벽 경계선으로 확실히 맞춰줍니다.
        rect_x = SCREEN_WIDTH - RECT_SIZE
        # 2. 이동 속도에 -1을 곱해 방향을 왼쪽으로 반전시킵니다.
        x_speed *= -1

    # [미션 2] 사각형의 '왼쪽 끝'이 화면 왼쪽 벽에 닿거나 넘었을 때
    elif rect_x <= 0:
        # 1. 파묻힘 방지를 위해 위치를 왼쪽 벽 경계선으로 확실히 맞춰줍니다.
        rect_x = 0
        # 2. 이동 속도에 -1을 곱해 방향을 다시 오른쪽으로 반전시킵니다.
        x_speed *= -1


    # 화면 그리기
    screen.fill('white') # 이전 프레임의 배경을 지우고
    pygame.draw.rect(screen, 'red', [rect_x, rect_y, RECT_SIZE, RECT_SIZE]) # 새로운 위치에 사각형 그리기
    pygame.display.flip()

    clock.tick(60)

pygame.quit()
