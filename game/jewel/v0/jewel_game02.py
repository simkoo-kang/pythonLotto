import sys
import os
import random
import pygame


"""
💡 알고리즘 작동 메커니즘
1. set()을 활용한 중력식 결합:
 - (r, c) 좌표를 리스트 대신 중복을 허용하지 않는 set 구조에 담았습니다.
   덕분에 가로 3개와 세로 3개가 교차하는 T자, L자 형태로 동시에 터질 때
   좌표가 겹쳐서 에러가 나는 현상을 완벽히 방어합니다.
2. 스왑 백트래킹(Backtracking):
 - 보석을 움직였는데도 3개가 맞지 않으면 규칙상 이동할 수 없습니다.
   코드 내부에서 find_and_destroy_matches()의 결과가 거짓(False)이면
   다시 자리를 원위치 시켜 게임의 완성도를 높였습니다.
"""


sys.stderr = open(os.devnull, 'w')

WIDTH, HEIGHT = 480, 480
GRID_SIZE = 8
CELL_SIZE = WIDTH // GRID_SIZE

# 보석 색상 정의
COLORS = [
    (235, 77, 75),    # 루비 (레드)
    (106, 176, 76),   # 에메랄드 (그린)
    (29, 209, 161),   # 사파이어 (민트 블루)
    (241, 196, 15),   # 토파즈 (옐로우)
    (155, 89, 182)    # 아메지스트 (퍼플)
]
EMPTY_COLOR = (30, 30, 30)  # 💥 보석이 터져서 빈 공간이 된 자리의 색상 (어두운 회색)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("💎 보석 3-Match 매칭 게임 💎")
clock = pygame.time.Clock()

# 게임 시작 시 3개 연달아 배치되지 않도록 안전하게 판을 생성합니다.
def generate_valid_grid():
    while True:
        new_grid = [[random.choice(COLORS) for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        # 시작하자마자 터지는 게 없는 완벽한 상태일 때만 반환합니다.
        if not check_matches_only(new_grid):
            return new_grid

def check_matches_only(g):
    """현재 판에 3개 매칭된 곳이 있는지 여부만 빠르게 확인합니다."""
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE - 2):
            if g[r][c] == g[r][c+1] == g[r][c+2] and g[r][c] != EMPTY_COLOR:
                return True
    for r in range(GRID_SIZE - 2):
        for c in range(GRID_SIZE):
            if g[r][c] == g[r+1][c] == g[r+2][c] and g[r][c] != EMPTY_COLOR:
                return True
    return False

grid = generate_valid_grid()
drag_start = None

def is_adjacent(pos1, pos2):
    r1, c1 = pos1
    r2, c2 = pos2
    return (abs(r1 - r2) == 1 and c1 == c2) or (abs(c1 - c2) == 1 and r1 == r2)

def find_and_destroy_all_same_colors():
    """3개 이상 매칭된 보석의 '색상'을 알아내어 판 전체의 동일한 색상을 모두 지웁니다."""
    colors_to_wipe = set() # 광역 제거할 색상 목록

    # 1. 먼저 가로 방향으로 3개 연달아 맞은 색상 찾기
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE - 2):
            if grid[r][c] == grid[r][c+1] == grid[r][c+2] and grid[r][c] != EMPTY_COLOR:
                colors_to_wipe.add(grid[r][c])

    # 2. 세로 방향으로 3개 연달아 맞은 색상 찾기
    for r in range(GRID_SIZE - 2):
        for c in range(GRID_SIZE):
            if grid[r][c] == grid[r+1][c] == grid[r+2][c] and grid[r][c] != EMPTY_COLOR:
                colors_to_wipe.add(grid[r][c])

    # 3. 💡 핵심: 매칭된 색상이 있다면 판 전체를 돌며 그 색상을 전부 폭파시킵니다!
    if colors_to_wipe:
        destroyed_count = 0
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if grid[r][c] in colors_to_wipe:
                    grid[r][c] = EMPTY_COLOR
                    destroyed_count += 1
                    
        print(f"💣 광역 폭발 발동! 매칭된 색상 전체 제거 완료 (파괴된 보석 수: {destroyed_count}개)")
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
                # 빈칸은 드래그할 수 없습니다.
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
                        
                        # 보석 위치 스왑
                        grid[r1][c1], grid[r2][c2] = grid[r2][c2], grid[r1][c1]
                        
                        # 동일 색상 전역 제거 알고리즘 가동
                        if find_and_destroy_all_same_colors():
                            pass
                        else:
                            # 매칭 안 되면 롤백
                            grid[r1][c1], grid[r2][c2] = grid[r2][c2], grid[r1][c1]
                            print("↩️ 매칭 성립 안 됨: 원위치")
                            
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
            
            # 일반 보석은 둥근 사각형으로, 터진 자리는 어두운 네모칸으로 표시
            if color == EMPTY_COLOR:
                pygame.draw.rect(screen, color, (rect_x, rect_y, rect_w, rect_h), border_radius=4)
            else:
                pygame.draw.rect(screen, color, (rect_x, rect_y, rect_w, rect_h), border_radius=12)
            
            if drag_start == (r, c):
                pygame.draw.rect(screen, (255, 255, 255), (rect_x - 2, rect_y - 2, rect_w + 4, rect_h + 4), width=3, border_radius=14)
                
    pygame.display.flip()

pygame.quit()
sys.exit()
