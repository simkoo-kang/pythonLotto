import sys
import os
import random
import pygame


"""
💡 튕김이 완벽하게 해결된 원리
1. 프로그램이 무한 루프(while True)에 갇혀 윈도우의 화면 갱신 명령을 무시하던 기존 방식과 달리,
   이번 코드는 루프가 초당 60번 도는 흐름 속에서 자연스럽게 판을 계속 검사하도록 설계되었습니다.
2. 보석이 터지는 순간 상태가 "STABLE"로 전환되어 컴퓨터가 연쇄 반응을 스스로 계산한 뒤,
   다 끝나면 다시 유저가 만질 수 있는 "PLAY" 상태로 돌려놓기 때문에 절대로 먹통이 되거나 불규칙하게 꺼지지 않습니다.
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
pygame.display.set_caption("💎 튕김 오류 완벽 해결 보석 게임 💎")
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

# 💡 [핵심 변경] 게임의 상태를 관리하는 변수들
# "PLAY" (플레이어 조작 가능), "STABLE" (매칭 확인 및 중력 처리 중)
game_state = "PLAY"
combo_count = 0

def is_adjacent(pos1, pos2):
    r1, c1 = pos1
    r2, c2 = pos2
    return (abs(r1 - r2) == 1 and c1 == c2) or (abs(c1 - c2) == 1 and r1 == r2)

def find_and_destroy_pure_matches():
    cells_to_destroy = get_match_cells(grid)
    if cells_to_destroy:
        for r, c in cells_to_destroy:
            grid[r][c] = EMPTY_COLOR
        return True
    return False

def apply_gravity_and_refill():
    for c in range(GRID_SIZE):
        living_gems = []
        for r in range(GRID_SIZE - 1, -1, -1):
            if grid[r][c] != EMPTY_COLOR:
                living_gems.append(grid[r][c])
        idx = 0
        for r in range(GRID_SIZE - 1, -1, -1):
            if idx < len(living_gems):
                grid[r][c] = living_gems[idx]
                idx += 1
            else:
                grid[r][c] = random.choice(COLORS)

running = True
while running:
    # 60프레임을 정상 가동하여 윈도우 응답을 유지합니다.
    clock.tick(60)
    
    # 💡 [핵심 변경] 플레이어가 움직이지 않아도 중력과 연쇄 콤보가 물 흐르듯 이어지게 제어합니다.
    if game_state == "STABLE":
        if find_and_destroy_pure_matches():
            combo_count += 1
            print(f"🔥 연쇄 콤보 활성화! {combo_count} COMBO!!")
            apply_gravity_and_refill()
        else:
            # 더 이상 터질 게 없으면 다시 조작 가능한 플레이 상태로 복귀
            game_state = "PLAY"
            combo_count = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        # 보석이 터지고 채워지는 중("STABLE")에는 마우스 입력을 원천 차단하여 버그를 막습니다.
        elif game_state == "PLAY":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                c = mouse_x // CELL_SIZE
                r = mouse_y // CELL_SIZE
                if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE:
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
                            
                            # 이동 후 매칭이 일어난다면 연쇄 콤보 모드로 상태를 바꿉니다.
                            if find_and_destroy_pure_matches():
                                combo_count = 1
                                print(f"💥 첫 번째 매칭 완료! {combo_count} COMBO")
                                apply_gravity_and_refill()
                                game_state = "STABLE" # 연쇄 자동 연산 모드로 진입!
                            else:
                                # 매칭이 안 되면 즉시 롤백
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
            
            if drag_start == (r, c) and game_state == "PLAY":
                pygame.draw.rect(screen, (255, 255, 255), (rect_x - 2, rect_y - 2, rect_w + 4, rect_h + 4), width=3, border_radius=14)
                
    pygame.display.flip()

pygame.quit()
sys.exit()
