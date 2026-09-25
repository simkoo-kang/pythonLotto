"""
메인 실행 파일 및 게임 관리 루프
1. 특수 아이템 드레그 안된다.
2. 초기 화면에 플로펠러 구조가 맞추어져 있다.
"""

import sys
import os
import pygame
from game.jewel.cell import create_cell_by_type
from game.jewel.settings import (
    WIDTH,
    HEIGHT,
    SCORE_PANEL_HEIGHT,
    GRID_SIZE,
    CELL_SIZE,
    EMPTY_COLOR,
)
from game.jewel.board import Board

import io
from game.jewel.settings import BGM, POP_WAV
from util.str_util import Str

if sys.stdout:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🚀 객체지향 퍼즐 게임 🚀")
clock = pygame.time.Clock()
game_font = pygame.font.SysFont("malgungothic", 28, bold=True)

match_sound = None
try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if os.path.exists(os.path.join(current_dir, POP_WAV)):
        match_sound = pygame.mixer.Sound(os.path.join(current_dir, POP_WAV))
    if os.path.exists(os.path.join(current_dir, BGM)):
        pygame.mixer.music.load(os.path.join(current_dir, BGM))
        pygame.mixer.music.set_volume(0.4)
        pygame.mixer.music.play(-1)
except Exception:
    pass

board = Board()

current_score = 0
current_combo = 0 

state, mouse_down_pos, active_gem, swap_back_coords, rainbow_color_target = (
    "READY",
    None,
    None,
    None,
    (255, 255, 255),
)
destroyed, items = [], []

