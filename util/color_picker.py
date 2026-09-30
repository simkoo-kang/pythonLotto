import tkinter as tk
from pynput import mouse
import pyautogui

# 🚀 단독으로 열리고 닫히는 독립형 컬러 피커 클래스
class ColorPickerWindow(tk.Toplevel):
    def __init__(self, parent):
        # 부모 창 위에 독립된 서브 창을 생성합니다.
        super().__init__(parent)
        
        self.title("단독 컬러 스포이드")
        self.geometry("360x220")
        self.resizable(False, False)
        
        # 윈도우 스타일 고정 (메인 창 위에 항상 배치 및 포커스 고정)
        self.transient(parent)
        self.grab_set()

        # [레이아웃 1] 상단 상태 안내 레이블
        self.info_lbl = tk.Label(self, text="아래 버튼을 누르면 스포이드 모드가 시작됩니다.", font=("맑은 고딕", 9))
        self.info_lbl.pack(pady=12)

        # [레이아웃 2] 결과 표시 영역 (시각적 그룹화를 위해 Frame 사용)
        result_frame = tk.Frame(self, relief="solid", bd=1)
        result_frame.pack(pady=5, fill="x", padx=25)

        # 색상 미리보기 네모 박스
        self.color_box = tk.Label(result_frame, bg="#FFFFFF", width=8, height=3, relief="flat")
        self.color_box.pack(side="left", padx=15, pady=10)

        # 텍스트 코드 표기 레이블
        self.code_lbl = tk.Label(result_frame, text="HEX: #FFFFFF\nRGB: (255, 255, 255)", 
                                 font=("맑은 고딕", 10, "bold"), justify="left")
        self.code_lbl.pack(side="left", padx=(10, 0)) # 오른쪽 간격 규칙 반영

        # [레이아웃 3] 추출 제어 버튼
        self.start_btn = tk.Button(self, text="화면 클릭하여 색상 추출", 
                                   font=("맑은 고딕", 10, "bold"), bg="#f3f3f3",
                                   command=self.activate_picker, padx=10, pady=5)
        self.start_btn.pack(pady=18)

        self.listener = None

    def activate_picker(self):
        """전역 마우스 클릭 감지 엔진을 비동기로 시작합니다."""
        self.start_btn.config(text="모니터 화면 아무 곳이나 클릭하세요...", state="disabled")
        self.info_lbl.config(text="창 밖의 바탕화면, 브라우저 등을 클릭하면 색상이 추출됩니다.", fg="blue")
        
        # pynput 전역 리스너 작동
        self.listener = mouse.Listener(on_click=self.on_global_click)
        self.listener.start()

    def on_global_click(self, x, y, button, pressed):
        """모니터 전역 스크린 클릭 이벤트 발생 시 실행되는 콜백"""
        if pressed:
            try:
                # 클릭한 해상도 좌표 (x, y)의 실제 디스플레이 픽셀 색상 대입
                r, g, b = pyautogui.pixel(int(x), int(y))
                hex_code = f"#{r:02x}{g:02x}{b:02x}".upper()
                
                # Toplevel 인스턴스 자신의 GUI 스레드로 안전하게 데이터 토스 전달
                self.after(0, lambda: self.update_picker_ui(r, g, b, hex_code))
            except Exception as e:
                print(f"픽셀 추출 오류: {e}")
                
            self.start_btn.config(state="normal")
            return False  # 클릭을 1회 감지했으므로 전역 마우스 후킹 리스너를 즉시 종료

    def update_picker_ui(self, r, g, b, hex_code):
        """추출된 색상을 Toplevel 단독 창 내부 위젯들에 맵핑"""
        self.color_box.config(bg=hex_code)
        self.code_lbl.config(text=f"HEX: {hex_code}\nRGB: ({r}, {g}, {b})")
        self.start_btn.config(text="화면 클릭하여 색상 추출")
        self.info_lbl.config(text="추출 성공! HEX 코드가 클립보드에 복사되었습니다. ✅", fg="green")
        
        # 사용 편의를 위해 컴퓨터 클립보드에 자동으로 글자 입력
        self.clipboard_clear()
        self.clipboard_append(hex_code)


# --- [메인 GUI 테스트 베드] ---
if __name__ == "__main__":
    root = tk.Tk()
    root.title("메인 프로그램")
    root.geometry("350x150")

    # 버튼을 누르면 독립된 ColorPickerWindow(Toplevel) 인스턴스가 단독 생성됩니다.
    open_btn = tk.Button(root, text="독립형 컬러 피커 창 열기", 
                         command=lambda: ColorPickerWindow(root), font=("맑은 고딕", 10), padx=10, pady=5)
    open_btn.pack(pady=45)

    root.mainloop()
