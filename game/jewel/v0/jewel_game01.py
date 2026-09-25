import os
import random
import sys

import pygame



"""
🧠 보석 퍼즐 게임의 4단계 핵심 원리
1. 격자(Grid) 판 만들기:
 - 8x8 크기의 2차원 리스트(배열)를 만들고,
   거기에 1~5번까지 서로 다른 색상의 보석 번호를 무작위로 채워 넣습니다.
2. 마우스 제어:
 - 사용자가 마우스로 보석 하나를 누르고 인접한 칸으로 드래그하면,
   두 보석의 배열 위치를 서로 바꾸어 줍니다.
3. 매칭 검사 (가장 재미있는 부분!):
 - 가로나 세로로 같은 보석이 3개 이상 연속으로 모였는지 체크하여,
   조건이 맞으면 점수를 올리고 해당 보석들을 펑! 터뜨려 화면에서 지웁니다.
4. 중력 법칙:
 - 터져서 빈자리가 생기면 위에 있던 보석들이 아래로 툭 떨어지게 만들고,
   맨 윗줄의 빈칸에는 새로운 보석을 생성해 채워 넣습니다.
"""

"""
💡 코드 구현 핵심 포인트
1. mouse_x // CELL_SIZE 법칙:
 - 마우스 픽셀 좌표(예: X=150, Y=210)를 게임판 격자 인덱스(예: 2행 3열)로 수학적 나눗셈 연산(//)을 통해 완벽하게 치환하여 인식합니다.
2. is_adjacent() 필터링:
 - abs(r1 - r2) + abs(c1 - c2) == 1 공식을 활용하여 대각선 이동이나 멀리 떨어진 보석과의 버그성 교체를 완벽히 방어합니다.
3. grid[r1][c1], grid[r2][c2] = ... 스왑:
 - 변수를 임시로 담아둘 필요 없이 한 줄로 배열 안의 데이터 메모리 주소를 상호 맞바꾸는 파이썬 전용의 편리한 문법을 적용했습니다.
"""

# 불필요한 시스템 경고 및 오디오 관련 경고창 출력 숨기기
sys.stderr = open(os.devnull, 'w')


# 1. 게임 기본 설정
"""
WIDTH, HEIGHT = 500, 500
GRID_SIZE = 8
CELL_SIZE = WIDTH // GRID_SIZE

# 보석 색상 정의 (RGB)
COLORS = [
    (255, 0, 0),    # 🔴 빨강
    (0, 255, 0),    # 🟢 초록
    (0, 0, 255),    # 🔵 파랑
    (255, 255, 0),  # 🟡 노랑
    (255, 0, 255)   # 🟣 보라
]
"""

WIDTH, HEIGHT = 480, 480
GRID_SIZE = 8
CELL_SIZE = WIDTH // GRID_SIZE

COLORS = [
    (235, 77, 75),    # 루비 (레드)
    (106, 176, 76),   # 에메랄드 (그린)
    (29, 209, 161),   # 사파이어 (민트 블루)
    (241, 196, 15),   # 토파즈 (옐로우)
    (155, 89, 182)    # 아메지스트 (퍼플)
]

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
# pygame.display.set_caption("💎 파이썬 보석 퍼즐 게임 💎")
# pygame.display.set_caption("💎 보석 위치 바꾸기 실습 💎")
pygame.display.set_caption("💎 보석 마우스 드래그 게임 💎")

clock = pygame.time.Clock()

# 2. 8x8 게임판에 무작위 보석 배치 (2차원 리스트) (랜덤 색상 채우기)
grid = [[random.choice(COLORS) for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]


# 드래그 상태 저장 변수
drag_start = None  # 드래그를 시작한 (행, 열)

def is_adjacent(pos1, pos2):
    """두 격자 좌표가 상하좌우로 인접해 있는지 검사합니다."""
    r1, c1 = pos1
    r2, c2 = pos2
    return (abs(r1 - r2) == 1 and c1 == c2) or (abs(c1 - c2) == 1 and r1 == r2)

running = True
while running:
    clock.tick(60)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        # 1. 마우스를 누르는 순간 (드래그 시작 지점 기록)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            c = mouse_x // CELL_SIZE
            r = mouse_y // CELL_SIZE
            if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE:
                drag_start = (r, c)
                
        # 2. 마우스를 떼는 순간 (드래그 종료 지점 확인 및 교체)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if drag_start is not None:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                c = mouse_x // CELL_SIZE
                r = mouse_y // CELL_SIZE
                
                if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE:
                    drag_end = (r, c)
                    
                    # 인접한 칸으로 드래그하여 놓았을 때 위치 교체
                    if is_adjacent(drag_start, drag_end):
                        r1, c1 = drag_start
                        r2, c2 = drag_end
                        grid[r1][c1], grid[r2][c2] = grid[r2][c2], grid[r1][c1]
                        print(f"🔄 드래그 교체: ({r1},{c1}) ↔ ({r2},{c2})")
                        
                drag_start = None  # 초기화

    # 화면 그리기
    screen.fill((44, 62, 80))
    
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            color = grid[r][c]
            rect_x = c * CELL_SIZE + 4
            rect_y = r * CELL_SIZE + 4
            rect_w = CELL_SIZE - 8
            rect_h = CELL_SIZE - 8
            
            pygame.draw.rect(screen, color, (rect_x, rect_y, rect_w, rect_h), border_radius=12)
            
            # 드래그 중인 시작 보석 강조 표시
            if drag_start == (r, c):
                pygame.draw.rect(screen, (255, 255, 255), (rect_x - 2, rect_y - 2, rect_w + 4, rect_h + 4), width=3, border_radius=14)
 
    pygame.display.flip()

pygame.quit()
sys.exit()
