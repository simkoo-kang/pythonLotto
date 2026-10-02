import os
import sys
from tkinter import filedialog

# ⚡ [핵심] 파이썬이 VLC 미디어 플레이어 엔진(DLL)을 찾을 수 있도록 시스템 경로에 강제 추가
# 64비트 윈도우의 기본 VLC 설치 경로입니다.
vlc_path = r"C:\Program Files\VideoLAN\VLC"

if os.path.exists(vlc_path):
    # Windows 환경에서 외부 C 라이브러리(DLL) 검색 경로에 추가하는 표준 방식
    os.add_dll_directory(vlc_path)

import tkinter as tk
from tkinter import ttk
import vlc


# PyInstaller 단일 파일 내부(.exe 리소스) 절대 경로를 찾는 함수
def get_resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)


class MultiApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("종합 게임 & 미디어 플레이어")
        self.geometry("800x650")

        # 메인 컨테이너 생성
        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)

        # 메뉴 바 생성
        self.create_menu()

        # 화면들을 관리할 딕셔너리
        self.frames = {}

        # 각 화면 클래스 등록
        for F in (MenuScreen, JigsawScreen, VideoScreen):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # 처음 시작할 때 메뉴 화면을 띄움
        self.show_frame("MenuScreen")

        # 창 종료 이벤트 바인딩
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_menu(self):
        menubar = tk.Menu(self)
        nav_menu = tk.Menu(menubar, tearoff=0)
        nav_menu.add_command(
            label="메인 메뉴로 이동", command=lambda: self.show_frame("MenuScreen")
        )
        nav_menu.add_command(
            label="직소 퍼즐 시작", command=lambda: self.show_frame("JigsawScreen")
        )
        nav_menu.add_command(
            label="동영상 보기", command=lambda: self.show_frame("VideoScreen")
        )
        nav_menu.add_command(
            label="동영상 선택", command=lambda: self.select_file()
        )
        nav_menu.add_separator()
        nav_menu.add_command(label="종료", command=self.on_closing)
        menubar.add_cascade(label="프로그램 메뉴", menu=nav_menu)
        self.config(menu=menubar)

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

        # 비디오 화면에서 탈출할 때 영상 일시정지 처리
        if page_name != "VideoScreen" and "VideoScreen" in self.frames:
            self.frames["VideoScreen"].stop_video_on_leave()
    
    def select_file(self):
        print("select file ===============================")
        # 1. 먼저 동영상 보기 화면으로 UI를 전환합니다.
        self.show_frame("VideoScreen")

        # 2. self.frames 딕셔너리에서 생성되어 있는 VideoScreen 객체를 안전하게 꺼냅니다.
        video_page = self.frames.get("VideoScreen")

        # 3. VideoScreen 내부에 만들어 두신 open_and_read_video() 함수를 강제로 트리거(실행)합니다.
        if video_page and hasattr(video_page, "open_and_read_video"):
            video_page.open_and_read_video()
    
    def on_closing(self):
        """백그라운드 데드락을 무시하고 OS 레벨에서 즉시 강제 종료합니다."""
        print("종료 프로세스 강제 시작...")

        # 1. 먼저 눈에 보이는 창을 즉시 숨겨서 사용자가 체감하는 종료 속도를 높입니다.
        try:
            self.withdraw()
        except:
            pass

        # 2. 부드러운 해제를 시도하되, 여기서 멈추더라도 상관없게 만듭니다.
        video_page = self.frames.get("VideoScreen")
        if video_page:
            if hasattr(video_page, "player") and video_page.player:
                try:
                    video_page.player.stop()
                except:
                    pass

        # 3. 🔥 [최종 해결책] os._exit(0) 도입
        # sys.exit()은 내부 정리(Clean-up) 과정을 거치느라 멈출 수 있지만,
        # os._exit()은 OS에게 '이 메모리 당장 회수해'라고 명령하므로 렉 없이 0.1초 만에 완전히 꺼집니다.
        print("프로그램 프로세스 완전 강제 종료.")
        os._exit(0)


