import tkinter as tk

class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.geometry("300x200")
        
        # 테스트용 버튼
        btn = tk.Button(self.root, text="저장하기", command=self.on_save)
        btn.pack(pady=50)

    def on_save(self):
        # 작업 완료 후 토스트 알림 띄우기
        self.show_toast(self.root, "성공적으로 저장되었습니다!")

    # def show_toast(self, message, duration=2000):
    #     """외부 라이브러리 없이 구현한 순수 Tkinter 토스트 알림"""
    #     # 1. 테두리 없는 가벼운 최상위 팝업 창 생성
    #     toast = tk.Toplevel(self.root)
    #     toast.wm_overrideredirect(True)  # 타이틀바(X버튼 등) 제거
        
    #     # 2. 메인 창의 중앙 부근에 위치하도록 좌표 계산
    #     root_x = self.root.winfo_rootx()
    #     root_y = self.root.winfo_rooty()
    #     root_w = self.root.winfo_width()
    #     root_h = self.root.winfo_height()
        
    #     # 메인 창 아래쪽 중앙에 배치
    #     x = root_x + (root_w // 2) - 100
    #     y = root_y + root_h - 60
    #     toast.wm_geometry(f"+{x}+{y}")
        
    #     # 3. 토스트 스타일링 (어두운 반투명 느낌의 배경에 흰색 글씨)
    #     label = tk.Label(toast, text=message, bg="#333333", fg="white",
    #                      padx=15, pady=8, font=("맑은 고딕", 10, "bold"))
    #     label.pack()
        
    #     # 4. 항상 맨 위에 보이도록 설정
    #     toast.attributes("-topmost", True)
        
    #     # 5. 지정된 시간(밀리초)이 지나면 자동으로 닫히도록 타이머 설정
    #     toast.after(duration, toast.destroy)

    def show_toast(self, target_widget, message, duration=2000):
        """
        target_widget: Tk(), Toplevel(), Frame() 등 현재 화면에 있는 어떤 위젯이든 가능
        """
        toast = tk.Toplevel(self.root) # 또는 tk.Toplevel(target_widget)
        toast.wm_overrideredirect(True)
        
        # 💡 넘겨받은 위젯(또는 프레임/새창)의 절대 좌표와 크기를 구합니다.
        x = target_widget.winfo_rootx() + (target_widget.winfo_width() // 2) - 100
        y = target_widget.winfo_rooty() + target_widget.winfo_height() - 60
        toast.wm_geometry(f"+{x}+{y}")
        
        # 스타일 및 자동 삭제 로직은 동일
        label = tk.Label(toast, text=message, bg="#333333", fg="white", padx=15, pady=8)
        label.pack()
        toast.attributes("-topmost", True)
        toast.after(duration, toast.destroy)


if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()

    st = "abc" + "/" + ".txt"
    print(st)