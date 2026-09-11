import sys
import os

# 현재 실행 파일의 폴더 경로를 파이썬 라이브러리 검색 경로에 강제로 추가 [1]
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)
