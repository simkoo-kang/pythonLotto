
from collections import defaultdict

import munch

from util.str_util import Str

class Dic:

    def __init__(self):
        self.mydic = defaultdict(int)

    def toString(self) -> str:
        # 1. 각 키와 값을 문자열 라인으로 포맷팅하여 리스트로 생성
        lines = [f"{key}\t{Str.number_format(value)}" for key, value in self.mydic.items()]
        
        # 2. 줄바꿈 문자로 연결하여 하나의 문자열로 반환
        return "\n".join(lines)

    # key: true이면 key로 정렬, false이면 value로 정렬
    # reverse는 오름 차순(False) 순방, 내림 차순(True) 역방
    # second_key는 1차 정렬하고 값이 중복되면 그 중에서 2차 키로 정렬
    # second_reverse 2차 정렬
    def sort_new(self, key: bool=True, reverse: bool=False, second_key: bool=False, second_reverse: bool=False):
        idx = 0 if key else 1
        if second_key:
            sidx = 1 if idx==0 else 0
            if second_key:
                return dict(sorted(self.mydic.items(), key=lambda x: (x[idx], -x[sidx]), reverse=reverse))
            return dict(sorted(self.mydic.items(), key=lambda x: (x[idx], x[sidx]), reverse=reverse))

        return dict(sorted(self.mydic.items(), key=lambda x: x[idx], reverse=reverse))

    # key: true이면 key로 정렬, false이면 value로 정렬
    # reverse는 오름 차순(False) 순방, 내림 차순(True) 역방
    # second_key는 1차 정렬하고 값이 중복되면 그 중에서 2차 키로 정렬
    # second_reverse 2차 정렬
    def sort(self, key: bool=True, reverse: bool=False, second_key: bool=False, second_reverse: bool=False):
        self.mydic = self.sort_new(key=key, reverse=reverse, second_key=second_key, second_reverse=second_reverse)

    def clear(self):
        self.mydic.clear()

    def is_empty(self) -> bool:
        return len(self.mydic) == 0

    def get_size(self) -> int:
        return len(self.mydic)

    def contains_key(self, key) -> bool:
        return key in self.mydic

    def contains_value(self, value) -> bool:
        return value in self.mydic.values()

    def remove(self, key):
        if key in self.mydic:
            del self.mydic[key]

    def get(self, key):
        return self.mydic.get(key, None)

    def set(self, key, value):
        self.mydic[key] = value

    def add_dics(self, other_dic):
        for key, value in other_dic.items():
            self.mydic[key] += value

    def add_list(self, key_list: list):
        for key in key_list:
            self.mydic[key] += 1

    # count: default 1
    def add_dic(self, key, count: int=1):
        self.mydic[key] += count

    def get_dic(self, key) -> int:
        return self.mydic[key]

    def get_mydic(self) -> defaultdict:
        return self.mydic

    def get_keys(self):
        return self.mydic.keys()

    def get_values(self):
        return self.mydic.values()

    def get_iter(self):
        return iter(self.mydic.items())

    def items(self):
        return self.mydic.items()

    
    @staticmethod
    def to_munchify(dic: dict=None):
        if dic == None:
            dic = {}
        
        return munch.munchify(dic)
    
    @staticmethod
    def to_dict(dic: munch.Munch):
        return dic.toDict()
    

# ==================== 실행 및 검증 ====================
if __name__ == "__main__":
    mydic = Dic()
    mydic.add_dic("A", 5)
    mydic.add_dic("B", 3)
    mydic.add_dic("C", 8)
    mydic.add_dic("D", 1)

    print("Original Dictionary:")
    print(mydic.toString())

    print("\nSorted by Key (Ascending):")
    mydic.sort(key=True, reverse=False)
    print(mydic.toString())

    print("\nSorted by Key (Descending):")
    mydic.sort(key=True, reverse=True)
    print(mydic.toString())

    print("\nSorted by Value (Ascending):")
    mydic.sort(key=False, reverse=False)
    print(mydic.toString())

    print("\nSorted by Value (Descending):")
    mydic.sort(key=False, reverse=True)
    print(mydic.toString())
