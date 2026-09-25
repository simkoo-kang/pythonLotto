import sys
import os
import random
import pygame


"""
💡 추가된 UI 시스템 설명
1. pygame.font.SysFont 스크립트 메커니즘:
 - 컴퓨터에 내장된 '맑은 고딕(malgungothic)' 등 굵고 정갈한 서체를 불러와
   하이파이(Hi-Fi) 게임 라벨을 화면상에 정확히 투사(screen.blit)합니다.
2. 마우스 인덱스 보정 공식:
 - 게임창이 상단으로 늘어났기 때문에 사용자가 누르는 마우스 클릭 좌표에서
   스코어판 영역(mouse_y - SCORE_PANEL_HEIGHT)을 정밀하게 빼주어,
   보석 클릭 위치가 위아래로 어긋나던 오작동 버그를 원천 봉쇄했습니다.
3. 콤보 알림 컴포넌트:
 - 2연쇄 콤보 이상 연속으로 보석이 팡팡 터질 때는
   상단 우측에 붉은색 글씨로 X COMBO!라는 다이내믹 이펙트 라벨이 실시간으로 팝업되도록 가시성을 높였습니다.
"""

sys.stderr = open(os.devnull, 'w')

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
FALL_SPEED = 5


# 1. 게임 화면 및 격자 설정
SCORE_PANEL_HEIGHT = 80  # 💡 상단 점수판이 들어갈 공간 (80픽셀 확장)
GRID_WIDTH, GRID_HEIGHT = 480, 480
WIDTH = GRID_WIDTH
HEIGHT = GRID_HEIGHT + SCORE_PANEL_HEIGHT # 총 화면 높이

GRID_SIZE = 8
CELL_SIZE = GRID_WIDTH // GRID_SIZE

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
pygame.display.set_caption("💎 스코어보드 UI 탑재 보석 퍼즐 게임 💎")
clock = pygame.time.Clock()

# 💡 [점수 관련 변수 초기화]
current_score = 0
max_combo = 0

class Gem:
    def __init__(self, color, r, c, start_y_offset=0):
        self.color = color
        self.r = r
        self.c = c
        self.x = c * CELL_SIZE
        # 💡 보석의 목표 Y축 계산 시 SCORE_PANEL_HEIGHT 만큼 밑으로 밀어줍니다.
        self.target_y = r * CELL_SIZE + SCORE_PANEL_HEIGHT
        self.y = self.target_y + start_y_offset 

    def update_position(self):
        if self.y < self.target_y:
            self.y += FALL_SPEED
            if self.y > self.target_y:
                self.y = self.target_y
            return True
        return False

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
    global current_score, max_combo
    cells_to_destroy = get_match_cells()
    if cells_to_destroy:
        # 💡 [점수 획득 공식 적용] 터진 보석 수 × 100점 × 현재 콤보 배수 보너스
        earned_score = len(cells_to_destroy) * 100 * (combo_count + 1)
        current_score += earned_score
        
        # 최고 콤보수 갱신
        if combo_count > max_combo:
            max_combo = combo_count
            
        for r, c in cells_to_destroy:
            grid[r][c].color = EMPTY_COLOR
        return True
    return False

