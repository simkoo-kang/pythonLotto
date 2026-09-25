# main.py
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import random
import os

from piece import PuzzlePiece
from group_manager import GroupManager
from game_engine import JigsawEngine
from util.log_util import LogUtil
from game.pic.jigsaw.main01 import IMAGE_PATH
from game.pic.jigsaw.jigsaw_puzzle_00 import COLS, ROWS

IMAGE_PATH = "./game/pic/images/puzzle.png"
ROWS = 3
COLS = 3


class JigsawPuzzleApp:
    def __init__(self, root, image_path, rows, cols):
        self.root = root
        self.image_path = image_path
        self.rows = rows
        self.cols = cols
        self.image_path = image_path
        
        self.logger = LogUtil.get_logger("JigsawPussle")

        self.update_title()
        
        # 객체 관리 변수 초기화
        self.engine = None
        self.group_manager = GroupManager()
        self.selected_piece = None
        self.drag_data = {"x": 0, "y": 0, "start_grid_pos": 0}
        
        # 캔버스 참조 변수
        self.canvas = None

        # UI 레이아웃 생성
        self.setup_ui()
        
        # 첫 게임 시작
        self.start_new_game()

    def update_title(self):
        """[추가] 현재 이미지 이름과 난이도를 기반으로 창 타이틀을 동적으로 변경합니다."""
        file_name = os.path.basename(self.image_path)
        # 예: "직소 퍼즐 [puzzle_image.jpg] - 난이도: 3x3"
        self.root.title(f"직소 퍼즐 [{file_name}] - 난이도: {self.cols}x{self.rows}")

    def setup_ui(self):
        """상단 컨트롤러 영역(이미지 선택, 난이도 버튼)을 구성합니다."""
        # [에러 해결]: unknown option "-padding" 문제를 padx, pady로 해결
        self.control_frame = tk.Frame(self.root, bg="#34495e")
        self.control_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        # 2. 이미지 선택 버튼
        self.btn_select_img = tk.Button(
            self.control_frame, text="🖼️ 이미지 불러오기", 
            command=self.change_image, bg="#e67e22", fg="white", 
            font=("Arial", 11, "bold"), relief=tk.RAISED, padx=10, pady=5
        )
        self.btn_select_img.pack(side=tk.LEFT, padx=10, pady=5)

        # 난이도 안내 텍스트
        self.lbl_diff = tk.Label(
            self.control_frame, text="난이도 선택:", 
            bg="#34495e", fg="#ecf0f1", font=("Arial", 11, "bold")
        )
        self.lbl_diff.pack(side=tk.LEFT, padx=5)

        # 3. 끊겼던 코드 구현: 난이도 선택 버튼들 (3x3, 4x4, 5x5) 리스트 루프 생성
        for size in [3,4,5]:
            btn = tk.Button(
                self.control_frame, 
                text=f"{size} x {size}", 
                command=lambda s=size: self.change_difficulty(s),
                bg="#3498db", 
                fg="white", 
                font=("Arial", 10, "bold"),
                relief=tk.RAISED,
                padx=8,
                pady=4
            )
            btn.pack(side=tk.LEFT, padx=4, pady=5)

    def load_image(self, path):
        """이미지를 읽어오고 창 크기에 맞게 최적화 비율 조절을 합니다."""
        if not os.path.exists(path):
            img = Image.new('RGB', (450, 450), color='#3498db')
            from PIL import ImageDraw
            d = ImageDraw.Draw(img)
            d.text((120, 210), "Please Select Image!", fill="#ffffff", font=None)
            img.save(path)
        
        self.logger.debug(path)
            
        self.original_image = Image.open(path)
        self.img_width, self.img_height = self.original_image.size
        
        # 모니터 해상도를 고려해 최대 500픽셀로 제한
        max_size = 500
        if self.img_width > max_size or self.img_height > max_size:
            self.original_image.thumbnail((max_size, max_size))
            self.img_width, self.img_height = self.original_image.size

        self.piece_width = self.img_width // self.cols
        self.piece_height = self.img_height // self.rows

    def start_new_game(self):
        """게임을 리셋하고 새 캔버스에 이벤트를 바인딩하여 마우스 먹통을 방지합니다."""
        # 기존 캔버스가 존재하면 깨끗하게 삭제하여 잔상이 남거나 마우스가 먹통되는 것 방지
        if self.canvas:
            self.canvas.destroy()

        # 이미지 정보 최신화
        self.load_image(self.image_path)
        
        # 가로/세로 동적 화면 크기 계산
        self.canvas_width = self.img_width + 100
        self.canvas_height = self.img_height + 120
        
        # 캔버스 새로 생성
        self.canvas = tk.Canvas(self.root, width=self.canvas_width, height=self.canvas_height, bg="#2c3e50", highlightthickness=0)
        self.canvas.pack(side=tk.BOTTOM, pady=10)

        # 게임판 시작 좌표 (화면 정중앙 정렬)
        start_x = (self.canvas_width - self.img_width) // 2
        self.start_y = 30

        # 물리 엔진 및 그룹 매니저 리인스턴스화
        self.engine = JigsawEngine(self.rows, self.cols, self.piece_width, self.piece_height, start_x, self.start_y)
        self.selected_piece = None

        # 퍼즐 조각 빌드 및 배치
        self.build_puzzle()
        
        # [핵심 수정]: 새 캔버스 객체에 마우스 이벤트를 반드시 새로 연결해야 먹통이 안 됩니다.
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        
        # 윈도우 창 위치 재조정
        self.center_window()

    def build_puzzle(self):
        temp_pieces = []
        correct_idx = 0
        for r in range(self.rows):
            for c in range(self.cols):
                left = c * self.piece_width
                top = r * self.piece_height
                crop_img = self.original_image.crop((left, top, left+self.piece_width, top+self.piece_height))
                tk_img = ImageTk.PhotoImage(crop_img)
                temp_pieces.append({"img": tk_img, "correct_idx": correct_idx})
                correct_idx += 1

        grid_positions = list(range(self.rows * self.cols))
        random.shuffle(grid_positions)

        canvas_ids = []
        for idx, info in enumerate(temp_pieces):
            current_grid_pos = grid_positions[idx]
            x, y = self.engine.get_coords_from_grid_pos(current_grid_pos)
            c_id = self.canvas.create_image(x, y, image=info["img"], tags="piece")
            canvas_ids.append(c_id)
            # [수정] 마지막 인자를 실제 뒤섞여 배치된 위치인 current_grid_pos로 바꿉니다.
            piece_obj = PuzzlePiece(c_id, info["img"], info["correct_idx"], current_grid_pos)
            self.engine.register_piece(piece_obj)

        self.group_manager.initialize_groups(canvas_ids)

    def change_image(self):
        """사용자가 컴퓨터에서 원하는 이미지를 직접 고를 수 있게 합니다."""
        file_types = [("Image files", "*.jpg *.jpeg *.png *.bmp *.gif")]
        selected = filedialog.askopenfilename(title="퍼즐로 사용할 이미지 선택", filetypes=file_types)
        if selected:
            self.logger.debug(selected)
            
            self.image_path = selected
            self.start_new_game() # 새 이미지로 판 새로짜기

    def change_difficulty(self, size):
        """난이도 버튼 클릭 시 호출되어 격자 크기를 변경합니다."""
        self.rows = size
        self.cols = size
        self.start_new_game() # 새 난이도로 판 새로짜기

    def center_window(self):
        self.root.update_idletasks()
        # 전체 윈도우 창의 높이는 캔버스 높이 + 상단 컨트롤러 프레임 높이 고려
        frame_height = self.control_frame.winfo_height()
        total_height = self.canvas_height + frame_height + 20
        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        x = (screen_width - self.canvas_width) // 2
        y = (screen_height - total_height) // 2
        self.root.geometry(f"{self.canvas_width}x{total_height}+{x}+{y}")

    def on_press(self, event):
        clicked_item = self.canvas.find_closest(event.x, event.y)
        if not clicked_item: return
        
        target_id = clicked_item[0] if isinstance(clicked_item, tuple) else clicked_item
        
        if "piece" in self.canvas.gettags(target_id):
            self.selected_piece = self.engine.get_piece_by_id(target_id)
            if self.selected_piece:
                self.drag_data["x"] = event.x
                self.drag_data["y"] = event.y
                self.drag_data["start_grid_pos"] = self.selected_piece.current_grid_pos
                
                for p_id in self.group_manager.get_group(target_id):
                    self.canvas.tag_raise(p_id)

    def on_drag(self, event):
        if not self.selected_piece: return
        delta_x = event.x - self.drag_data["x"]
        delta_y = event.y - self.drag_data["y"]
        
        for p_id in self.group_manager.get_group(self.selected_piece.id):
            self.canvas.move(p_id, delta_x, delta_y)
            
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def on_release(self, event):
        if not self.selected_piece: return

        cx, cy = self.canvas.coords(self.selected_piece.id)
        target_grid_pos = self.engine.get_grid_pos_from_coords(cx, cy)
        start_grid_pos = self.drag_data["start_grid_pos"]
        
        start_r, start_c = start_grid_pos // self.cols, start_grid_pos % self.cols
        target_r, target_c = target_grid_pos // self.cols, target_grid_pos % self.cols
        
        delta_r = target_r - start_r
        delta_c = target_c - start_c

        current_group = self.group_manager.get_group(self.selected_piece.id)

        my_old_positions = []
        my_new_positions = {}
        out_of_bounds = False

        for p_id in current_group:
            p = self.engine.get_piece_by_id(p_id)
            my_old_positions.append(p.current_grid_pos)
            
            curr_r, curr_c = p.current_grid_pos // self.cols, p.current_grid_pos % self.cols
            new_r = curr_r + delta_r
            new_c = curr_c + delta_c
            
            if not (0 <= new_r < self.rows and 0 <= new_c < self.cols):
                out_of_bounds = True
                break
            my_new_positions[p_id] = new_r * self.cols + new_c

        if out_of_bounds:
            delta_r, delta_c = 0, 0
            for p_id in current_group:
                my_new_positions[p_id] = self.engine.get_piece_by_id(p_id).current_grid_pos

        opponents = []
        for p in self.engine.pieces:
            if p.id not in current_group and p.current_grid_pos in my_new_positions.values():
                opponents.append(p)

        if opponents and not out_of_bounds:
            available_slots = [pos for pos in my_old_positions if pos not in my_new_positions.values()]
            for idx, opp in enumerate(opponents):
                if idx < len(available_slots):
                    opp.current_grid_pos = available_slots[idx]
                else:
                    opp.current_grid_pos = opp.current_grid_pos - (delta_r * self.cols + delta_c)
            
            for p_id in current_group:
                self.engine.get_piece_by_id(p_id).current_grid_pos = my_new_positions[p_id]
        else:
           for p_id in current_group:
               self.engine.get_piece_by_id(p_id).current_grid_pos = my_new_positions[p_id]
               canvas_ids = [p.id for p in self.engine.pieces]
               self.group_manager.initialize_groups(canvas_ids)

        # 4. [그룹 해체 후 완전 재조립] - 실제 엔진에 등록된 순서대로 조각 ID를 일치시킵니다.
        # 기존에 복잡하게 매핑되던 canvas_ids 대신 엔진 리스트의 고유 ID를 직접 넘겨줍니다.
        self.group_manager.initialize_groups([p.id for p in self.engine.pieces])

        for p1 in self.engine.pieces:
            for p2 in self.engine.pieces:
                if p1.id == p2.id:
                    continue
                if self.engine.is_originally_neighbor(p1.correct_idx, p2.correct_idx):
                    r1, c1 = p1.current_grid_pos // self.cols, p1.current_grid_pos % self.cols
                    r2, c2 = p2.current_grid_pos // self.cols, p2.current_grid_pos % self.cols

                    orig_dr = (p1.correct_idx // self.cols) - (p2.correct_idx // self.cols)
                    orig_dc = (p1.correct_idx % self.cols) - (p2.correct_idx % self.cols)
                    curr_dr = r1 - r2
                    curr_dc = c1 - c2
                    if orig_dr == curr_dr and orig_dc == curr_dc:
                        self.group_manager.merge_groups(p1.id, p2.id)

        # 6. 모든 조각들을 각자 자기가 속한 격자 정중앙 좌표로 정렬 (자석 안착)
        # 최종 자석 안착 정렬

        for p in self.engine.pieces:
            sx, sy = self.engine.get_coords_from_grid_pos(p.current_grid_pos)
            self.canvas.coords(p.id, sx, sy)

        self.selected_piece = None

        # 7. 승리 판정 - 화면에 가려질 수 있는 텍스트 대신 확실한 팝업창을 띄웁니다.
        if self.engine.check_victory():
            import tkinter.messagebox as msgbox
            msgbox.showinfo("게임 완료", "🎉 축하합니다! 퍼즐을 완벽하게 완성하셨습니다! 🎉")

        # # 7. 승리 판정
        # if self.engine.check_victory():
        #     self.canvas.create_text(
        #         self.canvas_width // 2, self.canvas_height - 30,
        #         text="🎉 퍼즐을 완성했습니다! 축하합니다! 🎉",
        #         font=("Arial", 16, "bold"), fill="#2ecc71"
        #     )


if __name__ == "__main__":
    root = tk.Tk()
    app = JigsawPuzzleApp(root, image_path=IMAGE_PATH, rows=ROWS, cols=COLS)
    root.mainloop()
