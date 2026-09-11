import sys
import os
import random
import pygame


"""
💡 깔끔해진 코드 구조 요약
1. get_match_cells(g):
 - 순수하게 매칭된 좌표만 추려내는 수학적 연산기입니다.
   3개가 연속되든, 4개 혹은 5개가 연속되든 한 줄로 묶인 좌표들이 중복 없이 set에 깔끔하게 누적됩니다.
2. find_and_destroy_pure_matches():
 - 위 함수가 넘겨준 확실한 타격 리스트 좌표만 순회하며 EMPTY_COLOR로 변환해 줍니다.
   역할 분담이 확실하게 분리되어 가독성이 훨씬 좋아졌습니다!
"""


sys.stderr = open(os.devnull, 'w')

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
EMPTY_COLOR = (30, 30, 30)  # 터진 자리 색상

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("📐 순수 일렬 매칭(3,4,5개) 제어 실습 📐")
clock = pygame.time.Clock()

def generate_valid_grid():
    while True:
        new_grid = [[random.choice(COLORS) for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        if not get_match_cells(new_grid):
            return new_grid

# 💡 [핵심 수정] 가로/세로 3, 4, 5개 이상 일렬 매칭된 모든 좌표를 구해서 셋(Set)으로 반환하는 독립 함수입니다.
def get_match_cells(g):
    matched_cells = set()

    # 1. 가로 방향 연속 매칭 검사 (3개, 4개, 5개 이상 모두 커버)
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE - 2):
            # 세 칸의 색상이 같고, 빈칸이 아니라면 매칭 영역에 추가
            if g[r][c] == g[r][c+1] == g[r][c+2] and g[r][c] != EMPTY_COLOR:
                matched_cells.update([(r, c), (r, c+1), (r, c+2)])

    # 2. 세로 방향 연속 매칭 검사 (3개, 4개, 5개 이상 모두 커버)
    for r in range(GRID_SIZE - 2):
        for c in range(GRID_SIZE):
            if g[r][c] == g[r+1][c] == g[r+2][c] and g[r][c] != EMPTY_COLOR:
                matched_cells.update([(r, c), (r+1, c), (r+2, c)])

    return matched_cells

grid = generate_valid_grid()
drag_start = None

def is_adjacent(pos1, pos2):
    r1, c1 = pos1
    r2, c2 = pos2
    return (abs(r1 - r2) == 1 and c1 == c2) or (abs(c1 - c2) == 1 and r1 == r2)

# 💡 [핵심 수정] 위에서 구한 매칭 영역 함수를 호출하여 실제 보석을 지우는 실행 함수입니다.
def find_and_destroy_pure_matches():
    # 1. 현재 판에서 일렬 매칭된 좌표들을 모조리 긁어옵니다.
    cells_to_destroy = get_match_cells(grid)

    # 2. 매칭된 부분이 존재한다면 딱 그 좌표들만 지워줍니다.
    if cells_to_destroy:
        print(f"🎯 일렬 매칭 구역 확정! (총 {len(cells_to_destroy)}개 격자 제거)")
        for r, c in cells_to_destroy:
            grid[r][c] = EMPTY_COLOR
        return True
    return False

running = True
while running:
    clock.tick(60)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            c = mouse_x // CELL_SIZE
            r = mouse_y // CELL_SIZE
            if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE:
                if grid[r][c] != EMPTY_COLOR:
                    drag_start = (r, c)
                
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if drag_start is not None:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                c = mouse_x // CELL_SIZE
                r = mouse_y // CELL_SIZE
                
                if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE:
                    drag_end = (r, c)
                    
                    if is_adjacent(drag_start, drag_end):
                        r1, c1 = drag_start
                        r2, c2 = drag_end
                        
                        # 1. 일단 위치를 교체해 봅니다.
                        grid[r1][c1], grid[r2][c2] = grid[r2][c2], grid[r1][c1]
                        
                        # 2. 교체 후 순수 일렬 매칭이 생겼는지 판단하고 지웁니다.
                        if find_and_destroy_pure_matches():
                            pass
                        else:
                            # 매칭되는 일렬 구역이 없다면 다시 원위치로 롤백합니다.
                            grid[r1][c1], grid[r2][c2] = grid[r2][c2], grid[r1][c1]
                            print("↩️ 일렬 매칭 실패: 원위치")
                            
                drag_start = None

    # 화면 그리기
    screen.fill((44, 62, 80))
    
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            color = grid[r][c]
            rect_x = c * CELL_SIZE + 4
            rect_y = r * CELL_SIZE + 4
            rect_w = CELL_SIZE - 8
            rect_h = CELL_SIZE - 8
            
            if color == EMPTY_COLOR:
                pygame.draw.rect(screen, color, (rect_x, rect_y, rect_w, rect_h), border_radius=4)
            else:
                pygame.draw.rect(screen, color, (rect_x, rect_y, rect_w, rect_h), border_radius=12)
            
            if drag_start == (r, c):
                pygame.draw.rect(screen, (255, 255, 255), (rect_x - 2, rect_y - 2, rect_w + 4, rect_h + 4), width=3, border_radius=14)
       
    pygame.display.flip()

pygame.quit()
sys.exit()
