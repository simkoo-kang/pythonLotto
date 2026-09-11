import sys
import os
import random
import pygame

# 윈도우 한글 환경을 위한 입출력 보정
import io
if sys.stdout:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

WIDTH, HEIGHT = 480, 560
SCORE_PANEL_HEIGHT = 80
GRID_WIDTH, GRID_HEIGHT = 480, 480
GRID_SIZE = 8
CELL_SIZE = GRID_WIDTH // GRID_SIZE
SWAP_SPEED = 12

FALL_SPEED = 5

COLORS = [
    (235, 77, 75),   # 루비 (레드)
    (106, 176, 76),  # 에메랄드 (그린)
    (29, 209, 161),  # 사파이어 (민트 블루)
    (241, 196, 15),  # 토파즈 (옐로우)
    (155, 89, 182),  # 아메지스트 (퍼플)
]
EMPTY_COLOR = (30, 30, 30)

pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🚀 스와이프 퍼즐 게임 🚀")
clock = pygame.time.Clock()

match_sound = None
try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sound_path = os.path.join(current_dir, "pop.wav")
    if os.path.exists(sound_path):
        match_sound = pygame.mixer.Sound(sound_path)
    bgm_path = os.path.join(current_dir, "bgm.mp3")
    if os.path.exists(bgm_path):
        pygame.mixer.music.load(bgm_path)
        pygame.mixer.music.set_volume(0.4)
        pygame.mixer.music.play(-1)
except Exception:
    pass

current_score = 0

class Gem:
    def __init__(self, color, r, c):
        self.color = color
        self.r = r
        self.c = c
        self.x = c * CELL_SIZE
        self.target_x = self.x
        self.y = r * CELL_SIZE + SCORE_PANEL_HEIGHT
        self.target_y = self.y
        self.item_type = "NORMAL"

    def update(self):
        moved = False
        if self.x < self.target_x:
            self.x = min(self.x + SWAP_SPEED, self.target_x)
            moved = True
        elif self.x > self.target_x:
            self.x = max(self.x - SWAP_SPEED, self.target_x)
            moved = True
        if self.y < self.target_y:
            self.y = min(self.y + FALL_SPEED, self.target_y)
            moved = True
        elif self.y > self.target_y:
            self.y = max(self.y - FALL_SPEED, self.target_y)
            moved = True
        return moved

def check_initial_matches(g):
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE - 2):
            if g[r][c] == g[r][c+1] == g[r][c+2]: return True
    for r in range(GRID_SIZE - 2):
        for c in range(GRID_SIZE):
            if g[r][c] == g[r+1][c] == g[r+2][c]: return True
    return False

