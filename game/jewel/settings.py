

"""
설정 및 공통 상숫값
"""

POP_WAV = "../sound/pop.wav"
BGM = "../sound/bgm.mp3"

# === settings.py 전체 교체 코드 ===

# 1. 윈도우 창 크기 고정 (원하시는 대로 가로/세로를 더 키우셔도 됩니다)
WIDTH, HEIGHT = 600, 680  # 판이 커지므로 창 크기를 조금 더 넓게 조정했습니다.
SCORE_PANEL_HEIGHT = 80
GRID_WIDTH, GRID_HEIGHT = 576, 576  # 보석들이 그려질 실제 격자판 총 너비

# 2. 💡 [이 숫만 바꾸면 끝!] 원하시는 보드 크기를 지정하세요 (8, 16, 24 등)
GRID_SIZE = 16  # ⬅️ 16 * 16 판인 경우 16, 24 * 24 판인 경우 24로 이 숫자만 변경!

# 3. 💡 [자동 리사이징 수식] 격자 크기에 맞춰 보석 한 칸의 크기를 컴퓨터가 자동 계산합니다.
CELL_SIZE = GRID_WIDTH // GRID_SIZE

# 4. 애니메이션 속도 제어
SWAP_SPEED = 6
FALL_SPEED = 8

# 5. 기본 색상 구성 (기존 유지)
COLORS = [
    (235, 77, 75),   # 레드
    (106, 176, 76),  # 그린
    (29, 209, 161),  # 민트 블루
    (241, 196, 15),  # 옐로우
    (155, 89, 182)   # 퍼플
]
EMPTY_COLOR = (30, 30, 30)

MAX_MOVES = 35
TARGET_SCORE = 300000

DEFAULT_SCORE = 10
RAINBOW_BONUS = 50
BOMB_BONUS = 30
MISSILE_BONUS = 20
PROPELLER_BONUS = 20
