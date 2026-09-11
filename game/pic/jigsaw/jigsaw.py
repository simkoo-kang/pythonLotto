# main.py
import os

# # 현재 실행 경로와 util 폴더 경로를 시스템 패스에 추가
# current_dir = os.path.dirname(os.path.abspath(__file__))
# sys.path.append(current_dir)
# sys.path.append(os.path.join(current_dir, 'util'))

# # --- [필수 수정] PyInstaller 임시 폴더 경로 추적 함수 ---
# def resource_path(relative_path):
#     """ 실행 파일 내부(임시폴더) 또는 개발 환경의 절대 경로를 반환합니다. """
#     try:
#         # PyInstaller에 의해 실행될 때 압축 해제된 임시 폴더 경로 추출
#         base_path = sys._MEIPASS
#     except Exception:
#         # 일반 파이썬 코드로 실행 중일 때의 현재 폴더 경로
#         base_path = os.path.abspath(".")

#     return os.path.join(base_path, relative_path)

# # --- [수정] PyInstaller exe 및 일반 환경 모두 지원하는 경로 주입 ---
# try:
#     base_path = sys._MEIPASS  # exe 파일로 실행될 때의 임시 폴더 경로
# except Exception:
#     base_path = os.path.abspath(".")  # 일반 py 코드로 실행될 때의 경로

# # 시스템 패스에 최상위 폴더와 util 폴더를 강제 삽입 (맨 앞에 등록하여 최우선 검색)
# if base_path not in sys.path:
#     sys.path.insert(0, base_path)

# util_path = os.path.join(base_path, 'util')
# if util_path not in sys.path:
#     sys.path.insert(0, util_path)

import pygame

pygame.init()

import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import random

from piece import PuzzlePiece
from group_manager import GroupManager
from game_engine import JigsawEngine
from util.log_util import LogUtil


# --- [추가] 사운드 재생을 위한 믹서 초기화 ---
pygame.mixer.init()

# def load_sound(filename):
#     try:
#         return pygame.mixer.Sound(filename)
#     except pygame.error:
#         print(f"🔊 경고: {filename} 파일을 찾을 수 없어 소리가 나지 않습니다.")
#         return None

# 효과음 파일 불러오기
# effect_sound = load_sound("./game/ddong/effect.wav")
effect_sound = pygame.mixer.Sound("./game/ddong/effect.wav")
# effect_sound = pygame.mixer.Sound(resource_path("./game/ddong/effect.wav"))


# 배경음악 파일 로드 및 무한 반복(-1) 재생
pygame.mixer.music.load("./game/ddong/background2.mp3")
pygame.mixer.music.play(-1) 

DEFAULT_SIZE = 600


