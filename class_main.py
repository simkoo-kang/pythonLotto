from pathlib import Path

from util.log_util import LogUtil


class ClassMain:
    def __init__(self, filepath=None):
        if filepath == None:
            filepath = str(Path(__file__).parent)
        else:
            if not type(filepath) == str:
                filepath = str(filepath)

        self.logger = LogUtil.get_logger(filepath)
