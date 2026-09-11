import sys
import os
import random
import pygame


"""
보석이 떨어지는 모습을 눈으로 볼 수 있게 하려면,
보석마다 실제 화면상의 Y축 픽셀 좌표(이동 중인 위치)와 떨어지는 속도를 부여하여 매 프레임마다
조금씩 아래로 움직이도록 애니메이션 로직을 추가해야 합니다

💡 애니메이션이 부드럽게 연출되는 원리
1. Gem 클래스 도입:
 - 보석판 배열 정보 외에 개별 보석의 현재 미세한 실시간 픽셀 높이(gem.y)와 가야 할 바닥 높이(gem.target_y)를 분리했습니다.
2. 하늘 위 스폰 시스템:
 - 보석이 터져서 리필되는 새 보석들은 화면 바깥쪽 음수 영역(r - GRID_SIZE)의 가상 공중에 생성된 뒤,
   중력 법칙(FALL_SPEED)에 의해 아래로 미끄러져 내려오도록 설계되어 아주 자연스러운 낙하 연출이 완성되었습니다!
"""

sys.stderr = open(os.devnull, 'w')

"""
💡 달라진 애니메이션 최적화 공식
1. empty_count 기반 정밀 스폰:
 - 해당 열에서 파괴된 정확한 보석 개수(empty_count)를 계산해 낸 뒤,
   새 보석의 스폰 시작 좌표를 -(empty_count - r) * CELL_SIZE로 정렬시켰습니다.
2. 이렇게 하면 빈칸이 3개면 딱 3칸 높이 위쪽 천장 경계선에서부터 대기 순번대로 보석들이 지체 없이 촘촘하게 쏟아져 내려오게 되므로,
   터지자마자 리듬감 있게 위에서 보석 덩어리들이 쏟아지는 완벽한 모바일 터치 손맛이 구현됩니다!
"""

"""
# 💡 [여기서 속도를 조절하세요!] 
# 숫자가 작아질수록 보석이 더 부드럽고 느리게 굴러떨어집니다.
#  - FALL_SPEED = 3:
#     아주 묵직하고 찰지게 아래로 스르륵 흘러내리는 느낌 (속도감 있는 연출을 원치 않을 때 추천)
#  - FALL_SPEED = 4:
#     대부분의 모바일 퍼즐 게임에서 사용하는 가장 표준적이고 편안한 낙하 속도
#  - FALL_SPEED = 6:
#     약간 스피디하면서도 떨어지는 모션이 눈에 잘 밟히는 경쾌한 속도
"""
FALL_SPEED = 6



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
pygame.display.set_caption("💎 딜레이 제로 리필 보석 퍼즐 게임 💎")
clock = pygame.time.Clock()

class Gem:
    def __init__(self, color, r, c, start_y_offset=0):
        self.color = color
        self.r = r
        self.c = c
        self.x = c * CELL_SIZE
        self.target_y = r * CELL_SIZE
        # 실시간 연출 Y 좌표 적용
        self.y = self.target_y + start_y_offset 

    def update_position(self):
        """목표지점까지 낙하 속도에 맞춰 아래로 떨어지게 합니다."""
        if self.y < self.target_y:
            self.y += FALL_SPEED
            if self.y > self.target_y:
                self.y = self.target_y
            return True  # 이동 중
        return False  # 정착 완료

def generate_valid_grid():
    while True:
        temp_grid = [[random.choice(COLORS) for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        if not check_initial_matches(temp_grid):
            return [[Gem(temp_grid[r][c], r, c, 0) for c in range(GRID_SIZE)] for r in range(GRID_SIZE)]

def check_initial_matches(g):
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE - 2):
            if g[r][c] == g[r][c+1] == g[r][c+2]: return True
    for r in range(GRID_SIZE - 2):
        for c in range(GRID_SIZE):
            if g[r][c] == g[r+1][c] == g[r+2][c]: return True
    return False

def get_match_cells():
    matched_cells = set()
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE - 2):
            if grid[r][c].color == grid[r][c+1].color == grid[r][c+2].color and grid[r][c].color != EMPTY_COLOR:
                matched_cells.update([(r, c), (r, c+1), (r, c+2)])
    for r in range(GRID_SIZE - 2):
        for c in range(GRID_SIZE):
            if grid[r][c].color == grid[r+1][c].color == grid[r+2][c].color and grid[r][c].color != EMPTY_COLOR:
                matched_cells.update([(r, c), (r+1, c), (r+2, c)])
    return matched_cells

grid = generate_valid_grid()
drag_start = None
game_state = "PLAY"
combo_count = 0

def find_and_destroy_pure_matches():
    cells_to_destroy = get_match_cells()
    if cells_to_destroy:
        for r, c in cells_to_destroy:
            grid[r][c].color = EMPTY_COLOR
        return True
    return False

