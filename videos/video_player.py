import os
import sys

# ⚡ [1단계] 컴퓨터에 설치된 진짜 VLC 미디어 플레이어 엔진 경로 찾기 및 등록
vlc_path = r"C:\Program Files\VideoLAN\VLC"
if os.path.exists(vlc_path):
    os.add_dll_directory(vlc_path)

import vlc


# # 1. 현재 파일(video_player.py)의 상위 폴더인 'lotto' 경로를 계산합니다.
# curr_dir = os.path.dirname(os.path.abspath(__file__))  # movie 폴더
# parent_dir = os.path.dirname(curr_dir)                 # lotto 폴더

# # 2. 파이썬 탐색 경로(sys.path)에 'lotto' 폴더를 등록합니다.
# #    이렇게 하면 movie.playlist_popup을 'lotto/movie/...' 구조로 올바르게 찾아갑니다.
# if parent_dir not in sys.path:
#     sys.path.insert(0, parent_dir)

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import time

import logging

# PIL(Pillow) 라이브러리의 로그 레벨을 WARNING 이상으로 올려서 
# DEBUG, INFO 로그가 콘솔에 찍히지 않도록 차단합니다.
logging.getLogger("PIL").setLevel(logging.WARNING)

from util.log_util import LogUtil
from util.str_util import Str

from util.file_util import FileUtil  # 엔진 등록 후 정상 로드
from videos.playlist_popup import PlaylistPopup
# # 기존 Line 35 전후의 코드를 아래와 같이 변경합니다.
# try:
#     # 1. 메인 프로그램(lotto 폴더 기준)에서 호출되거나 방법 1로 실행될 때 작동
#     from movie.playlist_popup import PlaylistPopup
# except ModuleNotFoundError:
#     # 2. video_player.py를 직접 더블클릭하거나 단독 실행(movie 폴더 기준)할 때 작동
#     from playlist_popup import PlaylistPopup

from util.resource import ResUtil
from util.tk_util import TkUtil
from config.config_manager import ConfigManager
from util.text_file_manager import TextManager


# # 1. 실행 파일(.exe) 또는 스크립트(.py)가 위치한 진짜 물리적 폴더 경로 찾기
# if hasattr(sys, "_MEIPASS"):
#     curr_path = os.path.dirname(sys.executable)
# else:
#     curr_path = os.path.dirname(os.path.abspath(__file__))

# # 2. 파이썬이 모듈을 검색하는 경로 리스트(sys.path) 맨 앞에 이 진짜 경로를 주입합니다.
# if curr_path not in sys.path:
#     sys.path.insert(0, curr_path)


