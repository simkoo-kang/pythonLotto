import math

import pygame
import random
from config.config_manager import ConfigManager
from game.pygame_main import GameMain


class Rhythm(GameMain):
    def __init__(self, config, title):
        super().__init__(config, title)
        
        self.width, self.height = config.WIDTH, config.HEIGHT
        
        # 색상 정의
        self.COLOR_TEXT = (255, 255, 255) # 흰색
        self.COLOR_BG = (0, 0, 0)       # 검은색
        self.COLOR_LANE_BG = (30, 30, 30)
        self.COLOR_LANE_LINE = (100, 100, 100)
        self.COLOR_PERFECT = (255, 215, 0)   # 황금색
        self.COLOR_GOOD = (50, 255, 50)     # 연두색
        self.COLOR_MISS = (150, 150, 150)    # 회색

        # 노트를 위한 색상 (랜덤하게 사용)
        self.COLORS_NOTE = [(255, 50, 50), (50, 255, 50), (50, 50, 255), (255, 255, 50)]

        # 2. 게임 환경 변수 설정
        self.LANE_WIDTH = 100
        self.LANE_START_X = (self.width - (self.LANE_WIDTH * 4)) // 2
        self.KEYS = [pygame.K_d, pygame.K_f, pygame.K_j, pygame.K_k]  # 사용할 4개의 키
        self.KEY_NAMES = ['D', 'F', 'J', 'K']

        self.HIT_ZONE_Y = 500        # 판정선 Y 좌표
        self.HIT_ZONE_HEIGHT = 40    # 판정 범위
        self.JUDGE_DISPLAY_X = self.width // 2  # 판정 텍스트 표시 중앙 X
        self.JUDGE_DISPLAY_Y = self.height // 2 - 100 # 판정 텍스트 표시 중앙 Y
        self.KEY_TEXT_Y = self.HIT_ZONE_Y +self. HIT_ZONE_HEIGHT + 10 # 하단 키 텍스트 Y 좌표

        self.notes = []
        self.score = 0
        self.font = pygame.font.SysFont(None, 48)
        self.judge_font = pygame.font.SysFont(None, 80, bold=True)
        self.spawn_timer = 0

        # ===== [수정된 부분] 판정 관련 변수를 main() 함수 내부로 이동 =====
        self.latest_judgement = "" # 마지막 판정 텍스트
        self.judge_color = self.COLOR_TEXT # 마지막 판정 텍스트 색상
        self.judge_timer = 0 # 판정 텍스트 표시 타이머
        # ==================================================================

        self.tick = 60
    
    # 3. 노트 클래스 정의 (객체 지향 접근)
    class Note:
        def __init__(self, outer, lane):
            self.outer = outer
            self.lane = lane
            self.x = self.outer.LANE_START_X + (lane * self.outer.LANE_WIDTH)
            self.y = -50
            self.speed = 7
            self.color = self.outer.COLORS_NOTE[lane]
            self.active = True

        def update(self):
            self.y += self.speed
            if self.y > self.outer.height:
                self.active = False # 화면 밖으로 나가면 비활성화

        def draw(self, surface):
            pygame.draw.rect(surface, self.color, (self.x + 5, self.y, self.outer.LANE_WIDTH - 10, 25), border_radius=5)
    
    def event_prev(self):
        self.screen.fill(self.COLOR_BG)
        return True
    
    """_summary_
    overwriding methods
    """
    def event_next(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in self.KEYS:
                lane_index = self.KEYS.index(event.key)

                for note in self.notes:
                    if note.lane == lane_index and note.active:
                        diff = abs(note.y - self.HIT_ZONE_Y)
                        if diff <= self.HIT_ZONE_HEIGHT // 2: # Perfect
                            self.score += 10
                            self.latest_judgement = "PERFECT"
                            self.judge_color = self.COLOR_PERFECT
                            self.judge_timer = 30
                            note.active = False
                            break
                        elif diff <= self.HIT_ZONE_HEIGHT: # Good
                            self.score += 5
                            self.latest_judgement = "GOOD"
                            self.judge_color = self.COLOR_GOOD
                            self.judge_timer = 30
                            note.active = False
                            break
        
        return True
    
    def update_state(self):
        # --- [B] 로직 업데이트 ---
        # 1. 노트 생성 주기 조절
        self.spawn_timer += 1
        if self.spawn_timer > 25: 
            lane = random.randint(0, 3)
            self.notes.append(self.Note(self, lane))
            self.spawn_timer = 0

        # 2. 노트 이동 및 Miss 판정 처리
        active_notes = []
        for note in self.notes:
            if note.active:
                note.update()
                if note.y > self.height:
                    # 화면을 벗어난 노트는 Miss 처리
                    self.latest_judgement = "MISS"
                    self.judge_color = self.COLOR_MISS
                    self.judge_timer = 30
                else:
                    active_notes.append(note)

        self.notes = active_notes

        # 3. 판정 텍스트 타이머 감소
        if self.judge_timer > 0:
            self.judge_timer -= 1
        else:
            self.latest_judgement = ""
        
        return True

    def drawing(self):
        # --- [C] 화면 그리기 ---
        # 1. 배경 레인 그리기
        for i in range(4):
            rect_x = self.LANE_START_X + i * self.LANE_WIDTH
            pygame.draw.rect(self.screen, self.COLOR_LANE_BG, (rect_x, 0, self.LANE_WIDTH, self.height))
            pygame.draw.line(self.screen, self.COLOR_LANE_LINE, (rect_x, 0), (rect_x, self.height), 2)
        pygame.draw.line(self.screen, self.COLOR_LANE_LINE, (self.LANE_START_X + 4 * self.LANE_WIDTH, 0), (self.LANE_START_X + 4 * self.LANE_WIDTH, self.height), 2)

        # 2. 판정선 그리기
        pygame.draw.rect(
            self.screen,
            self.COLOR_TEXT,
            (self.LANE_START_X, self.HIT_ZONE_Y, self.LANE_WIDTH * 4, self.HIT_ZONE_HEIGHT),
            2,
        )

        # 3. 하단 키 표시 그리기
        for i in range(4):
            key_text = self.font.render(self.KEY_NAMES[i], True, self.COLOR_TEXT)
            text_rect = key_text.get_rect(center=(self.LANE_START_X + (i * self.LANE_WIDTH) + self.LANE_WIDTH // 2, self.KEY_TEXT_Y))
            self.screen.blit(key_text, text_rect)

        # 4. 노트 그리기
        for note in self.notes:
            note.draw(self.screen)

        # 5. 판정 텍스트 출력
        if self.latest_judgement:
            judge_text = self.judge_font.render(self.latest_judgement, True, self.judge_color)
            text_rect = judge_text.get_rect(center=(self.JUDGE_DISPLAY_X, self.JUDGE_DISPLAY_Y))
            self.screen.blit(judge_text, text_rect)

        # 6. 점수 텍스트 출력
        score_text = self.font.render(f"Score: {self.score}", True, self.COLOR_TEXT)
        self.screen.blit(score_text, (20, 20))

        return self.tick
    
    def update_display(self):
        pygame.display.flip()


# ==================== 실행 및 검증 ====================
if __name__ == "__main__":
    config_manager = ConfigManager(__file__)
    key = "rhythm"
    if config_manager.inited:
        config = config_manager.settings.get(key)
        if config == None:
            config = config_manager.dict_to_munchify()
            config_manager.settings[key] = config
            config.WIDTH, config.HEIGHT = 800, 600
            
            print(config_manager.settings)
            config_manager.save()

        cls_main = Rhythm(config=config, title="리듬 게임 - 판정 기능 추가 (오류 수정)")
        cls_main.run()