# 💡 [딜레이 버그 핵심 수정 부분]
def apply_gravity_and_setup_fall():
    for c in range(GRID_SIZE):
        # 현재 열에서 살아남은 보석들 수집 (아래에서부터 위로)
        living_gems = []
        for r in range(GRID_SIZE - 1, -1, -1):
            if grid[r][c].color != EMPTY_COLOR:
                living_gems.append(grid[r][c])
        
        # 이번 열에서 터져서 사라진 총 빈칸의 개수를 계산합니다.
        empty_count = GRID_SIZE - len(living_gems)
        
        idx = 0
        for r in range(GRID_SIZE - 1, -1, -1):
            if idx < len(living_gems):
                # 기존 보석들을 재배치
                grid[r][c] = living_gems[idx]
                grid[r][c].r = r
                grid[r][c].target_y = r * CELL_SIZE
                idx += 1
            else:
                # 💥 [버그 해결] 천장 너머 뜬구름이 아니라, 화면 바로 위 경계선에서 차례대로 생성합니다.
                # 'empty_count'와 격자 연산을 활용해 화면 최상단 바로 위 영역에서 부드럽게 대기 후 진입하도록 오프셋을 좁혔습니다.
                offset_y = -(r + 1) * CELL_SIZE
                new_gem = Gem(random.choice(COLORS), r, c, offset_y)
                # 현재 배치 상태에서 실제 이동감을 살리기 위해 시작 높이 강제 정렬
                new_gem.y = - (empty_count - r) * CELL_SIZE
                grid[r][c] = new_gem

def is_adjacent(pos1, pos2):
    r1, c1 = pos1
    r2, c2 = pos2
    return (abs(r1 - r2) == 1 and c1 == c2) or (abs(c1 - c2) == 1 and r1 == r2)

running = True
while running:
    clock.tick(60)
    
    if game_state == "FALLING":
        is_any_gem_moving = False
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if grid[r][c].update_position():
                    is_any_gem_moving = True
        if not is_any_gem_moving:
            game_state = "STABLE"

    elif game_state == "STABLE":
        if find_and_destroy_pure_matches():
            combo_count += 1
            print(f"🔥 연쇄 콤보! {combo_count} COMBO!!")
            apply_gravity_and_setup_fall()
            game_state = "FALLING"
        else:
            game_state = "PLAY"
            combo_count = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        elif game_state == "PLAY":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                c = mouse_x // CELL_SIZE
                r = mouse_y // CELL_SIZE
                if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE:
                    if grid[r][c].color != EMPTY_COLOR:
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
                            
                            grid[r1][c1], grid[r2][c2] = grid[r2][c2], grid[r1][c1]
                            grid[r1][c1].r, grid[r1][c1].target_y = r1, r1 * CELL_SIZE
                            grid[r2][c2].r, grid[r2][c2].target_y = r2, r2 * CELL_SIZE
                            grid[r1][c1].y = r1 * CELL_SIZE
                            grid[r2][c2].y = r2 * CELL_SIZE
                            
                            if find_and_destroy_pure_matches():
                                combo_count = 1
                                print(f"💥 첫 번째 매칭! {combo_count} COMBO")
                                apply_gravity_and_setup_fall()
                                game_state = "FALLING"
                            else:
                                grid[r1][c1], grid[r2][c2] = grid[r2][c2], grid[r1][c1]
                                grid[r1][c1].r, grid[r1][c1].target_y = r1, r1 * CELL_SIZE
                                grid[r2][c2].r, grid[r2][c2].target_y = r2, r2 * CELL_SIZE
                                grid[r1][c1].y = r1 * CELL_SIZE
                                grid[r2][c2].y = r2 * CELL_SIZE
                                print("↩️ 매칭 실패: 원위치")
                    drag_start = None

    # 4. 화면 렌더링
    screen.fill((44, 62, 80))
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            gem = grid[r][c]
            rect_x = c * CELL_SIZE + 4
            rect_y = int(gem.y) + 4
            rect_w = CELL_SIZE - 8
            rect_h = CELL_SIZE - 8
            
            if gem.color == EMPTY_COLOR:
                pygame.draw.rect(screen, gem.color, (rect_x, rect_y, rect_w, rect_h), border_radius=4)
            else:
                pygame.draw.rect(screen, gem.color, (rect_x, rect_y, rect_w, rect_h), border_radius=12)
            
            if drag_start == (r, c) and game_state == "PLAY":
                pygame.draw.rect(screen, (255, 255, 255), (rect_x - 2, rect_y - 2, rect_w + 4, rect_h + 4), width=3, border_radius=14)
                
    pygame.display.flip()

pygame.quit()
sys.exit()
