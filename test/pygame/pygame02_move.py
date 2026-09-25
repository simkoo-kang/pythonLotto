""" 
[예제] 오른쪽으로 끝없이 이동하는 도형 (pygame006.py)
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
x_speed = 5 # 사각형의 이동 속도

clock = pygame.time.Clock()
running = True

while running:
    # 이벤트 처리 (키보드, 마우스 입력 확인)
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and (event.key == pygame.K_ESCAPE or event.key == pygame.K_q)):
            running = False
        
#    ===== 1. 여기에 코드를 작성해주세요 =====
    # [미션 1] 도형을 오른쪽으로 계속 이동시키기
    # 힌트: 사각형의 현재 x 좌표에 이동 속도를 계속 더해주세요.
    rect_x += 10

    # [미션 2] 화면 오른쪽 밖으로 나가면, 왼쪽 밖에서 다시 나타나게 하기
    # 힌트: 사각형의 x 좌표가 화면 전체 너비보다 커졌다면?
    if rect_x > SCREEN_WIDTH - RECT_SIZE:

        # 사각형의 x 좌표를 화면 왼쪽 바깥(사각형 크기만큼 마이너스 위치)으로 옮겨주세요.
        rect_x = 0

    # 화면 그리기
    screen.fill('white') # 이전 프레임의 배경을 지우고
    pygame.draw.rect(screen, 'red', [rect_x, rect_y, RECT_SIZE, RECT_SIZE]) # 새로운 위치에 사각형 그리기
    pygame.display.flip()

    clock.tick(5)

pygame.quit()
