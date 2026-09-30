import os
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog

from util.resource import ResUtil
from util.tk_util import TkUtil
from util.log_util import LogUtil


class PlaylistPopup:

    def __init__(self, parent_window, width=450, height=450, playlist_dir=None):
        """
        parent_window: 메인 Tk 또는 Toplevel 창, 메인 플레이어 객체 (데이터 연동용)
        """
        self.parent = parent_window # 메인 플레이어의 변수나 함수에 접근하기 위함
        
        self.logger = LogUtil.get_logger(__file__)
        
        self.width, self.height = width, height
        self.playlist_dir = playlist_dir

        self.relative_path = self.parent.relative_path
        
        self.logger.debug(f"self.relative_path: {self.relative_path}")

        # 현재 열려있는 재생 목록 파일 경로 기억 (일반 '저장' 시 사용)
        # 메인 플레이어에 이미 저장된 경로가 없다면 None으로 시작합니다.
        self.current_file_path = getattr(self.parent, "current_file_path", None)
        
        # 1. 팝업 창 생성 및 초기 설정
        self.popup = tk.Toplevel(self.parent)
        self.popup.title("재생 목록 관리")
        self.popup.geometry(f"{self.width}x{self.height}")
        
        self.parent.popup = self.popup

        # 모달 설정 (팝업이 켜져 있는 동안 메인 창 클릭 방지)
        self.popup.grab_set()
        self.popup.protocol("WM_DELETE_WINDOW", self.close_popup)
        
        # 💡 탐색기 아이콘 버그를 피하는 깔끔한 주입 방법
        self.popup.iconbitmap(ResUtil.resource_path(self.relative_path, "icon.ico"))

        # ⚠️ 중요: 이미지 객체는 가비지 컬렉터(메모리 삭제) 방지를 위해 self 변수로 들고 있어야 합니다.
        self.load_button_images()

        # 2. UI 부품 생성 및 배치
        self.create_widgets()

    def load_button_images(self):
        """버튼에 사용할 PNG 이미지들을 메모리에 로드"""
        img_dir = f"{self.relative_path}/image"
        self.logger.debug(f"load_button_images: img_dir = {img_dir}")
        wh = 18
        try:
            self.img_file = TkUtil.load_image_force(ResUtil.resource_path(img_dir, "img_file.png"), wh, wh)
            self.img_folder = TkUtil.load_image_force(ResUtil.resource_path(img_dir, "img_folder.png"), wh, wh)
            self.img_del = TkUtil.load_image_force(ResUtil.resource_path(img_dir, "img_del.png"), wh, wh)
            # self.img_saveas = TkUtil.load_image_force(ResUtil.resource_path(img_dir, "img_saveas.png"), wh, wh)
            self.img_repeat = TkUtil.load_image_force(ResUtil.resource_path(img_dir, "img_repeat.png"), wh, wh)
            self.img_close = TkUtil.load_image_force(ResUtil.resource_path(img_dir, "img_close.png"), wh, wh)
        except Exception as e:
            print(f"이미지 로딩 실패 (기본 글자 버튼으로 대체용 콘솔로그): {e}")
            self.img_file = None
            self.img_folder = None
            self.img_del = None
            # self.img_saveas = None
            self.img_repeat = None
            self.img_close = None

    def create_widgets(self):
        # 상단 리스트박스
        self.listbox = tk.Listbox(self.popup, selectmode=tk.MULTIPLE, font=("Arial", 10))
        self.listbox.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # 메인 플레이어의 playlist 데이터를 리스트박스에 채우기
        for item in self.parent.playlist:
            self.listbox.insert(tk.END, item)

        # 하단 버튼들을 모아줄 프레임 (가로 배치용)
        button_frame = tk.Frame(self.popup)
        button_frame.pack(side=tk.BOTTOM, anchor=tk.E, pady=15, padx=20)

        # 버튼 생성 및 가로 정렬
        if self.img_file:
            add_btn = tk.Button(button_frame, image=self.img_file, command=self.add_item)
            add_btn.image = self.img_file
        else:
            add_btn = tk.Button(button_frame, text="파일 추가", command=self.add_item)
        add_btn.pack(side=tk.LEFT, padx=5)

        if self.img_folder:
            folder_btn = tk.Button(button_frame, image=self.img_folder, command=self.add_folder)
            folder_btn.image = self.img_folder
        else:
            folder_btn = tk.Button(button_frame, text="파일 추가", command=self.add_folder)
        folder_btn.pack(side=tk.LEFT, padx=5)

        if self.img_repeat:
            repeat_btn = tk.Button(button_frame, image=self.img_repeat, command=self.set_repeat)
            repeat_btn.image = self.img_repeat
        else:
            repeat_btn = tk.Button(button_frame, text="반복 설정", command=self.set_repeat)
        repeat_btn.pack(side=tk.LEFT, padx=5)
        
        if self.img_del:
            del_btn = tk.Button(button_frame, image=self.img_del, bg="#ff4d4d", fg="white", command=self.delete_item)
            del_btn.image = self.img_del
        else:
            del_btn = tk.Button(button_frame, text="선택 삭제", bg="#ff4d4d", fg="white", command=self.delete_item)
        del_btn.pack(side=tk.LEFT, padx=5)

        if self.img_close:
            close_btn = tk.Button(button_frame, image=self.img_close, command=self.close_popup)
            close_btn.image = self.img_close
        else:
            close_btn = tk.Button(button_frame, text="닫기", command=self.close_popup)
        close_btn.pack(side=tk.LEFT, padx=5)

    def delete_item(self):
        selected = self.listbox.curselection()
        if not selected:
            messagebox.showwarning("알림", "삭제할 동영상을 선택해 주세요.")
            return

        idx = selected
        if idx == self.parent.current_index:
            messagebox.showerror(
                "오류", "현재 재생 중인 동영상은 삭제할 수 없습니다."
            )
            return

        if messagebox.askyesno("삭제 확인", "선택한 항목을 제거하시겠습니까?"):
            self.listbox.delete(idx)
            # self.parent.playlist.pop(idx)
            self.parent.remove_file(index=idx)
            if idx < self.parent.current_index:
                self.parent.current_index -= 1

    def add_item(self):
        """[파일 추가] 탐색기를 열어 다중 동영상 파일 선택 후 등록"""
        files = filedialog.askopenfilenames(
            title="동영상 파일 추가",
            filetypes=(("동영상 파일", "*.mp4 *.avi *.mkv"), ("모든 파일", "*.*")),
        )
        if files:
            for file_path in files:
                self.parent.append_file(file_path)
                self.listbox.insert(tk.END, os.path.basename(file_path))

    def add_folder(self):
        """[폴더 추가] 특정 폴더 내부의 모든 동영상 파일을 통째로 긁어오기"""
        folder = filedialog.askdirectory(title="동영상 폴더 선택")
        if folder:
            # 폴더 내부 파일 탐색 후 동영상 확장자만 필터링해서 추가
            valid_extensions = (".mp4", ".avi", ".mkv")
            for filename in os.listdir(folder):
                if filename.lower().endswith(valid_extensions):
                    full_path = os.path.join(folder, filename)
                    self.parent.append_file(full_path)
                    self.listbox.insert(tk.END, filename)

    def set_repeat(self):
        opts = ["파일 반복", "전체 반복", "취소"]
        index, selected = TkUtil.ask_selection(self.popup, "반복 선택", "반복을 선택하세요.", opts)
        self.logger.debug(f"{index} = {selected}")
        if selected and index and index < 2:
            self.parent.loop_file = True

    def close_popup(self):
        """안전하게 팝업창을 닫고 메인 창 마우스 락 해제"""
        self.popup.grab_release()
        self.popup.destroy()
        self.parent.popup = None
