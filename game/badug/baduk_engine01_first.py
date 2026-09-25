import tkinter as tk
from tkinter import ttk
from collections import deque

"""
BadukEngine과 BadukTsumegoGUI 분리:
 - 화면 그리는 도구(GUI)와 활로를 계산하는 머리(Engine)를 깔끔하게 분리했습니다.
   그래야 나중에 로직을 고쳐도 화면이 깨지지 않습니다.

on_board_click 내의 따내기 시퀀스:
 - 돌이 놓이자마자 remove_dead_stones(opponent) 함수가 발동하여 상대편 돌 중 숨이 막힌 돌들을 리스트에서 0으로 밀어버립니다.
   그 직후 refresh_stones_on_screen이 호출되면서 화면에서 돌이 실시간으로 싹 사라지는 시각 효과를 만들어 냅니다.
"""


# ==========================================
# 🧠 1단계: 사활 핵심 알고리즘 엔진
# ==========================================
class BadukEngine:
    def __init__(self, size=13):
        self.size = size
        # 0: 빈칸, 1: 흑돌, 2: 백돌
        self.board = [[0] * size for _ in range(size)]

    def is_valid_coord(self, x, y):
        """좌표가 바둑판 내부 영역인지 체크"""
        return 0 <= x < self.size and 0 <= y < self.size

    def get_neighbors(self, x, y):
        """상하좌우 인접 좌표 리스트 반환"""
        neighbors = []
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if self.is_valid_coord(nx, ny):
                neighbors.append((nx, ny))
        return neighbors

    def find_group_and_liberties(self, start_x, start_y):
        """BFS 알고리즘을 사용하여 같은 색 돌 무리(Group)와 남은 활로(Liberties)를 계산"""
        stone_color = self.board[start_x][start_y]
        if stone_color == 0:
            return set(), set()

        queue = deque([(start_x, start_y)])
        group = {(start_x, start_y)}
        liberties = set()

        while queue:
            x, y = queue.popleft()
            for nx, ny in self.get_neighbors(x, y):
                if self.board[nx][ny] == 0:
                    liberties.add((nx, ny))  # 빈 공간 = 활로
                elif self.board[nx][ny] == stone_color and (nx, ny) not in group:
                    group.add((nx, ny))  # 연결된 같은 편 돌
                    queue.append((nx, ny))

        return group, liberties

    def remove_dead_stones(self, target_color):
        """바둑판 전체를 검사하여 활로가 0이 된 상대방 돌을 모두 따내기(제거)"""
        visited = set()
        captured_count = 0

        for x in range(self.size):
            for y in range(self.size):
                if self.board[x][y] == target_color and (x, y) not in visited:
                    group, liberties = self.find_group_and_liberties(x, y)
                    visited.update(group)

                    # 숨구멍(활로)이 0개라면 바둑판에서 들어냄
                    if len(liberties) == 0:
                        for gx, gy in group:
                            self.board[gx][gy] = 0
                            captured_count += 1
        return captured_count


