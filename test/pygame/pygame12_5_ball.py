import pygame
import math
import random

# 초기화
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Multi-Ball Elastic Collision")
clock = pygame.time.Clock()

class Ball:
    def __init__(self, x, y, radius, color):
        self.x = x
        self.y = y
        self.radius = radius
        # 반지름을 기준으로 질량(Mass) 비례 설정
        self.mass = radius 
        self.color = color
        # 초기 속도 무작위 지정 (-3 ~ 3)
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-3, 3)

    def move(self):
        self.x += self.vx
        self.y += self.vy

        # 벽 충돌 처리
        if self.x - self.radius < 0:
            self.x = self.radius
            self.vx *= -1
        elif self.x + self.radius > WIDTH:
            self.x = WIDTH - self.radius
            self.vx *= -1

        if self.y - self.radius < 0:
            self.y = self.radius
            self.vy *= -1
        elif self.y + self.radius > HEIGHT:
            self.y = HEIGHT - self.radius
            self.vy *= -1

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

def handle_ball_collisions(balls):
    num_balls = len(balls)
    
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

# 무작위 볼 리스트 생성 (예: 15개의 공)
balls = []
for _ in range(15):
    radius = random.randint(15, 35)
    # 시작할 때 서로 겹치지 않게 여유 공간을 두고 스폰
    x = random.randint(radius, WIDTH - radius)
    y = random.randint(radius, HEIGHT - radius)
    color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
    balls.append(Ball(x, y, radius, color))

# 게임 루프
running = True
while running:
    clock.tick(60)
    screen.fill((20, 20, 20))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 1. 모든 볼 이동
    for ball in balls:
        ball.move()

    # 2. 모든 볼의 충돌 일괄 처리
    handle_ball_collisions(balls)

    # 3. 모든 볼 그리기
    for ball in balls:
        ball.draw(screen)

    pygame.display.flip()

pygame.quit()
