import sys
import os
import random
import pygame
import io
from game.jewel.settings import WIDTH, HEIGHT, SCORE_PANEL_HEIGHT, GRID_SIZE, CELL_SIZE, EMPTY_COLOR, COLORS
from game.jewel.board import Board
from game.jewel.cell import create_cell_by_type
from game.jewel.settings import BGM, POP_WAV
from util.str_util import Str

if sys.stdout: sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("✨ 화려한 파티클 보석 퍼즐 ✨")
clock = pygame.time.Clock()
game_font = pygame.font.SysFont("malgungothic", 28, bold=True)

match_sound = None
try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if os.path.exists(os.path.join(current_dir, POP_WAV)): match_sound = pygame.mixer.Sound(os.path.join(current_dir, POP_WAV))
    if os.path.exists(os.path.join(current_dir, BGM)):
        pygame.mixer.music.load(os.path.join(current_dir, BGM))
        pygame.mixer.music.set_volume(0.4); pygame.mixer.music.play(-1)
except Exception: pass

# 💡 [파티클 클래스 설계] 파르르 튀는 작은 불꽃 알갱이 객체
class Particle:
    def __init__(self, x, y, color):
        self.x, self.y = x, y
        self.color = color
        # 사방으로 불꽃이 튀도록 무작위 속도 부여
        self.vx = random.uniform(-4, 4)
        self.vy = random.uniform(-6, 2)  # 위쪽으로 더 잘 튕기게 배치
        self.gravity = 0.25               # 아래로 떨어지는 중력 적용
        self.radius = random.randint(3, 6) # 알갱이 크기
        self.alpha = 255                  # 투명도

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity           # 중력 더하기
        self.alpha = max(0, self.alpha - 8) # 서서히 페이드아웃
        return self.alpha > 0

    def draw(self, surface):
        if self.alpha <= 0: return
        # 투명도를 지원하는 파티클 서피스 드로잉
        p_surf = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        r, g, b = self.color
        pygame.draw.circle(p_surf, (r, g, b, self.alpha), (self.radius, self.radius), self.radius)
        surface.blit(p_surf, (self.x - self.radius, self.y - self.radius))

board = Board()
current_score = 0
current_combo = 0
state, mouse_down_pos, active_gem, swap_back_coords, rainbow_color_target = "READY", None, None, None, (255, 255, 255)
destroyed, items = [], []

# 💡 실시간 파티클 객체들을 담아둘 매니저 리스트
particles = []

