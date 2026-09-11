import pygame
import sys
import random
from collections import deque

# 게임 설정
WIDTH, HEIGHT = 600, 600
GRID_SIZE = 20
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE
FPS = 30  # AI의 빠른 연산을 위해 프레임 속도를 높였습니다.

# 색상 정의
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
GRAY = (40, 40, 40)

class AISnakeGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("AI 자동 실행 스네이크 게임 (BFS)")
        self.clock = pygame.time.Clock()
        self.reset_game()

    def reset_game(self):
        # 뱀 초기 위치 (중앙)
        self.snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = (1, 0) # 우측 방향 시작
        self.food = self.spawn_food()
        self.score = 0
        self.game_over = False

    def spawn_food(self):
        while True:
            food = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
            if food not in self.snake:
                return food

    def get_bfs_path(self):
        """BFS(너비 우선 탐색) 알고리즘으로 먹이까지의 최단 경로를 찾습니다."""
        start = self.snake[0]
        target = self.food
        
        # 탐색을 위한 큐와 방문 기록, 경로 추적용 딕셔너리
        queue = deque([start])
        visited = {start}
        parent = {}

        # 상, 하, 좌, 우 이동 방향
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]

        while queue:
            current = queue.popleft()

            if current == target:
                # 목적지에 도달하면 첫 번째 이동할 좌표를 추적하여 반환
                path = []
                while current in parent:
                    path.append(current)
                    current = parent[current]
                return path[::-1]  # 경로를 정방향으로 뒤집어 반환

            for dx, dy in directions:
                next_node = (current[0] + dx, current[1] + dy)

                # 벽에 부딪히지 않고, 뱀의 몸통(꼬리 끝 제외)에 부딪히지 않는지 체크
                if (0 <= next_node[0] < GRID_WIDTH and 
                    0 <= next_node[1] < GRID_HEIGHT and 
                    next_node not in self.snake[:-1] and 
                    next_node not in visited):
                    
                    visited.add(next_node)
                    parent[next_node] = current
                    queue.append(next_node)
        
        return None  # 경로를 찾지 못한 경우

    def get_safe_move(self):
        """먹이로 가는 길이 막혔을 때, 생존할 수 있는 빈 공간을 찾습니다."""
        head = self.snake[0]
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        
        for dx, dy in directions:
            next_node = (head[0] + dx, head[1] + dy)
            if (0 <= next_node[0] < GRID_WIDTH and 
                0 <= next_node[1] < GRID_HEIGHT and 
                next_node not in self.snake[:-1]):
                return (dx, dy)  # 살 수 있는 방향 반환
                
        return self.direction  # 정말 갈 곳이 없다면 원래 방향 유지

    def handle_ai(self):
        """AI가 매 프레임 경로를 계산하여 방향을 자동 전환합니다."""
        path = self.get_bfs_path()

        if path:
            # 최단 경로의 첫 번째 스텝으로 방향 결정
            next_step = path[0]
            self.direction = (next_step[0] - self.snake[0][0], next_step[1] - self.snake[0][1])
        else:
            # 먹이로 가는 길이 막혔다면 생존 모드 발동
            self.direction = self.get_safe_move()

    def update(self):
        if self.game_over:
            return

        # AI 조작 적용
        self.handle_ai()

        # 뱀 머리 이동
        new_head = (self.snake[0][0] + self.direction[0], self.snake[0][1] + self.direction[1])

        # 벽 충돌 검사
        if not (0 <= new_head[0] < GRID_WIDTH and 0 <= new_head[1] < GRID_HEIGHT):
            self.game_over = True
            return

        # 자기 몸통 충돌 검사
        if new_head in self.snake[:-1]:
            self.game_over = True
            return

        # 뱀 머리 추가
        self.snake.insert(0, new_head)

        # 먹이를 먹었는지 확인
        if new_head == self.food:
            self.score += 10
            self.food = self.spawn_food()
        else:
            self.snake.pop()  # 먹이를 안 먹었다면 꼬리 제거하여 길이 유지

    def draw(self):
        self.screen.fill(BLACK)

        # 뱀 그리기 (머리는 조금 더 밝은 녹색)
        for i, block in enumerate(self.snake):
            rect = pygame.Rect(block[0] * GRID_SIZE, block[1] * GRID_SIZE, GRID_SIZE - 2, GRID_SIZE - 2)
            color = (0, 255, 100) if i == 0 else GREEN
            pygame.draw.rect(self.screen, color, rect)

        # 먹이 그리기
        food_rect = pygame.Rect(self.food[0] * GRID_SIZE, self.food[1] * GRID_SIZE, GRID_SIZE - 2, GRID_SIZE - 2)
        pygame.draw.rect(self.screen, RED, food_rect)

        # 점수 표시
        font = pygame.font.SysFont("malgungothic", 25)
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))

        if self.game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(150)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))
            
            go_font = pygame.font.SysFont("malgungothic", 40, bold=True)
            sub_font = pygame.font.SysFont("malgungothic", 20)
            
            go_text = go_font.render("GAME OVER (AI DIED)", True, RED)
            sub_text = sub_font.render("다시 시작하려면 'R'을 누르세요", True, WHITE)
            
            self.screen.blit(go_text, (WIDTH // 2 - go_text.get_width() // 2, HEIGHT // 2 - 50))
            self.screen.blit(sub_text, (WIDTH // 2 - sub_text.get_width() // 2, HEIGHT // 2 + 10))

        pygame.display.flip()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r and self.game_over:
                        self.reset_game()

            self.update()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = AISnakeGame()
    game.run()
