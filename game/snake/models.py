# models.py
import pygame

# 글로벌 환경 설정
WIDTH, HEIGHT = 400, 400
GRID_SIZE = 20
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE
FPS = 30

# 색상 상수
# WHITE = (255, 255, 255)
# GREEN = (0, 255, 100)
# BODY_COLOR = (0, 180, 70)
# RED = (255, 50, 50)
# BLACK = (15, 15, 15)

# models.py (기존 파일 내용 중 색상 상수 부분에 GRAY만 추가)
WHITE = (255, 255, 255)
GREEN = (0, 255, 100)
BODY_COLOR = (0, 180, 70)
RED = (255, 50, 50)
BLACK = (15, 15, 15)
GRAY = (100, 100, 100)  # 👈 장애물 벽으로 사용할 회색 추가

class Snake:
    """뱀의 좌표 배열 관리 및 물리적 전진을 담당하는 클래스"""
    def __init__(self):
        # 화면 중앙 부근에서 3칸 크기로 시작
        self.body = [
            (GRID_WIDTH // 2, GRID_HEIGHT // 2),
            (GRID_WIDTH // 2 - 1, GRID_HEIGHT // 2),
            (GRID_WIDTH // 2 - 2, GRID_HEIGHT // 2)
        ]
        self.direction = (1, 0) # 초기 이동 방향 (우측)

    def move(self, next_dir, food_pos):
        """AI가 결정한 방향으로 머리를 이동하고 먹이 습득 여부를 반환"""
        self.direction = next_dir
        head = self.body[0]
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])
        
        # 새로운 머리 삽입
        self.body.insert(0, new_head)
        
        # 먹이를 먹었는지 판정
        if new_head == food_pos:
            return True
        else:
            self.body.pop() # 먹이를 먹지 않았다면 꼬리 한 칸 탈락(길이 유지)
            return False