# 🚀 [핵심] 독립된 새 창(Toplevel)으로 구동되는 동영상 플레이어 클래스
class VideoPlayer(tk.Tk):

    def __init__(self, config_file_path=None):
        # tk.Toplevel을 상속받아 독립된 서브 창을 생성합니다.
        super().__init__()
        
        # 1. 실행 파일(.exe) 또는 스크립트(.py)가 위치한 진짜 물리적 폴더 경로 찾기
        if hasattr(sys, "_MEIPASS"):
            self.base_path = os.path.dirname(sys.executable)
        else:
            self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.logger.debug(f"현재 위치: {self.base_path} ===================")

        # logger for debugging
        self.logger = LogUtil.get_logger(__file__)
        
        self.relative_path = FileUtil.filename(FileUtil.parent(__file__))
        
        # config_manager and default value
        self._init_config(config_file_path)
        
        # icon
        icon_path = ResUtil.resource_path(self.relative_path, "player.ico")
        self.iconbitmap(icon_path)
        
        self.create_menu()
        
        fg, bg = "black", "#F0F0F0"
        
        # init movie player
        self._init_movie_player(fg, bg)
        
        # --- 하단 컨트롤 바 영역 ---
        self._init_bottom_controlbar(fg, bg)

        # 🚀 [단축키 전역 설정] 창 전체 영역 어디서든 무조건 낚아채어 작동하도록 세팅
        self._init_binding()

        # ⚡ [3단계] 동영상이 패킹되거나 놓여있을 실제 전체 절대 경로 획득
        self.video_file_path = os.path.join(self.base_path, self.default_movie)

        root_items, item_name, key_name = "items", "item", "title"
        playlist_path = os.path.join(self.playlist_dir, "playlist.tms")
        self.playlist = TextManager(file_path=playlist_path, root_name=root_items, item_name=item_name, key_name=key_name)
        """_summary_
        <items>
            <item>
                <title> 재생 목록 파일명 </title>
                <path> 파일 전체 경로 </path>
                <loop> False </loop>
            </item>
        </items>
        """
        self.current_play = None # <item> ... </item>
        self.current_index = -1 # prev, next에서 사용하는 인덱스
        
        self.playlist_name = None # 재생 목록 파일명
        self.popup = None # 재생 목록 편집용 팝업
        
        # 비디오 파일 연동 검증 및 자동 로딩
        if os.path.exists(self.video_file_path):
            self.file_list.append(self.video_file_path)
            self.play_list.append(FileUtil.filename(self.video_file_path))
            self.current_index = 0
            self.start_video()
        else:
            self.time_label.config(text="영상 파일 없음", fg="red")
            self.current_index = -1

        # 윈도우 우측 상단 X 닫기 버튼 이벤트 인터셉트
        self.protocol("WM_DELETE_WINDOW", self.on_window_close)

        # 🚀 [해결 장치 2] 윈도우 제어 포커스 강제 독점 선언 (가장 중요)
        # 창이 열리자마자 윈도우가 모든 키보드/마우스 입력권을 이 동영상 창으로 강제로 끌고 옵니다.
        self.lift()
        self.focus_force()
        self.grab_set()
    
        # 실시간 탐색 바 동기화 타이머 시작
        self.update_ui_loop()

    def _init_config(self, config_file_path=None):
        """_summary_
        initialize config_manager
        Args:
            config_file_path (str, None): D:/Workspace/vscode/lotto/movie . Defaults to None.
        """
        self.logger.debug(f"config_file_path: {config_file_path}")
        file_path = config_file_path if config_file_path else FileUtil.parent(__file__)
        self.logger.debug(file_path)
        self.config_manager = ConfigManager(file_path, False)
        if self.config_manager.get_value("movies") == None:
            self.config_manager.set_value("width", 800)
            self.config_manager.set_value("height", 640)
            self.config_manager.set_value("popup_width", 450)
            self.config_manager.set_value("popup_height", 450)
            self.config_manager.set_value("default_movie", "movies/test.mkv")
            self.config_manager.set_value("default_movie_dir", "D:/Workspace/vscode/lotto/movie/movies")
            self.config_manager.set_value("movies_dir", f"{self.base_path}/movies")
            self.config_manager.set_value("capture_dir", f"{self.base_path}/capture")
            self.config_manager.set_value("playlist_dir", f"{self.base_path}/playlist")
            self.config_manager.save()
        
        self.width = self.config_manager.get_value("width")
        self.height = self.config_manager.get_value("height")
        self.popup_width = self.config_manager.get_value("popup_width")
        self.popup_height = self.config_manager.get_value("popup_height")
        
        self.default_movie = self.config_manager.get_value("default_movie")
        self.default_movie_dir = self.config_manager.get_value("default_movie_dir")
        
        self.movies_dir = self.config_manager.get_value("movies_dir")
        self.capture_dir = self.config_manager.get_value("capture_dir")
        self.playlist_dir = self.config_manager.get_value("playlist_dir")
    
    def _init_movie_player(self, fg, bg):
        self.title("🎬 동영상 플레이어")
        self.geometry(f"{self.width}x{self.height}")
        
        # 동영상이 출력될 검은색 캔버스 프레임 생성
        self.video_frame = tk.Frame(self, bg=bg)
        self.video_frame.pack(expand=True, fill="both", padx=10, pady=10)

        # 💡 중요: 캔버스 프레임이 실제 ID를 가질 수 있도록 창을 강제 업데이트합니다.
        # self.update() 

        # 안정적인 소프트웨어 디코딩 세팅 및 VLC 인스턴스 생성
        vlc_options = ["--no-video-title-show", "--quiet"]
        self.instance = vlc.Instance(vlc_options)
        if self.instance is None:
            self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()

        # 윈도우 창 ID 바인딩 및 VLC 입력 가로채기 원천 차단
        self.player.set_hwnd(self.video_frame.winfo_id())
        self.player.video_set_mouse_input(False)
        self.player.video_set_key_input(False)
        
        # 기본 사운드 음량 세팅 (50%)
        self.player.audio_set_volume(50)
    
    def _init_bottom_controlbar(self, fg, bg):
        self.control_frame = tk.Frame(self, bg=bg)
        self.control_frame.pack(fill="x", side="bottom", pady=10)

        # 재생 / 일시정지 버튼
        self.play_btn = tk.Button(
            self.control_frame, text="▶ 재생", width=10, command=self.toggle_video
        )
        self.play_btn.pack(side="left", padx=10)

        # 시간 표시 레이블
        self.time_label = tk.Label(
            self.control_frame, text="00:00 / 00:00", fg=fg, bg=bg
        )
        self.time_label.pack(side="left", padx=10)

        # 배율 표시 레이블
        self.scale_label = tk.Label(
            self.control_frame, text="크기: 1.0x", fg=fg, bg=bg
        )
        self.scale_label.pack(side="right", padx=(0, 10))

        # 볼륨 표시 레이블
        self.volume_label = tk.Label(
            self.control_frame, text="🔊 볼륨: 50%", fg=fg, bg=bg
        )
        self.volume_label.pack(side="right", padx=(10, 0))

        # 탐색 바 (Seek Bar)
        self.seek_bar = ttk.Scale(
            self.control_frame, from_=0, to=1000, orient="horizontal"
        )
        self.seek_bar.pack(side="left", expand=True, fill="x", padx=10)

        # 탐색 바 드래그 마우스 바인딩
        self.seek_bar.bind("<ButtonPress-1>", self.on_slider_press)
        self.seek_bar.bind("<ButtonRelease-1>", self.on_slider_release)

        self.slider_locked = False
        self.controls_visible = True
    
    def _init_binding(self):
        self.bind("<space>", self.on_space_click)
        self.bind("<Left>", self.seek_backward)
        self.bind("<Right>", self.seek_forward)
        self.bind("<MouseWheel>", self.on_mouse_wheel)
        # 🚀 [새 단축키 추가] Tab, Page Up, Page Down 바인딩
        self.bind("<Tab>", self.toggle_controls)
        self.bind("<Prior>", self.pdge_up)  # Prior = Page Up 의 Tkinter 명칭
        self.bind("<Next>", self.pdge_dn)  # Next = Page Down 의 Tkinter 명칭

        # 만약 새 창 안에서 Alt+A 등의 특정 단축키를 처리하고 싶다면 여기에 따로 연결합니다.
        self.bind("<Alt-a>", self.save_playlist_as)
        self.bind("<Alt-A>", self.save_playlist_as)
        
        self.bind("<Control-o>", self.open_playlist)
        self.bind("<Control-o>", self.open_playlist)

        self.bind("<Control-e>", self.capture_screen)
        self.bind("<Control-E>", self.capture_screen)

        self.bind("<Escape>", self.on_window_close)    # ESC 키
        self.bind("q", self.on_window_close)
        self.bind("Q", self.on_window_close)

        # 2. 🚀 [핵심] 레이블에 왼쪽 마우스 더블 클릭 이벤트 바인딩
        self.bind("<Double-Button-1>", self.on_double_click)

        # self.bind("<Key>", self.on_key_press) # key pressed
        
        # 🚀 [새 단축키 추가] 숫자 키 1, 2, 3 누르면 상응하는 영상 배율로 스위칭
        self.bind("1", lambda e: self.change_video_size(0.5))
        self.bind("2", lambda e: self.change_video_size(1.0))
        self.bind("3", lambda e: self.change_video_size(1.5))

        # 컨트롤바 마우스 휠 보조 바인딩 (이벤트 씹힘 방지)
        self.control_frame.bind("<MouseWheel>", self.on_mouse_wheel)
        self.time_label.bind("<MouseWheel>", self.on_mouse_wheel)
        self.volume_label.bind("<MouseWheel>", self.on_mouse_wheel)
        self.seek_bar.bind("<MouseWheel>", self.on_mouse_wheel)

    def create_menu(self):
        menubar = tk.Menu(self)
        nav_menu = tk.Menu(menubar, tearoff=0)
        nav_menu.add_command(
            label="동영상 선택", command=lambda: self.open_and_read_video()
        )
        nav_menu.add_command(
            label="동영상 폴더 선택", command=lambda: self.open_and_read_folder()
        )
        nav_menu.add_command(
            label="다음...", command=lambda: self.next_video()
        )
        nav_menu.add_separator()
        nav_menu.add_command(label="종료", command=self.on_window_close)
        menubar.add_cascade(label="파일", menu=nav_menu)
        
        nav_menu = tk.Menu(menubar, tearoff=0)
        nav_menu.add_command(
            label="재생 목록", command=lambda: self.open_playlist_popup()
        )
        nav_menu.add_separator()
        nav_menu.add_command(label="재생 목록 불러오기(CTRL+O)", command=self.save_playlist_as)
        nav_menu.add_command(label="재생 목록 다른이름으로 저장(Alt+A)", command=self.save_playlist_as)
        nav_menu.add_command(label="화면 캡쳐(Ctrl+E)", command=self.capture_screen)
        menubar.add_cascade(label="재생", menu=nav_menu)
        
        self.config(menu=menubar)
    
    def append_file(self, filepath):
        """ 목록에 파일 추가 """
        self.file_list.append(filepath)
        self.play_list.append(os.path.basename(filepath))
    
    def remove_file(self, filepath=None, index=None):
        """ 목록에 파일 삭제 """
        if filepath == None and index == None:
            messagebox.showwarning("알림", "삭제할 동영상을 선택해 주세요.")
            return
        if filepath == None:
            self.file_list.pop(index)
            self.play_list.pop(index)
        else:
            self.file_list.remove(filepath)
            self.play_list.remove(os.path.basename(filepath))
    
    def save_playlist_as(self, event):
        """💾 [다른 이름으로 저장] 내 재생목록 데이터(.txt)로 독립 추출하기"""
        file_path = filedialog.asksaveasfilename(
            initialdir=".",
            title="재생 목록 다른 이름으로 저장",
            filetypes=(("재생목록 텍스트", "*.txt"), ("모든 파일", "*.*")),
            defaultextension=".txt",
        )

        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as file:
                    for path in self.file_list:
                        file.write(path + "\n")

                self.playlist_name = file_path

                messagebox.showinfo("완료", "목록이 새 파일로 성공적으로 저장되었습니다!")
                self.logger.debug(f"재생 목록을 저장: {file_path}")
                return file_path
            except Exception as e:
                messagebox.showerror("오류", f"저장 중 실패: {e}")
        return None
    
    def open_playlist(self, event):
        """ 재생 목록 읽어 오기 """
        filetypes = [("재생 목록 파일", "*.txt"), ("모든 파일", "*.*")]
        if self.default_movie_dir:
            file_path = filedialog.askopenfilename(
                title="재생 목록 파일을 선택하세요.",
                initialdir=self.default_movie_dir,
                filetypes=filetypes
            )
        else:
            file_path = filedialog.askopenfilename(
                title="재생 목록 파일을 선택하세요",
                filetypes=filetypes
            )
        
        if file_path:
            self.logger.debug(f"재생 목록 선택: {file_path}")
            filelist = FileUtil.read_lines(file_path=file_path)
            flst = []
            for line in filelist:
                if Str.is_blank(line):
                    continue
                flst.append(line)
            
            if not Str.is_blank_list(flst):
                self.file_list = []
                self.play_list = []
                self.playlist_name = file_path
                for name in flst:
                    self.file_list.append(name)
                    self.play_list.append(FileUtil.filename(name))
                
                self.current_index = 0
                self.first_video()
    
    def open_playlist_popup(self):
        # 1. 새로운 팝업 창 생성
        PlaylistPopup(self, self.popup_width, self.popup_height, self.playlist_dir)
    
    def open_and_read_video(self):
        """사용자가 직접 컴퓨터에서 영상 파일을 탐색하여 읽어오도록 만듭니다."""
        filetypes = [("동영상 파일", "*.mp4 *.avi *.mkv *.wmv"), ("모든 파일", "*.*")]
        if self.default_movie_dir:
            file_path = filedialog.askopenfilename(
                title="재생할 영상 파일을 선택하세요",
                initialdir=self.default_movie_dir,
                filetypes=filetypes,
            )
        else:
            file_path = filedialog.askopenfilename(
                title="재생할 영상 파일을 선택하세요",
                filetypes=filetypes,
            )

        if file_path:  # 사용자가 취소하지 않고 파일을 정상 선택했다면
            self.logger.debug(f"동영상 선택: {file_path}")
            
            """ 폴더 내 다른 파일도 읽어 오기 """
            self.movie_dir = os.path.dirname(file_path)
            
            # 대표적인 이미지 확장자 지정 (튜플 형태로 전달해야 endswith가 인식합니다)
            movie_extensions = (".mp4", ".mkv", ".avi", ".wmv")
    
            # 이미지 파일만 필터링하여 리스트에 저장
            self.file_list = FileUtil.files(self.movie_dir, movie_extensions)
            self.play_list = [FileUtil.filename(path) for path in self.file_list]
            
            self.current_index = self.file_list.index(file_path) # 무조건 하나는 있다. 선택했어니...
            
            self.start_video(file_path)
    
    def open_and_read_folder(self):
        """ 기본 경로 설정 (예: 프로젝트 루트 또는 현재 폴더) """
        if self.default_movie_dir is not None:
            # 🚀 askopenfilename 대신 askdirectory를 사용합니다!
            folder_path = filedialog.askdirectory(
                title="동영상 파일들이 들어있는 폴더를 선택하세요",
                initialdir=self.default_movie_dir,  # 🎯 마찬가지로 기본 경로 지정 가능
            )
        else:
            # 🚀 askopenfilename 대신 askdirectory를 사용합니다!
            folder_path = filedialog.askdirectory(
                title="동영상 파일들이 들어있는 폴더를 선택하세요",
            )

        if folder_path:
            self.logger.debug(f"동영상 폴더 선택: {folder_path}")
            
            self.movie_dir = folder_path
            # 대표적인 이미지 확장자 지정 (튜플 형태로 전달해야 endswith가 인식합니다)
            movie_extensions = (".mp4", ".mkv", ".avi", ".wmv")
    
            # 이미지 파일만 필터링하여 리스트에 저장
            self.file_list = FileUtil.files(self.movie_dir, movie_extensions)
            self.play_list = [FileUtil.filename(path) for path in self.file_list]
            self.current_index = 0 # 처음부터
            self.first_video()
    
    def start_video(self, filename: str=None):
        # 🚀 [해결 장치 2] 윈도우 제어 포커스 강제 독점 선언 (가장 중요)
        # 창이 열리자마자 윈도우가 모든 키보드/마우스 입력권을 이 동영상 창으로 강제로 끌고 옵니다.
        self.lift()
        self.focus_force()
        self.grab_set()
        
        # 기존 재생 중인 영상 정지
        self.player.stop()
        
        if filename is None:
            file_path = self.video_file_path
        else:
            file_path = filename
            self.video_file_path = file_path
            
        self.logger.debug(f"영상 재생 시작: {self.video_file_path}")
        if self.video_file_path in self.file_list:
            self.current_index = self.file_list.index(self.video_file_path)
        
        # self.title(FileUtil.filename(self.video_file_path))
        self.title(self.video_file_path)

        # 새 파일 경로로 미디어 객체 생성 후 로드
        new_media = self.instance.media_new(file_path)
        self.player.set_media(new_media)

        # 즉시 재생 시작
        # 1. 탐색 바 리셋
        self.seek_bar.set(0)
        
        # 2. 시간 레이블 리셋 (총 길이 변수가 self.total_time에 저장되어 있다고 가정)
        self.player.play()
        self.play_btn.config(text="⏸ 일시정지")
        self.update_ui_loop()

    def first_video(self):
        if not Str.is_blank_list(self.file_list):
            self.start_video(self.file_list[self.current_index])
    
    def next_video(self):
        if self.file_list:
            if 1 == len(self.file_list): # 지금 재생 중인 파일 반복
                self.start_video()
            else:
                index = (self.current_index + 1) % len(self.file_list)
                self.start_video(self.file_list[index]) # start_video에서 current_index 재설정
    
    def prev_video(self):
        if self.file_list:
            if 1 == len(self.file_list): # 지금 재생 중인 파일 반복
                self.start_video()
            else:
                index = (self.current_index - 1) % len(self.file_list)
                self.start_video(self.file_list[index]) # start_video에서 current_index 재설정
    
    def update_ui_loop(self):
        # 창이 닫혔는데 타이머가 도는 것을 방지하기 위해 존재 여부 체크
        if not self.winfo_exists():
            return
        
        state = self.player.get_state()
        # ⭐️ [플레이 종료 상황 완벽 감지] VLC 상태가 Ended(6)이거나 재생이 끝났을 때
        if state == vlc.State.Ended:
            self.on_video_ended()
            return
        
        if self.player and not self.slider_locked:
            length = self.player.get_length()
            time_ms = self.player.get_time()

            if length > 0 and time_ms >= 0:
                cur_sec = time_ms // 1000
                tot_sec = length // 1000
                cur_str = Str.to_string_time(cur_sec, type="hour")
                tot_str = Str.to_string_time(tot_sec, type="hour")
                self.time_label.config(
                    text=f"{cur_str} / {tot_str}"
                )

                position = self.player.get_position()
                self.seek_bar.set(position * 1000)

        self.after(200, self.update_ui_loop)

    def on_video_ended(self):
        """플레이가 종료했을 때 다음"""
        self.logger.debug(f"{self.video_file_path} 재생이 종료 되었습니다.{self.loop_file}")
        if self.loop_file:
            self.start_video()
        elif self.file_list and 0<len(self.file_list):
            self.next_video()

    def capture_screen(self, event):
        """별도 변수 없이 self 자체에서 위치와 크기를 직접 가져옵니다."""
        try:
            # 💡 self.root.winfo_xxxx() 가 아니라 self.winfo_xxxx() 로 바로 접근!
            x = self.winfo_rootx()
            y = self.winfo_rooty()
            w = self.winfo_width()
            h = self.winfo_height()

            if w <= 0 or h <= 0:
                return

            if not os.path.exists(self.capture_dir):
                os.makedirs(self.capture_dir)

            timestamp = time.strftime("%Y%m%d_%H%M%S")
            file_path = os.path.join(self.capture_dir, f"snapshot_{timestamp}.png")

            from PIL import ImageGrab
            
            # 내 창 영역만큼 스크린샷 찰칵!
            image = ImageGrab.grab(bbox=(x, y, x + w, y + h))
            image.save(file_path)

            # 💡 [수정] 무거운 messagebox 대신, 1.5초 뒤 자동으로 꺼지는 토스트 창 띄우기
            # self.show_toast(f"캡처 완료! 저장 위치: {file_path}", delay=1500)
            TkUtil.show_toast(self, f"캡처 완료! 저장 위치: {file_path}")
            # messagebox.showinfo("캡처 완료", f"저장 위치: {file_path}")

        except Exception as e:
            messagebox.showerror("오류", f"캡처 중 문제가 생겼습니다:\n{e}")

    def on_double_click(self, event):
        self.toggle_video()
    
    def on_key_press(self, event):
        """
        <KeyPress event send_event=True state=Mod1 keysym=k keycode=75 char='k' x=158 y=229>
        <KeyPress event send_event=True state=Mod1|0x40000 keysym=Up keycode=38 x=575 y=439>
        <KeyPress event send_event=True state=Mod1|0x40000 keysym=Down keycode=40 x=575 y=439>
        <KeyPress event send_event=True state=Mod1 keysym=8 keycode=56 char='8' x=428 y=485> 8 8 56
        <KeyPress event send_event=True state=Mod1 keysym=a keycode=65 char='a' x=428 y=485> 8 a 65
        <KeyPress event send_event=True state=Mod1 keysym=Alt_L keycode=18 x=428 y=485> 8 Alt_L 18
        <KeyPress event send_event=True state=Mod1 keysym=Control_L keycode=17 x=575 y=439>  8 Control_L 17
        <KeyPress event send_event=True state=Control|Mod1 keysym=Control_L keycode=17 x=575 y=439>  12 Control_L 17
        <KeyPress event send_event=True state=Control|Mod1 keysym=e keycode=69 char='\x05' x=575 y=439>  12 e 69
        
        <KeyPress event send_event=True state=Control|Mod1 keysym=Shift_L keycode=16 x=1105 y=-104> 12 Shift_L 16
        <KeyPress event send_event=True state=Shift|Control|Mod1 keysym=L keycode=76 char='\x0c' x=1105 y=-104> 13 L 76
        
        <KeyPress event send_event=True state=Mod1|0x20000 keysym=Control_L keycode=17 x=1105 y=-104> 131080 Control_L 17  Ctrl+Alt+l
        <KeyPress event send_event=True state=Control|Mod1|0x20000 keysym=l keycode=76 x=1105 y=-104> 131084 l 76  Ctrl+Alt+l
        
        <KeyPress event send_event=True state=Mod1|0x20000 keysym=Shift_L keycode=16 x=1105 y=-104> 131080 Shift_L 16  Alt+Shift+l
        <KeyPress event send_event=True state=Shift|Mod1|0x20000 keysym=K keycode=75 char='K' x=1105 y=-104> 131081 K 75  Alt+Shift+l

        <KeyPress event send_event=True state=Control|Mod1 keysym=o keycode=79 char='\x0f' x=504 y=-7> 12 o 79
        <KeyPress event send_event=True state=Mod1|0x20000 keysym=a keycode=65 char='a' x=504 y=-7> 131080 a 65
        """
        if self.popup and self.popup.winfo_exists():
            self.logger.debug("팝업이 열려 있습니다.")
            return
        
        if event.keysym == "Escape" or event.keysym.lower() == "q":  # keycode=27 OR 81
            self.logger.debug(f"종료 키가 눌러 졌습니다.({event})")
            
            self.on_window_close()
            return "break"
        
        print(event, event.state, event.keysym, event.keycode)
        if event.keysym == "Up" and event.keycode == 38:
            self.volume_up(5)
            return "break"
        elif event.keysym == "Down" and event.keycode == 40:
            self.volume_dn(5)
            return "break"
        elif event.state == 12 and event.keycode == 69: # Ctrl+E
            self.capture_screen()
            return "break"
        elif event.state == 12 and event.keycode == 79: # Ctrl+O
            self.capture_screen()
            return "break"
        elif event.state == 131080 and event.keycode == 65: # ALT+A
            self.save_playlist_as()
            return "break"
    
    def volume_up(self, vol):
        if self.player:
            current_volume = self.player.audio_get_volume()
            new_volume = min(100, current_volume + vol)

            self.player.audio_set_volume(new_volume)
            self.volume_label.config(text=f"🔊 볼륨: {new_volume}%")
    
    def volume_dn(self, vol):
        if self.player:
            current_volume = self.player.audio_get_volume()
            new_volume = max(0, current_volume - vol)

            self.player.audio_set_volume(new_volume)
            self.volume_label.config(text=f"🔊 볼륨: {new_volume}%")
    
    def toggle_video(self):
        if self.player.is_playing():
            self.player.pause()
            self.play_btn.config(text="▶ 재생")
        else:
            self.player.play()
            self.play_btn.config(text="⏸ 일시정지")

    def on_space_click(self, event):
        self.toggle_video()
    
    # 🚀 [버그 수정] 왼쪽 방향키: 비율 기준 안전하게 10초 뒤로 이동
    def seek_backward(self, event):
        if self.player:
            length_ms = self.player.get_length()
            if length_ms > 0:
                current_time_ms = self.player.get_time()
                # 10초(10,000ms) 전의 목표 시간 계산
                target_time_ms = max(0, current_time_ms - 10000)
                # 전체 길이 대비 목표 시간의 상대적 비율(0.0 ~ 1.0)을 계산하여 부드럽게 점프
                target_position = target_time_ms / length_ms
                self.player.set_position(target_position)

    # 🚀 [버그 수정] 오른쪽 방향키: 비율 기준 안전하게 10초 앞으로 이동
    def seek_forward(self, event):
        if self.player:
            length_ms = self.player.get_length()
            if length_ms > 0:
                current_time_ms = self.player.get_time()
                # 10초(10,000ms) 후의 목표 시간 계산
                target_time_ms = min(length_ms, current_time_ms + 10000)
                # 전체 길이 대비 목표 시간의 상대적 비율(0.0 ~ 1.0)을 계산하여 부드럽게 점프
                target_position = target_time_ms / length_ms
                self.player.set_position(target_position)

    def on_mouse_wheel(self, event):
        if event.delta > 0:
            self.volume_up(5)
        else:
            self.volume_dn(5)

        return "break"  # 부모 위젯으로 스크롤 이벤트 전파를 강제 중지

    # 🚀 기능 1: Tab 키 누르면 하단 컨트롤 바 토글 (보이기/숨기기)
    def toggle_controls(self, event):
        if self.controls_visible:
            self.control_frame.pack_forget()  # 화면에서 숨기기
            self.controls_visible = False
        else:
            self.control_frame.pack(fill="x", side="bottom", pady=10)  # 다시 배치
            self.controls_visible = True
        return "break"  # Tab 키 고유의 위젯 포커스 이동 기능을 강제로 비활성화

    # 🚀 기능 2: Page Up 키 누르면 볼륨 큰 폭으로 올리기 (10% 증가)
    def pdge_up(self, event):
        """
        <KeyPress event send_event=True state=Mod1|0x40000 keysym=Prior keycode=33 x=389 y=542>
        """
        self.prev_video()

    # 🚀 기능 3: Page Down 키 누르면 볼륨 큰 폭으로 내리기 (10% 감소)
    def pdge_dn(self, event):
        """
        <KeyPress event send_event=True state=Mod1|0x40000 keysym=Next keycode=34 x=389 y=542>
        """
        self.next_video()
    
    # 🚀 [핵심 신규 기능] 동영상 해상도를 감지하여 창 크기를 정밀 배율로 제어
    def change_video_size(self, scale_factor):
        if self.player:
            self.logger.debug(f"영상 사이즈 변경: {scale_factor}배")
            
            # 1. 현재 사용 중인 모니터의 전체 해상도(가로, 세로) 구하기
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()

            # 작업 표시줄 등을 고려하여 모니터 실제 가용 최대 크기 제한 버퍼 설정 (여유 여백 60픽셀)
            max_allowed_width = screen_width - 60
            max_allowed_height = screen_height - 120

            # 2. 비디오의 원래 원본 해상도 추출
            width = self.player.video_get_width()
            height = self.player.video_get_height()

            if width <= 0 or height <= 0:
                width, height = 800, 600  # 기본 안전값 방어용

            # 3. 배율이 적용된 타겟 창 크기 계산 (컨트롤 바 패딩 포함)
            target_width = int(width * scale_factor) + 20
            target_height = int(height * scale_factor) + 80

            # 🚨 [방어선 1] 만약 요구한 크기가 모니터 스크린 크기보다 크다면 모니터 최댓값으로 강제 고정
            is_capped = False
            if target_width > max_allowed_width:
                # 가로 세로 비율 유지하며 가로 기준 고정
                ratio = max_allowed_width / target_width
                target_width = max_allowed_width
                target_height = int(target_height * ratio)
                is_capped = True

            if target_height > max_allowed_height:
                # 가로 세로 비율 유지하며 세로 기준 고정
                ratio = max_allowed_height / target_height
                target_height = max_allowed_height
                target_width = int(target_width * ratio)
                is_capped = True

            # 4. 🚨 [방어선 2] 창이 화면 우측이나 하단 밖으로 탈출하지 않도록 위치(X, Y) 보정
            # 현재 창의 좌상단 위치 기준값 구하기
            current_x = self.winfo_x()
            current_y = self.winfo_y()

            # 새 창 크기가 모니터 끝을 치고 나가는지 검사하여 위치 당겨오기
            if current_x + target_width > screen_width:
                current_x = screen_width - target_width - 30
            if current_y + target_height > screen_height:
                current_y = screen_height - target_height - 70

            # 최소 화면 위치 방어 (좌상단이 마이너스로 튀는 것 방지)
            current_x = max(10, current_x)
            current_y = max(10, current_y)

            # 5. 최종 보정된 크기와 위치를 Tkinter에 주입
            self.geometry(f"{target_width}x{target_height}+{current_x}+{current_y}")

            # 레이블에 상태 반영
            display_text = f"크기: {scale_factor}x"
            if is_capped:
                display_text += " (최대제한)"
            self.scale_label.config(text=display_text)

    def on_slider_press(self, event):
        self.slider_locked = True

    def on_slider_release(self, event):
        if self.player:
            target_pos = self.seek_bar.get() / 1000.0
            self.player.set_position(target_pos)
        self.slider_locked = False

    def on_window_close(self, event=None):
        """플레이어 창만 닫을 때 메모리를 깨끗하게 정리하고 창을 소멸시킵니다."""
        try:
            if self.player:
                self.player.stop()
                self.player.release()
            if self.instance:
                self.instance.release()
        except Exception as e:
            pass
        self.destroy()  # 메인 프로세스는 살려두고 이 창만 소멸


if __name__ == "__main__":
    app = VideoPlayer()
    app.mainloop()
