"""
파이게임 기본 구조 (pygame001.py)
"""
import pygame  # 1. 파이게임 모듈 불러오기

pygame.init()  # 2. 파이게임 초기화

screen = pygame.display.set_mode((400, 300))  # 3. 게임 화면 만들기 (가로 400, 세로 300)
pygame.display.set_caption("나의 첫 파이게임")
clock = pygame.time.Clock()  # 클럭 설정 (FPS 조절용)

running = True  # 게임 루프 제어 변수

# 4. 이벤트 루프 실행 (게임이 실행되는 동안 무한 반복)
while running:
    # 4-1. 이벤트 처리 (키보드, 마우스 입력, 창 닫기 등)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # 창 닫기(X) 버튼을 눌렀을 때
            running = False

    # 4-2. 게임 상태 업데이트 (캐릭터 이동, 충돌 체크 등)

    # 4-3. 게임 화면 그리기
    screen.fill("white") # 화면을 하얀색으로 채우기
    pygame.display.update()  # 화면 업데이트 (그린 내용을 화면에 반영)

    clock.tick(60)  # FPS 설정 (초당 60프레임)

pygame.quit()  # 5. 게임 종료
