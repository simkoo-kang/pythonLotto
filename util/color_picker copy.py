import tkinter as tk
from pynput import mouse  # 전역 마우스 클릭 이벤트를 감지하는 라이브러리
import pyautogui          # 특정 좌표의 픽셀 색상을 추출하는 라이브러리

class GlobalColorPickerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("전역 모니터 스크린 컬러 피커")
        self.root.geometry("400x250")
        
        # 1. 상단 안내 및 결과 레이블
        self.info_label = tk.Label(root, text="아래 버튼을 누르면 색상 추출 모드가 시작됩니다.", font=("맑은 고딕", 10))
        self.info_label.pack(pady=15)
        
        # 색상 결과창 (미리보기 박스)
        self.color_preview = tk.Label(root, bg="#f0f0f0", width=25, height=3, relief="ridge", bd=2)
        self.color_preview.pack(pady=10)
        
        self.result_label = tk.Label(root, text="HEX: #F0F0F0\nRGB: (240, 240, 240)", font=("맑은 고딕", 11, "bold"))
        self.result_label.pack(pady=5)
        
        # 2. 제어 버튼
        self.start_btn = tk.Button(root, text="스포이드 모드 시작 (화면 클릭)", command=self.start_picking, bg="#e1e1e1", padx=10, pady=5)
        self.start_btn.pack(pady=15)
        
        self.listener = None  # 마우스 리스너 객체 저장용 변수

    def start_picking(self):
        """버튼을 누르면 전역 마우스 클릭 감지 리스너를 실행합니다."""
        self.start_btn.config(text="화면 아무 곳이나 클릭하세요...", state="disabled")
        self.info_label.config(text="모니터 화면 어디든 클릭하면 색상이 추출되고 모드가 종료됩니다.", fg="blue")
        
        # 비동기로 작동하는 전역 마우스 클릭 리스너 가동
        self.listener = mouse.Listener(on_click=self.on_screen_click)
        self.listener.start()

    def on_screen_click(self, x, y, button, pressed):
        """윈도우 화면 아무 곳이나 마우스 클릭 이벤트가 발생하면 호출되는 콜백"""
        # 마우스를 누르는 순간(pressed=True)에만 작동하도록 필터링
        if pressed:
            try:
                # 1. 마우스가 클릭된 전역 좌표 (x, y)의 픽셀 RGB 색상 추출
                # pyautogui.pixel(x, y)는 (R, G, B) 형태의 튜플을 반환합니다.
                r, g, b = pyautogui.pixel(int(x), int(y))
                hex_code = f"#{r:02x}{g:02x}{b:02x}".upper()
                
                # 2. 안전한 GUI 스레드 갱신을 위해 .after()나 스레드 안전 방식으로 UI 업데이트 함수 호출
                self.root.after(0, lambda: self.update_ui_result(r, g, b, hex_code))
                
            except Exception as e:
                print(f"색상 추출 실패 (주 모니터 범위를 벗어났을 수 있습니다): {e}")
                
            # 3. 색상을 한 번 뽑았으므로 전역 마우스 리스너를 즉시 멈춰 픽셀 추출 모드를 종료합니다.
            self.start_btn.config(state="normal")
            return False 

    def update_ui_result(self, r, g, b, hex_code):
        """추출된 색상 정보를 Tkinter 인터페이스에 출력하는 함수"""
        self.color_preview.config(bg=hex_code)
        self.result_label.config(text=f"HEX: {hex_code}\nRGB: ({r}, {g}, {b})")
        self.start_btn.config(text="스포이드 모드 시작 (화면 클릭)")
        self.info_label.config(text="색상 추출 성공! 클립보드 복사 완료 ✅", fg="green")
        
        # 선택한 HEX 코드를 컴퓨터 클립보드에 자동으로 복사해주는 편의 기능
        self.root.clipboard_clear()
        self.root.clipboard_append(hex_code)


# --- 프로그램 기동 ---
if __name__ == "__main__":
    root = tk.Tk()
    app = GlobalColorPickerApp(root)
    root.mainloop()
