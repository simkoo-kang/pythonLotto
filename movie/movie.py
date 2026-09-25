import os
import sys
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

# ⚡ [1단계] 컴퓨터에 설치된 진짜 VLC 미디어 플레이어 엔진 경로 찾기 및 등록
vlc_path = r"C:\Program Files\VideoLAN\VLC"
if os.path.exists(vlc_path):
    os.add_dll_directory(vlc_path)

import vlc
from util.file_util import FileUtil  # 엔진 등록 후 정상 로드


# ⚡ [2단계] 단일 파일(.exe) 빌드 시 내부 임시 폴더 경로를 추적하는 함수
def get_resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)


class SingleVideoPlayer(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("단독 비디오 플레이어")
        self.geometry("800x600")

        self.create_menu()
        
        # ⚡ [3단계] 동영상이 패킹되거나 놓여있을 실제 전체 절대 경로 획득
        self.video_file_path = get_resource_path("test.mkv")

        # 동영상이 출력될 검은색 캔버스 프레임 생성
        self.video_frame = tk.Frame(self, bg="black")
        self.video_frame.pack(expand=True, fill="both", padx=10, pady=10)

        # 안정적인 소프트웨어 디코딩 세팅 및 VLC 인스턴스 생성
        # vlc_options = ["--no-hw-dec", "--no-video-title-show"]
        vlc_options = []
        self.instance = vlc.Instance(vlc_options)
        if self.instance is None:
            self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()

        # 윈도우 창 ID 바인딩 및 VLC 입력 가로채기 원천 차단
        self.player.set_hwnd(self.video_frame.winfo_id())
        self.player.video_set_mouse_input(False)
        self.player.video_set_key_input(False)

        # --- 하단 컨트롤 바 영역 ---
        control_frame = tk.Frame(self, bg="#222222")
        control_frame.pack(fill="x", side="bottom", pady=10)

        # 재생 / 일시정지 버튼
        self.play_btn = tk.Button(
            control_frame, text="▶ 재생", width=10, command=self.toggle_video
        )
        self.play_btn.pack(side="left", padx=10)

        # 시간 표시 레이블
        self.time_label = tk.Label(
            control_frame, text="00:00 / 00:00", fg="white", bg="#222222"
        )
        self.time_label.pack(side="left", padx=10)

        # 볼륨 표시 레이블
        self.volume_label = tk.Label(
            control_frame, text="🔊 볼륨: 50%", fg="white", bg="#222222"
        )
        self.volume_label.pack(side="right", padx=10)

        # 탐색 바 (Seek Bar)
        self.seek_bar = ttk.Scale(
            control_frame, from_=0, to=1000, orient="horizontal"
        )
        self.seek_bar.pack(side="left", expand=True, fill="x", padx=10)

        # 탐색 바 드래그 마우스 바인딩
        self.seek_bar.bind("<ButtonPress-1>", self.on_slider_press)
        self.seek_bar.bind("<ButtonRelease-1>", self.on_slider_release)

        self.slider_locked = False

        # 기본 사운드 음량 세팅 (50%)
        self.player.audio_set_volume(50)

        # 🚀 [단축키 전역 설정] 창 전체 영역 어디서든 무조건 낚아채어 작동하도록 세팅
        self.bind_all("<space>", self.on_space_click)
        self.bind_all("<Left>", self.seek_backward)
        self.bind_all("<Right>", self.seek_forward)
        self.bind_all("<MouseWheel>", self.on_mouse_wheel)

        self.bind("<Key>", self.on_key_press) # key pressed
        
        # 🚀 [새 단축키 추가] Tab, Page Up, Page Down 바인딩
        self.bind_all("<Tab>", self.toggle_controls)
        self.bind_all("<Prior>", self.pdge_up)  # Prior = Page Up 의 Tkinter 명칭
        self.bind_all("<Next>", self.pdge_dn)  # Next = Page Down 의 Tkinter 명칭

        # 🚀 [새 단축키 추가] 숫자 키 1, 2, 3 누르면 상응하는 영상 배율로 스위칭
        self.bind_all("1", lambda e: self.change_video_size(0.5))
        self.bind_all("2", lambda e: self.change_video_size(1.0))
        self.bind_all("3", lambda e: self.change_video_size(1.5))

        # 컨트롤바 마우스 휠 보조 바인딩 (이벤트 씹힘 방지)
        control_frame.bind("<MouseWheel>", self.on_mouse_wheel)
        self.time_label.bind("<MouseWheel>", self.on_mouse_wheel)
        self.volume_label.bind("<MouseWheel>", self.on_mouse_wheel)
        self.seek_bar.bind("<MouseWheel>", self.on_mouse_wheel)

        # 비디오 파일 연동 검증 및 자동 로딩
        if os.path.exists(self.video_file_path):
            self.start_video()
            # media = self.instance.media_new(self.video_file_path)
            # self.player.set_media(media)
        else:
            self.time_label.config(text="영상 파일 없음", fg="red")

        # 윈도우 우측 상단 X 닫기 버튼 이벤트 인터셉트
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # 실시간 탐색 바 동기화 타이머 시작
        self.update_ui_loop()

    def create_menu(self):
        menubar = tk.Menu(self)
        nav_menu = tk.Menu(menubar, tearoff=0)
        nav_menu.add_command(
            label="동영상 선택", command=lambda: self.open_and_read_video()
        )
        nav_menu.add_command(
            label="다음...", command=lambda: self.open_and_read_video()
        )
        nav_menu.add_separator()
        nav_menu.add_command(label="종료", command=self.on_closing)
        menubar.add_cascade(label="프로그램 메뉴", menu=nav_menu)
        self.config(menu=menubar)
    
    def open_and_read_video(self):
        """사용자가 직접 컴퓨터에서 영상 파일을 탐색하여 읽어오도록 만듭니다."""
        file_path = filedialog.askopenfilename(
            title="재생할 영상 파일을 선택하세요",
            filetypes=[("동영상 파일", "*.mp4 *.avi *.mkv"), ("모든 파일", "*.*")],
        )

        if file_path:  # 사용자가 취소하지 않고 파일을 정상 선택했다면
            print(f"사용자가 선택한 영상 경로: {file_path}")
            self.start_video(file_path)

            # # 기존 재생 중인 영상 정지
            # self.player.stop()
            
            # self.video_file_path = get_resource_path("test.mkv")
            
            # # 새 파일 경로로 미디어 객체 생성 후 로드
            # new_media = self.instance.media_new(file_path)
            # self.player.set_media(new_media)

            # # 즉시 재생 시작
            # self.player.play()
            # self.play_btn.config(text="⏸ 일시정지")
    
    def start_video(self, filename: str=None):
        if filename is None:
            file_path = self.video_file_path
        else:
            file_path = filename
            self.video_file_path = file_path
            
        self.title(FileUtil.filename(self.video_file_path))
        
        # 기존 재생 중인 영상 정지
        self.player.stop()

        # 새 파일 경로로 미디어 객체 생성 후 로드
        new_media = self.instance.media_new(file_path)
        self.player.set_media(new_media)

        # 즉시 재생 시작
        self.player.play()
        self.play_btn.config(text="⏸ 일시정지")
    
    def update_ui_loop(self):
        if self.player and not self.slider_locked:
            length = self.player.get_length()
            time_ms = self.player.get_time()

            if length > 0 and time_ms >= 0:
                cur_sec = time_ms // 1000
                tot_sec = length // 1000
                self.time_label.config(
                    text=f"{cur_sec//60:02d}:{cur_sec%60:02d} / {tot_sec//60:02d}:{tot_sec%60:02d}"
                )

                position = self.player.get_position()
                self.seek_bar.set(position * 1000)

        self.after(200, self.update_ui_loop)

    def on_key_press(self, event):
        """<KeyPress event send_event=True state=Mod1 keysym=k keycode=75 char='k' x=158 y=229>"""
        if event.keysym == "Escape" or event.keysym.lower() == "q":  # keycode=27 OR 81
            self.on_closing()
    
    def toggle_video(self):
        if self.player.is_playing():
            self.player.pause()
            self.play_btn.config(text="▶ 재생")
        else:
            self.player.play()
            self.play_btn.config(text="⏸ 일시정지")

    def on_space_click(self, event):
        self.toggle_video()

    def seek_backward(self, event):
        if self.player:
            current_time = self.player.get_time()
            self.player.set_time(max(0, current_time - 10000))  # 10초 전

    def seek_forward(self, event):
        if self.player:
            current_time = self.player.get_time()
            total_length = self.player.get_length()
            self.player.set_time(min(total_length, current_time + 10000))  # 10초 후

    def on_mouse_wheel(self, event):
        if self.player:
            current_volume = self.player.audio_get_volume()
            if event.delta > 0:
                new_volume = min(100, current_volume + 5)
            else:
                new_volume = max(0, current_volume - 5)

            self.player.audio_set_volume(new_volume)
            self.volume_label.config(text=f"🔊 볼륨: {new_volume}%")

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
        pass
        # if self.player:
        #     current_volume = self.player.audio_get_volume()
        #     new_volume = min(100, current_volume + 10)
        #     self.player.audio_set_volume(new_volume)
        #     self.volume_label.config(text=f"🔊 볼륨: {new_volume}%")

    # 🚀 기능 3: Page Down 키 누르면 볼륨 큰 폭으로 내리기 (10% 감소)
    def pdge_dn(self, event):
        pass
        # if self.player:
        #     current_volume = self.player.audio_get_volume()
        #     new_volume = max(0, current_volume - 10)
        #     self.player.audio_set_volume(new_volume)
        #     self.volume_label.config(text=f"🔊 볼륨: {new_volume}%")
    
    # 🚀 [핵심 신규 기능] 동영상 해상도를 감지하여 창 크기를 정밀 배율로 제어
    def change_video_size(self, scale_factor):
        if self.player:
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

            print(
                f"창 조절 완료 -> 크기: {target_width}x{target_height}, 위치: X:{current_x} Y:{current_y}"
            )

    def on_slider_press(self, event):
        self.slider_locked = True

    def on_slider_release(self, event):
        if self.player:
            target_pos = self.seek_bar.get() / 1000.0
            self.player.set_position(target_pos)
        self.slider_locked = False

    def on_closing(self):
        """백그라운드 스레드 무한 대기를 씹고 OS 레벨에서 프로세스를 완전 클린 킬 처리합니다."""
        print("종료 프로세스 강제 즉시 실행...")
        try:
            self.withdraw()  # 창 감추기
            if self.player:
                self.player.stop()
        except:
            pass
        os._exit(0)  # 무조건 0.1초 만에 깔끔한 강제 종료 보장


if __name__ == "__main__":
    app = SingleVideoPlayer()
    app.mainloop()
