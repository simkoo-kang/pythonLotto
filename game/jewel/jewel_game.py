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
    # 매칭 때 소리
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if os.path.exists(os.path.join(current_dir, POP_WAV)):
        match_sound = pygame.mixer.Sound(os.path.join(current_dir, POP_WAV))

    # 배경 음악
    if os.path.exists(os.path.join(current_dir, BGM)):
        pygame.mixer.music.load(os.path.join(current_dir, BGM))
        pygame.mixer.music.set_volume(0.4)
        pygame.mixer.music.play(-1)

except Exception:
    pass


# score, combo
current_score, current_combo = 0, 0
# 남은 횟수
left_moves = MAX_MOVES
# 게임 결과
game_result = "CLEAR" # None

state, mouse_down_pos, active_gem, swap_back_coords = "READY", None, None, None

# 무지개 교환 색상, 무지개 교환 아이템
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

    # 화면 배경을 흐리게 마스킹
    mask = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    mask.fill((0, 0, 0, 180))
    screen.blit(mask, (0, 0))

    # 결과 표시  게임 완료[목표 완수] 또는 종료(목표 미달)
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
