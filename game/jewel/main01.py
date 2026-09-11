"""
메인 실행 파일 및 게임 관리 루프
1. 특수 아이템 드레그 안된다.
2. 초기 화면에 플로펠러 구조가 맞추어져 있다.
"""

import sys
import os
import pygame
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
    screen.blit(
        game_font.render(f"SCORE : {current_score}", True, (255, 255, 255)), (20, 22)
    )

    animating = board.update_cells()

    if state == "SWAPPING" and not animating:
        destroyed, items = board.analyze_matches()
        
        # 💡 [버그 완벽 수정] 스왑이 끝난 직후, 교체된 두 칸 중에 특수 아이템이 하나라도 있다면 매칭 여부 불문 즉시 폭발 처리
        r1, c1, r2, c2 = swap_back_coords
        if board.grid[r1][c1].item_type != "NORMAL" or board.grid[r2][c2].item_type != "NORMAL":
            # 만약 둘 중 하나라도 특수 템이면 무조건 destroyed에 수동 추가하여 CLEARING 상태로 강제 전송
            if (r1, c1) not in destroyed: destroyed.append((r1, c1))
            if (r2, c2) not in destroyed: destroyed.append((r2, c2))
            if match_sound: match_sound.play()
            state = "CLEARING"
        elif destroyed:
            if match_sound: match_sound.play()
            state = "CLEARING"
        else:
            # 특수 아이템도 없고, 일반 3매칭도 없다면 원상 복구
            board.grid[r1][c1], board.grid[r2][c2] = board.grid[r2][c2], board.grid[r1][c1]
            board.grid[r1][c1].r, board.grid[r1][c1].c, board.grid[r1][c1].target_x, board.grid[r1][c1].target_y = r1, c1, c1*CELL_SIZE, r1*CELL_SIZE+SCORE_PANEL_HEIGHT
            board.grid[r2][c2].r, board.grid[r2][c2].c, board.grid[r2][c2].target_x, board.grid[r2][c2].target_y = r2, c2, c2*CELL_SIZE, r2*CELL_SIZE+SCORE_PANEL_HEIGHT
            state = "READY"

    elif state == "CLEARING" and not animating:
        exploded = set(destroyed)
        for r, c in list(exploded):
            if board.grid[r][c].item_type != "NORMAL":
                board.trigger_item_effect(
                    r, c, board.grid[r][c].item_type, rainbow_color_target, exploded
                )
        for r, c in exploded:
            board.grid[r][c].color, board.grid[r][c].item_type, current_score = (
                EMPTY_COLOR,
                "NORMAL",
                current_score + 10,
            )
        for item in items:
            (
                board.grid[item["r"]][item["c"]].color,
                board.grid[item["r"]][item["c"]].item_type,
            ) = (item["color"], item["type"])
        destroyed, items, state = [], [], "FALLING"
    elif state == "FALLING" and not animating:
        board.apply_fall()
        destroyed, items = board.analyze_matches()
        state = "CLEARING" if destroyed else "READY"

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == pygame.MOUSEBUTTONDOWN and state == "READY":
            mx, my = pygame.mouse.get_pos()
            if my > SCORE_PANEL_HEIGHT:
                c, r = mx // CELL_SIZE, (my - SCORE_PANEL_HEIGHT) // CELL_SIZE
                if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE:
                    # 💡 [버그 완벽 수정] 특수 아이템이라도 클릭 즉시 터뜨리지 않고, 드래그(스와이프) 시작점으로 등록합니다.
                    mouse_down_pos, active_gem = (mx, my), (r, c)

        elif event.type == pygame.MOUSEMOTION and mouse_down_pos and state == "READY":
            mx, my = pygame.mouse.get_pos()
            start_x, start_y = mouse_down_pos
            dx, dy = mx - start_x, my - start_y

            if abs(dx) > 18 or abs(dy) > 18:
                r1, c1 = active_gem
                dr, dc = (
                    (1 if dy > 0 else -1, 0)
                    if abs(dy) > abs(dx)
                    else (0, 1 if dx > 0 else -1)
                )
                r2, c2 = r1 + dr, c1 + dc

                if 0 <= r2 < GRID_SIZE and 0 <= c2 < GRID_SIZE:
                    # 💡 [버그 완벽 수정] 스와이프 드래그 시에는 즉시 터뜨리지 않고 자리를 교체하는 SWAPPING 상태로 진입시킵니다.
                    if board.grid[r1][c1].item_type == "RAINBOW":
                        rainbow_color_target = board.grid[r2][c2].color
                    elif board.grid[r2][c2].item_type == "RAINBOW":
                        rainbow_color_target = board.grid[r1][c1].color
                    else:
                        rainbow_color_target = (255, 255, 255)

                    board.grid[r1][c1], board.grid[r2][c2] = (
                        board.grid[r2][c2],
                        board.grid[r1][c1],
                    )
                    (
                        board.grid[r1][c1].r,
                        board.grid[r1][c1].c,
                        board.grid[r1][c1].target_x,
                        board.grid[r1][c1].target_y,
                    ) = (r1, c1, c1 * CELL_SIZE, r1 * CELL_SIZE + SCORE_PANEL_HEIGHT)
                    (
                        board.grid[r2][c2].r,
                        board.grid[r2][c2].c,
                        board.grid[r2][c2].target_x,
                        board.grid[r2][c2].target_y,
                    ) = (r2, c2, c2 * CELL_SIZE, r2 * CELL_SIZE + SCORE_PANEL_HEIGHT)
                    swap_back_coords, state = (r1, c1, r2, c2), "SWAPPING"
                mouse_down_pos, active_gem = None, None

        elif event.type == pygame.MOUSEBUTTONUP:
            mouse_down_pos, active_gem = None, None

    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            board.grid[r][c].draw(screen)

    pygame.display.flip()
    clock.tick(60)
