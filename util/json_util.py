import copy
import json
import re
from munch import Munch, munchify
import os
from pathlib import Path
from class_main import ClassMain
from util.file_util import FileUtil


class MunchJson(ClassMain):
    def __init__(
        self,
        data=None,
        file_path: str = None,
        filename: str = None,
        create_if_not: bool = True,
    ):
        if file_path == None:
            file_path = str(Path(__file__).parent)
        super().__init__(log_filedir=file_path)

        self.file_path = file_path
        self.filename = filename
        if data == None:
            if self.filename == None:
                self.data = munchify({})
            else:
                fullname = os.path.join(file_path, filename)
                if os.path.exists(fullname):
                    with open(fullname, "r", encoding="utf-8") as f:
                        self.data = json.load(f)

                    self.data = munchify(self.data)
                else:
                    self.data = munchify({})  # Dic.to_munchify()
                    if create_if_not:
                        self.save()
        else:
            if self.filename == None:
                if isinstance(data, Munch):
                    self.data = data
                else:
                    self.data = munchify(data)
            else:
                if isinstance(data, Munch):
                    self.data = data
                else:
                    self.data = munchify(data)

                if create_if_not and not os.path.exists(fullname):
                    self.save()

    def save(self):
        if self.filename == None:
            self.logger.debug("MunchJson. filename is None!")
            return

        if self.file_path and not os.path.exists(self.file_path):
            os.makedirs(self.file_path)

        filepath = os.path.join(self.file_path, self.filename)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.data.toDict(), f, indent=4, ensure_ascii=False)

    def put(self, key, value):
        self.data[key] = value

    def get(self, key):
        return self.data.get(key)

    def put_if_not(self, key, value):
        if self.get(key) == None:
            self.put(key, value)

    def contains_key(self, key):
        return False if self.get(key) == None else True

    def get_data(self):
        return self.data

    def set_data(self, data):
        if isinstance(data, Munch):
            self.data = data
        else:
            self.data = munchify(data)

    def add_data(self, data):
        if isinstance(data, Munch):
            # 방법 A: 새 Munch 객체로 합치기 (안전함)
            # merged_munch = Munch({**munch1, **munch2})
            # 방법 B: 기본 제공 연산자 후 다시 munchify
            # merged_munch = munchify(munch1 | munch2)
            self.data = Munch({**self.data, **data})
        else:
            # 두 딕셔너리 합치기 (중복된 키가 있다면 json2의 값이 덮어씁니다)
            # merged_json = json1 | json2
            mdata = munchify(data)
            self.data = Munch({**self.data, **mdata})

    def copy_of(self):
        return copy.deepcopy(self)


class Json(ClassMain):
    def __init__(
        self,
        data=None,
        file_path: str = None,
        file_name: str = None,
        create_if_not: bool = True,
    ):
        if file_path == None:
            file_path = str(Path(__file__).parent)
        super().__init__(log_filedir=file_path)

        self.file_path = file_path
        self.filename = file_name
        if data == None:
            if self.filename == None:
                self.data = {}
            else:
                fullname = os.path.join(file_path, self.filename)
                if os.path.exists(fullname):
                    with open(fullname, "r", encoding="utf-8") as f:
                        self.data = json.load(f)
                else:
                    self.data = {}  # Dic.to_munchify()
                    if create_if_not:
                        self.save()
        else:
            if self.filename == None:
                if isinstance(data, Munch):
                    self.data = data
                else:
                    self.data = munchify(data)
            else:
                if isinstance(data, Munch):
                    self.data = data
                else:
                    self.data = munchify(data)

                if create_if_not and not os.path.exists(fullname):
                    self.save()

    def save(self):
        if self.filename == None:
            self.logger.debug("filename is None!")
            return

        if self.file_path and not os.path.exists(self.file_path):
            os.makedirs(self.file_path)

        filepath = os.path.join(self.file_path, self.filename)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

    def put(self, key, value):
        self.data[key] = value

    def get(self, key):
        return self.data.get(key)

    def put_if_not(self, key, value):
        if self.get(key) == None:
            self.put(key, value)

    def contains_key(self, key):
        return False if self.get(key) == None else True

    def get_data(self):
        return self.data

    def set_data(self, data):
        if isinstance(data, Munch):
            self.data = data.toDict()
        else:
            self.data = data

    def add_data(self, data):
        if isinstance(data, Munch):
            # 방법 A: 새 Munch 객체로 합치기 (안전함)
            # merged_munch = Munch({**munch1, **munch2})
            # 방법 B: 기본 제공 연산자 후 다시 munchify
            # merged_munch = munchify(munch1 | munch2)
            self.data = self.data | data.toDict()
        else:
            # 두 딕셔너리 합치기 (중복된 키가 있다면 json2의 값이 덮어씁니다)
            # merged_json = json1 | json2
            self.data = self.data | data

    def copy_of(self):
        return copy.deepcopy(self)

    @staticmethod
    def to_list(set):
        return [list(coord) for coord in set]

    @staticmethod
    def save_pretty(filename, data, mode: str = "a"):
        # 1. 먼저 전체 데이터를 예쁘게 들여쓰기된 문자열로 바꿉니다.
        json_string = json.dumps(data, indent=4, ensure_ascii=False)

        # 2. 정규식을 이용해 1차원 숫자 배열 내부의 줄바꿈과 공백을 한 줄로 압축합니다.
        # [ 1, 2, ... ] 형태를 찾아서 대괄호 안의 공백과 줄바꿈을 지워줍니다.
        clean_json_string = re.sub(
            r"\[\s+([\d,\s]+)\s+\]",
            lambda m: "[" + re.sub(r"\s+", "", m.group(1)) + "]",
            json_string,
        )

        dir_name = os.path.dirname(filename)
        # foler가 없으면 생성
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name)

        # 3. 압축된 문자열을 파일에 그대로 씁니다.
        with open(filename, mode, encoding=FileUtil.DEFAULT_ENCODING) as f:
            f.write(clean_json_string)


# ==================== 실행 및 검증 ====================
if __name__ == "__main__":
    player = (1, 2)
    print(player, player[0], player[1])

    lst_player = list(player)
    print(lst_player, lst_player[0], lst_player[1])

    pos_set = {(1, 1), (2, 4), (2, 2)}
    print(Json.to_list(pos_set))

    json = Json()
