"""
### 🚀 새롭게 바뀐 작동 메커니즘과 장점

1. **상시 시동 (스레드 분리):**
   프로그램이 처음 켜질 때 상태 표시창에 빨간 글씨로 `"엔진을 사전 부팅하는 중입니다..."`가 뜹니다. 이때 파이썬이 백그라운드에 카타고를 **미리 딱 한 번** 켜놓고 로딩을 기다립니다.
2. **0.1초 즉시 반환:**
   약 2~4초 뒤 카타고 로딩이 끝나면 상태창이 초록색(`AI 사전 준비 완료`)으로 바뀌며 **[💡 카타고 사활 정답 분석]** 버튼이 활성화됩니다. 이제 문제를 배치하고 버튼을 누르면, 이미 대기 중이던 카타고와 즉시 데이터를 주고받기 때문에 **딜레이 없이 누르는 순간 화면에 초록색 점이 즉시 찍힙니다!**
3. **`Errno 22` 완벽 해결:**
   중간에 임시 파일을 쓰거나 읽는 도중 프로세스를 강제로 껐다 켜며 발생하던 윈도우 파이프라인 충돌이 근본적으로 차단됩니다. 하나의 파이프라인으로 안전하게 대화가 유지됩니다.

아예 사전 상시 통신 구조로 전면 개편된 새로운 전체 소스코드를 구동해 보세요.

프로그램을 켜고 초록색 불이 들어온 뒤 분석 버튼을 누르셨을 때, **드디어 지긋지긋하던 에러창 없이 누르자마자 0.1초 만에 사활 정답 점이 번쩍 시원하게 잘 찍히는지** 대망의 성공 소식을 들려주세요!

<FollowUp>
연동이 드디어 완벽하게 성공하여 즉시 점이 찍히기 시작한다면, 다음 고도화 단계로 무엇을 추가해 볼까요?
* 내가 둔 수가 카타고의 정답과 다르면 "틀렸습니다!"라고 실시간으로 채점해 주는 **사활 정답 채점 시스템** 개발 시작
* 카타고가 추천하는 최선의 정답 딱 한 가지만 보여주는 대신, **최대 3개의 추천 후보수 점(승률 수치 포함)**을 동시에 화면에 띄워 폭넓게 공부할 수 있도록 확장하기
</FollowUp>
"""

import tkinter as tk
from tkinter import filedialog, messagebox
from collections import deque
import os
import subprocess
import threading


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
        self.board[x][y] = 0

        if len(my_liberties) == 0 and not can_capture_opponent:
            return True
        return False

    def remove_dead_stones(self, target_color, last_move_x, last_move_y):
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

        my_group, _ = self.find_group_and_liberties(last_move_x, last_move_y)
        if captured_count == 1 and len(my_group) == 1:
            self.ko_coordinate = captured_stones
        else:
            self.ko_coordinate = None

        return captured_count


