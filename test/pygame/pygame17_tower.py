import math

import pygame
import random
from config.config_manager import ConfigManager
from game.pygame_main import GameMain


class TowerDefense(GameMain):
    def __init__(self, config, title):
        super().__init__(config, title)

        self.width, self.height = config.WIDTH, config.HEIGHT

        # 색상 및 게임 규칙 설정
        self.WHITE = (255, 255, 255)
        self.BLACK = (30, 30, 30)
        self.RED = (255, 80, 80)
        self.GREEN = (80, 255, 80)
        self.YELLOW = (255, 220, 0)
        self.TOWER_COST = 50
        self.KILL_REWARD = 15

        # 몬스터가 이동할 경로 (Start -> Goal)
        self.PATH = [
            (50, 550),
            (150, 550),
            (150, 450),
            (250, 450),
            (250, 150),
            (150, 150),
            (150, 50),
            (450, 50),
            (450, 550),
            (750, 550),
            (750, 450),
            (550, 450),
            (550, 250),
            (650, 250),
            (650, 50),
            (750, 50),
        ]

        # ==========================================
        # 3. 게임 시스템 변수 및 메인 루프
        # ==========================================
        self.enemies, self.towers, self.bullets = [], [], []
        self.castle_hp, self.gold, self.score, self.wave = 10, 100, 0, 1
        self.spawned_in_wave, self.timer = 0, 0
        self.font = pygame.font.SysFont("arial", 22, bold=True)

        self.tick = 60

    class Enemy:
        def __init__(self, outer, wave_level):
            self.outer = outer
            self.x, self.y = self.outer.PATH[0]
            self.target_idx = 1  # 다음 목표 지점 번호
            self.speed = random.uniform(1.2, 2.0) + (wave_level * 0.1)
            self.max_hp = 20 + (wave_level * 10)
            self.hp = self.max_hp

        def update(self):
            # 경로 리스트를 순서대로 따라가는 로직
            if self.target_idx < len(self.outer.PATH):
                tx, ty = self.outer.PATH[self.target_idx]
                dist = math.hypot(tx - self.x, ty - self.y)
                if dist > self.speed:
                    self.x += (tx - self.x) / dist * self.speed
                    self.y += (ty - self.y) / dist * self.speed
                else:
                    self.target_idx += 1  # 목표 지점 도착 시 다음 지점으로!
            return self.target_idx >= len(self.outer.PATH)  # 기지 도착 시 True 반환

        def draw(self):
            pygame.draw.circle(
                self.outer.screen, self.outer.RED, (int(self.x), int(self.y)), 15
            )
            # 체력바 (초록색 부분은 남은 체력 비율)
            pygame.draw.rect(
                self.outer.screen,
                self.outer.GREEN,
                (self.x - 15, self.y - 25, (self.hp / self.max_hp) * 30, 5),
            )

    class Bullet:
        def __init__(self, outer, x, y, target):
            self.outer = outer
            self.x, self.y = x, y
            self.target = target
            self.speed = 10
            self.active = True  # 총알의 활성화 상태

        def update(self, enemies):
            # 타겟이 사라졌는지 확인 (다른 타워가 먼저 처치했을 경우)
            if self.target not in enemies:
                self.active = False
                return

            # 타겟을 향해 유도탄처럼 이동
            dist = math.hypot(self.target.x - self.x, self.target.y - self.y)
            if dist > self.speed:
                self.x += (self.target.x - self.x) / dist * self.speed
                self.y += (self.target.y - self.y) / dist * self.speed
            else:
                self.target.hp -= 10  # 명중 시 데미지
                self.active = False

        def draw(self):
            pygame.draw.circle(
                self.outer.screen, self.outer.WHITE, (int(self.x), int(self.y)), 5
            )

    class Tower:
        def __init__(self, outer, x, y):
            self.outer = outer
            self.x, self.y = x, y
            self.range = 150
            self.cooldown = 0

        def update(self, enemies):
            if self.cooldown > 0:
                self.cooldown -= 1
            else:
                # 사정거리 내에 있는 적을 찾아 발사
                for e in enemies:
                    if math.hypot(e.x - self.x, e.y - self.y) <= self.range:
                        self.cooldown = 30  # 발사 후 대기 시간(쿨다운)
                        return self.outer.Bullet(self.outer, self.x, self.y, e)
            return None

        def draw(self):
            pygame.draw.rect(
                self.outer.screen, self.outer.YELLOW, (self.x - 20, self.y - 20, 40, 40)
            )

    """_summary_
    overwriding methods
    """

    def event_prev(self):
        self.screen.fill(self.BLACK)
        # 회색 길 그리기
        if len(self.PATH) > 1:
            pygame.draw.lines(self.screen, (50, 50, 50), False, self.PATH, 40)

        return True

    def event_next(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # 바둑판 눈금 정렬 (그리드 스냅)
            mx, my = pygame.mouse.get_pos()
            grid_x, grid_y = (mx // 40) * 40 + 20, (my // 40) * 40 + 20

            if self.gold >= self.TOWER_COST:
                self.towers.append(self.Tower(self, grid_x, grid_y))
                self.gold -= self.TOWER_COST

        return True

    def update_state(self):
        # --- 웨이브 및 적 생성 로직 ---
        self.timer += 1
        if self.spawned_in_wave < self.wave * 5:
            if self.timer >= 60:  # 1초(60프레임)마다 생성
                self.enemies.append(self.Enemy(self, self.wave))
                self.spawned_in_wave += 1
                self.timer = 0
        elif len(self.enemies) == 0:
            self.wave += 1
            spawned_in_wave = 0
            self.gold += 50  # 웨이브 클리어 보너스

        # --- 객체 업데이트 및 그리기 ---
        for t in self.towers:
            t.draw()
            new_bullet = t.update(self.enemies)
            if new_bullet:
                self.bullets.append(new_bullet)

        for b in self.bullets[:]:
            b.update(self.enemies)
            b.draw()
            if not b.active:
                self.bullets.remove(b)  # 명중했거나 타겟이 사라진 총알 제거

        for e in self.enemies[:]:
            if e.update():  # 기지 도착 시
                self.castle_hp -= 1
                self.enemies.remove(e)
            elif e.hp <= 0:  # 처치 시
                self.gold += self.KILL_REWARD
                self.score += 100
                self.enemies.remove(e)
            else:
                e.draw()

        return True

    def drawing(self):
        # --- UI 표시 ---
        info = self.font.render(
            f"WAVE: {self.wave} | GOLD: {self.gold} | HP: {self.castle_hp} | SCORE: {self.score}",
            True,
            self.WHITE,
        )
        self.screen.blit(info, (20, 10))

        if self.castle_hp <= 0:
            game_over_txt = self.font.render("GAME OVER", True, self.RED)
            self.screen.blit(game_over_txt, (self.width // 2 - 60, self.height // 2))
            return 0

        return self.tick

    def update_display(self):
        pygame.display.flip()

    def ending(self):
        pygame.time.delay(3000)  # 3초 대기 후 종료
        return True


# ==================== 실행 및 검증 ====================
if __name__ == "__main__":
    config_manager = ConfigManager(__file__)
    key = "tower"
    if config_manager.inited:
        config = config_manager.settings.get(key)
        if config == None:
            config = config_manager.dict_to_munchify()
            config_manager.settings[key] = config
            config.WIDTH, config.HEIGHT = 800, 600

            print(config_manager.settings)
            config_manager.save()

        cls_main = TowerDefense(config=config, title="전략 타워 디펜스")
        cls_main.run()
