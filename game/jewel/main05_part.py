import sys
import os
import random
import pygame
import io
from game.jewel.settings import (
    BGM,
    POP_WAV,
    WIDTH,
    HEIGHT,
    SCORE_PANEL_HEIGHT,
    GRID_SIZE,
    CELL_SIZE,
    EMPTY_COLOR,
    COLORS,
    MAX_MOVES,
    TARGET_SCORE,
)
from game.jewel.board import Board
from game.jewel.cell import Particle, create_cell_by_type
from util.str_util import Str

if sys.stdout:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🚀 프리미엄 보석 퍼즐 마스터 🚀")
clock = pygame.time.Clock()
game_font = pygame.font.SysFont("malgungothic", 24, bold=True)
result_font = pygame.font.SysFont("malgungothic", 56, bold=True)
sub_font = pygame.font.SysFont("malgungothic", 20, bold=True)


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
current_score, current_combo = 0, 0

left_moves = MAX_MOVES
game_result = None

state, mouse_down_pos, active_gem, swap_back_coords = "READY", None, None, None
rainbow_color_target, rainbow_item_target = (255, 255, 255), "NORMAL"
destroyed, items, particles = [], [], []


while True:

    screen.fill((20, 20, 20))
    pygame.draw.rect(screen, (40, 40, 40), (0, 0, WIDTH, SCORE_PANEL_HEIGHT))
    
    screen.blit(
        game_font.render(
            f"점수: {Str.number_format(current_score)} / {Str.number_format(TARGET_SCORE)}",
            True,
            (255, 255, 255),
        ),
        (15, 12),
    )
    screen.blit(
        game_font.render(
            f"남은 횟수: {left_moves}회",
            True,
            (255, 235, 50) if left_moves > 5 else (255, 50, 50),
        ),
        (15, 42),
    )
    
    if current_combo > 0:
        screen.blit(
            game_font.render(f"{current_combo} COMBO!", True, (50, 255, 255)), (420, 25)
        )

    # 💡 [실시간 클리어 조건 실시간 반영] 보석이 터지는 도중 점수가 도달하더라도 즉각 반영
    if game_result is None:
        if current_score >= TARGET_SCORE:
            game_result = "CLEAR"
        elif left_moves <= 0 and state == "READY":
            game_result = "GAMEOVER"

    # 💡 [종료 후 연출 및 재시작 액션 제어 블록]
    if game_result is not None:
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                board.grid[r][c].draw(screen)

        particles = [p for p in particles if p.update()]
        for p in particles:
            p.draw(screen)

        mask = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        mask.fill((0, 0, 0, 180))
        screen.blit(mask, (0, 0))

        msg = result_font.render(
            "STAGE CLEAR! 🌟" if game_result == "CLEAR" else "GAME OVER 💀",
            True,
            (50, 255, 100) if game_result == "CLEAR" else (255, 50, 50),
        )
        screen.blit(
            msg,
            (
                WIDTH // 2 - msg.get_width() // 2,
                HEIGHT // 2 - msg.get_height() // 2 - 20,
            ),
        )

        # 💡 [액션 추가] 유저가 다음 행동을 취할 수 있도록 재시작 안내 가이드 문구 출력
        sub_msg = sub_font.render(
            "다시 시작 [ R ], 종료 [ESC] 키를 누르세요", True, (240, 240, 240)
        )
        screen.blit(
            sub_msg,
            (
                WIDTH // 2 - sub_msg.get_width() // 2,
                HEIGHT // 2 - sub_msg.get_height() // 2 + 50,
            ),
        )

        # 💡 [키보드 액션 센서 가동]
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                if (
                    event.key == pygame.K_r
                ):  # R 키를 누르는 즉시 모든 장부를 초기화하고 새로 리셋 시작!
                    board = Board()
                    current_score, current_combo = 0, 0
                    left_moves = MAX_MOVES
                    game_result = None
                    state, mouse_down_pos, active_gem, swap_back_coords = (
                        "READY",
                        None,
                        None,
                        None,
                    )
                    destroyed, items, particles = [], [], []

                if (
                    event.key == pygame.K_q or event.key == pygame.K_ESCAPE
                ):  # Q, ESC 키를 누르는
                    pygame.quit()
                    sys.exit()

        pygame.display.flip()
        clock.tick(60)
        continue

    animating = board.update_cells()

    if state == "SWAPPING" and not animating:
        destroyed, items = board.analyze_matches()
        r1, c1, r2, c2 = swap_back_coords
        if (
            board.grid[r1][c1].item_type != "NORMAL"
            or board.grid[r2][c2].item_type != "NORMAL"
        ):
            if (r1, c1) not in destroyed:
                destroyed.append((r1, c1))
            if (r2, c2) not in destroyed:
                destroyed.append((r2, c2))
            if match_sound:
                match_sound.play()
            current_combo = 1
            state = "CLEARING"
        elif destroyed:
            if match_sound:
                match_sound.play()
            current_combo = 1
            state = "CLEARING"
        else:
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
            state = "READY"

    elif state == "CLEARING" and not animating:
        exploded = set(destroyed)
        for r, c in list(exploded):
            if board.grid[r][c].item_type != "NORMAL":
                board.trigger_item_effect(
                    r,
                    c,
                    board.grid[r][c].item_type,
                    rainbow_color_target,
                    exploded,
                    rainbow_item_target,
                )

        for r, c in exploded:
            p_color = board.grid[r][c].color
            if p_color != EMPTY_COLOR and p_color in COLORS:
                cx, cy = (
                    c * CELL_SIZE + CELL_SIZE // 2,
                    r * CELL_SIZE + SCORE_PANEL_HEIGHT + CELL_SIZE // 2,
                )

                # 💡 [스케일업 1] 보석 한 칸당 뿜어내는 파편 개수를 8개 ➡️ 20개로 대폭 상향!
                for _ in range(20):
                    p = Particle(cx, cy, p_color)

                    # 💡 [스케일업 2] 사방 폭발 반경과 속도를 훨씬 역동적으로 확장 (기존보다 2배 이상 멀리 튕김)
                    p.vx = random.uniform(-8, 8)  # 좌우 튕김 속도 강화 (-4~4 ➡️ -8~8)
                    p.vy = random.uniform(
                        -11, -1
                    )  # 위쪽으로 솟구치는 분수 효과 강화 (-6~2 ➡️ -11~-1)
                    p.gravity = 0.35  # 중력값을 올려 더 빠르게 아래로 떨어지도록 조율
                    p.radius = random.randint(2, 5)  # 알갱이 크기를 다양하게 믹스
                    p.alpha = 255
                    particles.append(p)

        combo_bonus = current_combo * 5
        for r, c in exploded:
            board.grid[r][c].color, board.grid[r][c].item_type, current_score = (
                EMPTY_COLOR,
                "NORMAL",
                current_score + (10 + combo_bonus),
            )
        for item in items:
            board.grid[item["r"]][item["c"]] = create_cell_by_type(
                item["type"], item["color"], item["r"], item["c"]
            )
        destroyed, items, state = [], [], "FALLING"

    elif state == "FALLING" and not animating:
        board.apply_fall()
        destroyed, items = board.analyze_matches()
        if destroyed:
            current_combo += 1
            if match_sound:
                match_sound.play()
            state = "CLEARING"
        else:
            current_combo, state = 0, "READY"

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == pygame.MOUSEBUTTONDOWN and state == "READY":
            mx, my = pygame.mouse.get_pos()
            if my > SCORE_PANEL_HEIGHT:
                c, r = mx // CELL_SIZE, (my - SCORE_PANEL_HEIGHT) // CELL_SIZE
                if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE:
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
                    # 두 타일이 모두 레인보우인지 감지 검사
                    is_both_rainbow = (
                        board.grid[r1][c1].item_type == "RAINBOW"
                        and board.grid[r2][c2].item_type == "RAINBOW"
                    )
                    is_rainbow_swap = (
                        board.grid[r1][c1].item_type == "RAINBOW"
                        or board.grid[r2][c2].item_type == "RAINBOW"
                    )

                    if is_both_rainbow:
                        # 💡 [레인보우 2개 결합] 특수 아이템 대상을 "ALL_CLEAR"로 설정하여 강제 기폭 전송!
                        rainbow_color_target = (255, 255, 255)
                        rainbow_item_target = "ALL_CLEAR"

                        board.grid[r1][c1], board.grid[r2][c2] = (
                            board.grid[r2][c2],
                            board.grid[r1][c1],
                        )
                        (
                            board.grid[r1][c1].r,
                            board.grid[r1][c1].c,
                            board.grid[r1][c1].target_x,
                            board.grid[r1][c1].target_y,
                        ) = (
                            r1,
                            c1,
                            c1 * CELL_SIZE,
                            r1 * CELL_SIZE + SCORE_PANEL_HEIGHT,
                        )
                        (
                            board.grid[r2][c2].r,
                            board.grid[r2][c2].c,
                            board.grid[r2][c2].target_x,
                            board.grid[r2][c2].target_y,
                        ) = (
                            r2,
                            c2,
                            c2 * CELL_SIZE,
                            r2 * CELL_SIZE + SCORE_PANEL_HEIGHT,
                        )
                        destroyed = [(r1, c1), (r2, c2)]
                        current_combo = 1
                        left_moves - 1
                        state = "CLEARING"

                    elif is_rainbow_swap:
                        # [기존 기능 유지] 레인보우와 일반/특수 템 간의 스왑
                        if board.grid[r1][c1].item_type == "RAINBOW":
                            rainbow_color_target = board.grid[r2][c2].color
                            rainbow_item_target = board.grid[r2][c2].item_type
                        else:
                            rainbow_color_target = board.grid[r1][c1].color
                            rainbow_item_target = board.grid[r1][c1].item_type

                        board.grid[r1][c1], board.grid[r2][c2] = (
                            board.grid[r2][c2],
                            board.grid[r1][c1],
                        )
                        (
                            board.grid[r1][c1].r,
                            board.grid[r1][c1].c,
                            board.grid[r1][c1].target_x,
                            board.grid[r1][c1].target_y,
                        ) = (
                            r1,
                            c1,
                            c1 * CELL_SIZE,
                            r1 * CELL_SIZE + SCORE_PANEL_HEIGHT,
                        )
                        (
                            board.grid[r2][c2].r,
                            board.grid[r2][c2].c,
                            board.grid[r2][c2].target_x,
                            board.grid[r2][c2].target_y,
                        ) = (
                            r2,
                            c2,
                            c2 * CELL_SIZE,
                            r2 * CELL_SIZE + SCORE_PANEL_HEIGHT,
                        )
                        destroyed = [(r1, c1), (r2, c2)]
                        current_combo = 1
                        state = "CLEARING"
                    else:
                        # 일반 보석 드래그 교체 처리
                        rainbow_color_target, rainbow_item_target = (
                            255,
                            255,
                            255,
                        ), "NORMAL"
                        board.grid[r1][c1], board.grid[r2][c2] = (
                            board.grid[r2][c2],
                            board.grid[r1][c1],
                        )
                        (
                            board.grid[r1][c1].r,
                            board.grid[r1][c1].c,
                            board.grid[r1][c1].target_x,
                            board.grid[r1][c1].target_y,
                        ) = (
                            r1,
                            c1,
                            c1 * CELL_SIZE,
                            r1 * CELL_SIZE + SCORE_PANEL_HEIGHT,
                        )
                        (
                            board.grid[r2][c2].r,
                            board.grid[r2][c2].c,
                            board.grid[r2][c2].target_x,
                            board.grid[r2][c2].target_y,
                        ) = (
                            r2,
                            c2,
                            c2 * CELL_SIZE,
                            r2 * CELL_SIZE + SCORE_PANEL_HEIGHT,
                        )
                        swap_back_coords, state = (r1, c1, r2, c2), "SWAPPING"

                mouse_down_pos, active_gem = None, None

        elif event.type == pygame.MOUSEBUTTONUP and state == "READY":
            if mouse_down_pos and active_gem:
                r, c = active_gem
                if board.grid[r][c].item_type != "NORMAL":
                    rainbow_color_target, rainbow_item_target = (
                        255,
                        255,
                        255,
                    ), "NORMAL"
                    destroyed, state = [(r, c)], "CLEARING"

            mouse_down_pos, active_gem = None, None

    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            board.grid[r][c].draw(screen)

    particles = [p for p in particles if p.update()]
    for p in particles:
        p.draw(screen)

    pygame.display.flip()
    clock.tick(60)
