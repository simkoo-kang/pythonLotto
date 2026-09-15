import math

import pygame
import random
from game.pygame_frame import GameFrame


class Sniper(GameFrame):
    def __init__(self):
        super().__init__(__file__, "스나이퍼: VIP 헬기 구출 작전")
        
        settings = self.config_manager.settings
        config = settings.get('sniper')
        if config == None:
            config = {}
            settings['sniper'] = config
            config['WIDTH'], config['HEIGHT'] = 800, 600
            config['WORLD_W'], config['WORLD_H'] = 2000, 1500
            config['vip_x'], config['vip_y'] = 200, 750
            config['spawn_event_timemillis'] = 1500
            
            self.logger.debug(settings)
            self.config_manager.save()
        
        self.width, self.height = config['WIDTH'], config['HEIGHT']
        self.world_w, self.world_h = config['WORLD_W'], config['WORLD_H']
        
        self.create_screen(width=self.width, height=self.height)
        
        # 1. 이미지  로드
        self.bg = pygame.Surface((self.world_w, self.world_h))
        self.bg.fill((40, 50, 40)) 
        for i in range(0, self.world_w, 200):
            pygame.draw.line(self.bg, (60, 80, 60), (i, 0), (i, self.world_h), 2)
            pygame.draw.line(self.bg, (60, 80, 60), (0, i), (self.world_w, i), 2)

        # 스코프 오버레이 레이어 만들기
        self.scope_layer = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.scope_layer.fill((0, 0, 0, 180)) 
        pygame.draw.circle(self.scope_layer, (0, 0, 0, 0), (self.width//2, self.height//2), 250) 
        pygame.draw.circle(self.scope_layer, (0, 0, 0), (self.width//2, self.height//2), 250, 5) 

        self.bg_x, self.bg_y = 0, 0
        self.score, self.is_firing = 0, 0
        self.game_over = False
        self.game_won = False
        
        # ==========================================
        # 3. 게임 초기 설정 (객체 생성)
        # ==========================================
        self.vip = self.VIP(self, config['vip_x'], config['vip_y'])
        self.enemies = []
        self.enemies_count = 12

        self.SPAWN_EVENT = pygame.USEREVENT + 1
        pygame.time.set_timer(self.SPAWN_EVENT, config['spawn_event_timemillis'])

        self.font = pygame.font.SysFont("arial", 30, bold=True)
        self.large_font = pygame.font.SysFont("arial", 60, bold=True)
        
        self.tick = 60
    
    class VIP:
        def __init__(self, outer, x, y):
            self.outer = outer
            self.x, self.y = x, y
            self.w, self.h = 40, 60
            self.hp, self.max_hp = 100, 100
            self.speed = 0.8

        def update(self):
            self.x += self.speed

        def draw(self, screen, bg_x, bg_y): # 배경 이동에 따른 VIP의 화면 내 위치 계산
            v_draw_x = (self.x + bg_x) % self.outer.world_w
            v_draw_y = (self.y + bg_y) % self.outer.world_h
            pygame.draw.rect(screen, (50, 150, 255), (v_draw_x, v_draw_y, self.w, self.h))
            # 체력바
            pygame.draw.rect(screen, (255, 0, 0), (v_draw_x, v_draw_y - 15, self.w, 8))
            hp_w = (self.hp / self.max_hp) * self.w
            pygame.draw.rect(screen, (0, 255, 0), (v_draw_x, v_draw_y - 15, max(0, hp_w), 8))

    class Enemy:
        def __init__(self, outer, x, y):
            self.outer = outer
            self.x, self.y = x, y
            self.w, self.h = 60, 80
            self.speed = random.uniform(1.0, 2.0) # 적마다 다른 속도로 이동

        def update(self, target_vip):
            dx, dy = target_vip.x - self.x, target_vip.y - self.y # VIP와의 거리 계산
            dist = math.hypot(dx, dy)
            if dist > 50: # 거리가 충분히 멀면 VIP를 향해 이동, 너무 가까우면 공격
                self.x += (dx/dist) * self.speed
                self.y += (dy/dist) * self.speed
            else:
                target_vip.hp -= 0.5 

        def draw(self, screen, bg_x, bg_y):
            draw_x = (self.x + bg_x) % self.outer.world_w # 배경 이동에 따른 적의 화면 내 위치 계산
            draw_y = (self.y + bg_y) % self.outer.world_h
            
            # 화면 밖에 있는 적은 그리지 않음 (성능 최적화)
            if -100 < draw_x < self.outer.width + 100 and -100 < draw_y < self.outer.height + 100:
                pygame.draw.rect(screen, (200, 50, 50), (draw_x, draw_y, self.w, self.h))
                pygame.draw.rect(screen, (255, 255, 255), (draw_x, draw_y, self.w, self.h), 2)
    
    """_summary_
    overwriding methods
    """
    def event_next(self, event):
        if not self.game_over and not self.game_won:
            if event.type == self.SPAWN_EVENT:
                if len(self.enemies) < self.enemies_count:
                    self.enemies.append(self.Enemy(self, random.randint(0, self.world_w), random.randint(0, self.world_h)))

            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.is_firing == 0: # 사격 반동이 없는 상태에서만 사격 가능
                    self.is_firing = 10 # 사격 반동
                    for en in self.enemies[:]: # 총알이 적과 충돌하는지 확인
                        sx = (en.x + self.bg_x) % self.world_w
                        sy = (en.y + self.bg_y) % self.world_h
                        if pygame.Rect(sx, sy, en.w, en.h).collidepoint(self.width//2, self.height//2):
                            score += 100
                            self.enemies.remove(en)
                            break
        
        return True
    
    def event_run(self):
        if not self.game_over and not self.game_won:
            mx, my = pygame.mouse.get_pos()
            self.bg_x -= (mx - self.width//2) * 0.1 # 마우스 위치에 따라 배경 이동
            self.bg_y -= (my - self.height//2) * 0.1

            self.vip.update()
            # 안전 지대(Safe Zone)에 도착하면 승리! (WORLD_W - 250)
            if self.vip.x >= self.world_w - 250:
                self.game_won = True
            if self.vip.hp <= 0:
                self.game_over = True
            for en in self.enemies:
                en.update(self.vip)
        
        return True 

    def drawing(self):
        # --- 3. 화면 그리기 ---
        self.screen.fill((0, 0, 0))
        
        # 배경 타일링 그리기 (목적: 배경이 움직여도 끊김 없이 이어지도록)
        lx, ly = self.bg_x % self.world_w, self.bg_y % self.world_h # 배경의 왼쪽 상단 좌표 계산
        self.screen.blit(self.bg, (lx - self.world_w, ly - self.world_h)) # 왼쪽 위
        self.screen.blit(self.bg, (lx, ly - self.world_h)) # 오른쪽 위
        self.screen.blit(self.bg, (lx - self.world_w, ly)) # 왼쪽 아래
        self.screen.blit(self.bg, (lx, ly)) # 오른쪽 아래

        # 안전 지대(SAFE ZONE) 및 헬기 착륙장 'H' 그리기
        sz_draw_x = (self.world_w - 250 + self.bg_x) % self.world_w
        sz_draw_y = (700 + self.bg_y) % self.world_h

        # 초록색 테두리와 텍스트
        pygame.draw.rect(self.screen, (0, 255, 100), (sz_draw_x, sz_draw_y, 250, 160), 4)
        sz_text = self.font.render("SAFE ZONE", True, (0, 255, 100))
        self.screen.blit(sz_text, (sz_draw_x + 35, sz_draw_y - 40))

        # 헬리패드 마크 (원과 H 그리기)
        center_x = sz_draw_x + 125
        center_y = sz_draw_y + 80
        pygame.draw.circle(self.screen, (0, 255, 100), (int(center_x), int(center_y)), 60, 5) # 원
        pygame.draw.line(self.screen, (0, 255, 100), (center_x - 30, center_y - 35), (center_x - 30, center_y + 35), 10) # H 왼쪽 기둥
        pygame.draw.line(self.screen, (0, 255, 100), (center_x + 30, center_y - 35), (center_x + 30, center_y + 35), 10) # H 오른쪽 기둥
        pygame.draw.line(self.screen, (0, 255, 100), (center_x - 30, center_y), (center_x + 30, center_y), 10) # H 가운데 연결선

        # 캐릭터 그리기
        self.vip.draw(self.screen, self.bg_x, self.bg_y)
        for en in self.enemies: en.draw(self.screen, self.bg_x, self.bg_y)

        # 총구 그리기 (화면 중앙 하단에 고정)
        gun_recoil = self.is_firing * 4 
        gun_x = self.width//2 - 40 
        pygame.draw.rect(self.screen, (30, 30, 30), (gun_x, self.height - 200 + gun_recoil, 80, 200)) # 총기 몸체
        pygame.draw.rect(self.screen, (10, 10, 10), (self.width//2 - 10, self.height - 250 + gun_recoil, 20, 100)) # 총구

        # 스코프 오버레이 및 십자선
        self.screen.blit(self.scope_layer, (0, 0))
        pygame.draw.line(self.screen, (0, 0, 0), (self.width//2 - 250, self.height//2), (self.width//2 + 250, self.height//2), 2)
        pygame.draw.line(self.screen, (0, 0, 0), (self.width//2, self.height//2 - 250), (self.width//2, self.height//2 + 250), 2)

        # 사격 애니메이션
        if self.is_firing > 0:
            pygame.draw.circle(self.screen, (255, 200, 0), (self.width//2, self.height//2), self.is_firing * 5, 3)
            self.is_firing -= 1

        pygame.draw.circle(self.screen, (255, 0, 0), (self.width//2, self.height//2), 5) 

        # UI 텍스트 출력
        score_surf = self.font.render(f"SCORE: {self.score:05d}  VIP HP: {int(max(0, self.vip.hp))}%", True, (255, 255, 255))
        self.screen.blit(score_surf, (20, 20))

        if self.game_over:
            self.screen.blit(self.large_font.render("MISSION FAILED", True, (255, 50, 50)), (150, 250))
        elif self.game_won:
            self.screen.blit(self.large_font.render("MISSION CLEAR", True, (50, 255, 50)), (150, 250))

        return self.tick


# ==================== 실행 및 검증 ====================
if __name__ == "__main__":
    cls_main = Sniper()
    cls_main.run()
