# util/file_util.py
import os
import shutil

class FileUtil:
    # 💡 [정적 필드 (Static Field) 선언]
    # 클래스명 자체로 바로 접근할 수 있으며, 모든 인스턴스가 이 값을 공유합니다.
    DEFAULT_PATH = r"D:\Workspace\vscode\lotto"
    CONF_PATH = os.path.join(DEFAULT_PATH, "conf")
    DEFAULT_ENCODING = "utf-8"

    
    @staticmethod
    def get_lotto_url(drw_no: int) -> str:
        # return f"https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo={drw_no}"
        # return "https://dhlottery.co.kr/lt645/result"
        return "https://dhlottery.co.kr"


    @staticmethod
    def get_current_dir() -> str:
        return os.getcwd()

    @staticmethod
    def get_lotto_make_filtered_file(round: int) -> str:
        return os.path.join(FileUtil.CONF_PATH, "make", f"{round}_filtered.txt")

    @staticmethod
    def get_lotto_make_all_file(round: int) -> str:
        return os.path.join(FileUtil.CONF_PATH, "make", f"{round}_all.txt")

    @staticmethod
    def get_lotto_make_file(round: int) -> str:
        return os.path.join(FileUtil.CONF_PATH, "make", f"{round}.txt")

    @staticmethod
    def get_lotto_selected_file(round: int) -> str:
        return os.path.join(FileUtil.CONF_PATH, "make", f"{round}_selected.txt")

    @staticmethod
    def writeAll(file_path: str, string: str, mode: str = "a") -> bool:
        """
        [파일 쓰기 기능]
        String[] (문자열 리스트)를 받아 해당 경로에 한 줄씩 기록합니다.
        - mode='a': 기존 내용 뒤에 이어서 쓰기 (기본값)
        - mode='w': 기존 내용 지우고 새로 쓰기
        """
        try:
            # 저장할 폴더가 없으면 상위 폴더까지 자동으로 생성
            dir_name = os.path.dirname(file_path)
            if dir_name and not os.path.exists(dir_name):
                os.makedirs(dir_name)
                
            with open(file_path, mode, encoding=FileUtil.DEFAULT_ENCODING) as file:
                file.write(string + "\n")
            return True
        except Exception as e:
            print(f"❌ 파일 쓰기 실패: {e}")
            return False

    @staticmethod
    def write_lines(file_path: str, string_array: list, mode: str = "a") -> bool:
        """
        [파일 쓰기 기능]
        String[] (문자열 리스트)를 받아 해당 경로에 한 줄씩 기록합니다.
        - mode='a': 기존 내용 뒤에 이어서 쓰기 (기본값)
        - mode='w': 기존 내용 지우고 새로 쓰기
        """
        try:
            # 저장할 폴더가 없으면 상위 폴더까지 자동으로 생성
            dir_name = os.path.dirname(file_path)
            if dir_name and not os.path.exists(dir_name):
                os.makedirs(dir_name)
                
            with open(file_path, mode, encoding=FileUtil.DEFAULT_ENCODING) as file:
                for line in string_array:
                    file.write(str(line) + "\n")
            return True
        except Exception as e:
            print(f"❌ 파일 쓰기 실패: {e}")
            return False

    @staticmethod
    def read_lines(file_path: str) -> list:
        """
        [파일 읽기 기능]
        해당 경로의 텍스트 파일을 읽어와 한 줄씩 잘라 String[] 배열로 반환합니다.
        """
        if not os.path.exists(file_path):
            print(f"⚠️ 파일을 찾을 수 없습니다: {file_path}")
            return []
            
        try:
            string_array = []
            with open(file_path, "r", encoding="utf-8") as file:
                for line in file:
                    # 줄바꿈 문자(\n, \r)를 제거하고 배열에 담기
                    string_array.append(line.strip())
            return string_array
        except Exception as e:
            print(f"❌ 파일 읽기 실패: {e}")
            return []



def clean_folder(path):
    if not os.path.exists(path):
        print("지정한 폴더가 존재하지 않습니다.")
        return
    
    # 2. 확장자별로 모을 폴더 이름을 지정합니다.
    file_types = {
        "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp"],
        "Documents": [".txt", ".pdf", ".docx", ".xlsx", ".pptx", ".hwp"],
        "Archives": [".zip", ".rar", ".7z", ".tar"],
        "Programs": [".exe", ".msi"]
    }

    # 폴더 내 모든 파일을 확인
    for filename in os.listdir(path):
        full_file_path = os.path.join(path, filename)
        
        # 파일이 아닌 폴더는 건너뜁니다.
        if os.path.isdir(full_file_path):
            continue
            
        # 파일의 확장자를 추출합니다 (.jpg, .txt 등)
        _, extension = os.path.splitext(filename)
        extension = extension.lower()
        
        # 설정한 확장자 그룹을 돌며 파일을 이동시킵니다.
        moved = False
        for folder_name, extensions in file_types.items():
            if extension in extensions:
                # 이동할 폴더가 없으면 새로 만듭니다.
                destination_folder = os.path.join(path, folder_name)
                os.makedirs(destination_folder, exist_ok=True)
                
                # 파일 이동
                shutil.move(full_file_path, os.path.join(destination_folder, filename))
                print(f"[이동] {filename} -> {folder_name} 폴더")
                moved = True
                break
        
        # 지정되지 않은 기타 확장자 처리
        if not moved and extension:
            etc_folder = os.path.join(path, "Others")
            os.makedirs(etc_folder, exist_ok=True)
            shutil.move(full_file_path, os.path.join(etc_folder, filename))
            print(f"[이동] {filename} -> Others 폴더")

    print("\n✨ 폴더 정리가 완료되었습니다!")


# ==================== 실행 및 검증 ====================
if __name__ == "__main__":

    # 1. 정리하고 싶은 폴더 경로를 지정합니다. (예: 다운로드 폴더나 바탕화면)
    # 윈도우 사용자는 경로 앞의 r을 그대로 두세요.
    # target_path = r"C:\Users\PC\Downloads" 

    # # 프로그램 실행
    # clean_folder(target_path)

    print(FileUtil.get_current_dir())