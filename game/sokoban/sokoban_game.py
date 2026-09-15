import pygame
import sys
import copy
from config.config_manager import ConfigManager
from game.pygame_main import GameMain

# 1. 기본 설정 및 색상 정의
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 480
GRID_SIZE = 40  # 각 타일의 크기 (40x40 픽셀)

# RGB 색상 설정
COLOR_BG = (240, 240, 240)  # 바탕 배경 (연한 회색)
COLOR_WALL = (127, 140, 141)  # 벽 (회색)
COLOR_FLOOR = (223, 230, 233)  # 바닥 (밝은 회색)
COLOR_TARGET = (255, 234, 167)  # 목적지 (노란색)
COLOR_PLAYER = (116, 185, 255)  # 플레이어 (파란색)
COLOR_BOX = (230, 126, 34)  # 일반 상자 (주황색)
COLOR_BOX_READY = (46, 204, 113)  # 목적지에 들어간 상자 (초록색)

# 2. 스테이지 맵 데이터 정의
# 0: 바닥, 1: 벽, 2: 목적지, 3: 상자, 4: 플레이어
INITIAL_MAP = [
    #     ,
    #  ,
    #  ,
    #  ,
    #  ,
    #  ,
    #  ,
    #  ,
    #  ,
    #  ,
    #  ,
    #     [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]


class SokobanGame(GameMain):
    def __init__(self, config, title):
        super().__init__(config=config, title=title)

        self.width, self.height = config.WIDTH, config.HEIGHT

        self.font = pygame.font.SysFont("malgungothic", 24)  # 윈도우 맑은고딕 폰트 적용
        self.reset_game()

    def reset_game(self):
        # 맵 데이터 복제 및 초기 맵 분리 저장
        self.map_data = copy.deepcopy(INITIAL_MAP)
        self.player_x = 0
        self.player_y = 0
        self.game_over = False

        # 플레이어 시작 위치 검색 및 바닥 처리
        for y in range(len(self.map_data)):
            for x in range(len(self.map_data[y])):
                if self.map_data[y][x] == 4:
                    self.player_x = x
                    self.player_y = y
                    self.map_data[y][x] = 0

    def move_player(self, dx, dy):
        if self.game_over:
            return

        next_x = self.player_x + dx
        next_y = self.player_y + dy

        # 이동하려는 칸이 벽(1)이면 이동 불가
        if INITIAL_MAP[next_y][next_x] == 1:
            return

        # 이동하려는 칸에 상자(3)가 있는 경우
        if self.map_data[next_y][next_x] == 3:
            box_next_x = next_x + dx
            box_next_y = next_y + dy

            # 상자가 이동할 다음 칸이 벽이 아니고 다른 상자도 없다면 밀기 성공
            if (
                INITIAL_MAP[box_next_y][box_next_x] != 1
                and self.map_data[box_next_y][box_next_x] != 3
            ):
                self.map_data[next_y][next_x] = 0  # 기존 상자 자리 비우기
                self.map_data[box_next_y][box_next_x] = 3  # 새로운 자리에 상자 배치
                self.player_x = next_x  # 플레이어 이동
                self.player_y = next_y
        else:
            # 상자가 없는 빈 바닥이나 목적지면 그냥 이동
            self.player_x = next_x
            self.player_y = next_y

        self.check_win()

    def check_win(self):
        # 모든 목적지(2) 자리에 상자(3)가 배치되었는지 검사
        for y in range(len(INITIAL_MAP)):
            for x in range(len(INITIAL_MAP[y])):
                if INITIAL_MAP[y][x] == 2 and self.map_data[y][x] != 3:
                    return
        self.game_over = True

    def draw(self):
        self.screen.fill(COLOR_BG)

        # 맵 그리기
        for y in range(len(self.map_data)):
            for x in range(len(self.map_data[y])):
                rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)

                # 1. 배경 레이어 (벽, 바닥, 목적지)
                base = INITIAL_MAP[y][x]
                if base == 1:
                    pygame.draw.rect(self.screen, COLOR_WALL, rect)
                elif base == 2:
                    pygame.draw.rect(self.screen, COLOR_TARGET, rect)
                else:
                    pygame.draw.rect(self.screen, COLOR_FLOOR, rect)

                # 타일 경계선 그리기
                pygame.draw.rect(self.screen, (200, 200, 200), rect, 1)

                # 2. 동적 오브젝트 레이어 (상자)
                if self.map_data[y][x] == 3:
                    box_color = COLOR_BOX_READY if base == 2 else COLOR_BOX
                    # 상자는 조금 더 작게 안쪽에 그림
                    box_rect = rect.inflate(-8, -8)
                    pygame.draw.rect(self.screen, box_color, box_rect)
                    pygame.draw.rect(self.screen, (0, 0, 0), box_rect, 2)

        # 3. 플레이어 그리기
        player_rect = pygame.Rect(
            self.player_x * GRID_SIZE, self.player_y * GRID_SIZE, GRID_SIZE, GRID_SIZE
        ).inflate(-6, -6)
        pygame.draw.ellipse(self.screen, COLOR_PLAYER, player_rect)
        pygame.draw.ellipse(self.screen, (0, 0, 0), player_rect, 2)

        # 4. 상단 텍스트 안내 및 게임 오버 서페이스
        if self.game_over:
            # 안내 문구 배경 박스
            text_bg = pygame.Rect(40, 200, 400, 80)
            pygame.draw.rect(self.screen, (0, 0, 0), text_bg)

            text_surface = self.font.render(
                "🎉 클리어! (R키를 눌러 재시작)", True, (255, 255, 255)
            )
            text_rect = text_surface.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            )
            self.screen.blit(text_surface, text_rect)

        pygame.display.flip()

    def run(self):
        while True:
            self.clock.tick(30)  # 30 FPS 제한

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.move_player(0, -1)
                    elif event.key == pygame.K_DOWN:
                        self.move_player(0, 1)
                    elif event.key == pygame.K_LEFT:
                        self.move_player(-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        self.move_player(1, 0)
                    elif event.key == pygame.K_r:  # R키 누르면 맵 초기화
                        self.reset_game()

            self.draw()


if __name__ == "__main__":
    config_manager = ConfigManager(__file__)
    key = "sokoban"
    config = config_manager.settings.get(key)
    if config == None:
        config = config_manager.dict_to_munchify()
        config_manager.settings[key] = config
        config.WIDTH, config.HEIGHT = 800, 600

        print(config_manager.settings)
        config_manager.save()

    cls_main = SokobanGame(config=config, title="스탠다드 상자 밀기 퍼즐")
    cls_main.run()
