import sys
import os
import random
import pygame


"""
기존의 순수 일렬 매칭 영역 추출 함수(get_match_cells)를 확장하여,
 4개가 연속으로 터지면 '가로/세로를 통째로 날려버리는 미사일 보석',
 5개 이상 연속으로 터지면 '주변 3x3 범위를 광역 폭파하는 폭탄 보석'이 터진 자리에 보너스로 생성되도록 설계했습니다.
이 특수 보석들은 일반 보석들 사이에 섞여 떨어지다가,
 유저가 드래그해서 터뜨리는 매칭 무리에 포함되는 순간 연쇄적으로 유도 폭발을 일으키며
 화면의 보석들을 시원하게 쓸어버립니다.

********************************************************************
### 💡 팁: VS Code에서 들여쓰기가 깨질 때의 꿀팁 단축키
만약 나중에 코드를 부분적으로 복사하다가 탭 정렬이 꼬였다면, VS Code 자체 기능을 이용해 1초 만에 자동 정렬할 수 있습니다.
* 영역을 드래그해서 선택한 뒤 **`Shift + Alt + F`** (맥은 `Shift + Option + F`)를 누르면,
VS Code가 파이썬 문법에 맞게 들여쓰기를 알아서 이쁘게 칼정렬해 줍니다. 
********************************************************************

### 💡 아이템 시스템 작동 방식 설명
1. **`get_match_segments()` 세그먼트 분리 탐색**:
 - 기존의 뭉뚱그려 한 번에 담는 방식에서 벗어나, 가로줄과 세로줄별로 **연속된 길이 정보**를 온전히 측정합니다.
   그 결과 길이가 `4`면 미사일, `5` 이상이면 폭탄이라는 정밀한 판단이 가능해졌습니다.
2. **`while loop_flag` 연쇄 다이너마이트 알고리즘**:
 - 미사일이 터지면서 날아간 줄에 **우연히 다른 폭탄이나 미사일이 걸려있다면,
   그 아이템까지 도미노처럼 연속으로 폭발**하는 화려한 연쇄 반응 시스템이 포함되어 있습니다.
3. **아이템 객체 렌더링 오프셋**:
 - 렌더링 루프 최하단에서 `gem.item_type` 검사를 수행하여 미사일(`MISSILE`)은 십자 타격용 동심원 링 마크를,
   폭탄(`BOMB`)은 사각형 마크를 겹쳐 그려 시각적 구분을 주었습니다.

4개나 5개를 나란히 조립해서 특수 보석을 만들어낸 뒤, 콤보 연쇄를 일으켜 스코어 보드의 점수를 광속으로 올려보세요!

기본 드래그 기능부터 특수 아이템 연쇄 격발 시스템까지 완벽한 모바일 사양 퍼즐 게임이 파이썬 코드로 완성되었습니다.
게임을 테스트해 보시면서 **미사일과 폭탄이 호쾌하게 잘 터지는지** 짜릿한 격발 소감을 알려주세요!
"""

sys.stderr = open(os.devnull, 'w')

FALL_SPEED = 5  


# 1. 게임 화면 및 격자 설정
SCORE_PANEL_HEIGHT = 80
GRID_WIDTH, GRID_HEIGHT = 480, 480
WIDTH = GRID_WIDTH
HEIGHT = GRID_HEIGHT + SCORE_PANEL_HEIGHT

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
# 💡 사운드 재생을 위한 믹서 모듈을 명시적으로 초기화합니다.
pygame.mixer.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🚀 미사일 & 폭탄 아이템 탑재 보석 퍼즐 🚀")
clock = pygame.time.Clock()

# 💡 [사운드 파일 로드 부] 코드와 같은 폴더에 'pop.wav' 파일을 넣어두세요!
# 파일이 없더라도 게임이 튕기지 않도록 예외 처리를 적용했습니다.
match_sound = None
try:
    # 파이썬 파일이 있는 진짜 폴더 경로 계산
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sound_path = os.path.join(current_dir, "pop.wav")
    
    # 1. 효과음 로드
    if os.path.exists(sound_path):
        match_sound = pygame.mixer.Sound(sound_path)
        print("✅ 효과음 파일(pop.wav) 연결 성공!")
        
    # 💡 [배경 음악 핵심 추가 부분] 
    # 2. game 폴더 내 bgm.mp3 파일 주소를 합성합니다.
    bgm_path = os.path.join(current_dir, "bgm.mp3")
    
    if os.path.exists(bgm_path):
        pygame.mixer.music.load(bgm_path) # 배경 음악 불러오기
        pygame.mixer.music.set_volume(0.4) # 볼륨 설정 (0.0 ~ 1.0 사이, 너무 크지 않게 0.4 추천)
        pygame.mixer.music.play(-1)        # 💡 -1을 넣으면 음악이 끝나도 끊임없이 무한 반복 재생됩니다!
        print("🎵 배경 음악(bgm.mp3) 무한 재생 시작!")
    else:
        print(f"⚠️ 배경 음악 없음. 경로 확인용: {bgm_path}")

