import math

import pygame
import random
from game.pygame_frame import GameFrame


class ShootingSpace(GameFrame):
    def __init__(self):
        super().__init__(__file__, "슈팅 게임")
        
        settings = self.config_manager.settings
        config = settings.get('space')
        if config == None:
            config = {}
            settings['space'] = config
            config['WIDTH'], config['HEIGHT'] = 800, 600
            config['bg_img'] = "./game/images/space/space.jpg"
            config['fighter_img'] = "./game/images/space/space_ship2.png"
            config['missile_img'] = "./game/images/space/missile.png"
            config['explosion_img'] = "./game/images/space/explosion.png"
            
            self.logger.debug(settings)
            self.config_manager.save()
        
        self.WIDTH, self.HEIGHT = config['WIDTH'], config['HEIGHT']
        
        # 1. 이미지  로드
        # 객체를 생성할 때마다 이미지를 매번 불러오면 게임이 느려지므로, 
        # 클래스 밖에서 한 번만 불러와서 변수에 저장해 둡니다.
        self.bg_img = pygame.image.load(config['bg_img'])
        self.bg_img = pygame.transform.scale(self.bg_img, (self.WIDTH, self.HEIGHT))
        
        self.create_screen(width=self.WIDTH, height=self.HEIGHT)

        self.fighter_img = pygame.transform.rotozoom(pygame.image.load(config['fighter_img']), False, 0.5).convert_alpha()
        self.missile_img = pygame.transform.rotozoom(pygame.image.load(config['missile_img']), False, 0.3).convert_alpha()
        self.explosion_img = pygame.transform.rotozoom(pygame.image.load(config['explosion_img']), False, 0.2).convert_alpha()

        # 운석 이미지는 1~7번까지 리스트로 준비
        self.rock_imgs = [pygame.transform.rotozoom(pygame.image.load(f'./game/images/space/rock{i}.png').convert_alpha(), False, 0.2) for i in range(1, 8)]
        self.score_font = pygame.font.SysFont("sans", 30)

        # ==========================================
        # 3. 게임 초기 설정 (객체 생성)
        # ==========================================
        self.fighter = self.Fighter(outer=self)
        self.missile_list = []
        self.rock = self.Rock(self)

        self.score = 0
    
    class Fighter:
        def __init__(self, outer):
            self.outer = outer
            self.image = self.outer.fighter_img
            self.rect = self.image.get_rect()
            self.width = self.outer.WIDTH
            self.height = self.outer.HEIGHT
            
            self.rect.centerx = self.width // 2
            self.rect.bottom = self.height
            self.speed = 5

        def move(self, keys):
            # 상태(State) 기반 부드러운 이동
            if keys[pygame.K_LEFT]:
                self.rect.x -= self.speed
            if keys[pygame.K_RIGHT]:
                self.rect.x += self.speed

            # 화면 이탈 방지
            if self.rect.left < 0:
                self.rect.left = 0
            elif self.rect.right > self.width:
                self.rect.right = self.width

        def draw(self, surface):
            surface.blit(self.image, self.rect)


    class Missile:
        def __init__(self, outer, x, y):
            self.outer = outer
            self.image = self.outer.missile_img
            self.rect = self.image.get_rect()
            # 전투기의 위치를 전달받아 미사일 시작 위치 설정
            self.rect.centerx = x
            self.rect.bottom = y
            self.speed = 10

        def update(self):
            self.rect.y -= self.speed

        def draw(self, surface):
            surface.blit(self.image, self.rect)


    class Rock:
        def __init__(self, outer):
            self.outer = outer
            self.speed = random.randint(3, 7) # 운석마다 속도도 다르게
            self.images = self.outer.rock_imgs
            self.width = self.outer.WIDTH
            self.height = self.outer.HEIGHT
            self.reset() # 처음 생성될 때 위치 초기화

        def reset(self):
            # 화면 위에서 랜덤한 이미지와 랜덤한 x좌표로 다시 나타남
            self.image = random.choice(self.images)
            self.rect = self.image.get_rect()
            self.rect.x = random.randint(0, self.width - self.rect.width)
            self.rect.y = -self.rect.height

        def update(self):
            self.rect.y += self.speed
            # 화면 아래로 완전히 벗어나면 다시 위로 리셋
            if self.rect.top > self.height:
                self.reset()

        def draw(self, surface):
            surface.blit(self.image, self.rect)
    
    def event_run(self):
        # pygame.mouse.get_pressed
        # --- 1. 이벤트 처리 ---
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE] or keys[pygame.K_q]:
            return False
        
        if keys[pygame.K_SPACE]:
            # 미사일 객체를 생성할 때 전투기의 현재 위치를 넘겨줌
            new_missile = self.Missile(self, self.fighter.rect.centerx, self.fighter.rect.top)
            self.missile_list.append(new_missile)
        
        return True 

    def update_state(self):
        # --- 2. 로직 업데이트 (객체들의 행동) ---
        keys = pygame.key.get_pressed()
        self.fighter.move(keys)
        self.rock.update()
        
        # 미사일 이동 및 충돌 처리
        for m in self.missile_list[:]:
            m.update()

            # 운석 충돌
            if m.rect.colliderect(self.rock.rect):
                self.missile_list.remove(m)
                self.score += 1
                self.screen.blit(self.explosion_img, self.rock.rect)
                self.rock.reset() # 운석을 새것으로 초기화
                continue

            # 화면 밖 이탈
            if m.rect.bottom <= 0:
                self.missile_list.remove(m)
    
        # 전투기와 운석 충돌
        if self.rock.rect.colliderect(self.fighter.rect):
            return False
        
        return True

    def drawing(self):
    # --- 3. 화면 그리기 ---
        self.screen.blit(self.bg_img, (0, 0))
        self.fighter.draw(self.screen)
        self.rock.draw(self.screen)

        for m in self.missile_list:
            m.draw(self.screen)

        # 텍스트 출력 (f-string 사용)
        text = self.score_font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(text, (20, 50))
        return self.tick


# ==================== 실행 및 검증 ====================
if __name__ == "__main__":
    cls_main = ShootingSpace()
    cls_main.run()
