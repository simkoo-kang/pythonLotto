import math

import pygame
import random
from config.config_manager import ConfigManager
from util.log_util import LogUtil


class Ball:
    def __init__(self, x, y, radius, color, min_radius):
        self.x = x
        self.y = y
        self.radius = radius
        # 반지름을 기준으로 질량(Mass) 비례 설정
        self.mass = radius
        self.color = color
        self.min_radius = min_radius

        speed = 4

        # 초기 속도 무작위 지정 (-3 ~ 3)
        self.vx = random.uniform(-speed, speed)
        self.vy = random.uniform(-speed, speed)
        # self.WIDTH, self.HEIGHT = width, height
        # print("Ball created")

    def move(self, width, height):
        self.x += self.vx
        self.y += self.vy

        # 벽 충돌 처리
        if self.x - self.radius < 0:
            self.x = self.radius
            self.vx *= -1
            self.radius -= 1

        elif self.x + self.radius > width:
            self.x = width - self.radius
            self.vx *= -1
            self.radius -= 1

        if self.y - self.radius < 0:
            self.y = self.radius
            self.vy *= -1
            self.radius -= 1

        elif self.y + self.radius > height:
            self.y = height - self.radius
            self.vy *= -1
            self.radius -= 1

        if self.radius < self.min_radius - 5:
            return False
        return True

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)


class PygameBallMain:
    def __init__(self):
        self.logger = LogUtil.get_logger(self.__class__.__name__)

        config_manager = ConfigManager(__file__)

        # --- [메인 실행부] ---
        pygame.init()

        settings = config_manager.settings
        config = settings.get("ball")
        if config == None:
            config = {}
            settings["ball"] = config
            config["WIDTH"], config["HEIGHT"] = 800, 600

            self.logger.debug(settings)
            config_manager.save()

        self.WIDTH, self.HEIGHT = config["WIDTH"], config["HEIGHT"]
        radius_limits = config.get("radius_limits")
        if radius_limits == None:
            config.radius_limits = {"min": 15, "max": 35}

            self.logger.debug(settings)
            print(settings)
            config_manager.save()

        self.min_radius = config.radius_limits.min
        self.max_radius = config.radius_limits.max

        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("클래스 실습: Ball Factory")
        self.clock = pygame.time.Clock()

        # 생성된 공 객체들을 담을 바구니(리스트)
        self.ball_list = []

        self.clicked = False

    def handle_ball_collisions(self, balls):
        num_balls = len(balls)
        if num_balls < 2:
            # self.logger.debug(f"balls = {num_balls}개 입니다.")
            return

        # 💡 핵심: 조합(Combination) 구조로 중복 없이 모든 쌍을 검사
        for i in range(num_balls):
            for j in range(i + 1, num_balls):
                b1 = balls[i]
                b2 = balls[j]

                dx = b2.x - b1.x
                dy = b2.y - b1.y
                distance = math.hypot(dx, dy)
                min_dist = b1.radius + b2.radius

                # 충돌 조건 검사
                if distance < min_dist:
                    if distance == 0:  # 완전히 겹쳐서 거리가 0인 경우 예외 처리
                        distance = 0.1

                    # 1. 겹침(Overlap) 해결
                    overlap = min_dist - distance
                    nx = dx / distance
                    ny = dy / distance

                    # 반반씩 밀어내기
                    b1.x -= nx * overlap * 0.5
                    b1.y -= ny * overlap * 0.5
                    b2.x += nx * overlap * 0.5
                    b2.y += ny * overlap * 0.5

                    # 2. 벡터 사영용 접선 벡터
                    tx = -ny
                    ty = nx

                    # 3. 법선, 접선 속도 분해
                    v1n = b1.vx * nx + b1.vy * ny
                    v1t = b1.vx * tx + b1.vy * ty
                    v2n = b2.vx * nx + b2.vy * ny
                    v2t = b2.vx * tx + b2.vy * ty

                    # 4. 탄성 충돌 공식을 적용한 새로운 법선 속도 계산
                    m1, m2 = b1.mass, b2.mass
                    v1n_after = (v1n * (m1 - m2) + 2 * m2 * v2n) / (m1 + m2)
                    v2n_after = (v2n * (m2 - m1) + 2 * m1 * v1n) / (m1 + m2)

                    # 5. 기존 접선 속도와 결합하여 x, y 속도로 재조립
                    b1.vx = v1n_after * nx + v1t * tx
                    b1.vy = v1n_after * ny + v1t * ty
                    b2.vx = v2n_after * nx + v2t * tx
                    b2.vy = v2n_after * ny + v2t * ty

    def new_ball(self, mx, my):
        # self.logger.debug(f"{mx}, {my}")
        radius = random.randint(self.min_radius, self.max_radius)
        # 시작할 때 서로 겹치지 않게 여유 공간을 두고 스폰
        color = (
            random.randint(50, 255),
            random.randint(50, 255),
            random.randint(50, 255),
        )
        return Ball(x=mx, y=my, radius=radius, color=color, min_radius=self.min_radius)

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
                    new_ball = self.new_ball(mx, my)  # 클래스 호출 (인스턴스 생성)
                    self.ball_list.append(new_ball)  # 리스트에 보관
                    self.clicked = True

            # 리스트에 담긴 모든 공들을 하나씩 꺼내서 명령하기
            new_ball_list = []
            for ball in self.ball_list:
                if ball.move(self.WIDTH, self.HEIGHT):
                    # 이동해라!
                    new_ball_list.append(ball)

            self.ball_list = new_ball_list
            self.handle_ball_collisions(self.ball_list)

            for ball in self.ball_list:
                ball.draw(self.screen)  # 그려져라!

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()


# ==================== 실행 및 검증 ====================
if __name__ == "__main__":
    cls_main = PygameBallMain()
    cls_main.run()
