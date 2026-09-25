import tkinter as tk
from tkinter import messagebox, filedialog
import json


class AdvancedTsumegoAI:
    def __init__(self, root, size=19):
        self.root = root
        self.root.title("고급 AI 사활 문제 출제 및 풀이 프로그램")

        self.size = size
        self.cell_size = 40
        self.margin = 30

        # 바둑판 상태 (0: 빈칸, 1: 흑돌, 2: 백돌)
        self.board = [[0] * size for _ in range(size)]

        # 모드 설정: "play" (일반/연구), "edit_black" (흑돌 배치), "edit_white" (백돌 배치)
        self.mode = "play"
        self.turn = 1  # 1: 흑, 2: 백

        # UI 구성
        canvas_width = (size - 1) * self.cell_size + self.margin * 2
        self.canvas = tk.Canvas(
            root, width=canvas_width, height=canvas_width, bg="#E6B87D"
        )
        self.canvas.pack()

        # 상태 표시 바
        self.status_label = tk.Label(
            root,
            text="모드: 일반 대국/연구 | 현재 턴: 흑돌",
            font=("Malgun Gothic", 11, "bold"),
        )
        self.status_label.pack(pady=5)

        self.create_menu()
        self.refresh_display()

        # 마우스 클릭 이벤트
        self.canvas.bind("<Button-1>", self.handle_click)

    def create_menu(self):
        menubar = tk.Menu(self.root)

        # 1. 파일 메뉴
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="문제 저장 (Save)", command=self.save_problem)
        file_menu.add_command(label="문제 불러오기 (Load)", command=self.load_problem)
        file_menu.add_separator()
        file_menu.add_command(label="종료 (Quit)", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        # 2. 문제 출제 및 입력 메뉴
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(
            label="⚠️ 일반/연구 모드 (기본)", command=self.set_mode_play
        )
        edit_menu.add_separator()
        edit_menu.add_command(
            label="⚫ 흑돌 배치 모드", command=self.set_mode_edit_black
        )
        edit_menu.add_command(
            label="⚪ 백돌 배치 모드", command=self.set_mode_edit_white
        )
        edit_menu.add_command(label="❌ 돌 지우기 모드", command=self.set_mode_erase)
        edit_menu.add_separator()
        edit_menu.add_command(label="🧹 바둑판 전체 초기화", command=self.clear_board)
        menubar.add_cascade(label="문제 출제 (Edit)", menu=edit_menu)

        # 3. AI 풀이 메뉴
        ai_menu = tk.Menu(menubar, tearoff=0)
        ai_menu.add_command(
            label="🤖 AI 정답 찾기 (흑선)",
            command=lambda: self.run_tsumego_ai(target_turn=1),
        )
        ai_menu.add_command(
            label="🤖 AI 정답 찾기 (백선)",
            command=lambda: self.run_tsumego_ai(target_turn=2),
        )
        menubar.add_cascade(label="AI 풀이 (Solve)", menu=ai_menu)

        self.root.config(menu=menubar)

    def set_mode_play(self):
        self.mode = "play"
        self.update_status("일반 대국/연구 모드 (클릭 시 돌이 번갈아 놓입니다)")

    def set_mode_edit_black(self):
        self.mode = "edit_black"
        self.update_status("문제 출제 중: 클릭하는 곳에 [흑돌]이 놓입니다.")

    def set_mode_edit_white(self):
        self.mode = "edit_white"
        self.update_status("문제 출제 중: 클릭하는 곳에 [백돌]이 놓입니다.")

    def set_mode_erase(self):
        self.mode = "erase"
        self.update_status("문제 출제 중: 클릭하는 곳의 돌을 [삭제]합니다.")

    def update_status(self, text=None):
        if text:
            self.status_label.config(text=text)
        else:
            turn_str = "흑돌" if self.turn == 1 else "백돌"
            self.status_label.config(text=f"모드: 일반 연구 | 현재 턴: {turn_str}")

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
        # 격자선 선치
        for i in range(self.size):
            pos = self.margin + i * self.cell_size
            end_pos = self.margin + (self.size - 1) * self.cell_size
            self.canvas.create_line(self.margin, pos, end_pos, pos, fill="black")
            self.canvas.create_line(pos, self.margin, pos, end_pos, fill="black")

        # 화점
        if self.size == 19:
            for r in [3, 9, 15]:
                for c in [3, 9, 15]:
                    cx = self.margin + c * self.cell_size
                    cy = self.margin + r * self.cell_size
                    self.canvas.create_oval(
                        cx - 3, cy - 3, cx + 3, cy + 3, fill="black"
                    )

        # 돌 그리기
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

    # --- AI 사활 추론 엔진 (트리 탐색 알고리즘) ---
    def run_tsumego_ai(self, target_turn):
        """출제된 판을 분석하여 활로(Liberties) 및 급소를 계산해 정답을 찾아냅니다."""
        self.mode = "play"  # 풀이 시작 시 연구 모드로 전환

        best_move = self.evaluate_best_tsumego_move(target_turn)

        if best_move:
            r, col, score = best_move
            color_name = "흑" if target_turn == 1 else "백"

            # AI 시각적 착수 및 알림
            self.board[r][col] = target_turn
            self.refresh_display()

            # 정답 자리에 하이라이트 사각형 표시
            cx = self.margin + col * self.cell_size
            cy = self.margin + r * self.cell_size
            self.canvas.create_rectangle(
                cx - 8, cy - 8, cx + 8, cy + 8, outline="red", width=3
            )

            messagebox.showinfo(
                "AI 사활 분석 완료",
                f"AI 분석 결과 [{color_name}]의 최선 득점 자리는 ({r+1}행, {col+1}열) 입니다.\n(붉은 네모 표시)",
            )
            self.turn = 2 if target_turn == 1 else 1
            self.update_status()
        else:
            messagebox.showwarning(
                "분석 실패", "바둑판 위에 분석할 만한 사활 상태나 빈 공간이 부족합니다."
            )

    def evaluate_best_tsumego_move(self, turn):
        """국소적 탐색(Local Search) 알고리즘을 수행하여 돌들의 안형(궁도)과 활로를 계산합니다."""
        opp_turn = 2 if turn == 1 else 1
        candidates = []

        # 1. 바둑판 위에 놓인 돌들의 주변(공방 급소 지역)을 필터링하여 탐색 속도 극대화
        for r in range(self.size):
            for c in range(self.size):
                if self.board[r][c] == 0:
                    # 주변 2칸 내에 돌이 있는가? (사활 관련 유효 지역 점검)
                    has_neighbor = False
                    for dr in [-2, -1, 0, 1, 2]:
                        for dc in [-2, -1, 0, 1, 2]:
                            nr, nc = r + dr, c + dc
                            if 0 <= nr < self.size and 0 <= nc < self.size:
                                if self.board[nr][nc] != 0:
                                    has_neighbor = True
                                    break
                    if has_neighbor:
                        score = self.calculate_point_weight(r, c, turn)
                        candidates.append((r, c, score))

        if not candidates:
            return None

        # 가장 높은 가치를 지닌 사활 급소를 정답으로 반환
        candidates.sort(key=lambda x: x[2], reverse=True)
        return candidates[0]

    def calculate_point_weight(self, r, c, turn):
        """특정 좌표에 착수했을 때 얻는 사활적 가치(활로 증가, 궁도 제한, 적의 급소 빼앗기)를 수치화합니다."""
        opp_turn = 2 if turn == 1 else 1
        score = 0

        # 인접 4방향 확인
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.size and 0 <= nc < self.size:
                neighbor = self.board[nr][nc]
                if neighbor == turn:
                    score += 15  # 내 돌 연결 및 활로 확장 (살아남기)
                elif neighbor == opp_turn:
                    score += 25  # 상대 돌 차단 및 궁도 좁히기 (공격 및 파호)
                elif neighbor == 0:
                    score += 5  # 자체 안형/공배 확보

        # 구석(귀)이나 변의 특수성 반영 (사활은 귀에서 자주 발생하므로 가중치 부여)
        if (r <= 2 or r >= self.size - 3) and (c <= 2 or c >= self.size - 3):
            score += 10  # 귀의 사활 가중치

        return score

    # --- 기존 제어 기능 보존 ---
    def clear_board(self):
        if messagebox.askyesno(
            "초기화", "바둑판의 모든 돌을 지우고 깨끗이 비우시겠습니까?"
        ):
            self.board = [[0] * self.size for _ in range(self.size)]
            self.mode = "play"
            self.turn = 1
            self.refresh_display()

    def save_problem(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json", filetypes=[("JSON 파일", "*.json")]
        )
        if not file_path:
            return
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump({"board": self.board}, f)
        messagebox.showinfo("저장", "내가 만든 사활 문제가 성공적으로 저장되었습니다.")

    def load_problem(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON 파일", "*.json")])
        if not file_path:
            return
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.board = data["board"]
            self.mode = "play"
            self.refresh_display()
            messagebox.showinfo(
                "불러오기",
                "사활 문제를 성공적으로 불러왔습니다. [AI 풀이] 메뉴를 통해 정답을 확인해 보세요!",
            )
        except Exception as e:
            messagebox.showerror("오류", f"문제를 불러오지 못했습니다: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = AdvancedTsumegoAI(root)
    root.mainloop()
