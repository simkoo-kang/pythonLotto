import os
import logging
from logging.handlers import RotatingFileHandler
import sys

from util.str_util import Str


class LogUtil:

    @staticmethod
    def get_logger(
        name: str = "AppLogger",
        log_dir: str = "./logs",
        log_file: str = "app.log",
        level: int = logging.DEBUG,
    ) -> logging.Logger:

        # root_logger = logging.getLogger()
        # root_logger.setLevel(logging.DEBUG)
        # root_logger.handlers.clear()

        # handler = logging.StreamHandler(sys.stdout)
        # handler.setFormatter(
        #     logging.Formatter("[{asctime}] {levelname} - {message}", style="{")
        # )
        # root_logger.addHandler(handler)

        """
        설정된 핸들러(콘솔, 파일)가 포함된 로거 객체를 반환합니다.
        이미 핸들러가 존재하면 중복 등록을 방지합니다.
        """
        # logging.basicConfig(style="{")
        # force=True를 추가해 기존 설정을 무시하고 강제로 적용합니다.
        logging.basicConfig(
            level=logging.DEBUG,
            format="[{asctime}] {levelname} - {message}",
            style="{",  # 중괄호 스타일 지정
            force=True,
        )

        logger = logging.getLogger(name)
        logger.setLevel(level)
        # 💡 이 한 줄을 추가하면 루트 로거로 로그가 전파되지 않아 2줄씩 나오지 않습니다.
        logger.propagate = False

        # 핸들러 중복 등록 방지 (이미 설정되어 있다면 기존 로거 반환)
        if logger.handlers:
            return logger

        # 공통 로그 포맷 지정 (시간 - 로거이름 - 레벨 - 메시지)
        LOG_FORMAT = "[%(asctime)s] [%(name)s] [%(levelname)s] [%(filename)s:%(lineno)d] [%(funcName)s] - %(message)s"
        log_format = logging.Formatter(LOG_FORMAT, datefmt="%Y-%m-%d %H:%M:%S")

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
                file_path, maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8"
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
    b = [5, 6, 7, 8, 9, 0]
    c = a + b
    d = sorted(list(set(c)))
    print(c, d)

    print(0, 3, a[0:3])
    print(1, 3, a[1:3])
    print(0, 12, c[0:12])
    print(0, 12, c[:12])
    print(len(c), c[0:12])

    logger = LogUtil.get_logger(__file__)
    str = "abc"
    logger.debug(f"{str}")