while True:
    screen.fill((20, 20, 20))
    pygame.draw.rect(screen, (40, 40, 40), (0, 0, WIDTH, SCORE_PANEL_HEIGHT))

    # 💡 [점수판 UI 강화] 현재 콤보 수치도 화면 상단에 실시간으로 선명하게 Blit 출력
    score_text = game_font.render(f"SCORE : {Str.number_format(current_score)}", True, (255, 255, 255))
    screen.blit(score_text, (20, 22))
    
    if current_combo > 0:
        combo_text = game_font.render(f"{current_combo} COMBO!", True, (255, 235, 50))
        screen.blit(combo_text, (300, 22))
    
    animating = board.update_cells()

    if state == "SWAPPING" and not animating:
        destroyed, items = board.analyze_matches()
        
        # 💡 [버그 완벽 수정] 드래그가 끝난 직후, 교체된 두 칸 중에 특수 아이템이 하나라도 있었다면 매칭 여부 불문 폭발 상태로 강제 진입시킵니다.
        r1, c1, r2, c2 = swap_back_coords
        if board.grid[r1][c1].item_type != "NORMAL" or board.grid[r2][c2].item_type != "NORMAL":
            if (r1, c1) not in destroyed: destroyed.append((r1, c1))
            if (r2, c2) not in destroyed: destroyed.append((r2, c2))
            if match_sound: match_sound.play()
            current_combo = 1
            state = "CLEARING"
        elif destroyed:
            if match_sound: match_sound.play()
            current_combo = 1
            state = "CLEARING"
        else:
            # 특수 템도 없고 매칭도 없다면 원상 복구
            board.grid[r1][c1], board.grid[r2][c2] = board.grid[r2][c2], board.grid[r1][c1]
            board.grid[r1][c1].r, board.grid[r1][c1].c, board.grid[r1][c1].target_x, board.grid[r1][c1].target_y = r1, c1, c1*CELL_SIZE, r1*CELL_SIZE+SCORE_PANEL_HEIGHT
            board.grid[r2][c2].r, board.grid[r2][c2].c, board.grid[r2][c2].target_x, board.grid[r2][c2].target_y = r2, c2, c2*CELL_SIZE, r2*CELL_SIZE+SCORE_PANEL_HEIGHT
            state = "READY"
            
    elif state == "CLEARING" and not animating:
        exploded = set(destroyed)
        for r, c in list(exploded):
            if board.grid[r][c].item_type != "NORMAL": 
                board.trigger_item_effect(r, c, board.grid[r][c].item_type, rainbow_color_target, exploded, rainbow_item_target)
        
        # 💡 [콤보 보너스 공식 적용] 기본 10점에 (현재 콤보 수 x 5점) 가산점 부여! 
        # 예: 1콤보는 개당 15점, 2연속 콤보는 개당 20점, 3연속 콤보는 개당 25점씩 누적 폭발!
        combo_bonus = current_combo * 5
        for r, c in exploded: 
            board.grid[r][c].color, board.grid[r][c].item_type = EMPTY_COLOR, "NORMAL"
            current_score += (10 + combo_bonus)
            
        for item in items: 
            board.grid[item["r"]][item["c"]] = create_cell_by_type(item["type"], item["color"], item["r"], item["c"])
            
        destroyed, items, state = [], [], "FALLING"
        
    elif state == "FALLING" and not animating:
        board.apply_fall()
        # 보석들이 다 떨어져서 정착한 직후, 하늘에서 내린 보석들로 인해 '자동 연쇄 매칭'이 생겼는지 재검사
        destroyed, items = board.analyze_matches()
        if destroyed:
            current_combo += 1  # 💡 [버그 완벽 수정] 공백이 채워지면서 자동으로 또 터졌으므로 콤보 카운트 1 증가!
            if match_sound: match_sound.play()
            state = "CLEARING"
        else:
            current_combo = 0  # 💡 더 이상 터질 게 없다면 연속 콤보 기록을 0으로 깨끗하게 초기화
            state = "READY"

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
        elif event.type == pygame.MOUSEBUTTONDOWN and state == "READY":
            mx, my = pygame.mouse.get_pos()
            if my > SCORE_PANEL_HEIGHT:
                c, r = mx // CELL_SIZE, (my - SCORE_PANEL_HEIGHT) // CELL_SIZE
                if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE:
                    # 💡 [버그 완벽 수정 1] 누르는 순간에는 특수 템이든 일반 보석이든 절대로 먼저 터뜨리지 않고, 
                    # 사용자가 클릭을 할지 드래그를 할지 알 수 없으므로 우선 시작 타이밍 좌표만 캡처 보관합니다!
                    mouse_down_pos = (mx, my)
                    active_gem = (r, c)
                        
        elif event.type == pygame.MOUSEMOTION and mouse_down_pos and state == "READY":
            mx, my = pygame.mouse.get_pos()
            start_x, start_y = mouse_down_pos
            dx, dy = mx - start_x, my - start_y
            
            # 마우스를 누른 채 사방 격자로 18픽셀 이상 확실하게 밀었을 때만 '드래그 스왑' 시스템 가동
            if abs(dx) > 18 or abs(dy) > 18:
                r1, c1 = active_gem
                dr, dc = (1 if dy > 0 else -1, 0) if abs(dy) > abs(dx) else (0, 1 if dx > 0 else -1)
                r2, c2 = r1 + dr, c1 + dc
                
                if 0 <= r2 < GRID_SIZE and 0 <= c2 < GRID_SIZE:
                    # 레인보우와 특수 템 간의 결합 교체 캡처 감지기
                    is_rainbow_swap = (board.grid[r1][c1].item_type == "RAINBOW" or board.grid[r2][c2].item_type == "RAINBOW")
                    
                    if is_rainbow_swap:
                        if board.grid[r1][c1].item_type == "RAINBOW":
                            rainbow_color_target = board.grid[r2][c2].color
                            rainbow_item_target = board.grid[r2][c2].item_type
                        else:
                            rainbow_color_target = board.grid[r1][c1].color
                            rainbow_item_target = board.grid[r1][c1].item_type
                        
                        # 레인보우와 다른 칸이 드래그 교체되면 자리를 바꾼 뒤 즉시 폭발 상태로 전송
                        board.grid[r1][c1], board.grid[r2][c2] = board.grid[r2][c2], board.grid[r1][c1]
                        board.grid[r1][c1].r, board.grid[r1][c1].c, board.grid[r1][c1].target_x, board.grid[r1][c1].target_y = r1, c1, c1*CELL_SIZE, r1*CELL_SIZE+SCORE_PANEL_HEIGHT
                        board.grid[r2][c2].r, board.grid[r2][c2].c, board.grid[r2][c2].target_x, board.grid[r2][c2].target_y = r2, c2, c2*CELL_SIZE, r2*CELL_SIZE+SCORE_PANEL_HEIGHT
                        destroyed = [(r1, c1), (r2, c2)]
                        state = "CLEARING"
                    else:
                        # 일반 보석 및 기타 일반 특수 템 사방 드래그 교체 처리
                        rainbow_color_target = (255, 255, 255)
                        rainbow_item_target = "NORMAL"
                        board.grid[r1][c1], board.grid[r2][c2] = board.grid[r2][c2], board.grid[r1][c1]
                        board.grid[r1][c1].r, board.grid[r1][c1].c, board.grid[r1][c1].target_x, board.grid[r1][c1].target_y = r1, c1, c1*CELL_SIZE, r1*CELL_SIZE+SCORE_PANEL_HEIGHT
                        board.grid[r2][c2].r, board.grid[r2][c2].c, board.grid[r2][c2].target_x, board.grid[r2][c2].target_y = r2, c2, c2*CELL_SIZE, r2*CELL_SIZE+SCORE_PANEL_HEIGHT
                        swap_back_coords, state = (r1, c1, r2, c2), "SWAPPING"
                        
                # 드래그 센서 처리가 완벽히 끝났으므로 예약 마우스 좌표 해제
                mouse_down_pos, active_gem = None, None
                
        elif event.type == pygame.MOUSEBUTTONUP and state == "READY":
            # 💡 [버그 완벽 수정 2] 마우스를 전혀 밀지 않고 제자리에서 '톡 클릭했다가 놓았을 때만' 단독 기폭 장치 가동!
            if mouse_down_pos and active_gem:
                r, c = active_gem
                if board.grid[r][c].item_type != "NORMAL":
                    rainbow_color_target = (255, 255, 255)
                    rainbow_item_target = "NORMAL"
                    destroyed = [(r, c)]
                    state = "CLEARING"
            mouse_down_pos, active_gem = None, None

    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            board.grid[r][c].draw(screen)

    pygame.display.flip()
    clock.tick(60)