# ==========================================
# 🎨 2단계: Tkinter 그래픽 유저 인터페이스
# ==========================================
class BadukTsumegoGUI:
    def __init__(self, root, board_size=13):
        self.root = root
        self.root.title("파이썬 사활 프로그램 v1.0")

        # 사활 로직 엔진 세팅
        self.board_size = board_size
        self.engine = BadukEngine(size=self.board_size)
        self.current_turn = 1  # 1: 흑돌 시작, 2: 백돌

        # 그래픽 환경 수치 세팅 (13줄 판에 맞춰 최적화)
        self.cell_size = 40
        self.margin = 35
        board_pixel_size = (self.board_size - 1) * self.cell_size + (self.margin * 2)

        # 스타일 테두리 및 레이아웃 구성
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.pack()

        # 상단 상태 알림창
        self.status_label = ttk.Label(
            self.main_frame,
            text="흑의 차례입니다. 바둑판을 클릭하여 착수하세요.",
            font=("Malgun Gothic", 11, "bold"),
        )
        self.status_label.pack(pady=5)

        # 전통 바둑판 색상(#E6B473)의 캔버스 생성
        self.canvas = tk.Canvas(
            self.main_frame,
            width=board_pixel_size,
            height=board_pixel_size,
            bg="#E6B473",
            highlightthickness=1,
            highlightbackground="#A07040",
        )
        self.canvas.pack()

        # 하단 메뉴 버튼 (리셋)
        self.reset_button = ttk.Button(
            self.main_frame, text="판 비우기 (초기화)", command=self.reset_game
        )
        self.reset_button.pack(pady=10)

        # 초기 화면 그리기 및 마우스 클릭 바인딩
        self.draw_board_lines()
        self.canvas.bind("<Button-1>", self.on_board_click)

    def draw_board_lines(self):
        """바둑판 선과 화점(Star Points) 그리기"""
        self.canvas.delete("grid_line")

        # 가로줄, 세로줄 그리기
        for i in range(self.board_size):
            offset = self.margin + i * self.cell_size
            # 가로줄
            self.canvas.create_line(
                self.margin,
                offset,
                self.margin + (self.board_size - 1) * self.cell_size,
                offset,
                fill="#403020",
                width=1,
                tags="grid_line",
            )
            # 세로줄
            self.canvas.create_line(
                offset,
                self.margin,
                offset,
                self.margin + (self.board_size - 1) * self.cell_size,
                fill="#403020",
                width=1,
                tags="grid_line",
            )

        # 화점(Star Points) 마킹 (13줄 판 기준 4군데 또는 중심점 배치)
        # 예시로 13줄 규격의 표준 화점 위치 지정 (3, 6, 9번째 줄 교차점)
        star_positions = (
            [3, 6, 9]
            if self.board_size == 13
            else [3, self.board_size // 2, self.board_size - 4]
        )
        for sx in star_positions:
            for sy in star_positions:
                # 중심점이나 외곽 화점 그리기
                cx = self.margin + sx * self.cell_size
                cy = self.margin + sy * self.cell_size
                r = 3
                self.canvas.create_oval(
                    cx - r, cy - r, cx + r, cy + r, fill="#403020", tags="grid_line"
                )

    def on_board_click(self, event):
        """바둑판을 마우스로 클릭했을 때 호출되는 핵심 이벤트 가로채기 함수"""
        # 마우스 픽셀 위치를 바둑판 격자 좌표(0~12)로 변환
        x = round((event.x - self.margin) / self.cell_size)
        y = round((event.y - self.margin) / self.cell_size)

        # 1. 올바른 경계 안쪽이고 빈 곳인지 체크
        if self.engine.is_valid_coord(x, y) and self.engine.board[x][y] == 0:
            # 2. 로직 엔진 배열에 현재 턴의 돌 배치
            self.engine.board[x][y] = self.current_turn

            # 3. 내 착수로 인해 활로가 0이 된 상대방 돌 무리 검색 후 따내기
            opponent = 2 if self.current_turn == 1 else 1
            captured_count = self.engine.remove_dead_stones(target_color=opponent)

            # 4. 데이터 기반으로 화면에 바둑돌 리프레시
            self.refresh_stones_on_screen()

            # 5. 착수 성공 후 차례 전환 및 상단 알림 텍스트 갱신
            self.current_turn = opponent
            turn_text = "흑" if self.current_turn == 1 else "백"
            status_msg = f"{turn_text}의 차례입니다."
            if captured_count > 0:
                status_msg += f" (상대 돌 {captured_count}개를 따냈습니다!)"
            self.status_label.config(text=status_msg)

    def refresh_stones_on_screen(self):
        """현재 엔진의 2차원 리스트 데이터를 기준으로 바둑돌 그래픽 원본을 갱신"""
        self.canvas.delete("stone")

        for x in range(self.board_size):
            for y in range(self.board_size):
                stone_type = self.engine.board[x][y]
                if stone_type == 0:
                    continue

                # 픽셀 좌표 역산
                cx = self.margin + x * self.cell_size
                cy = self.margin + y * self.cell_size
                r = self.cell_size // 2 - 2  # 선에 딱 붙지 않게 약간 작게 반지름 설정

                if stone_type == 1:
                    # 흑돌 그리기 (입체감을 위해 은은한 흰색 테두리)
                    self.canvas.create_oval(
                        cx - r,
                        cy - r,
                        cx + r,
                        cy + r,
                        fill="#101010",
                        outline="#404040",
                        width=1,
                        tags="stone",
                    )
                elif stone_type == 2:
                    # 백돌 그리기 (구분을 위해 얇은 회색 테두리)
                    self.canvas.create_oval(
                        cx - r,
                        cy - r,
                        cx + r,
                        cy + r,
                        fill="#FFFFFF",
                        outline="#B0B0B0",
                        width=1,
                        tags="stone",
                    )

    def reset_game(self):
        """판을 비우고 초기화"""
        self.engine = BadukEngine(size=self.board_size)
        self.current_turn = 1
        self.status_label.config(text="흑의 차례입니다. 바둑판을 클릭하여 착수하세요.")
        self.canvas.delete("stone")


# ==========================================
# 🎬 프로그램 메인 루프 실행
# ==========================================
if __name__ == "__main__":
    window = tk.Tk()
    # 사활 배치용으로 가장 쾌적한 13줄 바둑판으로 시작합니다. (9줄 등으로 자유롭게 변경 가능)
    app = BadukTsumegoGUI(window, board_size=13)
    window.mainloop()
