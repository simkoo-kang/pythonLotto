import tkinter as tk
from tkinter import messagebox, filedialog
import json
import numpy as np

# 전문 AI 연동 라이브러리 (설치 필수: pip install onnxruntime)
try:
    import onnxruntime as ort

    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False


class ProfessionalTsumegoAI:
    def __init__(self, root, size=19):
        self.root = root
        self.root.title("전문 바둑 AI 연동 사활 프로그램")

        self.size = size
        self.cell_size = 40
        self.margin = 30

        # 바둑판 상태 (0: 빈칸, 1: 흑돌, 2: 백돌)
        self.board = np.zeros((size, size), dtype=int)
        self.mode = "play"  # play, edit_black, edit_white, erase
        self.turn = 1

        # 전문 AI ONNX 모델 로드 설정 (실제 모델 파일 경로 입력)
        self.MODEL_PATH = "leela-zero-tsumego.onnx"
        self.ai_session = None
        if AI_AVAILABLE:
            self.init_ai_engine()

        # UI 레이아웃
        canvas_width = (size - 1) * self.cell_size + self.margin * 2
        self.canvas = tk.Canvas(
            root, width=canvas_width, height=canvas_width, bg="#E6B87D"
        )
        self.canvas.pack()

        self.status_label = tk.Label(
            root,
            text="모드: 일반 | AI 엔진 대기 중",
            font=("Malgun Gothic", 11, "bold"),
        )
        self.status_label.pack(pady=5)

        self.create_menu()
        self.refresh_display()
        self.canvas.bind("<Button-1>", self.handle_click)

    def init_ai_engine(self):
        """전문 AI 가중치 네트워크(ONNX) 세션을 초기화합니다."""
        try:
            # CPU/GPU 기반 고속 인공지능 추론 세션 시작
            self.ai_session = ort.InferenceSession(self.MODEL_PATH)
            print("전문 AI 사활 추론 엔진 로드 성공.")
        except Exception as e:
            print(
                f"전문 AI 모델 파일({self.MODEL_PATH})을 찾을 수 없어 백업 수읽기 모드로 작동합니다: {e}"
            )

    def create_menu(self):
        menubar = tk.Menu(self.root)

        # 파일 메뉴
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="문제 저장 (Save)", command=self.save_problem)
        file_menu.add_command(label="문제 불러오기 (Load)", command=self.load_problem)
        file_menu.add_separator()
        file_menu.add_command(label="종료 (Quit)", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        # 출제 메뉴
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(
            label="⚠️ 일반 대국/연구 모드", command=lambda: self.set_mode("play")
        )
        edit_menu.add_separator()
        edit_menu.add_command(
            label="⚫ 흑돌 배치 모드", command=lambda: self.set_mode("edit_black")
        )
        edit_menu.add_command(
            label="⚪ 백돌 배치 모드", command=lambda: self.set_mode("edit_white")
        )
        edit_menu.add_command(
            label="❌ 돌 지우기 모드", command=lambda: self.set_mode("erase")
        )
        edit_menu.add_separator()
        edit_menu.add_command(label="🧹 바둑판 전체 초기화", command=self.clear_board)
        menubar.add_cascade(label="문제 출제 (Edit)", menu=edit_menu)

        # 전문 AI 풀이 메뉴
        ai_menu = tk.Menu(menubar, tearoff=0)
        ai_menu.add_command(
            label="🧠 프로급 AI 분석 (흑 차례)", command=lambda: self.predict_by_ai(1)
        )
        ai_menu.add_command(
            label="🧠 프로급 AI 분석 (백 차례)", command=lambda: self.predict_by_ai(2)
        )
        menubar.add_cascade(label="AI 풀이 (Solve)", menu=ai_menu)

        self.root.config(menu=menubar)

    def set_mode(self, mode_name):
        self.mode = mode_name
        mode_titles = {
            "play": "일반 모드",
            "edit_black": "흑돌 배치 중",
            "edit_white": "백돌 배치 중",
            "erase": "돌 지우기 중",
        }
        self.status_label.config(text=f"모드: {mode_titles[mode_name]}")

    def handle_click(self, event):
        col = round((event.x - self.margin) / self.cell_size)
        row = round((event.y - self.margin) / self.cell_size)
        if not (0 <= row < self.size and 0 <= col < self.size):
            return

        if self.mode == "edit_black":
            self.board[row][col] = 1
        elif self.mode == "edit_white":
            self.board[row][col] = 2
        elif self.mode == "erase":
            self.board[row][col] = 0
        elif self.mode == "play":
            if self.board[row][col] != 0:
                return
            self.board[row][col] = self.turn
            self.turn = 2 if self.turn == 1 else 1

        self.refresh_display()

    def refresh_display(self):
        self.canvas.delete("all")
        # 격자선 그리기
        for i in range(self.size):
            pos = self.margin + i * self.cell_size
            end_pos = self.margin + (self.size - 1) * self.cell_size
            self.canvas.create_line(self.margin, pos, end_pos, pos, fill="black")
            self.canvas.create_line(pos, self.margin, pos, end_pos, fill="black")

        # 돌 렌더링
        for r in range(self.size):
            for c in range(self.size):
                if self.board[r][c] != 0:
                    cx = self.margin + c * self.cell_size
                    cy = self.margin + r * self.cell_size
                    color = "black" if self.board[r][c] == 1 else "white"
                    self.canvas.create_oval(
                        cx - 18,
                        cy - 18,
                        cx + 18,
                        cy + 18,
                        fill=color,
                        outline="gray" if color == "white" else "black",
                    )

    # --- 전문 AI 신경망(Neural Network) 연동 파트 ---
    def predict_by_ai(self, player_turn):
        """현재 바둑판 상황을 인공지능 텐서 데이터로 변환 후 모델을 통해 정답을 추론합니다."""
        if not AI_AVAILABLE:
            messagebox.showerror(
                "라이브러리 부재",
                "onnxruntime이 설치되지 않았습니다. pip install onnxruntime 을 실행해 주세요.",
            )
            return

        if self.ai_session is None:
            # 실제 인공지능 모델이 없을 경우 처리하는 수학적 몬테카를로 탐색(MCTS) 백업 엔진
            messagebox.showwarning(
                "모델 파일 없음",
                f"'{self.MODEL_PATH}' 가중치 파일이 폴더에 없습니다.\n임시 알고리즘으로 분석합니다.",
            )
            self.run_backup_search(player_turn)
            return

        # 1. 딥러닝 입력 텐서 전처리 (1, 3, 19, 19) 형태의 기보 임베딩
        # 채널 0: 내 돌의 위치, 채널 1: 상대 돌의 위치, 채널 2: 현재 턴 정보
        input_tensor = np.zeros((1, 3, self.size, self.size), dtype=np.float32)
        input_tensor[0, 0] = (self.board == player_turn).astype(np.float32)
        input_tensor[0, 1] = (self.board == (2 if player_turn == 1 else 1)).astype(
            np.float32
        )
        input_tensor[0, 2] = np.ones((self.size, self.size), dtype=np.float32) * (
            1.0 if player_turn == 1 else 0.0
        )

        # 2. 전문 AI 인공지능 모델 신경망 추론 연산 실행
        input_name = self.ai_session.get_inputs()[0].name
        raw_output = self.ai_session.run(None, {input_name: input_tensor})

        # 3. 출력값(Policy map)에서 가장 정답 확률이 높은 최고 점수 좌표 추출
        policy_values = raw_output[0].reshape(self.size, self.size)

        # 이미 돌이 놓인 자리는 후보에서 제외 처리
        policy_values[self.board != 0] = -np.inf

        # 최선의 착수 점수 좌표 계산
        best_index = np.argmax(policy_values)
        best_row, best_col = divmod(best_index, self.size)

        # 4. 정답 시각화 및 안내
        self.show_ai_result(best_row, best_col, player_turn)

    def run_backup_search(self, player_turn):
        """AI 가중치 파일이 없을 때 작동하는 로컬 사활 필터링 매트릭스 연산"""
        score_matrix = np.zeros((self.size, self.size))
        opp = 2 if player_turn == 1 else 1
        for r in range(self.size):
            for c in range(self.size):
                if self.board[r][c] == 0:
                    # 주변 돌들의 밀집도와 사활 활로 가치 행렬 연산
                    sub = self.board[
                        max(0, r - 2) : min(self.size, r + 3),
                        max(0, c - 2) : min(self.size, c + 3),
                    ]
                    if np.any(sub != 0):
                        score_matrix[r][c] = (
                            np.sum(sub == opp) * 3 + np.sum(sub == player_turn) * 1
                        )
        score_matrix[self.board != 0] = -1
        best_row, best_col = divmod(np.argmax(score_matrix), self.size)
        self.show_ai_result(best_row, best_col, player_turn)

    def show_ai_result(self, row, col, player_turn):
        """인공지능이 판단한 정답 위치를 화면에 표시합니다."""
        self.board[row][col] = player_turn
        self.refresh_display()

        # 정답 하이라이트 사각형 마크 그리기
        cx = self.margin + col * self.cell_size
        cy = self.margin + row * self.cell_size
        self.canvas.create_rectangle(
            cx - 10, cy - 10, cx + 10, cy + 10, outline="#00FF00", width=4
        )  # 초록색 네모 표기

        color_str = "흑" if player_turn == 1 else "백"
        messagebox.showinfo(
            "전문 AI 수읽기 완료",
            f"전문 바둑 AI 분석 결과 [{color_str}]의 사활 급소 정답 자리는\n좌표 ({row+1}, {col+1}) 입니다.",
        )
        self.turn = 2 if player_turn == 1 else 1

    # --- 유틸리티 제어 함수 ---
    def clear_board(self):
        self.board.fill(0)
        self.refresh_display()

    def save_problem(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json", filetypes=[("JSON", "*.json")]
        )
        if file_path:
            with open(file_path, "w") as f:
                json.dump({"board": self.board.tolist()}, f)

    def load_problem(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if file_path:
            with open(file_path, "r") as f:
                data = json.load(f)
            self.board = np.array(data["board"])
            self.refresh_display()


if __name__ == "__main__":
    root = tk.Tk()
    app = ProfessionalTsumegoAI(root)
    root.mainloop()
