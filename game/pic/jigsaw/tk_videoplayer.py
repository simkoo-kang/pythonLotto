import os
import sys
import tkinter as tk
from tkinter import ttk

# ⚡ [1단계] 컴퓨터에 설치된 진짜 VLC 미디어 플레이어 엔진 경로 찾기 및 등록
vlc_path = r"C:\Program Files\VideoLAN\VLC"
if os.path.exists(vlc_path):
    os.add_dll_directory(vlc_path)
else:
    print("경고: VLC 미디어 플레이어가 지정된 경로에 설치되어 있지 않습니다.")

import vlc

from util.resource import ResUtil


# 🚀 [핵심] 독립된 새 창(Toplevel)으로 구동되는 VLC 동영상 플레이어 클래스
class VideoPlayerWindow(tk.Toplevel):

    def __init__(self, parent, video_path):
        # tk.Toplevel을 상속받아 독립된 서브 창을 생성합니다.
        super().__init__(parent)
        
        self.title("VLC 동영상 재생 스크린")
        self.geometry("700x530")
        
        # 모달(Modal) 창 설정: 메인 창 중앙 정렬 및 포커스 고정
        self.transient(parent)
        self.grab_set()
        
        # 1. 영상 프레임이 출력될 라벨 위젯 (배경 검은색)
        self.video_label = tk.Label(self, bg="black")
        self.video_label.pack(expand=True, fill="both", padx=10, pady=5)
        
        # 2. 하단 컨트롤 프레임 및 상태 표시 바 구성
        control_frame = tk.Frame(self)
        control_frame.pack(fill="x", padx=10, pady=10)
        
        self.time_label = tk.Label(control_frame, text="00:00 / 00:00", font=("맑은 고딕", 10))
        self.time_label.pack(side="left", padx=5)
        
        # 실시간 진행 상황을 보여주는 프로그레스 바
        self.progress_bar = ttk.Progressbar(control_frame, orient="horizontal", mode="determinate")
        self.progress_bar.pack(side="left", expand=True, fill="x", padx=10)
        
        # 3. 💡 VLC 인스턴스 및 미디어 플레이어 초기화
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        
        # Tkinter 라벨 위젯의 윈도우 ID를 VLC에 바인딩하여 라벨 내부에 영상이 그려지도록 설정
        # (Tcl/Tk 9.0 64비트 호환성 완벽 반영)
        win_id = self.video_label.winfo_id()
        if sys.platform.startswith('win'):
            self.player.set_hwnd(win_id)
        elif sys.platform.startswith('linux'):
            self.player.set_xwindow(win_id)
        elif sys.platform.startswith('darwin'):
            self.player.set_nsobject(win_id)

        # 4. 미디어 로드 및 파일 재생
        self.media = self.instance.media_new(video_path)
        self.player.set_media(self.media)
        self.player.play()
        
        # 사용자가 창 우측 상단 'X' 버튼을 눌러 중간에 닫을 때의 안전 해제 핸들러
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 5. 💡 VLC 이벤트 루프 대신 tkinter .after()를 활용한 무결점 상황/종료 감지 루프 시작
        self.update_loop()

    # --- 💡 클래스 내부 이벤트 핸들러 메서드들 ---
    
    def update_loop(self):
        """VLC 외부 스레드 충돌을 피하기 위해 tkinter 타이머로 현재 진행 상황과 종료를 추적하는 루프"""
        state = self.player.get_state()
        
        # ⭐️ [플레이 종료 상황 완벽 감지] VLC 상태가 Ended(6)이거나 재생이 끝났을 때
        if state == vlc.State.Ended:
            self.on_video_ended()
            return
            
        elif state == vlc.State.Playing:
            # 현재 재생 시간 및 총 재생 시간 가져오기 (밀리초 단위를 초 단위로 환산)
            current_ms = self.player.get_time()
            total_ms = self.player.get_length()
            
            if total_ms > 0:
                current_sec = current_ms // 1000
                total_sec = total_ms // 1000
                
                # 프로그레스 바 갱신 (0 ~ 100 비율 반영)
                progress_percent = (current_ms / total_ms) * 100
                self.progress_bar["value"] = progress_percent
                
                # 하단 시간 문자열 동기화
                cur_m, cur_s = divmod(current_sec, 60)
                tot_m, tot_s = divmod(total_sec, 60)
                self.time_label.config(text=f"{cur_m:02d}:{cur_s:02d} / {tot_m:02d}:{tot_s:02d}")
                
        # 0.2초(200ms)마다 상태를 주기적으로 체크
        self.loop_id = self.after(200, self.update_loop)

    def on_video_ended(self):
        print("▶ [VLC 감지] 동영상이 성공적으로 끝까지 재생되었습니다.")
        self.cleanup()
        
        # 부모 메인 GUI 창의 전역 상태 레이블 업데이트 제어
        status_label.config(text="상태: 동영상 시청 완료 (VLC 확인됨) ✅", fg="green")
        
        # 1초 후 현재 동영상 플레이어 서브 창 자동 종료
        self.after(1000, self.destroy)

    def cleanup(self):
        """VLC 미디어 플레이어 엔진 자원을 안전하게 정지 및 해제"""
        if hasattr(self, 'loop_id'):
            self.after_cancel(self.loop_id)
        if self.player:
            self.player.stop()
            self.player.release()
        if self.instance:
            self.instance.release()

    def on_closing(self):
        """유저가 시청 중 창을 강제로 닫을 때 VLC 좀비 프로세스가 남지 않도록 예외 처리"""
        self.cleanup()
        self.destroy()


# --- [메인 GUI 진입 및 테스트 가동] ---
def start_video():
    # 설계한 VLC Toplevel 클래스 인스턴스 오픈
    VideoPlayerWindow(root, VIDEO_FILE)


# --- 메인 GUI 테스트 실행부 ---
root = tk.Tk()
root.title("메인 윈도우")
root.geometry("400x200")


# ⚠️ 실제 컴퓨터에 존재하는 mp4 파일명으로 바꾸어 테스트하세요.
VIDEO_FILE = ResUtil.resource_path("game/pic/jigsaw/movie", "test.mkv")

play_btn = tk.Button(root, text="클래스 기반 Toplevel 플레이어 열기", 
                     command=start_video, padx=10, pady=5)
play_btn.pack(pady=30)

status_label = tk.Label(root, text="상태: 대기 중", font=("맑은 고딕", 11, "bold"))
status_label.pack()

root.mainloop()
