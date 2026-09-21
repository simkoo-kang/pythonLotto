import tkinter as tk
from tkinter import filedialog, messagebox
from collections import deque
import os


# ==========================================
# 🧠 1단계: 사활 핵심 알고리즘 엔진
# ==========================================
class BadukEngine:
    def __init__(self, size=13):
        self.size = size
        # 2차원 리스트(13x13) 안전하게 생성 (0: 빈칸, 1: 흑돌, 2: 백돌)
        self.board = [[0 for _ in range(size)] for _ in range(size)]

    def is_valid_coord(self, x, y):
        return 0 <= x < self.size and 0 <= y < self.size

    def get_neighbors(self, x, y):
        neighbors = []
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if self.is_valid_coord(nx, ny):
                neighbors.append((nx, ny))
        return neighbors

    def find_group_and_liberties(self, start_x, start_y):
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
                    liberties.add((nx, ny))
                elif self.board[nx][ny] == stone_color and (nx, ny) not in group:
                    group.add((nx, ny))
                    queue.append((nx, ny))

        return group, liberties

    def remove_dead_stones(self, target_color):
        visited = set()
        captured_count = 0

        for x in range(self.size):
            for y in range(self.size):
                if self.board[x][y] == target_color and (x, y) not in visited:
                    group, liberties = self.find_group_and_liberties(x, y)
                    visited.update(group)

                    if len(liberties) == 0:
                        for gx, gy in group:
                            self.board[gx][gy] = 0
                            captured_count += 1
        return captured_count


