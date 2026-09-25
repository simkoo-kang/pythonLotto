import os
import shutil
from util.log_util import LogUtil

logger = LogUtil.get_logger("ProjectClean")

# 삭제할 디렉토리 이름과 파일 확장자 정의
TARGET_DIRECTORIES = ["__pycache__", ".pytest_cache", ".egg-info", "build", "dist"]
TARGET_EXTENSIONS = [".pyc", ".pyo"]

def clean_project(root_dir: str = "."):
    deleted_dirs_count = 0
    deleted_files_count = 0
    
    logger.info(f"프로젝트 청소를 시작합니다. 루트 경로: {os.path.abspath(root_dir)}")

    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):
        # 1. 대상 디렉토리(폴더) 삭제
        for dirname in dirnames:
            if dirname in TARGET_DIRECTORIES:
                full_path = os.path.join(dirpath, dirname)
                try:
                    shutil.rmtree(full_path)
                    deleted_dirs_count += 1
                    logger.debug(f"삭제된 폴더: {full_path}")
                except Exception as e:
                    logger.error(f"폴더 삭제 실패 ({full_path}): {e}")

        # 2. 대상 파일 삭제
        for filename in filenames:
            if any(filename.endswith(ext) for ext in TARGET_EXTENSIONS):
                full_path = os.path.join(dirpath, filename)
                try:
                    os.remove(full_path)
                    deleted_files_count += 1
                    logger.debug(f"삭제된 파일: {full_path}")
                except Exception as e:
                    logger.error(f"파일 삭제 실패 ({full_path}): {e}")

    # 삼항 연산자를 활용한 결과 메시지 포맷팅
    status = "성공" if (deleted_dirs_count > 0 or deleted_files_count > 0) else "정리할 항목 없음"
    
    # 앞서 배운 Number Format (콤마 표기) 적용
    logger.info(
        f"== 청소 완료 [{status}] ==\n"
        f"- 삭제된 폴더 수: {deleted_dirs_count:,}개\n"
        f"- 삭제된 파일 수: {deleted_files_count:,}개"
    )

if __name__ == "__main__":
    clean_project()