while True:
    screen.fill((20, 20, 20))
    pygame.draw.rect(screen, (40, 40, 40), (0, 0, WIDTH, SCORE_PANEL_HEIGHT))
    screen.blit(game_font.render(f"SCORE : {Str.number_format(current_score)}", True, (255, 255, 255)), (20, 22))
    
    if current_combo > 0:
        screen.blit(game_font.render(f"{current_combo} COMBO!", True, (255, 235, 50)), (300, 22))
    
    animating = board.update_cells()
            
    if state == "SWAPPING" and not animating:
        destroyed, items = board.analyze_matches()
        if destroyed:
            if match_sound: match_sound.play()
            current_combo = 1
            state = "CLEARING"
        else:
            r1, c1, r2, c2 = swap_back_coords
            board.grid[r1][c1], board.grid[r2][c2] = board.grid[r2][c2], board.grid[r1][c1]
            board.grid[r1][c1].r, board.grid[r1][c1].c, board.grid[r1][c1].target_x, board.grid[r1][c1].target_y = r1, c1, c1*CELL_SIZE, r1*CELL_SIZE+SCORE_PANEL_HEIGHT
            board.grid[r2][c2].r, board.grid[r2][c2].c, board.grid[r2][c2].target_x, board.grid[r2][c2].target_y = r2, c2, c2*CELL_SIZE, r2*CELL_SIZE+SCORE_PANEL_HEIGHT
            state = "READY"
            
    elif state == "CLEARING" and not animating:
        exploded = set(destroyed)
        for r, c in list(exploded):
            if board.grid[r][c].item_type != "NORMAL":
                # main.py 내 CLEARING 상태 내부의 trigger_item_effect 호출 코드 점검 및 수정
                board.trigger_item_effect(r, c, board.grid[r][c].item_type, rainbow_color_target, exploded, rainbow_item_target)
        
        # 💡 [파티클 스폰 엔진] 보석이 터지는 위치 좌표에 알갱이들을 무작위 폭풍 주입!
        for r, c in exploded:
            p_color = board.grid[r][c].color
            if p_color != EMPTY_COLOR and p_color in COLORS:
                # 보석 한 칸당 8개의 불꽃 파편 파르르 스폰
                center_x = c * CELL_SIZE + CELL_SIZE // 2
                center_y = r * CELL_SIZE + SCORE_PANEL_HEIGHT + CELL_SIZE // 2
                for _ in range(8):
                    particles.append(Particle(center_x, center_y, p_color))

        combo_bonus = current_combo * 5
        for r, c in exploded: 
            board.grid[r][c].color, board.grid[r][c].item_type = EMPTY_COLOR, "NORMAL"
            current_score += (10 + combo_bonus)
            
        for item in items: board.grid[item["r"]][item["c"]] = create_cell_by_type(item["type"], item["color"], item["r"], item["c"])
        destroyed, items, state = [], [], "FALLING"
        
    elif state == "FALLING" and not animating:
        board.apply_fall()
        destroyed, items = board.analyze_matches()
        if destroyed:
            current_combo += 1
            if match_sound: match_sound.play()
            state = "CLEARING"
        else:
            current_combo = 0
            state = "READY"

    for event in pygame.event.get():
        if event.type == pygame.QUIT: pygame.quit(); sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN and state == "READY":
            mx, my = pygame.mouse.get_pos()
            if my > SCORE_PANEL_HEIGHT:
                c, r = mx // CELL_SIZE, (my - SCORE_PANEL_HEIGHT) // CELL_SIZE
                if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE: mouse_down_pos, active_gem = (mx, my), (r, c)

        elif event.type == pygame.MOUSEMOTION and mouse_down_pos and state == "READY":
            mx, my = pygame.mouse.get_pos()
            start_x, start_y = mouse_down_pos
            dx, dy = mx - start_x, my - start_y
            
            # 마우스를 누른 채 사방 격자로 18픽셀 이상 확실하게 밀었을 때만 '드래그 스왑' 시작
            if abs(dx) > 18 or abs(dy) > 18:
                r1, c1 = active_gem
                dr, dc = (1 if dy > 0 else -1, 0) if abs(dy) > abs(dx) else (0, 1 if dx > 0 else -1)
                r2, c2 = r1 + dr, c1 + dc
                
                if 0 <= r2 < GRID_SIZE and 0 <= c2 < GRID_SIZE:
                    # 💡 [정밀 판정] 두 교체 대상 중 '레인보우'가 포함되어 있는지만 콕 집어 검사합니다.
                    has_rainbow = (board.grid[r1][c1].item_type == "RAINBOW" or board.grid[r2][c2].item_type == "RAINBOW")
                    
                    if has_rainbow:
                        # 레인보우와 교체되는 상대방 셀이 일반인지, 미사일/폭탄인지 고유 정보를 캡처
                        if board.grid[r1][c1].item_type == "RAINBOW":
                            rainbow_color_target = board.grid[r2][c2].color
                            rainbow_item_target = board.grid[r2][c2].item_type
                        else:
                            rainbow_color_target = board.grid[r1][c1].color
                            rainbow_item_target = board.grid[r1][c1].item_type
                        
                        # 레인보우 스왑은 장부 위치를 바꾼 직후, 색상 일치 여부 불문 즉시 강제 기폭 전송!
                        board.grid[r1][c1], board.grid[r2][c2] = board.grid[r2][c2], board.grid[r1][c1]
                        board.grid[r1][c1].r, board.grid[r1][c1].c, board.grid[r1][c1].target_x, board.grid[r1][c1].target_y = r1, c1, c1*CELL_SIZE, r1*CELL_SIZE+SCORE_PANEL_HEIGHT
                        board.grid[r2][c2].r, board.grid[r2][c2].c, board.grid[r2][c2].target_x, board.grid[r2][c2].target_y = r2, c2, c2*CELL_SIZE, r2*CELL_SIZE+SCORE_PANEL_HEIGHT
                        
                        destroyed = [(r1, c1), (r2, c2)]
                        current_combo = 1
                        state = "CLEARING"
                    else:
                        # 💡 [정밀 보정] 폭탄, 미사일, 프로펠러 및 일반 보석은 우선 자리가 부드럽게 바뀌는 SWAPPING 상태로 안전하게 보냅니다!
                        rainbow_color_target = (255, 255, 255)
                        rainbow_item_target = "NORMAL"
                        
                        board.grid[r1][c1], board.grid[r2][c2] = board.grid[r2][c2], board.grid[r1][c1]
                        board.grid[r1][c1].r, board.grid[r1][c1].c, board.grid[r1][c1].target_x, board.grid[r1][c1].target_y = r1, c1, c1*CELL_SIZE, r1*CELL_SIZE+SCORE_PANEL_HEIGHT
                        board.grid[r2][c2].r, board.grid[r2][c2].c, board.grid[r2][c2].target_x, board.grid[r2][c2].target_y = r2, c2, c2*CELL_SIZE, r2*CELL_SIZE+SCORE_PANEL_HEIGHT
                        
                        swap_back_coords, state = (r1, c1, r2, c2), "SWAPPING"
                        
                mouse_down_pos, active_gem = None, None

        elif event.type == pygame.MOUSEBUTTONUP and state == "READY":
            if mouse_down_pos and active_gem:
                r, c = active_gem
                if board.grid[r][c].item_type != "NORMAL":
                    rainbow_color_target, rainbow_item_target = (255, 255, 255), "NORMAL"
                    destroyed = [(r, c)]
                    state = "CLEARING"
            mouse_down_pos, active_gem = None, None

    # 보석 격자 드로잉
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE): board.grid[r][c].draw(screen)
        
    # 💡 [파티클 실시간 연산 및 렌더링 루프] 
    # 파편 무리가 매 프레임 업데이트되며 투명도가 다 깎인 파편은 리스트에서 자동 메모리 해제
    particles = [p for p in particles if p.update()]
    for p in particles:
        p.draw(screen)

    pygame.display.flip()
    clock.tick(60)
