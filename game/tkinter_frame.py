import tkinter as tk
from tkinter import messagebox
from config.config_manager import ConfigManager


class HeaderFrame(tk.Frame):
    def __init__(self, master, **kwargs):
        """_summary_
        1. 상단 프레임 영역 (독립된 UI 컴포넌트로 구성)
        """
        super().__init__(master, **kwargs)
        self.configure(bg="#2c3e50", height=60)
        # 중요: 자식 요소 때문에 크기가 줄어들지 않도록 설정
        self.pack_propagate(False)

        # 타이틀 라벨 라벨
        self.title_label = tk.Label(
            self,
            text="구조적 프레임 시스템",
            font=("Helvetica", 14, "bold"),
            fg="white",
            bg="#2c3e50",
        )
        self.title_label.pack(side="left", padx=15, pady=15)


class ContentFrame(tk.Frame):
    def __init__(self, master, **kwargs):
        """_summary_
        2. 메인 콘텐츠 프레임 영역
        """
        super().__init__(master, **kwargs)
        self.configure(padx=20, pady=20)

        # 텍스트 입력창
        self.entry_label = tk.Label(
            self, text="텍스트를 입력하세요:", font=("Malgun Gothic", 10)
        )
        self.entry_label.pack(anchor="w", pady=(0, 5))

        self.input_entry = tk.Entry(self, font=("Malgun Gothic", 11), width=30)
        self.input_entry.pack(fill="x", pady=(0, 15))

        # 알림 버튼
        self.alert_btn = tk.Button(
            self,
            text="입력값 확인",
            font=("Malgun Gothic", 10, "bold"),
            bg="#3498db",
            fg="white",
            command=self.show_message,
        )
        self.alert_btn.pack(fill="x", ipady=5)

    def show_message(self):
        user_text = self.input_entry.get()
        if user_text.strip():
            messagebox.showinfo("알림", f"입력된 내용: {user_text}")
        else:
            messagebox.showwarning("경고", "내용을 입력해 주세요.")


class MenuFrame(tk.Frame):
    def __init__(self, master, **kwargs):
        """_summary_
        메뉴 프레임 영역
        """
        super().__init__(master, **kwargs)
        
        self.root = master
        self.configure(padx=20, pady=20)
        
    def create_menu(self):
        """ 종료 기능이 탑재된 메뉴바 구성"""
        menu_bar = tk.Menu(self.root)

        # 파일 메뉴 풀다운 항목 정의
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(
            label="사활 문제 불러오기 (.sgf)", command=self.load_sgf_file
        )
        file_menu.add_command(
            label="사활 문제 저장하기 (.sgf)", command=self.save_sgf_file
        )
        file_menu.add_separator()
        file_menu.add_command(label="프로그램 종료", command=self.root.quit_close)

        # 메뉴바에 파일 메뉴 등록
        menu_bar.add_cascade(label="파일(File)", menu=file_menu)
        self.root.config(menu=menu_bar)
    
    def load_sgf_file(self):
        pass
    
    def save_sgf_file(self):
        pass


class TkinterFrame(tk.Tk):

    def __init__(self, file_path):
        """_summary_
        3. 메인 애플리케이션 윈도우 관리자
        """
        super().__init__()
        
        from util.log_util import LogUtil

        self.logger = LogUtil.get_logger(file_path)
        
        self.config_manager = ConfigManager(file_path, False)
        if self.config_manager.settings.get("") is None:
            self.config_manager.settings.width = 800
            self.config_manager.settings.height = 600
            self.config_manager.save()
        
        self.width = self.config_manager.settings.width
        self.height = self.config_manager.settings.height

        # 메인 창 설정
        self.title("Tkinter 구조화 레이아웃")
        self.geometry(f"{self.width}x{self.height}")
        self.resizable(False, False)

        # 컴포넌트 프레임 배치
        self.setup_ui()

        # 키보드 이벤트 바인딩 (창 전체에 적용)
        self.bind("<Key>", self.on_key_press) # key pressed
        self.bind("<Button-1>", self.on_mouse_click) # left click
        self.bind("<Button-3>", self.on_mouse_right_click)  # 우클릭

    def setup_ui(self):
        # 메뉴 프레임
        self.menubar = MenuFrame(self)
        self.menubar.create_menu()
        
        # 상단 헤더 프레임 부착 (상단 고정, 가로 꽉 채움)
        self.header = HeaderFrame(self)
        self.header.pack(side="top", fill="x")

        # 하단 콘텐츠 프레임 부착 (남은 공간을 모두 채움)
        self.content = ContentFrame(self)
        self.content.pack(side="top", fill="both", expand=True)
    
    def on_key_press(self, event):
        """<KeyPress event send_event=True state=Mod1 keysym=k keycode=75 char='k' x=158 y=229>"""
        if event.keysym == "Escape" or event.keysym.lower() == "q":  # keycode=27 OR 81
            self.quit_close()
    
    def on_mouse_click(self, event):
        """<ButtonPress event state=Mod1 num=1 x=141 y=173>"""
        pass
    
    def on_mouse_right_click(self, event):
        """<ButtonPress event state=Mod1 num=3 x=186 y=168>"""
        pass
    
    def quit_close(self):
        self.quit()


# 프로그램 실행
if __name__ == "__main__":
    app = TkinterFrame()
    app.mainloop()
