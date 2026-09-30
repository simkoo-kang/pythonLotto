
import os
import sys


class ResUtil:
    
    @staticmethod
    def resource_path(relative_path, file_path):
        try:
            base_path = sys._MEIPASS
            return os.path.join(base_path, file_path)
        except Exception:
            # 개발 환경(VS Code)에서 실제 파일이 들어있는 하위 경로 지정
            # 만약 이미지를 루트에 두셨다면 os.path.abspath(relative_path)로 쓰셔도 됩니다.
            return os.path.abspath(os.path.join(relative_path, file_path))


# ==================== 실행 및 검증 ====================
if __name__ == "__main__":
    print(ResUtil.resource_path("game/pic/jigsaw", "icon.ico"))
