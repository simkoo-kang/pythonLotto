import sys
import os
import random
import pygame

"""
### 🎨 핵심 구현 세부 스펙 분석
1. 가로 4개 연속 매칭 (H_MISSILE) ➡️ 세로 미사일(V_MISSILE) 보급:
 - 가로로 길게 맞췄으므로 반대로 세로줄 전체를 뚫어버리는 미사일 아이템이 터진 자리에 생성됩니다.
2. 세로 4개 연속 매칭 (V_MISSILE) ➡️ 가로 미사일(H_MISSILE) 보급:
 - 세로로 길게 맞췄으므로 반대로 가로줄 전체를 뚫어버리는 미사일 아이템이 생성됩니다.
3. 미사일 + 미사일 맞교환 ➡️ 십자 폭발 (CROSS_BLAST):
 - 가로/세로 종류에 상관없이 미사일 아이템 2개를 서로 교환하면,
   그 교차점을 기준으로 가로 한 줄과 세로 한 줄 전체가 동시에 지워지는 강력한 십자 폭발이 일어납니다.
"""

sys.stderr = open(os.devnull, "w")

FALL_SPEED = 5

# 1. 화면 및 레이아웃 구조 설정
SCORE_PANEL_HEIGHT = 80
GRID_WIDTH, GRID_HEIGHT = 480, 480
WIDTH = GRID_WIDTH
HEIGHT = GRID_HEIGHT + SCORE_PANEL_HEIGHT

GRID_SIZE = 8
CELL_SIZE = GRID_WIDTH // GRID_SIZE
FALL_SPEED = 5

COLORS = [
    (235, 77, 75),  # 루비 (레드)
    (106, 176, 76),  # 에메랄드 (그린)
    (29, 209, 161),  # 사파이어 (민트 블루)
    (241, 196, 15),  # 토파즈 (옐로우)
    (155, 89, 182),  # 아메지스트 (퍼플)
]
EMPTY_COLOR = (30, 30, 30)

pygame.init()
# 💡 사운드 재생을 위한 믹서 모듈을 명시적으로 초기화합니다.
pygame.mixer.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🚀 가로/세로 미사일 분리 탑재 퍼즐 🚀")
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
        pygame.mixer.music.load(bgm_path)  # 배경 음악 불러오기
        pygame.mixer.music.set_volume(
            0.4
        )  # 볼륨 설정 (0.0 ~ 1.0 사이, 너무 크지 않게 0.4 추천)
        pygame.mixer.music.play(
            -1
        )  # 💡 -1을 넣으면 음악이 끝나도 끊임없이 무한 반복 재생됩니다!
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
        # 💡 아이템 속성 세분화: "NORMAL", "BOMB", "H_MISSILE"(가로), "V_MISSILE"(세로), "PROPELLER", "RAINBOW"
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
        temp_grid = [
            [random.choice(COLORS) for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)
        ]
        if not check_initial_matches(temp_grid):
            return [
                [Gem(temp_grid[r][c], r, c, 0) for c in range(GRID_SIZE)]
                for r in range(GRID_SIZE)
            ]


def check_initial_matches(g):
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE - 2):
            if g[r][c] == g[r][c + 1] == g[r][c + 2]:
                return True
    for r in range(GRID_SIZE - 2):
        for c in range(GRID_SIZE):
            if g[r][c] == g[r + 1][c] == g[r + 2][c]:
                return True
    return False


def get_connected_same_color(start_r, start_c, target_color):
    from collections import deque

    connected = set()
    queue = deque([(start_r, start_c)])
    connected.add((start_r, start_c))
    while queue:
        r, c = queue.popleft()
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE:
                if (nr, nc) not in connected and grid[nr][nc].color == target_color:
                    connected.add((nr, nc))
                    queue.append((nr, nc))
    return connected