class JigsawPuzzleApp:
    def __init__(self, root):
        self.root = root
        # self.root.title("Object-Oriented Jigsaw Puzzle")
        
        # 기본 설정 (초기값 3x3)
        self.rows = 3
        self.cols = 3
        self.image_path = "./game/pic/images/puzzle.png"
        
        self.logger = LogUtil.get_logger("JigsawPussle")
        
        # 1. 상단 메뉴바 구성 (난이도 선택 및 이미지 선택)
        self.create_menu()

        # 2. 캔버스 초기 선언 (지정되지 않은 상태로 기본 생성 후 이미지 로드 시 크기 가동)
        self.canvas = tk.Canvas(root, bg="#2c3e50")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # 3. 마우스 안전 통합 바인딩 (컨테이너 자체에 선언하여 영구 인식 보장)
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

        # 4. 게임 상태 변수 초기화 및 첫 게임 시작
        self.selected_piece = None
        self.drag_data = {"x": 0, "y": 0, "start_grid_pos": 0}
        
        self.start_new_game()

    def update_title(self):
        """[추가] 현재 이미지 이름과 난이도를 기반으로 창 타이틀을 동적으로 변경합니다."""
        file_name = os.path.basename(self.image_path)
        # 예: "직소 퍼즐 [puzzle_image.jpg] - 난이도: 3x3"
        self.root.title(f"직소 퍼즐 [{file_name}] - 난이도: {self.cols}x{self.rows}")
        self.logger.debug(f"직소 퍼즐 [{file_name}] - 난이도: {self.cols}x{self.rows}")

    def create_menu(self):
        """상단 메뉴바를 생성합니다."""
        menubar = tk.Menu(self.root)
        
        # 파일 메뉴 (이미지 불러오기)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="이미지 선택...", command=self.change_image)
        file_menu.add_separator()
        file_menu.add_command(label="종료", command=self.root.quit)
        menubar.add_cascade(label="파일", menu=file_menu)
        
        # 난이도 메뉴
        difficulty_menu = tk.Menu(menubar, tearoff=0)
        difficulty_menu.add_command(label="초급 (3 x 3)", command=lambda: self.change_difficulty(3, 3))
        difficulty_menu.add_command(label="중급 (4 x 4)", command=lambda: self.change_difficulty(4, 4))
        difficulty_menu.add_command(label="고급 (5 x 5)", command=lambda: self.change_difficulty(5, 5))
        menubar.add_cascade(label="난이도", menu=difficulty_menu)
        
        # 배경음악 On/Off
        bgs_menu = tk.Menu(menubar, tearoff=0)
        bgs_menu.add_command(label="음악 변경", command=self.change_music_file)
        bgs_menu.add_separator()
        bgs_menu.add_command(label="배경 On", command=lambda: self.change_background_sound(False))
        bgs_menu.add_command(label="배경 Off", command=lambda: self.change_background_sound(True))
        menubar.add_cascade(label="배경음악", menu=bgs_menu)
        
        # 소리크기 조절(20%, 50%, 80%)
        volume_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="볼륨 조절", menu=volume_menu)

        # 클릭 시 해당 볼륨으로 변경
        volume_menu.add_command(label="소리 작게 (20%)", command=lambda: pygame.mixer.music.set_volume(0.2))
        volume_menu.add_command(label="소리 중간 (50%)", command=lambda: pygame.mixer.music.set_volume(0.5))
        volume_menu.add_command(label="소리 크게 (80%)", command=lambda: pygame.mixer.music.set_volume(0.8))

        self.root.config(menu=menubar)

    def change_image(self):
        """사용자가 컴퓨터에서 이미지를 선택하도록 팝업을 띄웁니다."""
        file_types = [("이미지 파일", "*.jpg *.jpeg *.png *.bmp *.gif")]
        selected = filedialog.askopenfilename(title="퍼즐로 사용할 이미지 선택", filetypes=file_types)
        
        if selected:
            self.image_path = selected
            self.start_new_game()
            
    def change_difficulty(self, rows, cols):
        """난이도를 변경하고 게임을 재시작합니다."""
        self.rows = rows
        self.cols = cols
        self.start_new_game()
    
    def change_background_sound(self, bgmOnOff: bool):
        if bgmOnOff:
            pygame.mixer.music.pause()  # 일시정지
            self.logger.debug("BGM 꺼짐")
        
        else:
            pygame.mixer.music.unpause()  # 다시 재생
            self.logger.debug("BGM 켜짐")
    
    def change_music_file(self):
        # 파일 탐색기 창 열기
        file_path = filedialog.askopenfilename(
            title="새로운 배경음악 선택",
            filetypes=[("Audio Files", "*.mp3 *.wav *.ogg")]
        )
        
        # 파일을 선택했을 경우에만 실행
        if file_path:
            pygame.mixer.music.stop()          # 기존 음악 멈추기
            pygame.mixer.music.load(file_path) # 새 음악 파일 로드
            pygame.mixer.music.play(-1)        # 무한 반복 재생 (-1)
            self.logger.debug(f"배경음악 변경됨: {file_path}")

    def start_new_game(self):
        """화면과 엔진을 완전히 청소하고 새로운 퍼즐을 빌드합니다."""
        # 캔버스 엘리먼트 전원 박멸 (방치 아이템 제거)
        self.canvas.delete("all")

        self.update_title();

        # 이미지 로드 및 사이즈 재계산
        self.load_image(self.image_path)
        
        # 화면 중앙 정렬 및 캔버스 창 리사이징
        self.canvas_width = self.img_width + 100
        self.canvas_height = self.img_height + 140
        self.canvas.config(width=self.canvas_width, height=self.canvas_height)
        
        start_x = (self.canvas_width - self.img_width) // 2
        start_y = 40

        # 핵심 엔진 새 제품으로 교체 (이전 찌꺼기 인덱스 파괴)
        self.engine = JigsawEngine(self.rows, self.cols, self.piece_width, self.piece_height, start_x, start_y)
        self.group_manager = GroupManager()
        
        self.selected_piece = None

        # 조각 쪼개고 새로 그리기
        self.build_puzzle()
        self.center_window()
        
        # 중요: 다이얼로그가 포커스를 뺏어갔을 수 있으므로 마우스 포커스 강제 복원
        self.canvas.focus_set()

    def load_image(self, path):
        if not os.path.exists(path):
            img = Image.new('RGB', (DEFAULT_SIZE, DEFAULT_SIZE), color='#3498db')
            from PIL import ImageDraw
            d = ImageDraw.Draw(img)
            d.text((150, 210), "Jigsaw Puzzle", fill="#ffffff")
            img.save(path)
            self.image_path = path
            
        self.original_image = Image.open(self.image_path)
        
        # 알파 채널(RGBA)이 있을 경우 RGB로 강제 변환하여 크롭 오류 방지
        if self.original_image.mode in ('RGBA', 'LA'):
            background = Image.new("RGB", self.original_image.size, (255, 255, 255))
            background.paste(self.original_image, mask=self.original_image.split()[-1])
            self.original_image = background
            
        self.img_width, self.img_height = self.original_image.size
        
        # 모니터에 알맞은 최대 크기로 최적화
        max_size = DEFAULT_SIZE
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
        temp_pieces = []
        correct_idx = 0
        for r in range(self.rows):
            for c in range(self.cols):
                left = c * self.piece_width
                top = r * self.piece_height
                
                # 정밀한 크롭 범위 연산
                right = left + self.piece_width
                bottom = top + self.piece_height
                
                crop_img = self.original_image.crop((left, top, right, bottom))
                tk_img = ImageTk.PhotoImage(crop_img)
                temp_pieces.append({"img": tk_img, "correct_idx": correct_idx})
                correct_idx += 1

        # 격자 공간 중복 없이 셔플
        grid_positions = list(range(self.rows * self.cols))
        random.shuffle(grid_positions)

        canvas_ids = []
        for idx, info in enumerate(temp_pieces):
            current_grid_pos = grid_positions[idx]
            x, y = self.engine.get_coords_from_grid_pos(current_grid_pos)
            
            c_id = self.canvas.create_image(x, y, image=info["img"], tags="piece")
            canvas_ids.append(c_id)

            piece_obj = PuzzlePiece(c_id, info["img"], info["correct_idx"], current_grid_pos)
            self.engine.register_piece(piece_obj)

        self.group_manager.initialize_groups(canvas_ids)
        self.reset_group()

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

    def reset_group(self):
        # 그룹 초기화 및 재생성
        # 4. [그룹 해체 후 완전 재조립] 
        canvas_ids = [p.id for p in self.engine.pieces]
        self.group_manager.initialize_groups(canvas_ids)

        # 5. [신규 그룹 재조립] 
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

        # 그룹 초기화 및 재생성
        # 4. [그룹 해체 후 완전 재조립] 
        self.reset_group()

        # 6. 모든 조각들을 각자 자기가 속한 격자 정중앙 좌표로 정렬 (자석 안착)
        # 최종 자석 안착 정렬
        for p in self.engine.pieces:
            sx, sy = self.engine.get_coords_from_grid_pos(p.current_grid_pos)
            self.canvas.coords(p.id, sx, sy)

        self.selected_piece = None

        # # 7. 승리 판정 - 화면에 가려질 수 있는 텍스트 대신 확실한 팝업창을 띄웁니다.
        # if self.engine.check_victory():
        #     import tkinter.messagebox as msgbox
        #     msgbox.showinfo("게임 완료", "🎉 축하합니다! 퍼즐을 완벽하게 완성하셨습니다! 🎉")

        # 7. 승리 판정
        if self.engine.check_victory():
            if effect_sound:
                effect_sound.play()
            # sound_manager.effect_play()
            
            # 대화 상자로 축하 메시지 출력 (화면에 글자 남기기보다 깔끔함)
            import tkinter.messagebox as msgbox
            # messagebox.showinfo("성공!", f"🎉 축하합니다! 퍼즐을 완성했습니다!")
            msgbox.showinfo("성공!", f"🎉 축하합니다! 퍼즐을 완성했습니다!")
            self.logger.debug(f"🎉 축하합니다! 퍼즐을 완성했습니다!")


if __name__ == "__main__":
    root = tk.Tk()
    app = JigsawPuzzleApp(root)
    root.mainloop()
