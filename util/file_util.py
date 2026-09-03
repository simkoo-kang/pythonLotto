# util/file_util.py
import os

class FileUtil:
    # 💡 [정적 필드 (Static Field) 선언]
    # 클래스명 자체로 바로 접근할 수 있으며, 모든 인스턴스가 이 값을 공유합니다.
    DEFAULT_PATH = r"D:\Workspace\vscode\lotto"
    CONF_PATH = os.path.join(DEFAULT_PATH, "conf")
    DEFAULT_ENCODING = "utf-8"

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
