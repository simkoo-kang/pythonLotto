import tkinter as tk
from tkinter import filedialog, messagebox
from collections import deque
import os
import subprocess


# ==========================================
# 🧠 1단계: 사활 핵심 알고리즘 및 바둑 규칙 엔진
# ==========================================
class BadukEngine:
    def __init__(self, size=13):
        self.size = size
        # 2차원 리스트(13x13)로 바둑판 안전 생성 (0: 빈칸, 1: 흑돌, 2: 백돌)
        self.board = [[0 for _ in range(size)] for _ in range(size)]
        # 패(Ko) 제한 규칙을 위한 임의 좌표 저장 변수
        self.ko_coordinate = None

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

    def is_suicide_move(self, x, y, stone_color):
        """자살수(착수금지) 여부를 판별하되, 상대 돌을 따낼 수 있다면 제외합니다."""
        self.board[x][y] = stone_color
        opponent_color = 2 if stone_color == 1 else 1

        can_capture_opponent = False
        visited = set()

        for nx, ny in self.get_neighbors(x, y):
            if self.board[nx][ny] == opponent_color and (nx, ny) not in visited:
                group, liberties = self.find_group_and_liberties(nx, ny)
                visited.update(group)
                if len(liberties) == 0:
                    can_capture_opponent = True
                    break

        _, my_liberties = self.find_group_and_liberties(x, y)
        self.board[x][y] = 0  # 원상 복구

        if len(my_liberties) == 0 and not can_capture_opponent:
            return True
        return False

    def remove_dead_stones(self, target_color, last_move_x, last_move_y):
        """활로가 0이 된 돌을 제거하고, 단 1개씩 교환되었을 경우 패(Ko) 상태로 지정합니다."""
        visited = set()
        captured_count = 0
        captured_stones = []

        for x in range(self.size):
            for y in range(self.size):
                if self.board[x][y] == target_color and (x, y) not in visited:
                    group, liberties = self.find_group_and_liberties(x, y)
                    visited.update(group)

                    if len(liberties) == 0:
                        for gx, gy in group:
                            self.board[gx][gy] = 0
                            captured_count += 1
                            captured_stones.append((gx, gy))

        # 패 규칙 실시간 정밀 검증
        my_group, _ = self.find_group_and_liberties(last_move_x, last_move_y)
        if captured_count == 1 and len(my_group) == 1:
            self.ko_coordinate = captured_stones[0]
        else:
            self.ko_coordinate = None

        return captured_count


