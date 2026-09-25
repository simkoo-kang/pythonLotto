# main.py
import pygame
import sys
import random
import math
from game.snake.models import WIDTH, HEIGHT, GRID_SIZE, GRID_WIDTH, GRID_HEIGHT, FPS, WHITE, GREEN, BODY_COLOR, RED, BLACK, GRAY
from game.snake.models import Snake
from game.snake.ai import SnakeAI

"""
models.py에서 FPS = 2 또는 5로 아주 낮춰보세요.
뱀이 한 칸씩 아주 느리게 움직이게 만들면,
"아, 얘가 먹이를 바로 옆에 두고도 갇힐까 봐 일부러 꼬리를 향해 뱅글 돌아서 진입하는구나!" 하는
알고리즘의 의도가 눈으로 정확히 보입니다.

print() 문을 적극 활용해 보세요.
decide_direction 함수 내부에 print("1단계 사냥 승인"), print("2단계 꼬리 추적") 같은
출력문을 심어두면 터미널 창에 실시간으로 AI의 심리 상태가 찍혀서 분석하기 훨씬 재밌어집니다.
"""


class SnakeGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("장애물 모드 도입 - AI 생존 스네이크")
        self.clock = pygame.time.Clock()
        self.ai = SnakeAI()
        
        self.TOTAL_CELLS = GRID_WIDTH * GRID_HEIGHT
        self.perfect_clear = False
        self.animation_timer = 0
        self.reset()

    def reset(self):
        self.snake = Snake()
        # [💡 핵심 수정 1] 맵 시작 시 고정 장애물 15개를 무작위로 배치합니다.
        self.obstacles = self.generate_obstacles(count=15)
        self.food = self.spawn_food()
        self.score = 0
        self.game_over = False
        self.perfect_clear = False
        self.animation_timer = 0

    def generate_obstacles(self, count):
        """뱀의 초기 위치와 겹치지 않는 곳에 고정 장애물 좌표 생성"""
        obstacles = set()
        while len(obstacles) < count:
            obs = (random.randint(1, GRID_WIDTH - 2), random.randint(1, GRID_HEIGHT - 2))
            # 뱀의 초기 몸통 3칸 위치와 겹치지 않게 방어
            if obs not in self.snake.body:
                obstacles.add(obs)
        return list(obstacles)

    def spawn_food(self):
        # 장애물과 뱀 몸통을 제외한 남은 공간 계산
        if len(self.snake.body) + len(self.obstacles) >= self.TOTAL_CELLS:
            return None
            
        while True:
            food = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
            # 뱀 몸통뿐만 아니라 [장애물] 위치에도 먹이가 안 생기도록 방어
            if food not in self.snake.body and food not in self.obstacles:
                return food

    def check_collision(self):
        head = self.snake.body[0]
        if not (0 <= head[0] < GRID_WIDTH and 0 <= head[1] < GRID_HEIGHT):
            return True
        if head in self.snake.body[1:]:
            return True
        # [💡 핵심 수정 2] 뱀 머리가 고정 장애물 벽에 부딪혔는지 검사
        if head in self.obstacles:
            return True
        return False

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r and (self.game_over or self.perfect_clear):
                        self.reset()

            if not self.game_over and not self.perfect_clear:
                if len(self.snake.body) + len(self.obstacles) >= self.TOTAL_CELLS:
                    self.perfect_clear = True
                else:
                    # [💡 핵심 수정 3] AI에게 내 몸통 정보 뒤에 장애물(obstacles) 리스트를 합쳐서 전달합니다.
                    # 이렇게 하면 AI가 장애물을 '내 몸통'과 똑같은 고정 벽으로 인식해서 알아서 피해갑니다!
                    combined_obstacles = self.snake.body + self.obstacles
                    
                    ai_decision = self.ai.decide_direction(combined_obstacles, self.food, self.snake.direction)
                    ate_food = self.snake.move(ai_decision, self.food)
                    
                    if ate_food:
                        self.score += 10
                        self.food = self.spawn_food()
                        
                    if self.check_collision():
                        self.game_over = True

            if self.perfect_clear:
                self.animation_timer += 1

            self.render()
            self.clock.tick(FPS)

    def render(self):
        self.screen.fill(BLACK)

        # [💡 핵심 수정 4] 화면에 회색 장애물 벽 렌더링
        for obs in self.obstacles:
            obs_rect = pygame.Rect(obs[0] * GRID_SIZE, obs[1] * GRID_SIZE, GRID_SIZE - 2, GRID_SIZE - 2)
            pygame.draw.rect(self.screen, GRAY, obs_rect)

        # 뱀 렌더링
        for i, block in enumerate(self.snake.body):
            rect = pygame.Rect(block[0] * GRID_SIZE, block[1] * GRID_SIZE, GRID_SIZE - 2, GRID_SIZE - 2)
            if self.perfect_clear:
                glow = int((math.sin(self.animation_timer * 0.1 + i * 0.05) + 1) * 30)
                color = (230 + glow, 180 + glow // 2, 30) if i == 0 else (200 + glow, 140, 20)
            else:
                color = GREEN if i == 0 else BODY_COLOR
            pygame.draw.rect(self.screen, color, rect)

        # 먹이 렌더링
        if self.food and not self.perfect_clear:
            food_rect = pygame.Rect(self.food[0] * GRID_SIZE, self.food[1] * GRID_SIZE, GRID_SIZE - 2, GRID_SIZE - 2)
            pygame.draw.rect(self.screen, RED, food_rect)

        # 스코어 보드
        if not self.perfect_clear:
            font = pygame.font.SysFont("arial", 20, bold=True)
            score_surface = font.render(f"SCORE: {self.score}", True, WHITE)
            self.screen.blit(score_surface, (15, 15))

        # 퍼펙트 클리어 연출
        if self.perfect_clear:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(160)
            pulse = int((math.sin(self.animation_timer * 0.08) + 1) * 20)
            overlay.fill((10 + pulse, 15 + pulse, 30))
            self.screen.blit(overlay, (0, 0))

            popup_w, popup_h = 320, 160
            popup_rect = pygame.Rect(WIDTH // 2 - popup_w // 2, HEIGHT // 2 - 50, popup_w, popup_h)
            pygame.draw.rect(self.screen, (30, 30, 40), popup_rect, border_radius=12)
            
            border_glow = int((math.sin(self.animation_timer * 0.1) + 1) * 25)
            pygame.draw.rect(self.screen, (210 + border_glow, 160 + border_glow, 10), popup_rect, width=3, border_radius=12)

            title_font = pygame.font.SysFont("arial", 26, bold=True)
            sub_font = pygame.font.SysFont("arial", 15)
            restart_font = pygame.font.SysFont("arial", 13)

            title_text = title_font.render("🏆 OBSTACLE CLEARED 🏆", True, (255, 215, 0))
            sub_text = sub_font.render(f"Score: {self.score} | Filled completely!", True, WHITE)
            restart_text = restart_font.render("Press 'R' to Restart Simulation", True, (160, 160, 170))

            self.screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 2 - 30))
            self.screen.blit(sub_text, (WIDTH // 2 - sub_text.get_width() // 2, HEIGHT // 2 + 15))
            self.screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 60))

        # 게임 오버 연출
        elif self.game_over:
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
