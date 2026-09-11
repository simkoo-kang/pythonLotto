# main.py
import pygame
import sys
import random
from game.snake.models import WIDTH, HEIGHT, GRID_SIZE, GRID_WIDTH, GRID_HEIGHT, FPS, WHITE, GREEN, BODY_COLOR, RED, BLACK
from game.snake.models import Snake
from game.snake.ai import SnakeAI

class SnakeGame:
    """화면 렌더링, 이벤트 감지 및 인게임 루프를 제어하는 통합 관리 시스템"""
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("정밀 모듈화 아키텍처 - 절대 생존 AI 스네이크")
        self.clock = pygame.time.Clock()
        self.ai = SnakeAI()
        self.reset()

    def reset(self):
        self.snake = Snake()
        self.food = self.spawn_food()
        self.score = 0
        self.game_over = False

    def spawn_food(self):
        """뱀 몸체와 겹치지 않는 위치에 무작위 먹이 생성"""
        while True:
            food = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
            if food not in self.snake.body:
                return food

    def check_collision(self):
        """벽면 충돌 또는 자신의 몸통을 깨물었는지 판정"""
        head = self.snake.body[0]
        if not (0 <= head[0] < GRID_WIDTH and 0 <= head[1] < GRID_HEIGHT):
            return True
        if head in self.snake.body[1:]:
            return True
        return False

    def run(self):
        """게임 무한 루프 가동 엔진"""
        while True:
            # 이벤트 수집 (종료 및 재시작 처리)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r and self.game_over:
                        self.reset()

            # AI 조작 제어 및 물리 업데이트
            if not self.game_over:
                ai_decision = self.ai.decide_direction(self.snake.body, self.food, self.snake.direction)
                ate_food = self.snake.move(ai_decision, self.food)
                
                if ate_food:
                    self.score += 10
                    self.food = self.spawn_food()
                    
                if self.check_collision():
                    self.game_over = True

            # 화면 갱신
            self.render()
            self.clock.tick(FPS)

    def render(self):
        self.screen.fill(BLACK)

        # 뱀 렌더링 (머리와 몸통 색 분리)
        for i, block in enumerate(self.snake.body):
            rect = pygame.Rect(block[0] * GRID_SIZE, block[1] * GRID_SIZE, GRID_SIZE - 2, GRID_SIZE - 2)
            pygame.draw.rect(self.screen, GREEN if i == 0 else BODY_COLOR, rect)

        # 먹이 렌더링
        food_rect = pygame.Rect(self.food[0] * GRID_SIZE, self.food[1] * GRID_SIZE, GRID_SIZE - 2, GRID_SIZE - 2)
        pygame.draw.rect(self.screen, RED, food_rect)

        # 스코어 UI 보드
        font = pygame.font.SysFont("arial", 20, bold=True)
        score_surface = font.render(f"SCORE: {self.score}", True, WHITE)
        self.screen.blit(score_surface, (15, 15))

        # 게임 오버 전면 마스크 레이어
        if self.game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))
            
            main_font = pygame.font.SysFont("arial", 32, bold=True)
            sub_font = pygame.font.SysFont("arial", 18)
            
            go_txt = main_font.render("AI SIMULATION FAILED", True, RED)
            sub_txt = sub_font.render("Press 'R' to Reboot Neural Network", True, WHITE)
            
            self.screen.blit(go_txt, (WIDTH // 2 - go_txt.get_width() // 2, HEIGHT // 2 - 35))
            self.screen.blit(sub_txt, (WIDTH // 2 - sub_txt.get_width() // 2, HEIGHT // 2 + 15))

        pygame.display.flip()

if __name__ == "__main__":
    game = SnakeGame()
    game.run()
