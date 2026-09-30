import tkinter as tk
from tkinter import ttk

from tkinter import simpledialog
from tkinter import messagebox
from PIL import Image, ImageTk
from util.log_util import LogUtil

class TkUtil:
    
    logger = LogUtil.get_logger(__file__)
    
    @staticmethod
    def show_toast(target_widget, message, duration=1500, fg="white", bg="#333333"):
        """_summary_
        메시지 보여주기
        Args:
            target_widget: Tk(), Toplevel(), Frame() 등 현재 화면에 있는 어떤 위젯이든 가능
            msg (str): 성공적으로 저장되었습니다.
            millis (int, 1500): 노출 시간 밀리초. Defaults to 1500.
        """
        """
        """
        toast = tk.Toplevel(target_widget)
        toast.wm_overrideredirect(True)
        
        # 💡 넘겨받은 위젯(또는 프레임/새창)의 절대 좌표와 크기를 구합니다.
        x = target_widget.winfo_rootx() + (target_widget.winfo_width() // 2) - 100
        y = target_widget.winfo_rooty() + target_widget.winfo_height() - 60
        toast.wm_geometry(f"+{x}+{y}")
        
        # 스타일 및 자동 삭제 로직은 동일
        label = tk.Label(toast, text=message, bg=bg, fg=fg, padx=15, pady=8)
        label.pack()
        toast.attributes("-topmost", True)
        toast.after(duration, toast.destroy)

    
    @staticmethod
    def ask_selection(parent, title, prompt, options):
        """_summary_
        기존 메인 창 위에 목록 선택 팝업을 띄우는 함수
        Args:
            parent (root): 메인 창 객체 (root)
            title (str): 팝업창 제목
            prompt (str): 안내 메시지
            options (list): 선택할 목록 리스트
        Returns:
            (index, 사용자가 선택한 문자열) 튜플 / 취소 시 (None, None)
        """
        # 1. 팝업창(Toplevel) 생성 및 설정
        popup = tk.Toplevel(parent)
        popup.title(title)
        popup.geometry("300x150")
        popup.resizable(False, False)
        
        # 메인 창 중앙에 위치시키기
        popup.transient(parent) 
        popup.grab_set()  # 팝업이 닫히기 전까지 메인 창 클릭 방지 (모달)

        # 결과를 저장할 공간 (인덱스와 값을 함께 담음)
        result = {"index": None, "value": None}

        # 2. 안내 레이블
        lbl = tk.Label(popup, text=prompt, font=("맑은 고딕", 10))
        lbl.pack(pady=10)

        # 3. 콤보박스 (목록 드롭다운)
        combo = ttk.Combobox(popup, values=options, state="readonly", width=25)
        combo.current(0)  # 첫 번째 항목 기본 선택
        combo.pack(pady=5)

        # 4. 확인 / 취소 버튼 이벤트 함수
        def on_confirm():
            # combo.current()는 선택된 항목의 0부터 시작하는 인덱스를 반환합니다.
            result["index"] = combo.current()  
            result["value"] = combo.get()
            popup.destroy()

        def on_cancel():
            popup.destroy()

        # 버튼 배치
        btn_frame = tk.Frame(popup)
        btn_frame.pack(pady=15)
        
        tk.Button(btn_frame, text="확인", width=8, command=on_confirm).pack(side="left", padx=5)
        tk.Button(btn_frame, text="취소", width=8, command=on_cancel).pack(side="left", padx=5)

        # 팝업창이 닫힐 때까지 메인 루프를 일시 대기
        parent.wait_window(popup)
        return result["index"], result["value"]

    @staticmethod
    def load_image(img_full_name, width=0, height=0):
        """ 이미지 로드 - 가로세로 비율을 유지하며 안전하게 리사이즈 """
        try:
            original_img = Image.open(img_full_name)
            orig_w, orig_h = original_img.size  # 원본 이미지의 진짜 크기
            
            # 가로, 세로가 모두 0이면 원본 그대로 반환
            if width == 0 and height == 0:
                return ImageTk.PhotoImage(original_img)
            
            # 한쪽만 입력되었거나 비율 유지가 필요한 경우 계산
            if width > 0 and height == 0:
                # 가로 기준 비율 계산
                height = int((width / orig_w) * orig_h)
            elif height > 0 and width == 0:
                # 세로 기준 비율 계산
                width = int((height / orig_h) * orig_w)
            else:
                if orig_w < orig_h:
                    width = int((height / orig_h) * orig_w)
                else:
                    height = int((width / orig_w) * orig_h)
        
            # 최종 결정된 size 튜플로 리사이즈 (품질 향상을 위해 LANCZOS 필터 적용)
            resized_img = original_img.resize(size=(int(width), int(height)), resample=Image.Resampling.LANCZOS)
            
            return ImageTk.PhotoImage(resized_img)
            
        except Exception as e:
            TkUtil.logger.debug(f"이미지 로딩 실패 (기본 글자 버튼으로 대체용 콘솔로그): {e}")
            return None
    
    def load_image_force(img_full_name, width=0, height=0):
        """ 이미지 로드 - resize(width, height) if width and height not = 0 """
        if width * height == 0:
            return ImageTk.PhotoImage(file=img_full_name)
        
        original_img = Image.open(img_full_name)
        resized_img = original_img.resize(size=(width, height))
        
        """ 이미지 로드 - 원본 비율을 무시하고 지정한 width, height 크기로 강제 고정 """
        try:
            original_img = Image.open(img_full_name)
            
            # 가로, 세로 인자가 입력되지 않았다면 기본 원본 크기로 반환
            if width == 0 or height == 0:
                return ImageTk.PhotoImage(original_img)
            
            # ⭐️ 원본 비율에 상관없이 사용자가 지정한 크기로 강제 리사이즈 진행
            # (int형으로 확실하게 변환 후 size 인자에 주입)
            resized_img = original_img.resize(size=(int(width), int(height)), resample=Image.Resampling.LANCZOS)
            
            return ImageTk.PhotoImage(resized_img)
            
        except Exception as e:
            TkUtil.logger.debug(f"이미지 로딩 실패 (기본 글자 버튼으로 대체용 콘솔로그): {e}")
        
        return None

    def message_box_yesno(parent, title, msg, icons=None, defs=None) -> bool:
        """_summary_
        yes or no
        Args:
            title (str)
            msg (str)
            icons (Literal['error', 'info', 'question', 'warning'] 'question', None)
            defs (Literal['yes', 'no'], None)
        Returns:
            bool: True if yes else False
        """
        return messagebox.askyesno(title=title, message=msg, icon=icons, default=defs, parent=parent)
    
    def message_box_okcancel(parent, title, msg, icons=None, defs=None) -> bool:
        """_summary_
        ok or cancel
        Args:
            title (str)
            msg (str)
            icons (Literal['error', 'info', 'question', 'warning'] 'question', None)
            defs (Literal['ok', 'cancel'], None)
        Returns:
            bool: True if yes else False
        """
        return messagebox.askokcancel(title=title, message=msg, icon=icons, default=defs, parent=parent)
    
    def simple_dialog_input_string(parent, title, msg, initval: str=None) -> str:
        """_summary_
        문자열 입력 받기 (str or None)
        Args:
            title (str)
            msg (str)
            initval (str, None)
        Returns:
            str or None
        """
        return simpledialog.askstring(title=title, prompt=msg, initialvalue=initval, parent=parent)
    
    def simple_dialog_input_int(parent, title, msg, initval: int=None, minval: int=None, maxval: int=None) -> int:
        """_summary_
        정수 입력 받기
        Args:
            title (str)
            msg (str)
            initval (int, None)
            minval (int, None)
            maxval (int, None)
        Returns:
            int or None
        """
        return simpledialog.askinteger(title=title, prompt=msg, initialvalue=initval, minvalue=minval, maxvalue=maxval, parent=parent)
    
    def simple_dialog_input_float(parent, title, msg, initval: float=None, minval: float=None, maxval: float=None):
        """_summary_
        실수 입력 받기
        Args:
            title (str)
            msg (str)
            initval (float, None)
            minval (float, None)
            maxval (float, None)
        Returns:
            float or None
        """
        return simpledialog.askfloat(title=title, prompt=msg, initialvalue=initval, minvalue=minval, maxvalue=maxval, parent=parent)


# ==================== 실행 및 검증 ====================
if __name__ == "__main__":
    
     # --- [실제 메인 GUI 사용 예시] ---
    def open_select_popup():
        fruits = ["사과 🍎", "바나나 🍌", "포도 🍇", "수박 🍉"]
        
        # 함수 호출로 간단하게 선택 값 받기
        index, selected = TkUtil.ask_selection(root, "과일 선택", "좋아하는 과일을 선택하세요:", fruits)
        
        if selected:
            status_label.config(text=f"선택된 과일: {index} {selected}", fg="blue")
        else:
            status_label.config(text="선택이 취소되었습니다.", fg="red")

    root = tk.Tk()
    root.title("메인 프로그램")
    root.geometry("400x200")

    tk.Button(root, text="목록 선택 팝업 열기", command=open_select_popup, padx=10, pady=5).pack(pady=30)
    status_label = tk.Label(root, text="상태: 대기 중", font=("맑은 고딕", 11, "bold"))
    status_label.pack()

    root.mainloop()
