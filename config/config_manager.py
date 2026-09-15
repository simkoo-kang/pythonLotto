"""
설정 파일 관리
"""

import json
import os
from munch import munchify


class ConfigManager:
    def __init__(self, abs_path, is_abs: bool = True, file_name="config.json"):
        if is_abs:
            current_file_dir = os.path.dirname(os.path.abspath(abs_path))
            self.config_filename = os.path.join(current_file_dir, file_name)
        else:
            self.config_filename = os.path.join(abs_path, file_name)

        # 파일이 존재하면 로드하고, 없으면 빈값으로 새로 생성
        if os.path.exists(self.config_filename):
            self.load()

        else:
            print(self.config_filename, " not exist!")
            self.settings = self.dict_to_munchify()
            self.save()

    def clear(self):
        self.settings.clear()

    def load(self):
        with open(self.config_filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.settings = munchify(data)  # 읽어올 때 munchify

    def dict_to_munchify(self, dic: dict = None):
        if dic == None:
            dic = {}

        return munchify(dic)

    def save(self):
        with open(self.config_filename, "w", encoding="utf-8") as f:
            # 저장할 때 toDict()로 원상복구
            json.dump(self.settings.toDict(), f, indent=4, ensure_ascii=False)


# 전역에서 쓸 수 있는 인스턴스를 단 하나만 생성 (싱글톤 효과)
# 이 파일이 import될 때는 이 객체만 안전하게 생성된다.
# settings = Config()