def generate_grid():
    # 첫 턴 무한루프 방지를 위해 최대 시도 횟수를 제한하여 안전성 확보
    for _ in range(100):
        temp_colors = [[random.choice(COLORS) for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        if not check_initial_matches(temp_colors):
            return [[Gem(temp_colors[r][c], r, c) for c in range(GRID_SIZE)] for r in range(GRID_SIZE)]
    # 예외 상황용 기본 격자 보급
    return [[Gem(random.choice(COLORS), r, c) for c in range(GRID_SIZE)] for r in range(GRID_SIZE)]

def analyze_matches(grid_data):
    h_lines, v_lines, squares = [], [], []
    for r in range(GRID_SIZE):
        c = 0
        while c < GRID_SIZE - 2:
            if grid_data[r][c].color != EMPTY_COLOR:
                l = 1
                while c + l < GRID_SIZE and grid_data[r][c].color == grid_data[r][c+l].color: l += 1
                if l >= 3:
                    h_lines.append({"cells": [(r, c+i) for i in range(l)], "len": l})
                    c += l; continue
            c += 1
    for c in range(GRID_SIZE):
        r = 0
        while r < GRID_SIZE - 2:
            if grid_data[r][c].color != EMPTY_COLOR:
                l = 1
                while r + l < GRID_SIZE and grid_data[r][c].color == grid_data[r+l][c].color: l += 1
                if l >= 3:
                    v_lines.append({"cells": [(r+i, c) for i in range(l)], "len": l})
                    r += l; continue
            r += 1
    for r in range(GRID_SIZE - 1):
        for c in range(GRID_SIZE - 1):
            color = grid_data[r][c].color
            if color != EMPTY_COLOR and grid_data[r][c+1].color == color and grid_data[r+1][c].color == color and grid_data[r+1][c+1].color == color:
                squares.append([(r, c), (r, c+1), (r+1, c), (r+1, c+1)])
    
    to_destroy, items = set(), []
    used_h, used_v = set(), set()
    for idx, h in enumerate(h_lines):
        if h["len"] >= 5 and idx not in used_h:
            used_h.add(idx); to_destroy.update(h["cells"])
            br, bc = h["cells"][h["len"]//2]
            items.append({"r": br, "c": bc, "color": (255,255,255), "type": "RAINBOW"})
    for idx, v in enumerate(v_lines):
        if v["len"] >= 5 and idx not in used_v:
            used_v.add(idx); to_destroy.update(v["cells"])
            br, bc = v["cells"][v["len"]//2]
            items.append({"r": br, "c": bc, "color": (255,255,255), "type": "RAINBOW"})
    
    for hi, h in enumerate(h_lines):
        if hi in used_h: continue
        for vi, v in enumerate(v_lines):
            if vi in used_v: continue
            inter = set(h["cells"]).intersection(set(v["cells"]))
            if inter:
                used_h.add(hi); used_v.add(vi)
                to_destroy.update(h["cells"]); to_destroy.update(v["cells"])
                # 🛠️ 언팩 에러 전면 보정: 리스트의 첫 튜플 데이터를 추출하도록 변경
                inter_list = list(inter)
                if inter_list:
                    cr, cc = inter_list[0]
                    items.append({"r": cr, "c": cc, "color": grid_data[cr][cc].color, "type": "BOMB"})
                
    for idx, h in enumerate(h_lines):
        if h["len"] == 4 and idx not in used_h:
            used_h.add(idx); to_destroy.update(h["cells"])
            br, bc = h["cells"][0]
            items.append({"r": br, "c": bc, "color": grid_data[br][bc].color, "type": "V_MISSILE"})
    for idx, v in enumerate(v_lines):
        if v["len"] == 4 and idx not in used_v:
            used_v.add(idx); to_destroy.update(v["cells"])
            br, bc = v["cells"][0]
            items.append({"r": br, "c": bc, "color": grid_data[br][bc].color, "type": "H_MISSILE"})
    for sq in squares:
        if not set(sq).intersection(to_destroy):
            to_destroy.update(sq); sr, sc = sq[0]
            items.append({"r": sr, "c": sc, "color": grid_data[sr][sc].color, "type": "PROPELLER"})
    for h in h_lines: to_destroy.update(h["cells"])
    for v in v_lines: to_destroy.update(v["cells"])
    return list(to_destroy), items

def trigger_item_effect(r, c, item_type, exploded_set):
    if (r, c) in exploded_set: return
    exploded_set.add((r, c))
    if item_type == "H_MISSILE":
        for i in range(GRID_SIZE): exploded_set.add((r, i))
    elif item_type == "V_MISSILE":
        for i in range(GRID_SIZE): exploded_set.add((i, c))
    elif item_type == "BOMB":
        for i in range(max(0, r - 2), min(GRID_SIZE, r + 3)):
            for j in range(max(0, c - 2), min(GRID_SIZE, c + 3)): exploded_set.add((i, j))
    elif item_type == "PROPELLER":
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            if 0 <= r + dr < GRID_SIZE and 0 <= c + dc < GRID_SIZE: exploded_set.add((r + dr, c + dc))

grid = generate_grid()
state = "READY"
mouse_down_pos = None
active_gem = None
swap_back_coords = None
destroyed = []
items = []

while True:
    screen.fill((20, 20, 20))
    pygame.draw.rect(screen, (40, 40, 40), (0, 0, WIDTH, SCORE_PANEL_HEIGHT))
    
    animating = False
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            if grid[r][c].update():
                animating = True
    
    if state == "SWAPPING" and not animating:
        destroyed, items = analyze_matches(grid)
        if destroyed:
            if match_sound: match_sound.play()
            state = "CLEARING"
        else:
            r1, c1, r2, c2 = swap_back_coords
            grid[r1][c1], grid[r2][c2] = grid[r2][c2], grid[r1][c1]
            grid[r1][c1].r, grid[r1][c1].c, grid[r1][c1].target_x, grid[r1][c1].target_y = r1, c1, c1*CELL_SIZE, r1*CELL_SIZE+SCORE_PANEL_HEIGHT
            grid[r2][c2].r, grid[r2][c2].c, grid[r2][c2].target_x, grid[r2][c2].target_y = r2, c2, c2*CELL_SIZE, r2*CELL_SIZE+SCORE_PANEL_HEIGHT
            state = "READY"
            
    elif state == "CLEARING" and not animating:
        exploded = set(destroyed)
        for r, c in destroyed:
            if grid[r][c].item_type != "NORMAL":
                trigger_item_effect(r, c, grid[r][c].item_type, exploded)
                
        for r, c in exploded:
            grid[r][c].color = EMPTY_COLOR
            grid[r][c].item_type = "NORMAL"
            current_score += 10
            
        for item in items:
            grid[item["r"]][item["c"]].color = item["color"]
            grid[item["r"]][item["c"]].item_type = item["type"]
        state = "FALLING"
        
    elif state == "FALLING" and not animating:
        for c in range(GRID_SIZE):
            for r in range(GRID_SIZE - 1, -1, -1):
                if grid[r][c].color == EMPTY_COLOR:
                    for k in range(r - 1, -1, -1):
                        if grid[k][c].color != EMPTY_COLOR:
                            grid[r][c].color, grid[k][c].color = grid[k][c].color, EMPTY_COLOR
                            grid[r][c].item_type, grid[k][c].item_type = grid[k][c].item_type, "NORMAL"
                            break
            for r in range(GRID_SIZE):
                if grid[r][c].color == EMPTY_COLOR:
                    grid[r][c].color = random.choice(COLORS)
                    grid[r][c].item_type = "NORMAL"
                    grid[r][c].y = SCORE_PANEL_HEIGHT - CELL_SIZE
                grid[r][c].r, grid[r][c].c = r, c
                grid[r][c].target_x = c * CELL_SIZE
                grid[r][c].target_y = r * CELL_SIZE + SCORE_PANEL_HEIGHT
        destroyed, items = analyze_matches(grid)
        if destroyed:
            state = "CLEARING"
        else:
            state = "READY"

    # === [이벤트 처리 루프 시작] ===
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
        elif event.type == pygame.MOUSEBUTTONDOWN and state == "READY":
            mx, my = pygame.mouse.get_pos()
            if my > SCORE_PANEL_HEIGHT:
                c = mx // CELL_SIZE
                r = (my - SCORE_PANEL_HEIGHT) // CELL_SIZE
                if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE:
                    mouse_down_pos = (mx, my)
                    active_gem = (r, c)
                    
        elif event.type == pygame.MOUSEMOTION and mouse_down_pos and state == "READY":
            mx, my = pygame.mouse.get_pos()
            start_x, start_y = mouse_down_pos
            dx = mx - start_x
            dy = my - start_y
            
            if abs(dx) > 18 or abs(dy) > 18:
                r1, c1 = active_gem
                dr, dc = 0, 0
                if abs(dx) > abs(dy):
                    dc = 1 if dx > 0 else -1
                else:
                    dr = 1 if dy > 0 else -1
                
                # 💡 [정밀 수정] r2 계산과 스왑 처리는 if/else 분기문 '밖'으로 수직 정렬되어야 합니다.
                r2, c2 = r1 + dr, c1 + dc
                if 0 <= r2 < GRID_SIZE and 0 <= c2 < GRID_SIZE:
                    grid[r1][c1], grid[r2][c2] = grid[r2][c2], grid[r1][c1]
                    grid[r1][c1].r, grid[r1][c1].c, grid[r1][c1].target_x, grid[r1][c1].target_y = r1, c1, c1*CELL_SIZE, r1*CELL_SIZE+SCORE_PANEL_HEIGHT
                    grid[r2][c2].r, grid[r2][c2].c, grid[r2][c2].target_x, grid[r2][c2].target_y = r2, c2, c2*CELL_SIZE, r2*CELL_SIZE+SCORE_PANEL_HEIGHT
                    swap_back_coords = (r1, c1, r2, c2)
                    state = "SWAPPING"
                
                # 드래그 처리가 한 번 끝났으므로 즉시 초기화 (들여쓰기 위치 주목)
                mouse_down_pos = None
                active_gem = None
                
        elif event.type == pygame.MOUSEBUTTONUP:
            mouse_down_pos = None
            active_gem = None

    # 💡 [정밀 수정] 보석을 화면에 그리는 루프는 event 루프 '바깥'인 이곳에 수직 정렬되어 배치되어야 실시간으로 보입니다.
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            gem = grid[r][c]
            rect = pygame.Rect(gem.x + 3, gem.y + 3, CELL_SIZE - 6, CELL_SIZE - 6)
            pygame.draw.rect(screen, gem.color, rect, border_radius=6)
            if gem.item_type == "H_MISSILE":
                pygame.draw.line(screen, (255,255,255), (gem.x+10, gem.y+CELL_SIZE//2), (gem.x+CELL_SIZE-10, gem.y+CELL_SIZE//2), 4)
            elif gem.item_type == "V_MISSILE":
                pygame.draw.line(screen, (255,255,255), (gem.x+CELL_SIZE//2, gem.y+10), (gem.x+CELL_SIZE//2, gem.y+CELL_SIZE-10), 4)
            elif gem.item_type == "BOMB":
                pygame.draw.rect(screen, (0,0,0), (gem.x+12, gem.y+12, CELL_SIZE-24, CELL_SIZE-24), 3)
            elif gem.item_type == "PROPELLER":
                pygame.draw.circle(screen, (255,255,255), (gem.x+CELL_SIZE//2, gem.y+CELL_SIZE//2), 6)

    pygame.display.flip()
    clock.tick(60)
