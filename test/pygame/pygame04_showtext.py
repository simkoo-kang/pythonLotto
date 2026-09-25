""" 
[예제] 타이머 만들기 (pygame008.py)
"""
import pygame
pygame.init()

SCREEN_WIDTH = 400
SCREEN_HEIGHT = 300
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("타이머 만들기")

# ===== 1. 폰트(글꼴) 설정하기 =====
# 파이게임의 기본 폰트를 사용하고, 크기가 50인 폰트 객체를 만들어 font 변수에 저장하세요.
font = pygame.font.SysFont("malgungothic", 24, bold=True)


# 시작 시간 기록하기 (게임이 막 시작된 순간의 시간을 저장해 둡니다)
start_ticks = pygame.time.get_ticks() 

clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill('black')

    # 흘러간 시간 계산하기
    # (현재 시간 - 시작 시간) / 1000을 해서 '초' 단위로 만듭니다.
    elapsed_time = (pygame.time.get_ticks() - start_ticks) / 1000

    # 소수점 아래는 버리고 정수(1, 2, 3...)로 만든 뒤, 문자로 변환합니다.
    timer_str = str(int(elapsed_time))


    # ===== 2. 글자를 이미지로 만들기 (렌더링) =====
    # 위에서 만든 문자열(timer_str)을 초록색('green') 글자 이미지로 만들어 text 변수에 저장하세요.
    text_surface = font.render("글자를 이미지로 만들기 (렌더링)", True, (50, 255, 255))


    # 화면 중앙에 출력
    screen.blit(text_surface, ((SCREEN_WIDTH-text_surface.get_width())/2, (SCREEN_HEIGHT-text_surface.get_height())/2))

    pygame.display.update()
    clock.tick(60)

pygame.quit()