except Exception as e:
    print(f"사운드 리소스 로드 실패: {e}")


current_score = 0
max_combo = 0

class Gem:
    def __init__(self, color, r, c, start_y_offset=0):
        self.color = color
        self.r = r
        self.c = c
        self.x = c * CELL_SIZE
        self.target_y = r * CELL_SIZE + SCORE_PANEL_HEIGHT
        self.y = self.target_y + start_y_offset 
        # 💡 [아이템 변수 추가] "NORMAL" (일반), "MISSILE" (십자형), "BOMB" (3x3 광역폭탄)
        self.item_type = "NORMAL"

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

# 💡 [정밀 매칭 계산] 단순히 합치는 게 아니라 몇 개가 연속되었는지 콤보 패턴을 추적합니다.
def get_match_segments():
    """가로, 세로별로 일렬 연속된 매칭 덩어리(List)들을 분리해서 수집합니다."""
    segments = []
    
    # 가로 검사
    for r in range(GRID_SIZE):
        c = 0
        while c < GRID_SIZE - 2:
            if grid[r][c].color != EMPTY_COLOR:
                match_len = 1
                while c + match_len < GRID_SIZE and grid[r][c].color == grid[r][c+match_len].color:
                    match_len += 1
                if match_len >= 3:
                    segments.append({"type": "H", "cells": [(r, c+i) for i in range(match_len)]})
                    c += match_len
                    continue
            c += 1
            
    # 세로 검사
    for c in range(GRID_SIZE):
        r = 0
        while r < GRID_SIZE - 2:
            if grid[r][c].color != EMPTY_COLOR:
                match_len = 1
                while r + match_len < GRID_SIZE and grid[r][c].color == grid[r+match_len][c].color:
                    match_len += 1
                if match_len >= 3:
                    segments.append({"type": "V", "cells": [(r+i, c) for i in range(match_len)]})
                    r += match_len
                    continue
            r += 1
    return segments

grid = generate_valid_grid()
drag_start = None
game_state = "PLAY"
combo_count = 0

