import os
import re
import sys


class Str:

    @staticmethod
    def is_han(ch) -> bool:
        return (
            (0xAC00 <= ch <= 0xD7A3)
            or (0x3131 <= ch <= 0x318F)
            or (0x1100 <= ch <= 0x11FF)
            or (0xD7B0 <= ch <= 0xD7FF)
        )
    
    @staticmethod
    def is_alpha(ch) -> bool:
        return ((65 <= ch <= 90) or (97 <= ch <= 122))

    @staticmethod
    def is_digit(ch) -> bool:
        return (48 <= ch <= 57)

    @staticmethod
    def strip_not_digit(s: str) -> str:
        return re.sub(r"\D", "", s)

    @staticmethod
    def number_format(number: int) -> str:
        return f"{number:,}"

    @staticmethod
    def get_class_name(clazz_object) -> str:
        return clazz_object.__class__.__name__

    def get_

# ==================== 실행 및 검증 ====================
if __name__ == "__main__":
    print(os.path.abspath("."))

    # 1. 현재 파일(.py 또는 .exe)이 실제로 위치한 '진짜 폴더 경로' 구하기
    if hasattr(sys, "_MEIPASS"):
        # PyInstaller 단일 파일(.exe)로 실행된 경우
        # 만약 이미지를 .exe 내부에 빌드(내장)했다면 sys._MEIPASS를 사용하고,
        # 이미지를 .exe 외부에 두고 쓸 거라면 os.path.dirname(sys.executable)을 사용합니다.
        print(sys._MEIPASS)
        base_path = os.path.dirname(sys.executable)
    else:
        # 일반 파이썬 환경(.py)으로 실행된 경우 (현재 스크립트 파일의 절대 경로 기준)
        base_path = os.path.dirname(os.path.abspath(__file__))

    # 2. 진짜 폴더 경로를 기준으로 image 폴더 연결
    folder_path = os.path.join(base_path, "image")

    print(f"고정된 이미지 폴더 경로: {folder_path}")