def apply_gravity_and_setup_fall():
    for c in range(GRID_SIZE):
        living_gems = []
        for r in range(GRID_SIZE - 1, -1, -1):
            if grid[r][c].color != EMPTY_COLOR:
                living_gems.append(grid[r][c])
        
        empty_count = GRID_SIZE - len(living_gems)
        
        idx = 0
        for r in range(GRID_SIZE - 1, -1, -1):
            if idx < len(living_gems):
                grid[r][c] = living_gems[idx]
                grid[r][c].r = r
                grid[r][c].target_y = r * CELL_SIZE + SCORE_PANEL_HEIGHT
                if grid[r][c].y > grid[r][c].target_y:
                    grid[r][c].y = grid[r][c].target_y - CELL_SIZE
                idx += 1
            else:
                new_gem = Gem(random.choice(COLORS), r, c, 0)
                new_gem.y = SCORE_PANEL_HEIGHT - (empty_count - r) * CELL_SIZE
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
                # 💡 마우스 Y축 입력 감지 시 점수판 영역만큼 오프셋을 빼줍니다.
                r = (mouse_y - SCORE_PANEL_HEIGHT) // CELL_SIZE
                if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE and mouse_y >= SCORE_PANEL_HEIGHT:
                    if grid[r][c].color != EMPTY_COLOR:
                        drag_start = (r, c)
                        
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if drag_start is not None:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    c = mouse_x // CELL_SIZE
                    r = (mouse_y - SCORE_PANEL_HEIGHT) // CELL_SIZE
                    
                    if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE:
                        drag_end = (r, c)
                        if is_adjacent(drag_start, drag_end):
                            r1, c1 = drag_start
                            r2, c2 = drag_end
                            
                            grid[r1][c1], grid[r2][c2] = grid[r2][c2], grid[r1][c1]
                            grid[r1][c1].r, grid[r1][c1].target_y = r1, r1 * CELL_SIZE + SCORE_PANEL_HEIGHT
                            grid[r2][c2].r, grid[r2][c2].target_y = r2, r2 * CELL_SIZE + SCORE_PANEL_HEIGHT
                            grid[r1][c1].y = r1 * CELL_SIZE + SCORE_PANEL_HEIGHT
                            grid[r2][c2].y = r2 * CELL_SIZE + SCORE_PANEL_HEIGHT
                            
                            if find_and_destroy_pure_matches():
                                combo_count = 1
                                apply_gravity_and_setup_fall()
                                game_state = "FALLING"
                            else:
                                grid[r1][c1], grid[r2][c2] = grid[r2][c2], grid[r1][c1]
                                grid[r1][c1].r, grid[r1][c1].target_y = r1, r1 * CELL_SIZE + SCORE_PANEL_HEIGHT
                                grid[r2][c2].r, grid[r2][c2].target_y = r2, r2 * CELL_SIZE + SCORE_PANEL_HEIGHT
                                grid[r1][c1].y = r1 * CELL_SIZE + SCORE_PANEL_HEIGHT
                                grid[r2][c2].y = r2 * CELL_SIZE + SCORE_PANEL_HEIGHT
                    drag_start = None

    # 4. 화면 전체 렌더링
    screen.fill((44, 62, 80))
    
    # 💡 [핵심 추가] 상단 스코어 보드 레이아웃 UI 드로잉
    pygame.draw.rect(screen, (24, 34, 44), (0, 0, WIDTH, SCORE_PANEL_HEIGHT)) # 어두운 패널 배경
    pygame.draw.rect(screen, (41, 128, 185), (0, SCORE_PANEL_HEIGHT - 4, WIDTH, 4)) # 패널 경계 푸른 선
    
    # 시스템 폰트 로드 (가독성이 좋은 기본 굵은 글씨체 설정)
    font_large = pygame.font.SysFont("malgungothic", 28, bold=True)
    font_small = pygame.font.SysFont("malgungothic", 14, bold=True)
    
    # 텍스트 라벨 내용 렌더링
    score_text = font_large.render(f"SCORE: {current_score:,}", True, (255, 255, 255))
    combo_text = font_small.render(f"MAX COMBO: {max_combo} 연쇄", True, (241, 196, 15))
    state_text = font_small.render(f"STATUS: {game_state}", True, (149, 165, 166))
    
    # 화면 위 최적의 픽셀 좌표에 글자 배치
    screen.blit(score_text, (20, 12))
    screen.blit(combo_text, (22, 50))
    screen.blit(state_text, (WIDTH - 130, 50))
    
    if combo_count >= 2:
        combo_alert = font_large.render(f"{combo_count} COMBO!", True, (231, 76, 60))
        screen.blit(combo_alert, (WIDTH - 180, 12))

    # 보석 판 그리기
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            gem = grid[r][c]
            rect_x = c * CELL_SIZE + 4
            rect_y = int(gem.y) + 4
            rect_w = CELL_SIZE - 8
            rect_h = CELL_SIZE - 8
            
            # 상단 스코어 패널 가림막 연출 (패널 너머 공중 영역 보석은 렌더링 생략)
            if rect_y > SCORE_PANEL_HEIGHT - 20:
                if gem.color == EMPTY_COLOR:
                    pygame.draw.rect(screen, gem.color, (rect_x, rect_y, rect_w, rect_h), border_radius=4)
                else:
                    pygame.draw.rect(screen, gem.color, (rect_x, rect_y, rect_w, rect_h), border_radius=12)
            
            if drag_start == (r, c) and game_state == "PLAY":
                pygame.draw.rect(screen, (255, 255, 255), (rect_x - 2, rect_y - 2, rect_w + 4, rect_h + 4), width=3, border_radius=14)
                
    pygame.display.flip()

pygame.quit()
sys.exit()
