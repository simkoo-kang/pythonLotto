import pygame
import random
from config.config_manager import ConfigManager


# --- [클래스 설계도: Ball] ---
class Ball:
    def __init__(self, x, y):
        # 1. 속성(상태) 정의
        self.x = x
        self.y = y
        self.min_radius, self.max_radius = 10, 30
        self.radius = random.randint(self.min_radius, self.max_radius)  # 반지름 랜덤
        self.color = (
            random.randint(50, 255),
            random.randint(50, 255),
            random.randint(50, 255),
        )  # 색상 랜덤

        # 이동 속도 및 방향 (dx: x축 변화량, dy: y축 변화량)
        self.dx = random.randint(-5, 5)
        self.dy = random.randint(-5, 5)

        # 멈춰있는 공이 없도록 속도 보정
        if self.dx == 0:
            self.dx = 3
        if self.dy == 0:
            self.dy = 3

    def move(self, width, height) -> bool:
        # 2. 행동(움직임) 정의
        self.x += self.dx
        self.y += self.dy

        # 벽 충돌 체크 (튕기기)
        if self.x - self.radius < 0 or self.x + self.radius > width:
            self.dx *= -1  # x방향 반전
            self.radius -= 1

        if self.y - self.radius < 0 or self.y + self.radius > height:
            self.dy *= -1  # y방향 반전
            self.radius -= 1

        if self.radius < self.min_radius - 5:
            return False

        return True

    def draw(self, screen):
        # 3. 그리기 행동
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)


class PygameClass:
    def __init__(self):
        config_manager = ConfigManager(__file__)

        # --- [메인 실행부] ---
        pygame.init()

        settings = config_manager.settings
        config = settings.get("ball")
        if config == None:
            config = {}
            settings["ball"] = config
            config["WIDTH"], config["HEIGHT"] = 800, 600
            config_manager.save()

        self.WIDTH, self.HEIGHT = config["WIDTH"], config["HEIGHT"]
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("클래스 실습: Ball Factory")
        self.clock = pygame.time.Clock()

        # 생성된 공 객체들을 담을 바구니(리스트)
        self.ball_list = []

        self.clicked = False

    def run(self):
        running = True
        while running:
            self.screen.fill((30, 30, 30))  # 배경색 (어두운 회색)

            for event in pygame.event.get():
                if event.type == pygame.QUIT or (
                    self.clicked and len(self.ball_list) == 0
                ):
                    running = False

                # 마우스를 클릭하면? -> 새로운 Ball '객체' 생성!
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    new_ball = Ball(mx, my)  # 클래스 호출 (인스턴스 생성)
                    self.ball_list.append(new_ball)  # 리스트에 보관
                    self.clicked = True

            # 리스트에 담긴 모든 공들을 하나씩 꺼내서 명령하기
            new_ball_list = []
            for ball in self.ball_list:
                if ball.move(self.WIDTH, self.HEIGHT):
                    # 이동해라!
                    new_ball_list.append(ball)
                    ball.draw(self.screen)  # 그려져라!

            self.ball_list = new_ball_list

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()


# ==================== 실행 및 검증 ====================
if __name__ == "__main__":
    cls_main = PygameClass()
    cls_main.run()
