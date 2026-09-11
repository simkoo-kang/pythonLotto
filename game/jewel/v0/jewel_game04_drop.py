import sys
import os
import random
import pygame


"""
💡 중력과 연쇄 반응의 알고리즘 원리
1. 역방향 리스트 추출 기법 (living_gems):
 - 아래 바닥 행(GRID_SIZE - 1)부터 천장 행(0)까지 세로줄 방향으로 훑으며 허공에 떠 있는
   진짜 보석만 순서대로 리스트에 이쁘게 쓸어 담습니다.
   빈 공간은 그냥 무시해 버리므로 보석들이 저절로 아래로 압축 정렬되는 마법이 일어납니다.
2. while True 콤보 파이프라인:
 - 보석이 떨어져서 정렬되면 판의 구조가 완전히 뒤바뀝니다.
   이때 while True 무한 루프가 "새로 바뀐 판에 혹시 짝이 또 맞는 게 생겼나?" 하고 한 번 더 훑어줍니다.
   만약 있으면 또 터뜨리고 중력을 작동하는 과정을 반복하여 애니팡 특유의 시원시원한 자동 연쇄 폭발(Combo)을 완벽하게 구현해 냅니다.
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
EMPTY_COLOR = (30, 30, 30)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🍏 중력 작동 및 무한 연쇄 콤보 보석 게임 🍏")
clock = pygame.time.Clock()

def generate_valid_grid():
    while True:
        new_grid = [[random.choice(COLORS) for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        if not get_match_cells(new_grid):
            return new_grid

def get_match_cells(g):
    matched_cells = set()
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE - 2):
            if g[r][c] == g[r][c+1] == g[r][c+2] and g[r][c] != EMPTY_COLOR:
                matched_cells.update([(r, c), (r, c+1), (r, c+2)])
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

def find_and_destroy_pure_matches():
    cells_to_destroy = get_match_cells(grid)
    if cells_to_destroy:
        print(f"💥 매칭 제거 완료! ({len(cells_to_destroy)}개 파괴)")
        for r, c in cells_to_destroy:
            grid[r][c] = EMPTY_COLOR
        return True
    return False

# 💡 [핵심 추가] 빈자리를 채우고 중력을 적용하는 알고리즘
def apply_gravity_and_refill():
    """모든 열을 검사하여 보석을 아래로 떨어뜨리고 맨 위에 새 보석을 채웁니다."""
    for c in range(GRID_SIZE):
        # 1. 밑에서부터 위로 올라가며 살아있는 보석만 추려냅니다.
        living_gems = []
        for r in range(GRID_SIZE - 1, -1, -1):
            if grid[r][c] != EMPTY_COLOR:
                living_gems.append(grid[r][c])
        
        # 2. 살아있는 보석을 아래 칸부터 순서대로 다시 배치합니다.
        idx = 0
        for r in range(GRID_SIZE - 1, -1, -1):
            if idx < len(living_gems):
                grid[r][c] = living_gems[idx]
                idx += 1
            else:
                # 3. 보석이 고갈된 윗자리(빈칸)에는 새로운 랜덤 보석을 채워 넣습니다.
                grid[r][c] = random.choice(COLORS)

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
                        
                        # 1. 보석 위치 교체
                        grid[r1][c1], grid[r2][c2] = grid[r2][c2], grid[r1][c1]
                        
                        # 2. 💡 [연쇄 폭발 시스템] 터뜨리기 -> 중력 드롭 -> 또 매칭되면 터뜨리기를 무한 반복합니다!
                        combo = 1
                        if find_and_destroy_pure_matches():
                            # 첫 폭발이 성립되면 중력 적용 후 연쇄 반응이 더 있는지 계속 검사합니다.
                            while True:
                                apply_gravity_and_refill() # 떨어뜨리고 보급하기
                                time.sleep(0.1) # 연쇄 터짐을 감지하기 위한 아주 짧은 간격
                                
                                # 떨어지고 나서 새로운 매칭이 또 일어났는가?
                                if find_and_destroy_pure_matches():
                                    combo += 1
                                    print(f"🔥 연쇄 콤보 발생! 연타 횟수: {combo} COMBO!!")
                                else:
                                    break # 더 이상 터질 게 없으면 연쇄 탈출
                        else:
                            # 아무것도 매칭이 안 되면 원래 자리로 원위치 시킵니다.
                            grid[r1][c1], grid[r2][c2] = grid[r2][c2], grid[r1][c1]
                            print("↩️ 매칭 실패: 원위치")
                            
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
            
            pygame.draw.rect(screen, color, (rect_x, rect_y, rect_w, rect_h), border_radius=12)
            
            if drag_start == (r, c):
                pygame.draw.rect(screen, (255, 255, 255), (rect_x - 2, rect_y - 2, rect_w + 4, rect_h + 4), width=3, border_radius=14)
                
    pygame.display.flip()

pygame.quit()
sys.exit()
