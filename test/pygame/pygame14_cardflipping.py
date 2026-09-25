import math

import pygame
import random
from game.pygame_frame import GameFrame


class Concentraion(GameFrame):
    def __init__(self):
        super().__init__(__file__, "메모리 게임")
        
        settings = self.config_manager.settings
        config = settings.get('cards')
        if config == None:
            config = {}
            settings['cards'] = config
            config['WIDTH'], config['HEIGHT'] = 800, 600
            config['card_imgs'] = [
                './game/images/jewel/jewel_red.png',
                './game/images/jewel/jewel_green.png',
                './game/images/jewel/jewel_blue.png',
                './game/images/jewel/jewel_yellow.png',
                './game/images/jewel/jewel_rainbow.png',
                './game/images/jewel/jewel_bomb.png',
                './game/images/jewel/jewel_missile_h.png',
                './game/images/jewel/jewel_missile_v.png'
            ],
            config["card_back_img"] = "./game/images/jewel/jewel_back2.png"
            
            self.logger.debug(settings)
            self.config_manager.save()
        
        self.WIDTH, self.HEIGHT = config['WIDTH'], config['HEIGHT']
        
        self.create_screen(width=self.WIDTH, height=self.HEIGHT)
        
        # 1. 이미지  로드
        self.cards = []
        for i in range(len(config["card_imgs"])):
            self.cards.append(pygame.image.load(config["card_imgs"][i]).convert_alpha())
        
        self.card_back = pygame.image.load(config["card_back_img"]).convert_alpha()

        # ==========================================
        # 3. 게임 초기 설정 (객체 생성)
        # ==========================================
        self.total = 12 
        self.cardlist = []
        self.firstcard = None # 첫 번째로 뒤집은 카드 저장용
        self.secondcard = None # 두 번째로 뒤집은 카드 저장용
        self.matched_count = 0  # 맞춘 카드 쌍의 수

        # 타이머 설정
        self.limit_time = 30    # 제한 시간 30초
        self.start_ticks = 0    # 게임 시작 시점 저장용

        # 카드 번호 리스트 생성 및 섞기
        number = [0, 1, 2, 3, 4, 5, 0, 1, 2, 3, 4, 5]
        random.shuffle(number)
        for i in range(self.total):
            self.cardlist.append(self.Card(self, i, number[i])) # 카드 객체 생성 및 리스트에 추가
    
    def ready(self):
        # 3초 동안 카드를 보여주는 단계
        self.screen.fill([0, 0, 0])
        font = pygame.font.SysFont(None, 100)
        text = font.render('Look!', True, [255, 255, 255])
        self.screen.blit(text, (320, 40))
        # 카드 모두 앞면으로 보여주기
        for card in self.cardlist:
            card.front = True
            card.draw()
        pygame.display.update()
        pygame.time.delay(3000)

        # 카드 모두 뒷면으로 돌리기
        for card in self.cardlist:
            card.front = False
        
        # 실제 게임 시작 시점의 틱(ms) 저장
        self.start_ticks = pygame.time.get_ticks()
        
        self.run()
    
    class Card:
        def __init__(self, outer, idx, number): # idx: 카드의 위치 인덱스, number: 카드의 번호
            self.outer = outer
            self.idx = idx
            self.number = number
            # 카드의 x, y 좌표 계산 (4열 기준)
            self.x = (self.idx % 4 + 1) * 150 
            self.y = (self.idx // 4 + 1) * 150 
            self.image = self.outer.cards[number] # pygame.image.load(f'card{number}.png')
            self.rect = self.image.get_rect(x=self.x, y=self.y)
            self.front = False

        def draw(self):
            if self.front:
                self.outer.screen.blit(self.image, (self.x, self.y))
            else:
                back = self.outer.card_back # pygame.image.load('card0.png')
                self.outer.screen.blit(back, (self.x, self.y))
    
    # 마우스 클릭 좌표(xy)가 카드와 겹치는지 확인
    def check(self, xy):
        for card in self.cardlist:
            if card.rect.collidepoint(xy) and not card.front:
                card.front = True
                card.draw()
                pygame.display.update()

                if self.firstcard is None: # 첫 번째 카드가 아직 선택되지 않은 경우
                    self.firstcard = card # 첫 번째 카드로 선택
                else:
                    if self.firstcard != card: # 같은 카드를 두 번 클릭한 경우는 무시
                        self.secondcard = card # 두 번째 카드로 선택
                        pygame.time.delay(500)
                        # 두 카드의 번호가 같으면 matched_count 증가, 다르면 카드 뒤집기
                        if self.firstcard.number == self.secondcard.number:
                            self.matched_count += 1
                        else:
                            # 짝이 맞지 않을 때 빨간색 경고 화면 효과
                            self.screen.fill([200, 0, 0])         # 배경을 빨간색으로 채움
                            for c in self.cardlist: c.draw() # 그 위에 카드들을 다시 그림
                            pygame.display.update()          # 화면 업데이트
                            pygame.time.delay(200)           # 0.2초 동안 빨간 화면 유지

                            self.firstcard.front = False
                            self.secondcard.front = False
                        # 카드 선택 초기화
                        self.firstcard = None
                        self.secondcard = None

    def draw(self, surface):
        surface.fill([0, 0, 0])

        # 시간 계산: (현재 틱 - 시작 틱) // 1000 = 흐른 시간(초)
        elapsed_time = (pygame.time.get_ticks() - self.start_ticks) // 1000
        remaining_time = self.limit_time - elapsed_time

        if remaining_time < 0: remaining_time = 0

        font = pygame.font.SysFont(None, 50)
        color = [255, 255, 255]
        if remaining_time <= 5: color = [255, 0, 0] # 5초 이하면 빨간색 경고

        timer_text = font.render(f"Time: {remaining_time}", True, color)
        self.screen.blit(timer_text, (600, 50))

        for card in self.cardlist:
            card.draw()

        return remaining_time
    
    def event_run(self):
        # pygame.mouse.get_pressed
        # --- 1. 이벤트 처리 ---
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE] or keys[pygame.K_q]:
            return False
        
        keys = pygame.mouse.get_pressed()
        """_summary_
        keys[0]: True if pygame.MOUSEBUTTONDOWN left click else False
        keys[1]: True if pygame.MOUSEBUTTONDOWN center(wheel) click else False
        keys[2]: True if pygame.MOUSEBUTTONDOWN right click else False
        """
        if keys[0]:
            self.check(pygame.mouse.get_pos())
        
        return True 

    def drawing(self):
        # --- 3. 화면 그리기 ---
        remain = self.draw(self.screen)
        # pygame.display.update()
        
        # 승리/패배 판정
        if self.matched_count == 6:
            print("Mission Clear!")
            return 0
        
        elif remain <= 0:
            print("Game Over...")
            return 0
    
        return self.tick


# ==================== 실행 및 검증 ====================
if __name__ == "__main__":
    cls_main = Concentraion()
    cls_main.ready()
