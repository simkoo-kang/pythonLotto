import tkinter as tk
from PIL import Image, ImageTk
import random
import os

# from util.log_util import LogUtil


"""
jigsaw/
│
├── piece.py         # 1. 개별 조각의 정보와 좌표를 담당하는 클래스
├── group_manager.py # 2. 조각 간의 결합(이웃) 및 일괄 이동을 담당하는 클래스
├── game_engine.py   # 3. 3x3 배치 및 스와프/승리 조건을 판단하는 핵심 로직
└── main.py          # 4. GUI 실행 및 마우스 이벤트를 연결하는 메인 진입점
"""


# --- CONFIGURATION ---
IMAGE_PATH = "./game/pic/puzzle.png"  # Path to your image
ROWS = 4                         # Number of rows
COLS = 4                         # Number of columns


# logger = LogUtil.get_logger("JigsawPuzzle")


class JigsawPuzzle:
    def __init__(self, root, image_path, rows, cols):
        self.root = root
        self.root.title("Python Jigsaw Puzzle")
        
        self.rows = rows
        self.cols = cols
        
        # 1. 이미지 로드 및 크기 조절
        if not os.path.exists(image_path):
            self.create_dummy_image(image_path)
            
        self.original_image = Image.open(image_path)
        self.img_width, self.img_height = self.original_image.size
        
        # 화면에 너무 크지 않게 조절 (최대 500픽셀)
        max_size = 500
        if self.img_width > max_size or self.img_height > max_size:
            self.original_image.thumbnail((max_size, max_size))
            self.img_width, self.img_height = self.original_image.size

        self.piece_width = self.img_width // self.cols
        self.piece_height = self.img_height // self.rows

        # 화면 중앙 배치를 위한 캔버스 크기 설정
        self.canvas_width = self.img_width + 100
        self.canvas_height = self.img_height + 140
        
        self.canvas = tk.Canvas(root, width=self.canvas_width, height=self.canvas_height, bg="#2c3e50")
        self.canvas.pack()

        # 게임판 시작 좌표 (화면 중앙 기준)
        self.start_x = (self.canvas_width - self.img_width) // 2
        self.start_y = 40

        self.pieces = []
        self.selected_piece = None
        self.drag_data = {"x": 0, "y": 0, "start_grid_pos": 0}

        self.setup_game()
        self.center_window()
        
    def center_window(self):
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - self.canvas_width) // 2
        y = (screen_height - self.canvas_height) // 2
        self.root.geometry(f"{self.canvas_width}x{self.canvas_height}+{x}+{y}")

    def create_dummy_image(self, path):
        print(f"Image '{path}' not found. Creating a temporary puzzle image...")
        img = Image.new('RGB', (450, 450), color='#3498db')
        from PIL import ImageDraw
        d = ImageDraw.Draw(img)
        d.text((160, 210), "Python Jigsaw!", fill="#ffffff")
        img.save(path)

    def setup_game(self):
        raw_pieces = []
        correct_index = 0
        for r in range(self.rows):
            for c in range(self.cols):
                left = c * self.piece_width
                top = r * self.piece_height
                right = left + self.piece_width
                bottom = top + self.piece_height

                crop_img = self.original_image.crop((left, top, right, bottom))
                tk_img = ImageTk.PhotoImage(crop_img)

                raw_pieces.append({
                    "image": tk_img,
                    "correct_idx": correct_index
                })
                correct_index += 1

        # 0~8번 자리를 무작위 배정하기 위해 섞음
        grid_positions = list(range(self.rows * self.cols))
        random.shuffle(grid_positions)

        # 섞인 위치대로 화면에 3*3 배치
        for current_grid_pos, piece_info in zip(grid_positions, raw_pieces):
            r = current_grid_pos // self.cols
            c = current_grid_pos % self.cols
            
            x = self.start_x + c * self.piece_width + (self.piece_width // 2)
            y = self.start_y + r * self.piece_height + (self.piece_height // 2)

            # 조각 생성 및 태그 설정
            canvas_id = self.canvas.create_image(x, y, image=piece_info["image"], tags="piece")

            self.pieces.append({
                "id": canvas_id,
                "image": piece_info["image"],
                "correct_idx": piece_info["correct_idx"],
                "current_grid_pos": current_grid_pos
            })

        # [핵심 수정] 캔버스 자체에 마우스 이벤트를 연결하여 인식률 100% 보장
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

    def get_grid_pos_from_coords(self, x, y):
        """좌표를 3x3 그리드 칸 번호(0~8)로 변환"""
        c = (x - self.start_x) // self.piece_width
        r = (y - self.start_y) // self.piece_height
        c = max(0, min(self.cols - 1, int(c)))
        r = max(0, min(self.rows - 1, int(r)))
        return r * self.cols + c

    def get_coords_from_grid_pos(self, grid_pos):
        """그리드 번호(0~8)를 실제 캔버스 중심 좌표(x, y)로 변환"""
        r = grid_pos // self.cols
        c = grid_pos % self.cols
        x = self.start_x + c * self.piece_width + (self.piece_width // 2)
        y = self.start_y + r * self.piece_height + (self.piece_height // 2)
        return x, y
    def on_press(self, event):
        # 클릭한 지점에 있는 가장 가까운 아이템 가져오기
        clicked_item = self.canvas.find_closest(event.x, event.y)
        if not clicked_item:
            return
            
        # [수정] get_tags -> gettags로 변경 및 튜플에서 첫 번째 아이템 지정([0])
        target_id = clicked_item[0]
        tags = self.canvas.gettags(target_id)
        
        if "piece" in tags:
            for piece in self.pieces:
                if piece["id"] == target_id:
                    self.selected_piece = piece
                    self.drag_data["x"] = event.x
                    self.drag_data["y"] = event.y
                    self.drag_data["start_grid_pos"] = piece["current_grid_pos"]
                    self.canvas.tag_raise(piece["id"]) # 잡은 조각을 맨 위로 올림
                    break

    def on_drag(self, event):
        if not self.selected_piece:
            return
        delta_x = event.x - self.drag_data["x"]
        delta_y = event.y - self.drag_data["y"]
        self.canvas.move(self.selected_piece["id"], delta_x, delta_y)
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def on_release(self, event):
        if not self.selected_piece:
            return

        target_grid_pos = self.get_grid_pos_from_coords(event.x, event.y)
        start_grid_pos = self.drag_data["start_grid_pos"]

        # 다른 조각 위에 놓았을 때 서로 위치 교환(Swap)
        target_piece = None
        for piece in self.pieces:
            if piece["current_grid_pos"] == target_grid_pos and piece["id"] != self.selected_piece["id"]:
                target_piece = piece
                break

        if target_piece:
            self.selected_piece["current_grid_pos"] = target_grid_pos
            target_piece["current_grid_pos"] = start_grid_pos
            tx, ty = self.get_coords_from_grid_pos(start_grid_pos)
            self.canvas.coords(target_piece["id"], tx, ty)
        else:
            self.selected_piece["current_grid_pos"] = start_grid_pos

        # 드래그한 조각 정중앙 안착
        sx, sy = self.get_coords_from_grid_pos(self.selected_piece["current_grid_pos"])
        self.canvas.coords(self.selected_piece["id"], sx, sy)

        self.selected_piece = None
        self.check_win_condition()

    def check_win_condition(self):
        is_victory = all(piece["current_grid_pos"] == piece["correct_idx"] for piece in self.pieces)
        if is_victory:
            self.canvas.create_text(
                self.canvas_width // 2, self.canvas_height - 50,
                text="🎉 정답입니다! 퍼즐 완성! 🎉",
                font=("Arial", 20, "bold"),
                fill="#2ecc71"
            )

if __name__ == "__main__":
    root = tk.Tk()
    game = JigsawPuzzle(root, IMAGE_PATH, ROWS, COLS)
    root.mainloop()
