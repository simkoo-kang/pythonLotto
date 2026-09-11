import random
import sys
import os
import pygame
import io
from game.jewel.settings import (BGM, CELL_SIZE, COLORS, DEFAULT_SCORE, EMPTY_COLOR, GRID_SIZE,
    HEIGHT, MAX_MOVES, POP_WAV, SCORE_PANEL_HEIGHT, TARGET_SCORE, WIDTH)
from game.jewel.board import Board
from game.jewel.cell import Particle, create_cell_by_type
from util.str_util import Str
from util.log_util import LogUtil

if sys.stdout:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


logger = LogUtil.get_logger(name="Jewel Matching Game")

logger.debug("=== start Gane ----------------")

pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🚀 프리미엄 보석 퍼즐 마스터 🚀")
clock = pygame.time.Clock()

game_font = pygame.font.SysFont("malgungothic", 24, bold=True)
result_font = pygame.font.SysFont("malgungothic", 56, bold=True)
sub_font = pygame.font.SysFont("malgungothic", 20, bold=True)

logger.debug("사운드 설정 ===")
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

logger.debug("루프 시작 ===")

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

    # 💡 [종료 후 연출 및 재시작 액션 제어 블록]
    if game_result is not None:
        
        # 💡 [버그 완벽 수정 - 잔상 클리너 장치] 
        # 게임이 멈추기 전, 아직 화면에 남아있는 파괴 중인 셀(터지다 만 잔상)들을 완전히 공백(EMPTY)으로 강제 초기화합니다.
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if board.grid[r][c].is_destroying or board.grid[r][c].alpha <= 0:
                    board.grid[r][c].color = EMPTY_COLOR
                    board.grid[r][c].item_type = "NORMAL"
                    board.grid[r][c].is_destroying = False
                    board.grid[r][c].alpha = 255

        # 공백 처리가 완벽히 완료된 상태의 보드판을 깨끗하게 화면에 드로잉
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
        is_item_trigger = (
            board.grid[r1][c1].item_type != "NORMAL"
            or board.grid[r2][c2].item_type != "NORMAL"
        )
        if is_item_trigger or destroyed:
            if (r1, c1) not in destroyed and board.grid[r1][c1].item_type != "NORMAL":
                destroyed.append((r1, c1))
            if (r2, c2) not in destroyed and board.grid[r2][c2].item_type != "NORMAL":
                destroyed.append((r2, c2))
            if match_sound:
                match_sound.play()
            current_combo, left_moves, state = 1, left_moves - 1, "CLEARING"
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
        
        # 💡 [정밀 보정 1] 보석 타일의 색상과 아이템 정보를 확실하게 공백으로 먼저 지워버립니다!
        # 💡 [정답 순서 고정] 먼저 화면에서 보석들의 색상을 시커먼 공백(EMPTY_COLOR)으로 완벽하게 지웁니다.
        for r, c in exploded: 
            board.grid[r][c].color, board.grid[r][c].item_type = EMPTY_COLOR, "NORMAL"
            current_score += (board.score_unit + combo_bonus)

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
            # 💡 [버그 완벽 수정] 상태(state)를 섣불리 가두지 않고, 
            # 연쇄 콤보가 완전히 끝난 시점에 새로운 중간 대기 상태인 "SETTLING"으로 안전하게 이주 시킵니다!
            state = "SETTLING"


    # 💡 [새로 추가된 정밀 물리 정착 상태 머신]
    # 보석들이 거의 다 내려와서 완전히 자석처럼 찰칵! 정착할 때까지 
    # 중력 함수(apply_fall)의 재실행 간섭 없이 오직 '물리 좌표'만 철저히 감시하며 대기하는 상태입니다.
    elif state == "SETTLING":
        all_settled = True
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                gem = board.grid[r][c]
                # 보석 객체의 실시간 좌표가 목표 격자 주소와 단 1픽셀이라도 다르면 아직 정착 안 됨!
                if gem.x != gem.target_x or gem.y != gem.target_y:
                    all_settled = False
                    break
        
        # 단 한 칸의 낙오자도 없이 100% 보석판 전체가 정지(침묵)했을 때 비로소 최종 판정 시작!
        if all_settled:
            current_combo = 0
            board.score_unit = DEFAULT_SCORE
            
            # --------------------------------------------------------------
            # 🎯 [최종 마스터 - 오차 없는 완벽한 정착 타이밍]
            # --------------------------------------------------------------
            if game_result is None:
                if current_score >= TARGET_SCORE: 
                    game_result = "CLEAR"        # 완벽하게 자리를 다 잡고 멈춘 화면 위로 우아하게 성공!
                elif left_moves <= 0: 
                    game_result = "GAMEOVER"     # 완벽히 정돈된 보드 위로 깔끔하게 실패!
            # --------------------------------------------------------------
            
            state = "READY"  # 모든 검증이 끝났으므로 비로소 다음 유저 입력을 받습니다.

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif (
            event.type == pygame.MOUSEBUTTONDOWN
            and state == "READY"
            and game_result is None
        ):
            mx, my = pygame.mouse.get_pos()
            if my > SCORE_PANEL_HEIGHT:
                c, r = mx // CELL_SIZE, (my - SCORE_PANEL_HEIGHT) // CELL_SIZE
                if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE:
                    mouse_down_pos, active_gem = (mx, my), (r, c)
                    if board.grid[r][c].item_type != "NORMAL":
                        if match_sound:
                            match_sound.play()

        elif (
            event.type == pygame.MOUSEMOTION
            and mouse_down_pos
            and state == "READY"
            and game_result is None
        ):
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
                    is_rainbow_swap = (
                        board.grid[r1][c1].item_type == "RAINBOW"
                        or board.grid[r2][c2].item_type == "RAINBOW"
                    )

                    if is_rainbow_swap:
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
                        destroyed, current_combo, left_moves, state = (
                            [(r1, c1), (r2, c2)],
                            1,
                            left_moves - 1,
                            "CLEARING",
                        )
                    else:
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

        elif event.type == pygame.MOUSEBUTTONUP:
            if mouse_down_pos and active_gem:
                r, c = active_gem
                if board.grid[r][c].item_type != "NORMAL":
                    rainbow_color_target, rainbow_item_target = (
                        255,
                        255,
                        255,
                    ), "NORMAL"
                    destroyed, state = [(r, c)], "CLEARING"

            # 안전하게 마우스 조작 센서값만 휘발 청소
            mouse_down_pos, active_gem = None, None

    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            board.grid[r][c].draw(screen)

    particles = [p for p in particles if p.update()]
    for p in particles:
        p.draw(screen)

    pygame.display.flip()
    clock.tick(60)