# ==========================================
# 🎨 2단계: Tkinter 그래픽 화면 및 메뉴 구성
# ==========================================
class BadukTsumegoGUI:
    def __init__(self, root, board_size=13):
        self.root = root
        self.root.title("파이썬 사활 툴 v1.4")

        self.board_size = board_size
        self.engine = BadukEngine(size=self.board_size)

        self.edit_mode = tk.StringVar(value="normal")
        self.current_turn = 1

        self.cell_size = 40
        self.margin = 35
        board_pixel_size = (self.board_size - 1) * self.cell_size + (self.margin * 2)

        # 🛠️ 상단 메뉴바 추가
        self.create_menu_bar()

        # 메인 프레임
        self.main_frame = tk.Frame(root, padx=15, pady=15)
        self.main_frame.pack()

        # 상단 상태 텍스트
        self.status_label = tk.Label(
            self.main_frame,
            text="흑의 차례입니다. 바둑판을 클릭하여 착수하세요.",
            font=("Malgun Gothic", 11, "bold"),
        )
        self.status_label.pack(pady=5)

        # 바둑판 캔버스
        self.canvas = tk.Canvas(
            self.main_frame,
            width=board_pixel_size,
            height=board_pixel_size,
            bg="#E6B473",
            highlightthickness=1,
            highlightbackground="#A07040",
        )
        self.canvas.pack(pady=5)

        self.create_edit_tools()

        # 전체 초기화 버튼
        self.reset_button = tk.Button(
            self.main_frame,
            text="판 전체 초기화",
            font=("Malgun Gothic", 10),
            command=self.reset_game,
            bg="#F0F0F0",
        )
        self.reset_button.pack(pady=10)

        self.draw_board_lines()
        self.canvas.bind("<Button-1>", self.on_board_click)
        self.canvas.bind("<Button-3>", self.on_board_right_click)  # 우클릭 지우개 추가

    def create_menu_bar(self):
        """파일 저장, 불러오기, 종료 기능이 탑재된 메뉴바 구성"""
        menu_bar = tk.Menu(self.root)

        # 파일 메뉴 풀다운 항목 정의
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(
            label="사활 문제 불러오기 (.sgf)", command=self.load_sgf_file
        )
        file_menu.add_command(
            label="사활 문제 저장하기 (.sgf)", command=self.save_sgf_file
        )
        file_menu.add_separator()
        file_menu.add_command(label="프로그램 종료", command=self.root.quit)

        # 메뉴바에 파일 메뉴 등록
        menu_bar.add_cascade(label="파일(File)", menu=file_menu)
        self.root.config(menu=menu_bar)

    def create_edit_tools(self):
        tools_frame = tk.LabelFrame(
            self.main_frame,
            text=" ♟️ 바둑판 편집/대국 도구 ",
            font=("Malgun Gothic", 9),
            padx=10,
            pady=10,
        )
        tools_frame.pack(fill="x", pady=10)

        tk.Radiobutton(
            tools_frame,
            text="일반 대국",
            variable=self.edit_mode,
            value="normal",
            command=self.update_status_by_mode,
            font=("Malgun Gothic", 10),
        ).pack(side="left", padx=10)
        tk.Radiobutton(
            tools_frame,
            text="⚫ 흑돌 연속",
            variable=self.edit_mode,
            value="add_black",
            command=self.update_status_by_mode,
            font=("Malgun Gothic", 10),
        ).pack(side="left", padx=10)
        tk.Radiobutton(
            tools_frame,
            text="⚪ 백돌 연속",
            variable=self.edit_mode,
            value="add_white",
            command=self.update_status_by_mode,
            font=("Malgun Gothic", 10),
        ).pack(side="left", padx=10)
        tk.Radiobutton(
            tools_frame,
            text="❌ 지우개",
            variable=self.edit_mode,
            value="delete",
            command=self.update_status_by_mode,
            font=("Malgun Gothic", 10),
        ).pack(side="left", padx=10)

    def update_status_by_mode(self):
        mode = self.edit_mode.get()
        if mode == "normal":
            turn_text = "흑" if self.current_turn == 1 else "백"
            self.status_label.config(text=f"일반 대국 모드: {turn_text}의 차례입니다.")
        elif mode == "add_black":
            self.status_label.config(
                text="흑돌 편집 모드: 클릭 시 흑돌이 연속 배치됩니다."
            )
        elif mode == "add_white":
            self.status_label.config(
                text="백돌 편집 모기: 클릭 시 백돌이 연속 배치됩니다."
            )
        elif mode == "delete":
            self.status_label.config(text="지우개 모드: 클릭 시 돌이 제거됩니다.")

    def draw_board_lines(self):
        self.canvas.delete("grid_line")
        for i in range(self.board_size):
            offset = self.margin + i * self.cell_size
            self.canvas.create_line(
                self.margin,
                offset,
                self.margin + (self.board_size - 1) * self.cell_size,
                offset,
                fill="#403020",
                width=1,
                tags="grid_line",
            )
            self.canvas.create_line(
                offset,
                self.margin,
                offset,
                self.margin + (self.board_size - 1) * self.cell_size,
                fill="#403020",
                width=1,
                tags="grid_line",
            )

        # 화점 위치 (13줄 전용 정석 좌표 설정)
        if self.board_size == 13:
            star_positions = [3, 6, 9]
        else:
            star_positions = [3, self.board_size // 2, self.board_size - 4]

        for sx in star_positions:
            for sy in star_positions:
                cx = self.margin + sx * self.cell_size
                cy = self.margin + sy * self.cell_size
                r = 3
                self.canvas.create_oval(
                    cx - r, cy - r, cx + r, cy + r, fill="#403020", tags="grid_line"
                )

    def on_board_click(self, event):
        """바둑판 마우스 왼쪽 클릭 시: 돌을 놓거나, 이미 돌이 있다면 지우기(토글)"""
        x = round((event.x - self.margin) / self.cell_size)
        y = round((event.y - self.margin) / self.cell_size)

        if not self.engine.is_valid_coord(x, y):
            return

        mode = self.edit_mode.get()

        # [⭐ 아이디어 반영 1] 지우개 모드이거나, 돌이 있는 곳을 '다시 누르면' 돌 제거
        if mode == "delete" or self.engine.board[x][y] != 0:
            self.engine.board[x][y] = 0
            self.refresh_stones_on_screen()
            return

        # (이하 빈 자리에 돌을 놓는 기존 모드별 로직)
        if mode == "add_black":
            self.engine.board[x][y] = 1
            self.engine.remove_dead_stones(target_color=2)
            self.refresh_stones_on_screen()

        elif mode == "add_white":
            self.engine.board[x][y] = 2
            self.engine.remove_dead_stones(target_color=1)
            self.refresh_stones_on_screen()

        elif mode == "normal":
            self.engine.board[x][y] = self.current_turn
            opponent = 2 if self.current_turn == 1 else 1
            captured_count = self.engine.remove_dead_stones(target_color=opponent)
            self.refresh_stones_on_screen()
            self.current_turn = opponent
            self.update_status_by_mode()
            if captured_count > 0:
                current_msg = self.status_label.cget("text")
                self.status_label.config(
                    text=current_msg + f" (상대 돌 {captured_count}개 따냄!)"
                )

    def on_board_right_click(self, event):
        """[⭐ 아이디어 반영 2] 바둑판 마우스 우클릭 시: 모드 상관없이 즉시 돌 지우기"""
        x = round((event.x - self.margin) / self.cell_size)
        y = round((event.y - self.margin) / self.cell_size)

        if not self.engine.is_valid_coord(x, y):
            return

        # 돌이 있는 자리라면 즉시 삭제 (지우개 작동)
        if self.engine.board[x][y] != 0:
            self.engine.board[x][y] = 0
            self.refresh_stones_on_screen()

    def refresh_stones_on_screen(self):
        self.canvas.delete("stone")
        for x in range(self.board_size):
            for y in range(self.board_size):
                stone_type = self.engine.board[x][y]
                if stone_type == 0:
                    continue
                cx = self.margin + x * self.cell_size
                cy = self.margin + y * self.cell_size
                r = self.cell_size // 2 - 2
                color = "#101010" if stone_type == 1 else "#FFFFFF"
                outline = "#404040" if stone_type == 1 else "#B0B0B0"
                self.canvas.create_oval(
                    cx - r,
                    cy - r,
                    cx + r,
                    cy + r,
                    fill=color,
                    outline=outline,
                    width=1,
                    tags="stone",
                )

    # ==========================================
    # 💾 파일 입출력(SGF) 및 메뉴 로직 추가
    # ==========================================
    def save_sgf_file(self):
        """현재 바둑판 배치를 표준 SGF 포맷 파일로 저장"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".sgf",
            filetypes=[("Smart Game Format 아카이브", "*.sgf"), ("모든 파일", "*.*")],
            title="사활 문제 저장하기",
        )
        if not file_path:
            return

        try:
            abc = "abcdefghijklmnopqrstuvwxyz"
            sgf_content = f"(;SZ[{self.board_size}]AP[PythonTsumegoTool:1.4]"

            black_stones = []
            white_stones = []

            for x in range(self.board_size):
                for y in range(self.board_size):
                    if self.engine.board[x][y] == 1:
                        black_stones.append(f"[{abc[x]}{abc[y]}]")
                    elif self.engine.board[x][y] == 2:
                        white_stones.append(f"[{abc[x]}{abc[y]}]")

            if black_stones:
                sgf_content += "AB" + "".join(black_stones)
            if white_stones:
                sgf_content += "AW" + "".join(white_stones)

            sgf_content += ")"

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(sgf_content)
            messagebox.showinfo(
                "저장 완료", "사활 문제가 SGF 파일로 정상 저장되었습니다."
            )
        except Exception as e:
            messagebox.showerror(
                "저장 오류", f"파일을 저장하는 도중 에러가 발생했습니다:\n{e}"
            )

    def load_sgf_file(self):
        """SGF 기보 파일을 읽어서 화면에 사활 배치 복원"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Smart Game Format 아카이브", "*.sgf"), ("모든 파일", "*.*")],
            title="사활 문제 불러오기",
        )
        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read().strip()

            if (
                f"SZ[{self.board_size}]" not in content
                and f"SZ[{self.board_size:02d}]" not in content
            ):
                if not messagebox.askyesno(
                    "규격 불일치",
                    f"이 파일은 {self.board_size}줄 바둑판 파일이 아닐 수 있습니다. 강제로 불러올까요?",
                ):
                    return

            # 바둑판 초기화
            self.engine = BadukEngine(size=self.board_size)
            abc = "abcdefghijklmnopqrstuvwxyz"

            # 정밀한 SGF 태그 파싱 (AB, AW 뒤의 모든 [xx] 추출)
            def parse_tag_stones(tag, color_val):
                if tag in content:
                    parts = content.split(tag)
                    for part in parts[1:]:
                        # 태그 뒤에 오는 연속된 괄호 쌍들을 추적
                        idx = 0
                        while idx < len(part) and part[idx] == "[":
                            pos = part[idx + 1 : idx + 3]
                            if len(pos) == 2 and pos[0] in abc and pos[1] in abc:
                                px = abc.index(pos[0])
                                py = abc.index(pos[1])
                                if self.engine.is_valid_coord(px, py):
                                    self.engine.board[px][py] = color_val
                            idx += 4

            parse_tag_stones("AB", 1)  # 흑돌 배치 복원
            parse_tag_stones("AW", 2)  # 백돌 배치 복원

            # 화면 갱신 및 상태 초기화
            self.refresh_stones_on_screen()
            self.edit_mode.set("normal")
            self.current_turn = 1
            self.update_status_by_mode()
            messagebox.showinfo(
                "불러오기 성공",
                "SGF 파일의 사활 배치를 바둑판에 성공적으로 복원했습니다.",
            )
        except Exception as e:
            messagebox.showerror("오류", f"SGF 파일을 해석하는 도중 실패했습니다:\n{e}")

    def reset_game(self):
        """판을 비우고 초기화"""
        self.engine = BadukEngine(size=self.board_size)
        self.current_turn = 1
        self.edit_mode.set("normal")
        self.update_status_by_mode()
        self.canvas.delete("stone")


# ==========================================
# 🎬 프로그램 메인 루프 실행
# ==========================================
if __name__ == "__main__":
    window = tk.Tk()
    app = BadukTsumegoGUI(window, board_size=13)
    window.mainloop()