def analyze_matches_and_setup_items():
    h_lines = []
    v_lines = []
    squares = []

    for r in range(GRID_SIZE):
        c = 0
        while c < GRID_SIZE - 2:
            if grid[r][c].color != EMPTY_COLOR:
                l = 1
                while c + l < GRID_SIZE and grid[r][c].color == grid[r][c + l].color:
                    l += 1
                if l >= 3:
                    h_lines.append(
                        {
                            "r": r,
                            "c_start": c,
                            "len": l,
                            "cells": [(r, c + i) for i in range(l)],
                        }
                    )
                    c += l
                    continue
            c += 1

    for c in range(GRID_SIZE):
        r = 0
        while r < GRID_SIZE - 2:
            if grid[r][c].color != EMPTY_COLOR:
                l = 1
                while r + l < GRID_SIZE and grid[r][c].color == grid[r + l][c].color:
                    l += 1
                if l >= 3:
                    v_lines.append(
                        {
                            "c": c,
                            "r_start": r,
                            "len": l,
                            "cells": [(r + i, c) for i in range(l)],
                        }
                    )
                    r += l
                    continue
            r += 1

    for r in range(GRID_SIZE - 1):
        for c in range(GRID_SIZE - 1):
            color = grid[r][c].color
            if (
                color != EMPTY_COLOR
                and grid[r][c + 1].color == color
                and grid[r + 1][c].color == color
                and grid[r + 1][c + 1].color == color
            ):
                squares.append([(r, c), (r, c + 1), (r + 1, c), (r + 1, c + 1)])

    cells_to_destroy = set()
    items_to_create = []

    used_h = set()
    used_v = set()

    # 1. 5개 일렬 매칭 ➡️ 미러볼(RAINBOW)
    for idx, h in enumerate(h_lines):
        if h["len"] >= 5 and idx not in used_h:
            used_h.add(idx)
            cells_to_destroy.update(h["cells"])
            br, bc = h["cells"][h["len"] // 2]
            items_to_create.append(
                {"r": br, "c": bc, "color": (255, 255, 255), "type": "RAINBOW"}
            )

    for idx, v in enumerate(v_lines):
        if v["len"] >= 5 and idx not in used_v:
            used_v.add(idx)
            cells_to_destroy.update(v["cells"])
            br, bc = v["cells"][v["len"] // 2]
            items_to_create.append(
                {"r": br, "c": bc, "color": (255, 255, 255), "type": "RAINBOW"}
            )

    # 2. T자, ㄱ자 모양 교차 검사 ➡️ 5x5 메가 폭탄(BOMB)
    for h_i, h in enumerate(h_lines):
        if h_i in used_h:
            continue
        for v_i, v in enumerate(v_lines):
            if v_i in used_v:
                continue
            intersect = set(h["cells"]).intersection(set(v["cells"]))
            if intersect:
                used_h.add(h_i)
                used_v.add(v_i)
                cells_to_destroy.update(h["cells"])
                cells_to_destroy.update(v["cells"])
                cr, cc = list(intersect)
                cluster = get_connected_same_color(cr, cc, grid[cr][cc].color)
                cells_to_destroy.update(cluster)
                items_to_create.append(
                    {"r": cr, "c": cc, "color": grid[cr][cc].color, "type": "BOMB"}
                )
                print("💥 [폭탄] T/ㄱ 교차 매칭 완료!")

    # 3. 💡 가로 4개 ➡️ 가로 미사일, 세로 4개 ➡️ 세로 미사일 분리 설계
    for idx, h in enumerate(h_lines):
        if h["len"] == 4 and idx not in used_h:
            used_h.add(idx)
            cells_to_destroy.update(h["cells"])
            br, bc = h["cells"][1]  # 두번째 보석 자리에 생성
            items_to_create.append(
                {"r": br, "c": bc, "color": grid[br][bc].color, "type": "H_MISSILE"}
            )
            print("🚀 [가로 미사일] 생성 예정 (-)")

    for idx, v in enumerate(v_lines):
        if v["len"] == 4 and idx not in used_v:
            used_v.add(idx)
            cells_to_destroy.update(v["cells"])
            br, bc = v["cells"][1]
            items_to_create.append(
                {"r": br, "c": bc, "color": grid[br][bc].color, "type": "V_MISSILE"}
            )
            print("🚀 [세로 미사일] 생성 예정 (|)")

    # 4. ㅁ자 네모 4개 ➡️ 프로펠러(PROPELLER)
    for sq in squares:
        if not set(sq).intersection(cells_to_destroy):
            cells_to_destroy.update(sq)
            sr, sc = sq[0]
            cluster = get_connected_same_color(sr, sc, grid[sr][sc].color)
            cells_to_destroy.update(cluster)
            items_to_create.append(
                {"r": sr, "c": sc, "color": grid[sr][sc].color, "type": "PROPELLER"}
            )

    for idx, h in enumerate(h_lines):
        if idx not in used_h:
            cells_to_destroy.update(h["cells"])
    for idx, v in enumerate(v_lines):
        if idx not in used_v:
            cells_to_destroy.update(v["cells"])

    return cells_to_destroy, items_to_create


def trigger_item_explosions(cells_to_destroy):
    loop_flag = True
    while loop_flag:
        loop_flag = False
        add_set = set()
        for r, c in cells_to_destroy:
            gem = grid[r][c]

            if gem.item_type == "BOMB":
                gem.item_type = "NORMAL"
                for dr in range(-2, 3):
                    for dc in range(-2, 3):
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE:
                            if (nr, nc) not in cells_to_destroy:
                                add_set.add((nr, nc))

            # 💡 [미사일 기능 분리 구현 부]
            elif gem.item_type == "H_MISSILE":  # 가로 한 줄 폭파
                gem.item_type = "NORMAL"
                for i in range(GRID_SIZE):
                    if (r, i) not in cells_to_destroy:
                        add_set.add((r, i))

            elif gem.item_type == "V_MISSILE":  # 세로 한 줄 폭파
                gem.item_type = "NORMAL"
                for i in range(GRID_SIZE):
                    if (i, c) not in cells_to_destroy:
                        add_set.add((i, c))

            elif gem.item_type == "PROPELLER":
                gem.item_type = "NORMAL"
                for _ in range(3):
                    tr, tc = random.randint(0, GRID_SIZE - 1), random.randint(
                        0, GRID_SIZE - 1
                    )
                    if (tr, tc) not in cells_to_destroy:
                        add_set.add((tr, tc))
        if add_set:
            cells_to_destroy.update(add_set)
            loop_flag = True


def find_and_destroy_pure_matches():
    global current_score, max_combo
    cells_to_destroy, items_to_create = analyze_matches_and_setup_items()
    if not cells_to_destroy:
        return False

    trigger_item_explosions(cells_to_destroy)

    current_score += len(cells_to_destroy) * 100 * (combo_count + 1)
    if combo_count > max_combo:
        max_combo = combo_count
    if match_sound:
        match_sound.play()

    for r, c in cells_to_destroy:
        grid[r][c].color = EMPTY_COLOR
        grid[r][c].item_type = "NORMAL"

    for it in items_to_create:
        r, c = it["r"], it["c"]
        grid[r][c].color = it["color"]
        grid[r][c].item_type = it["type"]
    return True

def execute_rainbow_swap(r1, c1, r2, c2):
    global current_score, game_state
    if grid[r1][c1].item_type == "RAINBOW":
        rainbow_r, rainbow_c = r1, c1
        target_r, target_c = r2, c2
    else:
        rainbow_r, rainbow_c = r2, c2
        target_r, target_c = r1, c1

    target_color = grid[target_r][target_c].color
    target_type = grid[target_r][target_c].item_type

    grid[rainbow_r][rainbow_c].color = EMPTY_COLOR
    grid[rainbow_r][rainbow_c].item_type = "NORMAL"
    if target_type == "NORMAL":
        print(f"🌈 전역 제거 발동! 모든 동색 보석 소멸!")
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if grid[r][c].color == target_color:
                    grid[r][c].color = EMPTY_COLOR
                    current_score += 150
    else:
        print(f"🚀 복제 합성 콤보! 모든 동색 보석이 [{target_type}] 속성 복제!")
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if grid[r][c].color == target_color:
                    grid[r][c].item_type = target_type
                    blast_cells = set()
                    for r in range(GRID_SIZE):
                        for c in range(GRID_SIZE):
                            if (
                                grid[r][c].color == target_color
                                or grid[r][c].item_type != "NORMAL"
                            ):
                                blast_cells.add((r, c))

                    trigger_item_explosions(blast_cells)
                    for r, c in blast_cells:
                        grid[r][c].color = EMPTY_COLOR
                        grid[r][c].item_type = "NORMAL"
                        current_score += len(blast_cells) * 200
                        apply_gravity_and_setup_fall()
                        game_state = "FALLING"

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


grid = generate_valid_grid()
drag_start = None
game_state = "PLAY"
combo_count = 0

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
                            if grid[r1][c1].item_type == "RAINBOW" or grid[r2][c2].item_type == "RAINBOW":
                                execute_rainbow_swap(r1, c1, r2, c2)
                            else:
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

            # 💡 [시각 오버레이 그래픽 갱신]
            if gem.item_type == "BOMB":
                pygame.draw.rect(screen, (255, 255, 255), (rect_x + 10, rect_y + 10, rect_w - 20, rect_h - 20), width=3, border_radius=4)
            elif gem.item_type == "H_MISSILE":
                # 가로 미사일 표식 (-)
                pygame.draw.line(screen, (255, 255, 255), (rect_x + 6, rect_y + rect_h//2), (rect_x + rect_w - 6, rect_y + rect_h//2), width=4)
            elif gem.item_type == "V_MISSILE":
                # 세로 미사일 표식 (|)
                pygame.draw.line(screen, (255, 255, 255), (rect_x + rect_w//2, rect_y + 6), (rect_x + rect_w//2, rect_y + rect_h - 6), width=4)
            elif gem.item_type == "PROPELLER":
                pygame.draw.circle(screen, (255, 255, 255), (rect_x + rect_w//2, rect_y + rect_h//2), 8, width=3)
            elif gem.item_type == "RAINBOW":
                pygame.draw.circle(screen, (200, 200, 200), (rect_x + rect_w//2, rect_y + rect_h//2), 14, width=4)
                pygame.draw.circle(screen, (255, 255, 255), (rect_x + rect_w//2, rect_y + rect_h//2), 6)
            
            if drag_start == (r, c) and game_state == "PLAY": 
                pygame.draw.rect(screen, (255, 255, 255), (rect_x - 2, rect_y - 2, rect_w + 4, rect_h + 4), width=3, border_radius=14)

    pygame.display.flip()

pygame.quit()
sys.exit()
