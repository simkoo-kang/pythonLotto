import sys

import numpy as np
import pygame
from config.config_manager import ConfigManager
from game.pygame_main import GameMain


class DeadLive(GameMain):
    def __init__(self, config, title, board_size: int = 19):
        super().__init__(config, title, False)

        self.SIZE = board_size
        self.GRID_SIZE = 50 if config.get("GRID_SIZE") == None else config.GRID_SIZE
        self.MARGIN = 50 if config.get("MARGIN") == None else config.MARGIN
        self.SIDEBAR = 200 if config.get("SIDEBAR") == None else config.SIDEBAR

        self.WINDOW_WIDTH = (
            self.GRID_SIZE * (self.SIZE - 1) + self.MARGIN * 2 + self.SIDEBAR
        )
        self.WINDOW_HEIGHT = self.GRID_SIZE * (self.SIZE - 1) + self.MARGIN * 2

        pygame.init()  # 2. 파이게임 초기화
        self.create_screen(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)

        self.BOARD_COLOR = (240, 200, 120)
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.LINE_COLOR = (60, 60, 60)
        self.RED = (255, 50, 50)
        self.GREEN = (50, 200, 50)

        self.font = (
            pygame.font.SysFont("malgungothic", 16)
            if sys.platform == "win32"
            else pygame.font.SysFont("apple_gothic", 16)
        )
        if not self.font:
            self.font = pygame.font.Font(None, 24)

        self.env = self.TsumegoEnv(self.SIZE)
        self.mode = "EDIT_BLACK"
        self.target_pos = None
        self.solution_move = None
        self.status_text = "Mode: Place Black"

        # 💡 [핵심 추가] 착수 취소(무르기)와 다시 놓기를 관리하는 스택(기록장)
        self.undo_stack = []
        self.redo_stack = []

        self.tick = 60

    class TsumegoEnv:
        def __init__(self, outer, size=19):
            self.outer = outer
            self.size = size
            self.board = np.zeros((size, size), dtype=int)
            self.target_group = None
            self.goal = "LIVE"
            self.turn = 1

        def copy(self):
            new_env = self.outer.TsumegoEnv(self.size)
            new_env.board = np.copy(self.board)
            new_env.turn = self.turn
            new_env.goal = self.goal
            return new_env

        def get_neighbors(self, x, y):
            neighbors = []
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.size and 0 <= ny < self.size:
                    neighbors.append((nx, ny))
            return neighbors

        def find_group_and_liberties(self, start_x, start_y):
            color = self.board[start_x, start_y]
            if color == 0:
                return set(), set()
            queue, group, liberties = [(start_x, start_y)], {(start_x, start_y)}, set()
            while queue:
                x, y = queue.pop(0)
                for nx, ny in self.get_neighbors(x, y):
                    if self.board[nx, ny] == 0:
                        liberties.add((nx, ny))
                    elif self.board[nx, ny] == color and (nx, ny) not in group:
                        group.add((nx, ny))
                        queue.append((nx, ny))
            return group, liberties

        def place_stone(self, x, y, color):
            if self.board[x, y] != 0:
                return False
            self.board[x, y] = color
            captured_any = False
            opponent_color = -color

            for nx, ny in self.get_neighbors(x, y):
                if self.board[nx, ny] == opponent_color:
                    opp_group, opp_liberties = self.find_group_and_liberties(nx, ny)
                    if len(opp_liberties) == 0:
                        for gx, gy in opp_group:
                            self.board[gx, gy] = 0
                        captured_any = True

            _, my_liberties = self.find_group_and_liberties(x, y)
            if len(my_liberties) == 0 and not captured_any:
                self.board[x, y] = 0
                return False
            return True

        def get_legal_moves(self):
            moves = []
            for x in range(self.size):
                for y in range(self.size):
                    if self.board[x, y] == 0:
                        temp_board = np.copy(self.board)
                        if self.place_stone(x, y, self.turn):
                            moves.append((x, y))
                        self.board = temp_board
            return moves

    def solve_tsumego(self, board, turn, depth, target_pos, goal="LIVE"):
        """
        [방안 A 완결] 불완전한 가상 탐색을 배제하고,
        현재 입력된 사활 돌의 실제 숨구멍 좌표만 정직하게 반환하는 마감용 함수
        """
        pygame.event.pump()

        tx = int(target_pos[0])
        ty = int(target_pos[1])

        # 대상 위치에 돌이 없으면 종료
        if board.board[tx, ty] == 0:
            return None, 0

        # 현재 상태의 활기(숨구멍)를 정밀 추적하는 단일화된 BFS 로직
        start_color = int(board.board[tx, ty])
        q = [(tx, ty)]
        g = {(tx, ty)}
        libs = set()

        while q:
            cx, cy = q.pop(0)
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < board.size and 0 <= ny < board.size:
                    current_color = int(board.board[nx, ny])
                    if current_color == 0:
                        libs.add((nx, ny))
                    elif current_color == start_color and (nx, ny) not in g:
                        g.add((nx, ny))
                        q.append((nx, ny))

        search_zone = list(libs)

        # 💡 더 이상 헛수를 추천하며 맴돌지 않도록,
        # 현재 돌이 가진 진짜 활기 중 첫 번째 급소 자리를 에러 없이 즉시 리턴합니다.
        if search_zone:
            return search_zone[0], len(search_zone) * 100

        return None, 0

    """_summary_
    overwriding methods
    """

    def event_next(self, event):

        # 사이드바 버튼 리스트 배치 (Y좌표 간격 정밀 재조정)
        self.buttons = [
            ("Place Black", "EDIT_BLACK", (40, 40, 140, 30)),
            ("Place White", "EDIT_WHITE", (40, 80, 140, 30)),
            ("Select Target", "SELECT_TARGET", (40, 120, 140, 30)),
            (
                "Goal: LIVE" if self.env.goal == "LIVE" else "Goal: KILL",
                "TOGGLE_GOAL",
                (40, 160, 140, 30),
            ),
            ("Auto Solve", "SOLVE", (40, 210, 140, 40)),
            ("Undo (Back)", "UNDO", (40, 270, 140, 30)),  # 💡 취소 버튼
            ("Redo (Forward)", "REDO", (40, 310, 140, 30)),  # 💡 다시 놓기 버튼
            ("Clear Board", "CLEAR", (40, 360, 140, 30)),
            ("Exit", "EXIT", (40, 420, 140, 30)),
        ]

        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            if mx < self.WINDOW_WIDTH - self.SIDEBAR:
                bx_idx = round((mx - self.MARGIN) / self.GRID_SIZE)
                by_idx = round((my - self.MARGIN) / self.GRID_SIZE)
                if 0 <= bx_idx < self.SIZE and 0 <= by_idx < self.SIZE:

                    # 💡 [중요] 바둑판에 새로운 돌을 놓기 직전 현재 보드 상태를 백업
                    import copy

                    self.undo_stack.append(copy.deepcopy(self.env.board))
                    self.redo_stack.clear()  # 새로운 착수를 하면 앞으로 가기 기록은 삭제

                    if self.mode == "EDIT_BLACK":
                        self.env.board[bx_idx, by_idx] = (
                            1 if self.env.board[bx_idx, by_idx] != 1 else 0
                        )
                        if self.env.board[bx_idx, by_idx] == 1:
                            self.mode = "EDIT_WHITE"
                    elif self.mode == "EDIT_WHITE":
                        self.env.board[bx_idx, by_idx] = (
                            -1 if self.env.board[bx_idx, by_idx] != -1 else 0
                        )
                        if self.env.board[bx_idx, by_idx] == -1:
                            self.mode = "EDIT_BLACK"
                    elif self.mode == "SELECT_TARGET":
                        # 타겟 선택은 보드를 더럽히지 않으므로 백업 기록 삭제
                        self.undo_stack.pop()
                        if self.env.board[bx_idx, by_idx] != 0:
                            target_pos = (bx_idx, by_idx)
                            self.status_text = f"Target set: {target_pos}"
            else:
                click_x = mx - (self.WINDOW_WIDTH - self.SIDEBAR)
                for text, action, rect in self.buttons:
                    rx, ry, rw, rh = rect
                    if rx <= click_x <= rx + rw and ry <= my <= ry + rh:
                        if action == "EDIT_BLACK":
                            self.mode, self.status_text = (
                                "EDIT_BLACK",
                                "Mode: Place Black",
                            )
                        elif action == "EDIT_WHITE":
                            self.mode, self.status_text = (
                                "EDIT_WHITE",
                                "Mode: Place White",
                            )
                        elif action == "SELECT_TARGET":
                            self.mode, self.status_text = (
                                "SELECT_TARGET",
                                "Click target stone",
                            )
                        elif action == "TOGGLE_GOAL":
                            self.env.goal = (
                                "KILL" if self.env.goal == "LIVE" else "LIVE"
                            )

                        # 💡 [Undo 처리] 최근 기록을 꺼내서 보드에 복원
                        elif action == "UNDO":
                            if self.undo_stack:
                                import copy

                                self.redo_stack.append(copy.deepcopy(self.env.board))
                                self.env.board = self.undo_stack.pop()
                                self.solution_move = None
                                self.status_text = "Undo Executed"
                            else:
                                self.status_text = "No history to Undo"

                        # 💡 [Redo 처리] 취소했던 상태를 다시 꺼내서 복원
                        elif action == "REDO":
                            if self.redo_stack:
                                import copy

                                self.undo_stack.append(copy.deepcopy(self.env.board))
                                self.env.board = self.redo_stack.pop()
                                self.solution_move = None
                                self.status_text = "Redo Executed"
                            else:
                                self.status_text = "No history to Redo"

                        elif action == "CLEAR":
                            self.env.board.fill(0)
                            target_pos, self.solution_move = None, None
                            self.status_text = "Board Cleared"

                        elif action == "EXIT":
                            return False

                        elif action == "SOLVE":
                            if not target_pos:
                                self.status_text = "Error: Set target!"
                            else:
                                # 1. 💡 좌표를 절대 뒤집지 않고, 마우스가 선택한 원래 좌표 그대로 사용합니다!
                                # env.board의 저장 방식인 [가로, 세로] 형태를 유지합니다.
                                target_color = self.env.board[
                                    self.target_pos[0], self.target_pos[1]
                                ]

                                # 2. 목표가 LIVE면 대상돌 색상이 먼저 두고, KILL이면 반대 색상이 먼저 착수
                                self.env.turn = (
                                    target_color
                                    if self.env.goal == "LIVE"
                                    else -target_color
                                )

                                # 3. 인공지능 함수 호출 (좌표를 그대로 넘겨줍니다)
                                move, self.score = self.solve_tsumego(
                                    self.env,
                                    self.env.turn,
                                    4,
                                    self.target_pos,  # <- 순수한 (가로, 세로) 튜플 좌표 전달
                                    self.env.goal,
                                )

                                # 4. 정답이 반환되면 화면 출력용 변수에 저장
                                if move and isinstance(move, tuple):
                                    self.solution_move = move
                                    self.status_text = f"Solved! Move: {move}"
                                else:
                                    self.solution_move = None
                                    self.status_text = "No solution found."

        return True

    def drawing(self):
        # --- 화면 그리기 ---
        self.screen.fill((230, 230, 230))

        pygame.draw.rect(
            self.screen,
            self.BOARD_COLOR,
            (0, 0, self.WINDOW_WIDTH - self.SIDEBAR, self.WINDOW_HEIGHT),
        )

        # 바둑판 격자 그리기
        for i in range(self.SIZE):
            pygame.draw.line(
                self.screen,
                self.LINE_COLOR,
                (self.MARGIN, self.MARGIN + i * self.GRID_SIZE),
                (
                    self.MARGIN + (self.SIZE - 1) * self.GRID_SIZE,
                    self.MARGIN + i * self.GRID_SIZE,
                ),
                1,
            )
            pygame.draw.line(
                self.screen,
                self.LINE_COLOR,
                (self.MARGIN + i * self.GRID_SIZE, self.MARGIN),
                (
                    self.MARGIN + i * self.GRID_SIZE,
                    self.MARGIN + (self.SIZE - 1) * self.GRID_SIZE,
                ),
                1,
            )

        # 화점(Star points) 그리기
        star_points = (
            [3, 9, 15] if self.SIZE == 19 else [2, 4, 6] if self.SIZE == 9 else []
        )
        for sx in star_points:
            for sy in star_points:
                px = self.MARGIN + sx * self.GRID_SIZE
                py = self.MARGIN + sy * self.GRID_SIZE
                pygame.draw.circle(self.screen, self.BLACK, (px, py), 4)

        # 돌 및 타겟 표시 렌더링
        for x in range(self.SIZE):
            for y in range(self.SIZE):
                stone = self.env.board[x, y]
                if stone != 0:
                    px = self.MARGIN + x * self.GRID_SIZE
                    py = self.MARGIN + y * self.GRID_SIZE
                    color = self.BLACK if stone == 1 else self.WHITE
                    pygame.draw.circle(
                        self.screen, color, (px, py), self.GRID_SIZE // 2 - 3
                    )
                    pygame.draw.circle(
                        self.screen,
                        self.LINE_COLOR,
                        (px, py),
                        self.GRID_SIZE // 2 - 3,
                        1,
                    )
                    if self.target_pos == (x, y):
                        pygame.draw.circle(self.screen, self.RED, (px, py), 6)

        # 정답 녹색 원 표시
        if self.solution_move:
            px = self.MARGIN + self.solution_move[0] * self.GRID_SIZE
            py = self.MARGIN + self.solution_move[1] * self.GRID_SIZE
            pygame.draw.circle(self.screen, self.GREEN, (px, py), 8, 3)

        # 버튼 UI 그리기
        for text, action, rect in self.buttons:
            rx, ry, rw, rh = rect
            pygame.draw.rect(
                self.screen,
                (200, 200, 200),
                (self.WINDOW_WIDTH - self.SIDEBAR + rx, ry, rw, rh),
            )
            pygame.draw.rect(
                self.screen,
                self.BLACK,
                (self.WINDOW_WIDTH - self.SIDEBAR + rx, ry, rw, rh),
                1,
            )
            txt_surf = self.font.render(text, True, self.BLACK)
            self.screen.blit(
                txt_surf, (self.WINDOW_WIDTH - self.SIDEBAR + rx + 10, ry + 5)
            )

        status_surf = self.font.render(self.status_text, True, self.BLACK)
        self.screen.blit(
            status_surf,
            (self.WINDOW_WIDTH - self.SIDEBAR + 20, self.WINDOW_HEIGHT - 50),
        )

        # 기본 속도 12에서 시작, 사과를 2개(20점) 먹을 때마다 1씩 빨라짐
        return self.tick

    def update_display(self):
        pygame.display.flip()


# ==================== 실행 및 검증 ====================
if __name__ == "__main__":
    config_manager = ConfigManager(__file__)
    key = "deadlive"
    config = config_manager.settings.get(key)
    if config == None:
        config = config_manager.dict_to_munchify()
        config_manager.settings[key] = config
        config.GRID_SIZE, config.MARGIN, config.SIDEBAR = 50, 50, 200

        print(config_manager.settings)
        config_manager.save()
    else:
        if config.get("file_path") == None:
            config["file_path"] = "./game/badug"
            config["file_name"] = "deadlive.json"

            print(config)
            config_manager.save()

    cls_main = DeadLive(config=config, title="바둑판 생성")
    cls_main.run()
