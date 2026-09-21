# util/file_util.py
import os
from pathlib import Path


class FileUtil:
    # 💡 [정적 필드 (Static Field) 선언]
    # 클래스명 자체로 바로 접근할 수 있으며, 모든 인스턴스가 이 값을 공유합니다.
    """default path D:\\Workspace\\vscode\\lotto """
    DEFAULT_PATH = r"D:\\Workspace\\vscode\\lotto"
    
    """ conf folder"""
    CONF_PATH = os.path.join(DEFAULT_PATH, "conf")
    
    """default encoding utr-8 """
    DEFAULT_ENCODING = "utf-8"

    @staticmethod
    def get_absolute_class_path(cls_or_instance):
        """만약 인스턴스(객체)가 들어왔다면, 해당 인스턴스의 __class__를 가져옵니다."""
        cls = (
            cls_or_instance
            if isinstance(cls_or_instance, type)
            else cls_or_instance.__class__
        )

        return f"{cls.__module__}.{cls.__qualname__}"

    @staticmethod
    def get_current_dir() -> str:
        """ current working dir """
        return os.getcwd()

    @staticmethod
    def get_lotto_make_filtered_file(round: int) -> str:
        """ D:\\Workspace\\vscode\\lotto\\conf\\make\\\\(round)_filtered.txt """
        return os.path.join(FileUtil.CONF_PATH, "make", f"{round}_filtered.txt")

    @staticmethod
    def get_lotto_make_all_file(round: int) -> str:
        """ D:\\Workspace\\vscode\\lotto\\conf\\make\\\\(round)_all.txt """
        return os.path.join(FileUtil.CONF_PATH, "make", f"{round}_all.txt")

    @staticmethod
    def get_lotto_make_file(round: int) -> str:
        """ D:\\Workspace\\vscode\\lotto\\conf\\make\\\\(round).txt """
        return os.path.join(FileUtil.CONF_PATH, "make", f"{round}.txt")

    @staticmethod
    def get_lotto_selected_file(round: int) -> str:
        """ D:\\Workspace\\vscode\\lotto\\conf\\make\\\\(round)_selected.txt """
        return os.path.join(FileUtil.CONF_PATH, "make", f"{round}_selected.txt")

    @staticmethod
    def exists(file_path: str) -> bool:
        """ os.path.exists(file_path) """
        return os.path.exists(file_path)

    @staticmethod
    def parent(file_path: str) -> str:
        """ str(Path(file_path).parent) """
        return str(Path(file_path).parent)

    @staticmethod
    def filesize(file_path: str) -> int:
        """ Path(file_path).stat().st_size """
        return Path(file_path).stat().st_size

    @staticmethod
    def ext(file_path: str, is_all: bool = True) -> str:
        """ .py if is_all else py """
        if is_all:
            return Path(file_path).suffix  # .py
        return Path(file_path).suffix[1:]  # py

    @staticmethod
    def filename(file_path: str, is_all: bool = True) -> str:
        """ json.py if is_all else json """
        if is_all:
            return Path(file_path).name  # json.py
        return Path(file_path).stem  # json

    @staticmethod
    def writeln(file_path: str, string: str, mode: str = "a") -> bool:
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


# ==================== 실행 및 검증 ====================
if __name__ == "__main__":

    print("current dir", FileUtil.get_current_dir())

    print("class abs path", FileUtil.get_absolute_class_path(FileUtil))

    # 예시 파일 경로
    file_path_str = r"D:\Workspace\vscode\lotto\game\sokoban\sokoban.py"

    # Path 객체 생성
    path = Path(file_path_str)

    # 각각의 요소 추출
    folder_path = path.parent  # 폴더 경로
    file_name = path.stem  # 확장자를 제외한 파일 이름
    file_ext = path.suffix  # 확장자 (점 '.' 포함)
    full_name = path.name  # 확장자를 포함한 전체 파일명

    # 출력 결과
    print(f"폴더 경로: {folder_path}")  # D:\Workspace\vscode\lotto\game\sokoban
    print(f"파일 이름: {file_name}")  # sokoban
    print(f"확 장 자 : {file_ext}")  # .py
    print(f"확 장 자 : {file_ext[1:]}")  # .py
    print(f"전체 파일명: {full_name}")  # sokoban.py
    print(f"사 이 즈 : {path.stat().st_size}")  # .py
