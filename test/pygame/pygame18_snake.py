import math

import pygame
import random
from config.config_manager import ConfigManager
from game.pygame_main import GameMain


class SnameMain(GameMain):
    def __init__(self, config, title):
        super().__init__(config, title)

        self.width, self.height, self.GRID_SIZE = (
            config.WIDTH,
            config.HEIGHT,
            config.GRID_SIZE,
        )

        # 색상 및 폰트 설정
        self.BLACK = (30, 30, 30)
        self.GREEN = (0, 255, 0)
        self.RED = (255, 50, 50)
        self.WHITE = (255, 255, 255)

        self.font = pygame.font.SysFont("arial", 24, True)
        self.large_font = pygame.font.SysFont("arial", 60, True)

        # 게임 시작 시 초기화
        self.snake, self.dx, self.dy, self.apple, self.score = self.reset_game()
        self.game_state = "PLAYING"  # 현재 게임 상태: PLAYING 또는 GAME_OVER

        self.tick = 60

    def reset_game(self):
        # 게임을 초기 상태로 되돌려주는 함수
        # 뱀은 화면 정중앙에서 시작합니다.
        start_x, start_y = self.width // 2, self.height // 2
        new_snake = [
            (start_x, start_y),
            (start_x + self.GRID_SIZE, start_y),
            (start_x + self.GRID_SIZE * 2, start_y),
        ]
        new_dx, new_dy = -self.GRID_SIZE, 0
        new_apple = (
            random.randint(0, (self.width // self.GRID_SIZE) - 1) * self.GRID_SIZE,
            random.randint(0, (self.height // self.GRID_SIZE) - 1) * self.GRID_SIZE,
        )
        return new_snake, new_dx, new_dy, new_apple, 0  # 뱀, 방향, 사과, 점수 0점 반환

    """_summary_
    overwriding methods
    """

    def event_next(self, event):
        if event.type == pygame.KEYDOWN:
            if self.game_state == "PLAYING":
                # 반대 방향으로 꺾어 바로 죽는 것 방지
                if event.key == pygame.K_UP and self.dy == 0:
                    self.dx, self.dy = 0, -self.GRID_SIZE
                elif event.key == pygame.K_DOWN and self.dy == 0:
                    self.dx, self.dy = 0, self.GRID_SIZE
                elif event.key == pygame.K_LEFT and self.dx == 0:
                    self.dx, self.dy = -self.GRID_SIZE, 0
                elif event.key == pygame.K_RIGHT and self.dx == 0:
                    self.dx, self.dy = self.GRID_SIZE, 0

            elif self.game_state == "GAME_OVER":
                # 게임 오버 상태일 때 'R' 키를 누르면 게임 재시작
                if event.key == pygame.K_r:
                    self.snake, self.dx, self.dy, self.apple, self.score = (
                        self.reset_game()
                    )
                    self.game_state = "PLAYING"

        return True

    def update_state(self):
        # --- 게임 로직 업데이트 ---
        if self.game_state == "PLAYING":
            head_x, head_y = self.snake[0]
            new_head = (head_x + self.dx, head_y + self.dy)
            new_head = (new_head[0] % self.width, new_head[1] % self.height)

            # 충돌 판정 (벽 밖으로 나가거나, 자기 몸에 부딪혔을 때)
            if (
                new_head[0] < 0
                or new_head[0] >= self.width
                or new_head[1] < 0
                or new_head[1] >= self.height
                or new_head in self.snake
            ):
                self.game_state = "GAME_OVER"
            else:
                # 뱀 이동
                self.snake.insert(0, new_head)

                # 사과 먹기 판정
                if new_head == self.apple:
                    self.score += 10
                    # 새로운 사과가 뱀 몸통과 겹치지 않는 곳에 생기도록 보장
                    while True:
                        self.apple = (
                            random.randint(0, (self.width // self.GRID_SIZE) - 1)
                            * self.GRID_SIZE,
                            random.randint(0, (self.height // self.GRID_SIZE) - 1)
                            * self.GRID_SIZE,
                        )
                        if self.apple not in self.snake:
                            break
                else:
                    self.snake.pop()  # 사과를 못 먹었다면 꼬리를 자름

        return True

    def drawing(self):
        # --- 화면 그리기 ---
        self.screen.fill(self.BLACK)

        # 사과 그리기
        pygame.draw.rect(
            self.screen,
            self.RED,
            (self.apple[0], self.apple[1], self.GRID_SIZE, self.GRID_SIZE),
        )

        # 뱀 그리기 (GRID_SIZE-1 을 주어 마디를 구분함)
        for s in self.snake:
            pygame.draw.rect(
                self.screen,
                self.GREEN,
                (s[0], s[1], self.GRID_SIZE - 1, self.GRID_SIZE - 1),
            )

        # 점수 텍스트 표시
        score_txt = self.font.render(f"SCORE: {self.score}", True, self.WHITE)
        self.screen.blit(score_txt, (15, 15))

        # 게임 오버 화면 표시
        if self.game_state == "GAME_OVER":
            # 반투명한 검은색 막을 씌워 배경을 어둡게 만듦
            overlay = pygame.Surface((self.width, self.height))
            overlay.set_alpha(150)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))

            over_txt = self.large_font.render("GAME OVER", True, self.RED)
            restart_txt = self.font.render("Press 'R' to Restart", True, self.WHITE)
            self.screen.blit(
                over_txt,
                (self.width // 2 - over_txt.get_width() // 2, self.height // 2 - 50),
            )
            self.screen.blit(
                restart_txt,
                (self.width // 2 - restart_txt.get_width() // 2, self.height // 2 + 30),
            )

        # 기본 속도 12에서 시작, 사과를 2개(20점) 먹을 때마다 1씩 빨라짐
        return 12 + (self.score // 20)

    def update_display(self):
        pygame.display.flip()


# ==================== 실행 및 검증 ====================
if __name__ == "__main__":
    config_manager = ConfigManager(__file__)
    key = "snake"
    if config_manager.inited:
        config = config_manager.settings.get(key)
        if config == None:
            config = config_manager.dict_to_munchify()
            config_manager.settings[key] = config
            config.WIDTH, config.HEIGHT, config.GRID_SIZE = 800, 600, 20

            print(config_manager.settings)
            config_manager.save()

        cls_main = SnameMain(config=config, title="스네이크 게임")
        cls_main.run()