# ==========================================
# 🎨 2단계: 그래픽 화면 UI 및 AI 연동부
# ==========================================
class BadukTsumegoGUI:
    def __init__(self, root, board_size=13):
        self.root = root
        self.root.title("파이썬 스마트 사활 연구소 v1.5")

        self.board_size = board_size
        self.engine = BadukEngine(size=self.board_size)

        self.edit_mode = tk.StringVar(value="normal")
        self.current_turn = 1  # 1: 흑, 2: 백

        # KataGo 경로 동기화 완료 (알려주신 최적 주소 반영)
        self.katago_dir = r"D:\Program Files\sabaki\katago"
        self.katago_exe = os.path.join(
            self.katago_dir, "katago-v1.18.1-eigenavx2-windows-x64.exe"
        )
        self.katago_model = os.path.join(
            self.katago_dir, "kata1-tf3-b11c768-s11750M-d6216M.bin.gz"
        )

        # AI 정답 힌트 좌표 메모리
        self.ai_recommended_move = None

        self.cell_size = 40
        self.margin = 35
        board_pixel_size = (self.board_size - 1) * self.cell_size + (self.margin * 2)

        # 상단 메뉴 구성
        self.create_menu_bar()

        # 레이아웃 프레임
        self.main_frame = tk.Frame(root, padx=15, pady=15)
        self.main_frame.pack()

        self.status_label = tk.Label(
            self.main_frame,
            text="흑의 차례입니다. 문제를 만들거나 바둑판을 클릭해 풀이를 검토하세요.",
            font=("Malgun Gothic", 11, "bold"),
        )
        self.status_label.pack(pady=5)

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

        # 하단 조작 제어 버튼바
        buttons_frame = tk.Frame(self.main_frame)
        buttons_frame.pack(pady=5)

        self.ai_button = tk.Button(
            buttons_frame,
            text="💡 카타고 사활 정답 분석",
            font=("Malgun Gothic", 10, "bold"),
            fg="white",
            bg="#2E7D32",
            padx=10,
            command=self.ask_katago_for_answer,
        )
        self.ai_button.pack(side="left", padx=5)

        self.reset_button = tk.Button(
            buttons_frame,
            text="판 전체 초기화",
            font=("Malgun Gothic", 10),
            command=self.reset_game,
            bg="#F0F0F0",
        )
        self.reset_button.pack(side="left", padx=5)

        self.draw_board_lines()

        # 마우스 입력 양손 제어 장착
        self.canvas.bind("<Button-1>", self.on_board_click)
        self.canvas.bind("<Button-3>", self.on_board_right_click)

        # 종료 시 유령 프로세스 누수 차단 연동
        self.root.protocol("WM_DELETE_WINDOW", self.on_close_program)

    def create_menu_bar(self):
        menu_bar = tk.Menu(self.root)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(
            label="사활 문제 불러오기 (.sgf)", command=self.load_sgf_file
        )
        file_menu.add_command(
            label="사활 문제 저장하기 (.sgf)", command=self.save_sgf_file
        )
        file_menu.add_separator()
        file_menu.add_command(label="프로그램 종료", command=self.on_close_program)
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
        tools_frame.pack(fill="x", pady=5)

        tk.Radiobutton(
            tools_frame,
            text="일반 대국(검토)",
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
                text="흑돌 편집 모드: 바둑판 클릭 시 흑돌이 연속 배치됩니다."
            )
        elif mode == "add_white":
            self.status_label.config(
                text="백돌 편집 모드: 바둑판 클릭 시 백돌이 연속 배치됩니다."
            )
        elif mode == "delete":
            self.status_label.config(
                text="지우개 모드: 클릭 시 바둑돌이 하나씩 지워집니다."
            )

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

        # [문법 완전 교정] 안전한 if-else 구조의 13줄 화점 세팅
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
        x = round((event.x - self.margin) / self.cell_size)
        y = round((event.y - self.margin) / self.cell_size)

        if not self.engine.is_valid_coord(x, y):
            return

        mode = self.edit_mode.get()

        # [아이디어 반영 1] 지우개 모드이거나 돌이 이미 있는 곳 좌클릭 시 토글 삭제
        if mode == "delete" or self.engine.board[x][y] != 0:
            self.engine.board[x][y] = 0
            self.engine.ko_coordinate = None
            self.ai_recommended_move = None
            self.refresh_stones_on_screen()
            return

        # 새 수 착수 시 이전 AI 잔상 소멸
        self.ai_recommended_move = None

        if mode == "add_black":
            self.engine.board[x][y] = 1
            self.engine.remove_dead_stones(2, x, y)
            self.refresh_stones_on_screen()
        elif mode == "add_white":
            self.engine.board[x][y] = 2
            self.engine.remove_dead_stones(1, x, y)
            self.refresh_stones_on_screen()
        elif mode == "normal":
            # 패(Ko) 룰 연동 검증
            if self.engine.ko_coordinate == [(x, y)]:
                messagebox.showwarning(
                    "패(劫) 착수 금지",
                    "패 규칙에 의거해 지금 즉시 되따낼 수 없습니다!\n다른 곳에 착수한 후 따내야 합니다.",
                )
                return

            # 자살수 룰 연동 검증
            if self.engine.is_suicide_move(x, y, self.current_turn):
                messagebox.showwarning(
                    "착수 금지", "바둑 규칙상 자살수는 착수할 수 없습니다."
                )
                return

            self.engine.board[x][y] = self.current_turn
            opponent = 2 if self.current_turn == 1 else 1
            captured_count = self.engine.remove_dead_stones(opponent, x, y)
            self.refresh_stones_on_screen()

            self.current_turn = opponent
            self.update_status_by_mode()
            if captured_count > 0:
                current_msg = self.status_label.cget("text")
                self.status_label.config(
                    text=current_msg + f" (상대 돌 {captured_count}개 획득!)"
                )

    def on_board_right_click(self, event):
        """[아이디어 반영 2] 마우스 오른쪽 클릭 시 즉각 지우개 작동"""
        x = round((event.x - self.margin) / self.cell_size)
        y = round((event.y - self.margin) / self.cell_size)
        if not self.engine.is_valid_coord(x, y):
            return

        if self.engine.board[x][y] != 0:
            self.engine.board[x][y] = 0
            self.engine.ko_coordinate = None
            self.ai_recommended_move = None
            self.refresh_stones_on_screen()

    def refresh_stones_on_screen(self):
        self.canvas.delete("stone")
        self.canvas.delete("ai_hint")

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

        # KataGo AI가 보낸 초록색 네온 정답 마커 표시
        if self.ai_recommended_move:
            ax, ay = self.ai_recommended_move
            cx = self.margin + ax * self.cell_size
            cy = self.margin + ay * self.cell_size
            r = self.cell_size // 4
            self.canvas.create_oval(
                cx - r,
                cy - r,
                cx + r,
                cy + r,
                fill="#00FF00",
                outline="#004D40",
                width=2,
                tags="ai_hint",
            )

    # ==========================================
    # 🤖 3단계: 백그라운드 KataGo GTP 연동 논리
    # ==========================================
    def send_gtp_command(self, process, cmd):
        process.stdin.write(cmd + "\n")
        process.stdin.flush()
        response = []
        while True:
            line = process.stdout.readline().strip()
            if not line:
                break
            response.append(line)
        return "\n".join(response)

    def ask_katago_for_answer(self):
        """현재 내 바둑판의 실시간 상태를 카타고에게 주입해 정답수를 회수함 (경로 공백 버그 수정)"""
        if not os.path.exists(self.katago_exe):
            messagebox.showerror(
                "엔진 부재",
                f"다음 경로에서 카타고 실행 파일을 찾지 못했습니다:\n{self.katago_exe}",
            )
            return

        self.status_label.config(
            text="카타고 AI가 정답 변화도를 분석 중입니다... 잠시만 대기하세요."
        )
        self.root.update()

        # [⭐ 핵심 수정] 경로에 공백이 있어도 안전하게 인식하도록 큰따옴표를 명시하거나 리스트 구조를 정밀화함
        cmd_args = [self.katago_exe, "gtp", "-model", self.katago_model]
        try:
            # 윈도우 환경에서 공백 경로 충돌을 방지하기 위해 생성 옵션과 인자 처리 강화
            proc = subprocess.Popen(
                cmd_args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                encoding="utf-8",
                creationflags=subprocess.CREATE_NO_WINDOW,  # 백그라운드 창 튀는 현상 방지
            )

            self.send_gtp_command(proc, f"boardsize {self.board_size}")
            self.send_gtp_command(proc, "clear_board")

            # 카타고 표준 좌표 매핑용 문자열 (I 제외 규격)
            abc = "ABCDEFGHJKLMNOPQRST"
            for x in range(self.board_size):
                for y in range(self.board_size):
                    stone = self.engine.board[x][y]
                    if stone != 0:
                        color = "black" if stone == 1 else "white"
                        gtp_x = abc[x]
                        gtp_y = self.board_size - y
                        self.send_gtp_command(proc, f"play {color} {gtp_x}{gtp_y}")

            current_color = "black" if self.current_turn == 1 else "white"
            ai_response = self.send_gtp_command(proc, f"genmove {current_color}")

            self.send_gtp_command(proc, "quit")
            proc.terminate()

            if ai_response.startswith("="):
                move_str = ai_response.replace("=", "").strip()
                if move_str.lower() != "pass" and len(move_str) >= 2:
                    col_char = move_str.upper()
                    row_num = int(move_str[1:])

                    arr_x = abc.index(col_char)
                    arr_y = self.board_size - row_num

                    self.ai_recommended_move = (arr_x, arr_y)
                    self.refresh_stones_on_screen()

                    turn_name = "흑" if self.current_turn == 1 else "백"
                    self.status_label.config(
                        text=f"분석 완수! 카타고 추천 {turn_name}의 정답수 ➔ [{col_char}{row_num}]"
                    )
                else:
                    self.status_label.config(
                        text="카타고 분석 결과: 이 국면은 착수하지 않고 패스(Pass)하는 것이 최선입니다."
                    )
            else:
                # 카타고 응답이 비정상적일 때 가시적인 오류 출력
                self.status_label.config(
                    text="카타고가 응답했지만 올바른 좌표를 받지 못했습니다."
                )

        except Exception as e:
            messagebox.showerror("AI 연동 장애", f"KataGo 통신 오류:\n{e}")
            self.update_status_by_mode()

    # ==========================================
    # 💾 4단계: 파일 시스템(SGF) 입출력
    # ==========================================
    def save_sgf_file(self):
        file_path = filedialog.asksavesasfilename(
            defaultextension=".sgf",
            filetypes=[("Smart Game Format 아카이브", "*.sgf"), ("모든 파일", "*.*")],
            title="사활 문제 저장하기",
        )
        if not file_path:
            return

        try:
            abc = "abcdefghijklmnopqrstuvwxyz"
            sgf_content = f"(;SZ[{self.board_size}]AP[PythonTsumegoTool:1.5]"
            black_stones, white_stones = [], []

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
                "저장 완료", "사활 문제가 성공적으로 영구 저장되었습니다."
            )
        except Exception as e:
            messagebox.showerror("오류", f"저장 실패:\n{e}")

    def load_sgf_file(self):
        """SGF 기보 파일을 읽어서 화면에 사활 배치 완벽 복원 (정규식 기반 버그 수정)"""
        import re  # 정규 표현식 라이브러리 추가

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
                    "규격 경고",
                    f"바둑판 줄 수가 현재 프로그램({self.board_size}줄)과 일치하지 않을 수 있습니다. 강제 로드할까요?",
                ):
                    return

            # 1. 바둑판 내부 데이터 완전 깨끗하게 리셋
            self.engine = BadukEngine(size=self.board_size)
            abc = "abcdefghijklmnopqrstuvwxyz"

            # 2. 정규 표현식으로 AB[...] 또는 AW[...] 뒤에 오는 모든 괄호 안의 두 글자 좌표를 추출
            # 예: AB[ab][cd][ef] 에서 ['ab', 'cd', 'ef']를 정확하게 뽑아냅니다.
            for stone_tag, color_val in [("AB", 1), ("AW", 2)]:
                # 태그가 시작되는 위치부터 닫히는 구조까지 정밀하게 매칭
                matches = re.finditer(r"" + stone_tag + r"((?:\[[a-z]{2}\])+)", content)
                for match in matches:
                    stone_block = match.group(1)
                    # 블록 안에서 두 글자 알파벳 좌표 추출
                    coords = re.findall(r"\[([a-z]{2})\]", stone_block)
                    for pos in coords:
                        px = abc.index(pos[0])
                        py = abc.index(pos[1])
                        if self.engine.is_valid_coord(px, py):
                            self.engine.board[px][py] = color_val

            # 3. 데이터가 주입되었으므로 화면 그래픽 완전히 리프레시
            self.refresh_stones_on_screen()

            # 4. 상태 변수 초기화
            self.edit_mode.set("normal")
            self.current_turn = 1
            self.ai_recommended_move = None
            self.update_status_by_mode()

            messagebox.showinfo(
                "로드 완수", "SGF 파일의 사활 배치를 바둑판 위에 완벽하게 복원했습니다!"
            )

        except Exception as e:
            messagebox.showerror("오류", f"불러오기 실패:\n{e}")

    def reset_game(self):
        self.engine = BadukEngine(size=self.board_size)
        self.current_turn = 1
        self.edit_mode.set("normal")
        self.ai_recommended_move = None
        self.update_status_by_mode()
        self.canvas.delete("stone")
        self.canvas.delete("ai_hint")

    def on_close_program(self):
        self.root.destroy()


if __name__ == "__main__":
    window = tk.Tk()
    app = BadukTsumegoGUI(window, board_size=13)
    window.mainloop()