# 1. 메뉴 선택 화면
class MenuScreen(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f0f0f0")
        self.controller = controller

        label = tk.Label(
            self, text="원하시는 메뉴를 선택하세요", font=("맑은 고딕", 18, "bold"), bg="#f0f0f0"
        )
        label.pack(pady=50)

        btn1 = tk.Button(
            self,
            text="🧩 직소 퍼즐",
            font=("맑은 고딕", 14),
            width=20,
            command=lambda: controller.show_frame("JigsawScreen"),
        )
        btn1.pack(pady=15)

        btn2 = tk.Button(
            self,
            text="🎬 동영상 보기",
            font=("맑은 고딕", 14),
            width=20,
            command=lambda: controller.show_frame("VideoScreen"),
        )
        btn2.pack(pady=15)


# 2. 직소 퍼즐 화면
class JigsawScreen(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent, bg="#e0f7fa")
        label = tk.Label(
            self, text="🧩 직소 퍼즐 프로그램 영역", font=("맑은 고딕", 16), bg="#e0f7fa"
        )
        label.pack(pady=30)
        info = tk.Label(
            self,
            text="(이곳에 퍼즐 캔버스 및 게임 코드가 구현됩니다)",
            bg="#e0f7fa",
        )
        info.pack(pady=10)


mkv = "test.mkv"

class VideoScreen(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent, bg="#222222")
        self.controller = controller

        self.video_file_path = get_resource_path(mkv)

        # 동영상이 화면에 직접 그려질 검은색 캔버스 프레임
        self.video_frame = tk.Frame(self, bg="black")
        self.video_frame.pack(expand=True, fill="both", padx=10, pady=10)

        # VLC 옵션 설정 및 플레이어 생성
        vlc_options = ["--no-video-title-show"]
        self.instance = vlc.Instance(vlc_options)
        self.player = self.instance.media_player_new()
        self.player.set_hwnd(self.video_frame.winfo_id())

        # 🚀 [해결 장치 1] VLC의 키보드/마우스 가로채기 차단 강제 설정
        self.player.video_set_mouse_input(False)
        self.player.video_set_key_input(False)

        # --- 하단 컨트롤 바 프레임 ---
        control_frame = tk.Frame(self, bg="#222222")
        control_frame.pack(fill="x", side="bottom", pady=10)

        # 재생/일시정지 버튼
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

        # 탐색 바 마우스 이벤트 바인딩
        self.seek_bar.bind("<ButtonPress-1>", self.on_slider_press)
        self.seek_bar.bind("<ButtonRelease-1>", self.on_slider_release)

        self.slider_locked = False

        # 기본 볼륨 설정 (50%)
        self.player.audio_set_volume(50)

        # 🚀 [해결 장치 2] 프로그램 전역(All)에 바인딩을 걸어 이벤트를 무조건 가로챕니다.
        # 이제 창 어디서든 스페이스바나 마우스 휠을 조작하면 파이썬이 즉각 인식합니다.
        self.bind_all("<space>", self.on_space_click)
        self.bind_all("<MouseWheel>", self.on_mouse_wheel)
        self.bind_all("<Left>", self.seek_backward)
        self.bind_all("<Right>", self.seek_forward)

        # 포커스가 튀어서 안 먹히는 현상을 완전히 막기 위해 하단 컨트롤 영역에도 2중 매칭
        control_frame.bind("<MouseWheel>", self.on_mouse_wheel)
        self.time_label.bind("<MouseWheel>", self.on_mouse_wheel)
        self.volume_label.bind("<MouseWheel>", self.on_mouse_wheel)
        self.seek_bar.bind("<MouseWheel>", self.on_mouse_wheel)

        # 비디오 파일 연결
        if os.path.exists(self.video_file_path):
            media = self.instance.media_new(self.video_file_path)
            self.player.set_media(media)

        # UI 업데이트 루프 시작
        self.update_ui_loop()

    def open_and_read_video(self):
        """사용자가 직접 컴퓨터에서 영상 파일을 탐색하여 읽어오도록 만듭니다."""
        file_path = filedialog.askopenfilename(
            title="재생할 영상 파일을 선택하세요",
            filetypes=[("동영상 파일", "*.mp4 *.avi *.mkv"), ("모든 파일", "*.*")],
        )

        if file_path:  # 사용자가 취소하지 않고 파일을 정상 선택했다면
            print(f"사용자가 선택한 영상 경로: {file_path}")

            # 기존 재생 중인 영상 정지
            self.player.stop()

            # 새 파일 경로로 미디어 객체 생성 후 로드
            new_media = self.instance.media_new(file_path)
            self.player.set_media(new_media)

            # 즉시 재생 시작
            self.player.play()
            self.play_btn.config(text="⏸ 일시정지")
    
    def toggle_video(self):
        if self.player.is_playing():
            self.player.pause()
            self.play_btn.config(text="▶ 재생")
        else:
            self.player.play()
            self.play_btn.config(text="⏸ 일시정지")
            self.focus_set()  # 이벤트를 잘 받도록 포커스 고정

    # 🚀 [추가 기능] 스페이스바 누르면 재생/일시정지 토글
    def on_space_click(self, event):
        # 만약 사용자가 다른 메뉴로 이동했다면 작동하지 않도록 방지
        if self.winfo_viewable():
            self.toggle_video()

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

    def seek_backward(self, event):
        if self.player and self.winfo_viewable():
            current_time = self.player.get_time()
            target_time = max(0, current_time - 10000)
            self.player.set_time(target_time)

    def seek_forward(self, event):
        if self.player and self.winfo_viewable():
            current_time = self.player.get_time()
            total_length = self.player.get_length()
            target_time = min(total_length, current_time + 10000)
            self.player.set_time(target_time)

    # 🚀 [보완 완료] 마우스 휠 동작 처리 함수
    def on_mouse_wheel(self, event):
        if self.player and self.winfo_viewable():
            try:
                current_volume = self.player.audio_get_volume()

                if event.delta > 0:
                    new_volume = min(100, current_volume + 5)
                elif event.delta < 0:
                    new_volume = max(0, current_volume - 5)
                else:
                    return

                self.player.audio_set_volume(new_volume)
                self.volume_label.config(text=f"🔊 볼륨: {new_volume}%")
            except Exception as e:
                print(f"볼륨 조절 오류: {e}")

    def on_slider_press(self, event):
        self.slider_locked = True

    def on_slider_release(self, event):
        if self.player:
            target_pos = self.seek_bar.get() / 1000.0
            self.player.set_position(target_pos)
        self.slider_locked = False

    def stop_video_on_leave(self):
        if self.player.is_playing():
            self.player.pause()
            self.play_btn.config(text="▶ 재생")



if __name__ == "__main__":
    app = MultiApp()
    app.mainloop()