def find_and_destroy_pure_matches():
    global current_score, max_combo
    segments = get_match_segments()
    if not segments:
        return False

    cells_to_destroy = set()
    items_to_create = [] # 터진 자리에 생성할 아이템 정보 보관용

    # 1. 매칭 덩어리를 분석하여 아이템 스폰 조건 수집
    for seg in segments:
        cells = seg["cells"]
        cells_to_destroy.update(cells)
        count = len(cells)
        
        # 스폰 베이스 좌표는 연속 구역의 정중앙 칸으로 설정
        base_r, base_c = cells[count // 2]
        base_color = grid[base_r][base_c].color
        
        if count == 4:
            items_to_create.append({"r": base_r, "c": base_c, "color": base_color, "type": "MISSILE"})
            print("🚀 [알림] 4단 합체! 미사일 보석 보급 예정!")
        elif count >= 5:
            items_to_create.append({"r": base_r, "c": base_c, "color": base_color, "type": "BOMB"})
            print("💣 [알림] 5단 초합체! 대형 폭탄 보석 보급 예정!")

    # 2. 💡 [연쇄 아이템 반응 트리거] 지워질 구역 안에 이미 미사일이나 폭탄이 있었다면 광역 제거를 가동합니다.
    loop_flag = True
    while loop_flag:
        loop_flag = False
        additional_destroyed = set()
        
        for r, c in cells_to_destroy:
            gem = grid[r][c]
            # 가) 미사일 격발 로직 (해당 십자선 가로줄 전체, 세로줄 전체 파괴)
            if gem.item_type == "MISSILE":
                gem.item_type = "NORMAL" # 중복 격발 방지
                for i in range(GRID_SIZE):
                    if (r, i) not in cells_to_destroy: additional_destroyed.add((r, i))
                    if (i, c) not in cells_to_destroy: additional_destroyed.add((i, c))
            # 나) 폭탄 격발 로직 (주변 3x3 범위 9칸 일괄 파괴)
            elif gem.item_type == "BOMB":
                gem.item_type = "NORMAL"
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE:
                            if (nr, nc) not in cells_to_destroy: additional_destroyed.add((nr, nc))
                            
        if additional_destroyed:
            cells_to_destroy.update(additional_destroyed)
            loop_flag = True # 새로 쓸려나간 구역에 또 아이템이 있을지 모르니 다시 스캔

    # 3. 데이터 일괄 삭제 및 점수 가산
    earned_score = len(cells_to_destroy) * 100 * (combo_count + 1)
    current_score += earned_score
    if combo_count > max_combo: max_combo = combo_count
    if match_sound: match_sound.play()

    for r, c in cells_to_destroy:
        grid[r][c].color = EMPTY_COLOR
        grid[r][c].item_type = "NORMAL"

    # 4. 💡 보석이 다 지워진 빈자리 중 아이템 생성 자리에 특수 속성을 부여합니다.
    for item in items_to_create:
        r, c = item["r"], item["c"]
        grid[r][c].color = item["color"]
        grid[r][c].item_type = item["type"]

    return True

def apply_gravity_and_setup_fall():
    for c in range(GRID_SIZE):
        living_gems = []
        for r in range(GRID_SIZE - 1, -1, -1):
            if grid[r][c].color != EMPTY_COLOR or grid[r][c].item_type != "NORMAL":
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


# 메인 루프 가동
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

    screen.fill((44, 62, 80))
    pygame.draw.rect(screen, (24, 34, 44), (0, 0, WIDTH, SCORE_PANEL_HEIGHT))
    pygame.draw.rect(screen, (41, 128, 185), (0, SCORE_PANEL_HEIGHT - 4, WIDTH, 4))

    font_large = pygame.font.SysFont("malgungothic", 28, bold=True)
    font_small = pygame.font.SysFont("malgungothic", 14, bold=True)

    score_text = font_large.render(f"SCORE: {current_score:,}", True, (255, 255, 255))
    combo_text = font_small.render(f"MAX COMBO: {max_combo} 연쇄", True, (241, 196, 15))
    state_text = font_small.render(f"STATUS: {game_state}", True, (149, 165, 166))
    
    screen.blit(score_text, (20, 12))
    screen.blit(combo_text, (22, 50))
    screen.blit(state_text, (WIDTH - 130, 50))
    
    if combo_count >= 2:
        combo_alert = font_large.render(f"{combo_count} COMBO!", True, (231, 76, 60))
        screen.blit(combo_alert, (WIDTH - 180, 12))

    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            gem = grid[r][c]
            rect_x = c * CELL_SIZE + 4
            rect_y = int(gem.y) + 4
            rect_w = CELL_SIZE - 8
            rect_h = CELL_SIZE - 8

            if rect_y > SCORE_PANEL_HEIGHT - 20:
                if gem.color == EMPTY_COLOR:
                    pygame.draw.rect(screen, gem.color, (rect_x, rect_y, rect_w, rect_h), border_radius=4)
                else:
                    pygame.draw.rect(screen, gem.color, (rect_x, rect_y, rect_w, rect_h), border_radius=12)

            if gem.item_type == "MISSILE":
                pygame.draw.circle(screen, (30, 30, 30), (rect_x + rect_w//2, rect_y + rect_h//2), 10)
                pygame.draw.circle(screen, (255, 255, 255), (rect_x + rect_w//2, rect_y + rect_h//2), 5)
            elif gem.item_type == "BOMB":
                pygame.draw.rect(screen, (255, 255, 255), (rect_x + rect_w//4, rect_y + rect_h//4, rect_w//2, rect_h//2), width=3, border_radius=4)

            if drag_start == (r, c) and game_state == "PLAY":
                pygame.draw.rect(screen, (255, 255, 255), (rect_x - 2, rect_y - 2, rect_w + 4, rect_h + 4), width=3, border_radius=14)

    # for r in range(GRID_SIZE):
    #     for c in range(GRID_SIZE):
    #         gem = grid[r][c]
    #         rect_x = c * CELL_SIZE + 4
    #         rect_y = int(gem.y) + 4
    #         rect_w = CELL_SIZE - 8
    #         rect_h = CELL_SIZE - 8
            
    #         if rect_y > SCORE_PANEL_HEIGHT - 20:
    #             if gem.color == EMPTY_COLOR:
    #                 pygame.draw.rect(screen, gem.color, (rect_x, rect_y, rect_w, rect_h), border_radius=4)
    #             else:
    #                 pygame.draw.rect(screen, gem.color, (rect_x, rect_y, rect_w, rect_h), border_radius=12)
            
    #         if drag_start == (r, c) and game_state == "PLAY":
    #             pygame.draw.rect(screen, (255, 255, 255), (rect_x - 2, rect_y - 2, rect_w + 4, rect_h + 4), width=3, border_radius=14)
                
    pygame.display.flip()

pygame.quit()
sys.exit()
