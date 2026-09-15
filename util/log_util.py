import os
import logging
from logging.handlers import RotatingFileHandler

from util.str_util import Str

class LogUtil:

    @staticmethod
    def get_logger(
        name: str = "AppLogger", 
        log_dir: str = "./logs", 
        log_file: str = "app.log", 
        level: int = logging.DEBUG
    ) -> logging.Logger:
        """
        설정된 핸들러(콘솔, 파일)가 포함된 로거 객체를 반환합니다.
        이미 핸들러가 존재하면 중복 등록을 방지합니다.
        """
        logging.basicConfig(style='{')
        logger = logging.getLogger(name)
        logger.setLevel(level)

        # 핸들러 중복 등록 방지 (이미 설정되어 있다면 기존 로거 반환)
        if logger.handlers:
            return logger

        # 공통 로그 포맷 지정 (시간 - 로거이름 - 레벨 - 메시지)
        LOG_FORMAT = "[%(asctime)s] [%(name)s] [%(levelname)s] [%(filename)s:%(lineno)d] [%(funcName)s] - %(message)s"
        log_format = logging.Formatter(LOG_FORMAT, datefmt='%Y-%m-%d %H:%M:%S')

        # 1. 콘솔 핸들러 설정
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_format)
        logger.addHandler(console_handler)

        # 2. 파일 핸들러 설정 (용량 기반 롤링 파일 핸들러)
        try:
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            file_path = os.path.join(log_dir, log_file)
            
            # 파일당 5MB 제한, 최대 5개까지 백업 유지, 한글 깨짐 방지 utf-8
            file_handler = RotatingFileHandler(
                file_path, 
                maxBytes=5 * 1024 * 1024, 
                backupCount=5, 
                encoding='utf-8'
            )
            file_handler.setFormatter(log_format)
            logger.addHandler(file_handler)
            
        except Exception as e:
            print(f"[LogUtil Error] 파일 핸들러 생성 실패: {e}")

        return logger


# ==================== 실행 및 검증 ====================
if __name__ == "__main__":
    # 요청하신 예시 데이터 입력
    a = [1, 2, 3, 4, 5, 6]
    b = [5,6,7,8,9,0]
    c=a+b
    d = sorted(list(set(c)))
    print(c, d)

    print(0,3,a[0:3])
    print(1,3,a[1:3])
    print(0,12,c[0:12])
    print(0,12,c[:12])
    print(len(c),c[0:12])

    lutil = LogUtil()
    print(Str.get_class_name(lutil))