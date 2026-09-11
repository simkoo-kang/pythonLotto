# main.py
import tkinter as tk
from PIL import Image, ImageTk
import random
import os

from piece import PuzzlePiece
from group_manager import GroupManager
from game_engine import JigsawEngine

IMAGE_PATH = "./game/pic/puzzle.png"
ROWS = 4
COLS = 4

class JigsawPuzzleApp:
    def __init__(self, root, image_path, rows, cols):
        self.root = root
        self.root.title("Object-Oriented Jigsaw Puzzle")
        
        self.rows = rows
        self.cols = cols
        
        # 이미지 로드 및 전처리
        self.load_image(image_path)
        
        # 레이아웃 크기 설정
        self.canvas_width = self.img_width + 100
        self.canvas_height = self.img_height + 140
        self.canvas = tk.Canvas(root, width=self.canvas_width, height=self.canvas_height, bg="#2c3e50")
        self.canvas.pack()

        # 정중앙 정렬 좌표
        start_x = (self.canvas_width - self.img_width) // 2
        start_y = 40

        # 모듈 부품(객체)들 인스턴스화 및 결합
        self.engine = JigsawEngine(rows, cols, self.piece_width, self.piece_height, start_x, start_y)
        self.group_manager = GroupManager()
        
        self.selected_piece = None
        self.drag_data = {"x": 0, "y": 0}

        self.build_puzzle()
        self.center_window()
        
        # 이벤트 바인딩
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

    def load_image(self, path):
        if not os.path.exists(path):
            img = Image.new('RGB', (450, 450), color='#3498db')
            from PIL import ImageDraw
            d = ImageDraw.Draw(img)
            d.text((150, 210), "OOP Jigsaw Puzzle", fill="#ffffff")
            img.save(path)
            
        self.original_image = Image.open(path)
        self.img_width, self.img_height = self.original_image.size
        
        max_size = 500
        if self.img_width > max_size or self.img_height > max_size:
            self.original_image.thumbnail((max_size, max_size))
            self.img_width, self.img_height = self.original_image.size

        self.piece_width = self.img_width // self.cols
        self.piece_height = self.img_height // self.rows

    def center_window(self):
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - self.canvas_width) // 2
        y = (screen_height - self.canvas_height) // 2
        self.root.geometry(f"{self.canvas_width}x{self.canvas_height}+{x}+{y}")

    def build_puzzle(self):
        # 1. 올바른 순서대로 이미지 조각 크롭 및 정보 생성
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

        # 2. [핵심 수정] 격자 공간(0~8번) 리스트를 만들고 이를 셔플합니다.
        # 이렇게 하면 모든 조각이 무조건 서로 다른 고유한 칸을 배정받아 절대 겹치지 않습니다.
        grid_positions = list(range(self.rows * self.cols))
        random.shuffle(grid_positions)

        canvas_ids = []
        # 생성된 조각(temp_pieces)에 셔플된 고유 격자 위치를 하나씩 1:1로 매칭
        for idx, info in enumerate(temp_pieces):
            # 이 조각이 배치될 고유 격자 위치 추출
            current_grid_pos = grid_positions[idx]
            
            # 계산된 격자 칸의 중심 좌표 구하기
            x, y = self.engine.get_coords_from_grid_pos(current_grid_pos)
            c_id = self.canvas.create_image(x, y, image=info["img"], tags="piece")
            canvas_ids.append(c_id)

            # Piece 객체 생성 시 중복 없는 격자 위치를 전달
            piece_obj = PuzzlePiece(c_id, info["img"], info["correct_idx"], current_grid_pos)
            self.engine.register_piece(piece_obj)

        # 3. 결합 그룹 초기화 (모든 조각이 고유한 자리에 떨어졌으므로 정마찰력으로 독립 배치됨)
        self.group_manager.initialize_groups(canvas_ids)

    def on_press(self, event):
        clicked_item = self.canvas.find_closest(event.x, event.y)
        if not clicked_item: return
        
        # 튜플 형태인 클릭 아이템에서 고유 ID 추출
        target_id = clicked_item[0] if isinstance(clicked_item, tuple) else clicked_item
        
        if "piece" in self.canvas.gettags(target_id):
            self.selected_piece = self.engine.get_piece_by_id(target_id)
            if self.selected_piece:
                self.drag_data["x"] = event.x
                self.drag_data["y"] = event.y
                
                # [핵심 추가] 드래그를 시작한 조각의 '현재 격자 위치'를 저장합니다.
                self.drag_data["start_grid_pos"] = self.selected_piece.current_grid_pos
                
                # 그룹 내 조각들 일괄 레이어 업 (드래그하는 조각들을 맨 위로)
                for p_id in self.group_manager.get_group(target_id):
                    self.canvas.tag_raise(p_id)

    def on_drag(self, event):
        if not self.selected_piece: return
        delta_x = event.x - self.drag_data["x"]
        delta_y = event.y - self.drag_data["y"]
        
        # 그룹 전체 동시 이동
        for p_id in self.group_manager.get_group(self.selected_piece.id):
            self.canvas.move(p_id, delta_x, delta_y)
            
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def on_release(self, event):
        if not self.selected_piece: return

        # 1. 마우스를 놓은 위치의 목표 격자 칸 계산
        cx, cy = self.canvas.coords(self.selected_piece.id)
        target_grid_pos = self.engine.get_grid_pos_from_coords(cx, cy)
        start_grid_pos = self.drag_data["start_grid_pos"]
        
        # 가로/세로 격자 이동량(변화량) 계산
        start_r, start_c = start_grid_pos // self.cols, start_grid_pos % self.cols
        target_r, target_c = target_grid_pos // self.cols, target_grid_pos % self.cols
        
        delta_r = target_r - start_r
        delta_c = target_c - start_c

        current_group = self.group_manager.get_group(self.selected_piece.id)

        # 2. 내 그룹 내의 모든 조각들이 새로 도달할 격자 위치(Map) 계산 및 경계선 체크
        my_old_positions = [] # 내가 비워줄 출발지 격자 목록
        my_new_positions = {} # 내가 들어갈 도착지 격자 목록
        out_of_bounds = False

        for p_id in current_group:
            p = self.engine.get_piece_by_id(p_id)
            my_old_positions.append(p.current_grid_pos)
            
            curr_r, curr_c = p.current_grid_pos // self.cols, p.current_grid_pos % self.cols
            new_r = curr_r + delta_r
            new_c = curr_c + delta_c
            
            # 격자 밖(3x3 영역 외)으로 탈출하려는 무리한 이동이면 스와프 전체 취소
            if not (0 <= new_r < self.rows and 0 <= new_c < self.cols):
                out_of_bounds = True
                break
            my_new_positions[p_id] = new_r * self.cols + new_c

        # 화면 밖으로 나가는 무리한 이동이면 전원 원위치 복귀 처리
        if out_of_bounds:
            delta_r, delta_c = 0, 0
            for p_id in current_group:
                my_new_positions[p_id] = self.engine.get_piece_by_id(p_id).current_grid_pos

        # 3. [완벽한 다대다 격자 Swap 매핑] 
        # 밀려날 상대방 조각들과 그들이 갈 수 있는 빈자리를 정확하게 1:1 매칭합니다.
        opponents = []
        for p in self.engine.pieces:
            if p.id not in current_group and p.current_grid_pos in my_new_positions.values():
                opponents.append(p)

        if opponents and not out_of_bounds:
            # 내 그룹이 비워줄 자리 중, 내 그룹이 새로 들어가지 않는 '진짜 빈자리'를 추려냅니다.
            available_slots = [pos for pos in my_old_positions if pos not in my_new_positions.values()]
            
            # 밀려나는 상대방 조각들을 내가 비워주는 진짜 빈 공간 슬롯에 순서대로 하나씩 꽂아넣습니다.
            for idx, opp in enumerate(opponents):
                if idx < len(available_slots):
                    opp.current_grid_pos = available_slots[idx]
                else:
                    # 이론상 남는 자리가 부족하면 원래 내 그룹이 있던 시작 위치의 여백으로 강제 이동하여 유실 방지
                    opp.current_grid_pos = opp.current_grid_pos - (delta_r * self.cols + delta_c)
            
            # 내 그룹 조각들은 안전하게 목표 구역으로 이동
            for p_id in current_group:
                self.engine.get_piece_by_id(p_id).current_grid_pos = my_new_positions[p_id]
        else:
            # 상대방이 없는 빈 곳이거나 복귀일 때
            for p_id in current_group:
                self.engine.get_piece_by_id(p_id).current_grid_pos = my_new_positions[p_id]

        # 4. [그룹 해체 후 완전 재조립] 
        canvas_ids = [p.id for p in self.engine.pieces]
        self.group_manager.initialize_groups(canvas_ids)

        # 5. [신규 그룹 재조립] 
        for p1 in self.engine.pieces:
            for p2 in self.engine.pieces:
                if p1.id == p2.id: continue
                
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
        for p in self.engine.pieces:
            sx, sy = self.engine.get_coords_from_grid_pos(p.current_grid_pos)
            self.canvas.coords(p.id, sx, sy)

        self.selected_piece = None
        
        # 7. 승리 판정
        if self.engine.check_victory():
            self.canvas.create_text(
                self.canvas_width // 2, self.canvas_height - 50,
                text="🎉 퍼즐 완성! (그룹 연동 성공) 🎉", font=("Arial", 20, "bold"), fill="#2ecc71"
            )

if __name__ == "__main__":
    root = tk.Tk()
    app = JigsawPuzzleApp(root, IMAGE_PATH, ROWS, COLS)
    root.mainloop()
