import pygame
from config.config_manager import ConfigManager
from game.pygame_main import GameMain
from game.sokoban.sokoban import Sokoban

from util.json_util import Json


class SokobanMain(GameMain):
    def __init__(self, config, title):
        super().__init__(config, title)

        self.width, self.height = (config.WIDTH, config.HEIGHT)
        self.TILE = 60

        self.font = pygame.font.SysFont("arial", 24, True)
        self.large_font = pygame.font.SysFont("arial", 60, True)

        # 색상 설정
        self.BLACK, self.GRAY, self.BLUE = (30, 30, 30), (120, 120, 120), (50, 150, 255)
        self.YELLOW, self.RED, self.WHITE = (
            (255, 200, 50),
            (255, 80, 80),
            (255, 255, 255),
        )
        self.GREEN = (80, 255, 80)

        # 2. 맵 데이터
        # 0: 바닥, 1: 벽, 2: 목적지, 3: 상자, 4: 플레이어
        # 5: 목적지 위의 상자 (상자3 + 목적지2) -> 초기 배치에 있을 수 있으므로 포함
        self.sokoban = Sokoban("./game/sokoban", "sokoban.json")
        self.level = self.sokoban.list[0]["matrix"]
        self.path = self.sokoban.list[0]["path"]

        (
            self.matrix_width,
            self.matrix_height,
            walls,
            targets,
            boxes,
            player_pos,
        ) = self.sokoban.analyze_map(self.level)

        # self.level = [[0] * self.matrix_width for _ in range(self.matrix_height)]

        self.targets = Json.to_list(targets)

        self.matrix_index = 0

        self.map_width = self.matrix_width * self.TILE
        self.map_height = self.matrix_height * self.TILE
        self.offset_x = (self.width - self.map_width) // 2
        self.offset_y = (self.height - self.map_height) // 2 + 20

        self.player, self.boxes, self.moves = self.reset_game(self.level)
        self.game_state = "PLAYING"  # 상태: PLAYING 또는 CLEAR

        self.tick = 60

    def reset_game(self, grid):
        # idx = self.matrix_index % self.matrix_height
        # self.level = self.sokoban.list[idx]["matrix"]
        # self.matrix_index += 1

        player, boxes = [], []
        for r in range(len(grid)):
            for c in range(len(grid[r])):
                if grid[r][c] == 4:
                    player = [c, r]
                elif grid[r][c] == 3:
                    boxes.append([c, r])

        # 💡 상자 위치를 벽과 겹치지 않는 빈 공간(y=3 줄)으로 모두 내렸습니다.
        return player, boxes, 0

    """_summary_
    overwriding methods
    """

    def event_next(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:  # 언제든 R을 누르면 재시작
                self.matrix_index += 1
                idx = self.matrix_index % self.matrix_height
                self.level = self.sokoban.list[idx]["matrix"]
                self.path = self.sokoban.list[idx]["path"]

                self.player, self.boxes, self.moves = self.reset_game(self.level)
                self.game_state = "PLAYING"

            if self.game_state == "PLAYING":
                dx, dy = 0, 0
                if event.key == pygame.K_UP:
                    dy = -1
                elif event.key == pygame.K_DOWN:
                    dy = 1
                elif event.key == pygame.K_LEFT:
                    dx = -1
                elif event.key == pygame.K_RIGHT:
                    dx = 1

                if dx != 0 or dy != 0:
                    nx, ny = self.player[0] + dx, self.player[1] + dy

                    if self.level[ny][nx] != 1:  # 벽이 아닐 때
                        if [nx, ny] in self.boxes:  # 앞에 상자가 있을 때
                            nnx, nny = nx + dx, ny + dy
                            # 상자 너머가 벽이 아니고, 다른 상자도 없다면
                            if (
                                self.level[nny][nnx] != 1
                                and [nnx, nny] not in self.boxes
                            ):
                                box_idx = self.boxes.index([nx, ny])
                                self.boxes[box_idx] = [nnx, nny]
                                self.player = [nx, ny]
                                self.moves += 1
                        else:  # 앞에 상자도 벽도 없을 때
                            self.player = [nx, ny]
                            self.moves += 1

                # 💡 승리 조건 체크: 모든 상자가 목적지 위에 있는지 확인
                clear = True
                for b in self.boxes:
                    if b not in self.targets:
                        clear = False
                        break

                if clear:
                    self.game_state = "CLEAR"

        return True

    def drawing(self):
        # --- 화면 그리기 ---
        self.screen.fill(self.BLACK)

        # 맵 그리기 (offset_x, offset_y를 더해서 정중앙에 그림)
        for y in range(len(self.level)):
            for x in range(len(self.level[y])):
                rect_x = self.offset_x + x * self.TILE
                rect_y = self.offset_y + y * self.TILE

                if self.level[y][x] == 1:  # 벽
                    pygame.draw.rect(
                        self.screen, self.GRAY, (rect_x, rect_y, self.TILE, self.TILE)
                    )
                    pygame.draw.rect(
                        self.screen,
                        self.BLACK,
                        (rect_x, rect_y, self.TILE, self.TILE),
                        2,
                    )  # 벽 테두리
                elif self.level[y][x] == 2:  # 목적지
                    pygame.draw.rect(
                        self.screen, self.RED, (rect_x, rect_y, self.TILE, self.TILE), 3
                    )

        # 상자 그리기
        for b in self.boxes:
            bx = self.offset_x + b[0] * self.TILE
            by = self.offset_y + b[1] * self.TILE
            # 상자가 목적지 위에 있으면 초록색으로, 아니면 노란색으로 변경
            color = self.GREEN if b in self.targets else self.YELLOW
            pygame.draw.rect(
                self.screen, color, (bx + 2, by + 2, self.TILE - 4, self.TILE - 4)
            )

        # 주인공 그리기
        px = self.offset_x + self.player[0] * self.TILE
        py = self.offset_y + self.player[1] * self.TILE
        pygame.draw.rect(
            self.screen, self.BLUE, (px + 5, py + 5, self.TILE - 10, self.TILE - 10)
        )

        # UI (이동 횟수 표시)
        ui_txt = self.font.render(
            f"MOVES: {self.moves}  |  Press 'R' to Restart", True, self.WHITE
        )
        self.screen.blit(ui_txt, (20, 20))

        path_txt = self.font.render(f"{self.path} ({len(self.path)})", True, self.WHITE)
        self.screen.blit(
            path_txt,
            (
                self.width // 2 - path_txt.get_width() // 2,
                self.offset_y - 1 * self.TILE,
            ),
        )

        # 클리어 메시지
        if self.game_state == "CLEAR":
            clear_txt = self.large_font.render("LEVEL CLEAR!", True, self.YELLOW)
            self.screen.blit(
                clear_txt,
                (self.width // 2 - clear_txt.get_width() // 2, self.height // 2 - 50),
            )

        # 기본 속도 12에서 시작, 사과를 2개(20점) 먹을 때마다 1씩 빨라짐
        return self.tick

    def update_display(self):
        pygame.display.flip()


# ==================== 실행 및 검증 ====================
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
    else:
        if config.get("file_path") == None:
            config["file_path"] = "./game/sokoban"
            config["file_name"] = "sokoban.json"

            print(config)
            config_manager.save()

    cls_main = SokobanMain(config=config, title="스탠다드 상자 밀기 퍼즐")
    cls_main.run()
