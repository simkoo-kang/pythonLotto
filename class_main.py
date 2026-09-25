from pathlib import Path

from util.log_util import LogUtil


class ClassMain:
    def __init__(self, log_filedir=None):
        if log_filedir == None:
            log_filedir = str(Path(__file__).parent)
        else:
            if not type(log_filedir) == str:
                log_filedir = str(log_filedir)

        self.logger = LogUtil.get_logger(log_filedir)

    def debug(self, *args):
        if not type(args[0]) == int and "{}" in args[0]:
            parts = args[0].split("{}")
            values = []
            for i in range(1, len(args)):
                values.append(str(args[i]))

            result = parts[0]
            for i in range(len(values)):
                result += values[i] + parts[i + 1]
            self.logger.debug(result)
        else:
            values = []
            for i in range(len(args)):
                values.append(str(args[i]))
            result = " ".join(values)
            self.logger.debug(result)


# ==================== 실행 및 검증 ====================
if __name__ == "__main__":
    classMain = ClassMain()
    classMain.logger.debug(f"{__file__}")

    classMain.debug("abc", 2, 34, 5)
    classMain.debug("{} {}", 5, "abd")

    classMain.logger.debug("%02d %02d %02d", 2, 4, 5)
    classMain.logger.debug("%02s %s", 5, "abd")