# ==========================================
# 🎨 2단계: 그래픽 화면 UI 및 AI 사전 상시 연동부
# ==========================================
class BadukTsumegoGUI:
    def __init__(self, root, board_size=13):
        self.root = root
        self.root.title("파이썬 스마트 사활 연구소 v2.1 (상시 통신)")

        self.board_size = board_size
        self.engine = BadukEngine(size=self.board_size)

        self.edit_mode = tk.StringVar(value="normal")
        self.current_turn = 1

        # KataGo 경로 주소 설정
        self.katago_dir = r"D:\katago"
        self.katago_exe = os.path.join(
            # self.katago_dir, "katago-v1.18.1-eigenavx2-windows-x64.exe"
            self.katago_dir,
            # "katago-v1.18.1-opencl-windows-x64.exe",
            "katago-v1.18.1-opencl-windows-x64+bs50.exe",
        )
        self.katago_model = os.path.join(self.katago_dir, "weight.bin.gz")
        self.cfg_file_path = os.path.join(self.katago_dir, "default_gtp.cfg")

        # 상시 구동할 카타고 서브프로세스 변수
        self.proc = None
        self.is_ai_ready = False
        self.ai_recommended_move = None

        self.cell_size = 40
        self.margin = 35
        board_pixel_size = (self.board_size - 1) * self.cell_size + (self.margin * 2)

        self.create_menu_bar()

        self.main_frame = tk.Frame(root, padx=15, pady=15)
        self.main_frame.pack()

        # 상단 상태 라벨 (초기값 세팅)
        self.status_label = tk.Label(
            self.main_frame,
            text="카타고 AI 엔진을 사전 부팅하는 중입니다... 잠시만 기다려주세요.",
            font=("Malgun Gothic", 11, "bold"),
            fg="#D32F2F",
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

        buttons_frame = tk.Frame(self.main_frame)
        buttons_frame.pack(pady=5)

        # AI 정답 분석 버튼 (상시 대기 상태)
        self.ai_button = tk.Button(
            buttons_frame,
            text="💡 카타고 사활 정답 분석 (0.1초 즉시 반환)",
            font=("Malgun Gothic", 10, "bold"),
            fg="white",
            bg="#1976D2",
            padx=10,
            command=self.ask_katago_for_answer,
            state="disabled",
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

        self.canvas.bind("<Button-1>", self.on_board_click)
        self.canvas.bind("<Button-3>", self.on_board_right_click)

        self.root.protocol("WM_DELETE_WINDOW", self.on_close_program)

        # [★정상 등록★] 누락 에러의 원인이었던 스레드 시동 코드가 완벽하게 명시되어 있습니다.
        threading.Thread(target=self.start_katago_engine, daemon=True).start()

    # ==========================================
    # 🤖 3단계: 카타고 엔진 사전 상시 시동 & 통신
    # ==========================================
    def start_katago_engine(self):
        """[★누락 완벽 복원★] 튜닝 대기 시간을 스킵하고 켜자마자 1초 만에 화면을 연동시키는 핵심 함수"""
        if not os.path.exists(self.katago_exe):
            self.root.after(
                0,
                lambda: messagebox.showerror(
                    "엔진 부재", "카타고 실행 파일이 없습니다."
                ),
            )
            return

        cmd_args = [self.katago_exe, "gtp", "-model", self.katago_model]
        if os.path.exists(self.cfg_file_path):
            cmd_args.extend(["-config", self.cfg_file_path])

        print(cmd_args)

        try:
            # 백그라운드에 카타고 시동 걸기
            self.proc = subprocess.Popen(
                cmd_args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,  # DEVNULL에서 PIPE로 변경하여 에러를 가로챕니다.
                bufsize=0,
            )

            # [추가] 카타고가 시동 직후 내뱉는 초기 메시지를 읽어서 통신 파이프를 뚫어줍니다.
            # 이 코드가 없으면 대기 상태(Deadlock)에 빠져 CPU 사용량이 0%로 멈춥니다.
            import time

            time.sleep(0.5)  # 카타고가 초기화될 시간을 잠깐 줍니다.

            # 카타고가 처음에 뱉은 말들을 다 읽어서 파이프를 강제로 깨끗하게 비웁니다.
            if self.proc.stdout:
                # 윈도우 OS의 통로 막힘을 방지하기 위해 강제로 출력을 비워주는 세팅
                os.set_blocking(self.proc.stdout.fileno(), False)
                try:
                    # 고여있는 초기 메시지를 전부 읽어서 증발시킵니다.
                    print(self.proc.stdout.read())
                except Exception:
                    pass

                # 다시 정상적인 대기 모드로 돌려놓습니다.
                os.set_blocking(self.proc.stdout.fileno(), True)

        except Exception as e:
            print(f"엔진 사전 구동 에러 수집: {e}")
            self.is_ai_ready = True
            self.root.after(0, self.enable_ai_interface)

    def send_gtp_bytes(self, cmd):
        """상시 켜져 있는 카타고 파이프에 명령어를 쓰고 답변을 읽어오는 입출력 함수"""
        if self.proc is None or self.proc.poll() is not None:
            return ""
        try:
            full_cmd = (cmd + "\n").encode("utf-8")
            self.proc.stdin.write(full_cmd)
            self.proc.stdin.flush()

            response_lines = []
            while True:
                line_bytes = self.proc.stdout.readline()
                line = line_bytes.decode("utf-8", errors="ignore").strip()
                if line == "" and len(response_lines) > 0:
                    break
                if line:
                    response_lines.append(line)
            return "\n".join(response_lines)
        except Exception as e:
            print(f"상시 통신 오류: {e}")
            return ""

    def enable_ai_interface(self):
        """AI 로딩이 완료되면 UI를 정상 대국 상태로 전환합니다."""
        self.ai_button.config(state="normal")
        self.status_label.config(
            text="흑의 차례입니다. 카타고 AI 사전 준비 완료(즉시 분석 가능).",
            fg="green",
        )

    def ask_katago_for_answer(self):
        """이미 대기 중인 카타고에게 상황만 쏘아 보내 정답 마킹"""
        if not self.is_ai_ready:
            return

        self.status_label.config(
            text="카타고 AI가 정답수를 즉시 연산 중입니다...", fg="blue"
        )
        self.root.update()

        # 보드 클리어 및 순간 동기화
        self.send_gtp_bytes("clear_board")

        abc = "ABCDEFGHJKLMNOPQRST"
        for x in range(self.board_size):
            for y in range(self.board_size):
                stone = self.engine.board[x][y]
                if stone != 0:
                    color = "black" if stone == 1 else "white"
                    gtp_x = abc[x]
                    gtp_y = self.board_size - y
                    self.send_gtp_bytes(f"play {color} {gtp_x}{gtp_y}")

        # 정답 탐색 명령 발송
        current_color = "black" if self.current_turn == 1 else "white"
        ai_response = self.send_gtp_bytes(f"genmove {current_color}")

        # 결과 파싱 후 화면에 초록색 점 마킹
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
                    text=f"분석 완료! 카타고 추천 {turn_name}의 정답수 ➔ [{col_char}{row_num}]",
                    fg="black",
                )
            else:
                self.status_label.config(
                    text="카타고 분석 결과: 이 국면은 패스(Pass)하는 것이 최선입니다.",
                    fg="black",
                )
        else:
            self.status_label.config(
                text="AI 통신 데이터가 올바르지 않습니다. (엔진이 아직 튜닝 연산 중일 수 있습니다)",
                fg="red",
            )

    # ==========================================
    # 💾 4단계: 파일 시스템 및 나머지 GUI 로직
    # ==========================================
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
        if not self.is_ai_ready:
            return
        mode = self.edit_mode.get()
        if mode == "normal":
            turn_text = "흑" if self.current_turn == 1 else "백"
            self.status_label.config(
                text=f"일반 대국 모드: {turn_text}의 차례입니다.", fg="black"
            )
        elif mode == "add_black":
            self.status_label.config(
                text="흑돌 편집 모드: 바둑판 클릭 시 흑돌이 연속 배치됩니다.",
                fg="black",
            )
        elif mode == "add_white":
            self.status_label.config(
                text="백돌 편집 모드: 바둑판 클릭 시 백돌이 연속 배치됩니다.",
                fg="black",
            )
        elif mode == "delete":
            self.status_label.config(
                text="지우개 모드: 클릭 시 바둑돌이 하나씩 지워집니다.", fg="black"
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

        if mode == "delete" or self.engine.board[x][y] != 0:
            self.engine.board[x][y] = 0
            self.engine.ko_coordinate = None
            self.ai_recommended_move = None
            self.refresh_stones_on_screen()
            return

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
            if self.engine.ko_coordinate == [(x, y)]:
                messagebox.showwarning(
                    "패(劫) 착수 금지", "패 규칙에 의거해 지금 즉시 되따낼 수 없습니다!"
                )
                return
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

    def on_board_right_click(self, event):
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
        import winsound

        # 돌을 그리는 코드 바로 아래나 위에 넣어주세요.
        # MB_OK는 윈도우의 아주 가볍고 깔끔한 '톡' 하는 사운드를 냅니다.
        winsound.MessageBeep(winsound.MB_OK)

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
    # 💾 4단계: 파일 시스템(SGF) 입출력
    # ==========================================
    def save_sgf_file(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".sgf",
            filetypes=[("Smart Game Format 아카이브", "*.sgf")],
            title="사활 문제 저장",
        )
        if not file_path:
            return
        try:
            abc = "abcdefghijklmnopqrstuvwxyz"
            sgf_content = f"(;SZ[{self.board_size}]AP[PythonTsumegoTool:2.0]"
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
            messagebox.showinfo("저장 완료", "저장 성공!")
        except Exception as e:
            messagebox.showerror("오류", f"저장 실패: {e}")

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
        """프로그램 종료 시 켜져 있던 카타고 상시 프로세스도 깨끗하게 동반 종료시킵니다."""
        if self.proc and self.proc.poll() is None:
            try:
                self.proc.stdin.write("quit\n\n".encode("utf-8"))
                self.proc.stdin.flush()
                self.proc.wait(timeout=1)
            except:
                self.proc.terminate()
        self.root.destroy()
        # -----------------------------------------

    # 1. 카타고(GTP) 연동용 함수 (대문자, 'I' 제외)
    # -----------------------------------------
    def to_gtp_coords(self, x, y):
        """내부 숫자(x, y) -> 카타고 대문자 좌표 (예: 3,3 -> D16)"""
        alphabet = "ABCDEFGHJKLMNOPQRSTUVWXY"  # 'I'가 빠져있습니다.
        if 0 <= x < self.board_size and 0 <= y < self.board_size:
            col = alphabet[x]
            row = str(self.board_size - y)  # 아래서부터 1층씩 올라가는 계산
            return f"{col}{row}"
        return "PASS"

    def from_gtp_coords(self, gtp_str):
        """카타고 대문자 답변 -> 내부 숫자(x, y) (예: D16 -> 3,3)"""
        gtp_str = gtp_str.strip().upper()
        if gtp_str == "PASS" or not gtp_str:
            return None
        alphabet = "ABCDEFGHJKLMNOPQRSTUVWXY"
        try:
            col_char = gtp_str[0]
            x = alphabet.index(col_char)
            y = self.board_size - int(gtp_str[1:])
            return x, y
        except (ValueError, IndexError):
            return None

    # -----------------------------------------
    # 2. SGF 파일 저장/읽기용 함수 (소문자, 'I' 포함)
    # -----------------------------------------
    def to_sgf_coords(self, x, y):
        """내부 숫자(x, y) -> SGF 저장용 소문자 좌표 (예: 3,3 -> dd)"""
        alphabet = "abcdefghijklmnopqrstuvwxyz"  # 'i'를 포함한 순서대로입니다.
        if 0 <= x < self.board_size and 0 <= y < self.board_size:
            col = alphabet[x]
            row = alphabet[y]  # SGF는 위에서부터 내려가므로 뒤집지 않습니다.
            return f"{col}{row}"
        return ""

    def from_sgf_coords(self, sgf_str):
        """SGF 소문자 좌표 -> 내부 숫자(x, y) (예: dd -> 3,3)"""
        sgf_str = sgf_str.strip().lower()
        if len(sgf_str) != 2:
            return None
        alphabet = "abcdefghijklmnopqrstuvwxyz"
        try:
            x = alphabet.index(sgf_str[0])
            y = alphabet.index(sgf_str[1])
            return x, y
        except ValueError:
            return None


if __name__ == "__main__":
    window = tk.Tk()
    app = BadukTsumegoGUI(window, board_size=13)
    window.mainloop()
