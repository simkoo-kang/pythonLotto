"""
파이게임 기본 구조
"""

from pathlib import Path
import sys

import pygame
from util.log_util import LogUtil
from config.config_manager import ConfigManager
from lotto.myfilter.base.crange.sectionrange_filter import SectionRangeFilter
from class_main import ClassMain


class GameMain(ClassMain):
    def __init__(self, config, title: str = None, is_init: bool = True):
        super().__init__(str(Path(__file__).parent))

        self.config = config
        if title == None:
            title = "GameMain"

        self.title = title

        if is_init:
            pygame.init()  # 2. 파이게임 초기화
            self.create_screen(config.WIDTH, config.HEIGHT)

    def create_screen(self, width, height):
        self.screen = pygame.display.set_mode(
            (width, height)
        )  # 3. 게임 화면 만들기 (가로 400, 세로 300)
        pygame.display.set_caption(title=self.title)
        self.clock = pygame.time.Clock()  # 클럭 설정 (FPS 조절용)

        # 실제 게임 시작 시점의 틱(ms) 저장
        self.start_tick = pygame.time.get_ticks()
        self.tick = 60

    def get_start_tick(self):
        return self.start_tick

    def get_tick(self):
        return self.tick

    def set_tick(self, tick: int = 60):
        self.tick = tick

    #  4-1. 이벤트 처리 (키보드, 마우스 입력, 창 닫기 등)
    def event_process(self) -> bool:
        if not self.event_prev():
            return False

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN
                and (event.key == pygame.K_q or event.key == pygame.K_ESCAPE)
            ):  # 창 닫기(X) 버튼을 눌렀을 때
                return False

            if not self.event_next(event):
                return False

        return self.event_run()

    def event_prev(self):
        return True

    def event_next(self, event) -> bool:
        return True

    def event_run(self):
        """_summary_
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE] or keys[pygame.K_q]:
            return False

        keys = pygame.mouse.get_pressed()
        keys[0]: True if pygame.MOUSEBUTTONDOWN left click else False
        keys[1]: True if pygame.MOUSEBUTTONDOWN center(wheel) click else False
        keys[2]: True if pygame.MOUSEBUTTONDOWN right click else False
        if keys[0]:
            self.check(pygame.mouse.get_pos())
        """
        return True

    def update_state(self) -> bool:
        return True

    """_summary_
    Returns:
        tick value: int
    """

    def drawing(self) -> int:
        self.screen.fill("white")  # 화면을 하얀색으로 채우기
        return 60

    def update_display(self):
        pygame.display.update()  # 화면 업데이트 (그린 내용을 화면에 반영)
        # pygame.display.flip() # 전체 화면 갱신

    def ending(self):
        return True

    def run(self):
        running = True  # 게임 루프 제어 변수
        # 4. 이벤트 루프 실행 (게임이 실행되는 동안 무한 반복)
        while running:
            # 4-1. 이벤트 처리 (키보드, 마우스 입력, 창 닫기 등)
            running = self.event_process()

            # for event in pygame.event.get():
            #     if event.type == pygame.QUIT:  # 창 닫기(X) 버튼을 눌렀을 때
            #         running = False

            # 4-2. 게임 상태 업데이트 (캐릭터 이동, 충돌 체크 등)
            if running:
                running = self.update_state()

                if running:
                    # 4-3. 게임 화면 그리기
                    tick = self.drawing()
                    # 화면 업데이트 (그린 내용을 화면에 반영)
                    self.update_display()

                    if tick < 1:
                        running = self.ending()
                    else:
                        self.clock.tick(tick)  # FPS 설정 (초당 60프레임)

        pygame.quit()  # 5. 게임 종료
        sys.exit()


# ==================== 실행 및 검증 ====================
if __name__ == "__main__":
    config_manager = ConfigManager(__file__)
    if config_manager.inited:
        config = config_manager.settings.get("default")

        gamemain = GameMain(config=config, title="실행 및 검증")
        # gamemain.create_screen(800, 600)
        gamemain.run()
