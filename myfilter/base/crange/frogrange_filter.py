from typing import List

import util.lotto_util as lotto_util
from myfilter.lotto_filter import ARangeFilter


# 개구리 패턴
class FrogRangeFilter(ARangeFilter):

    max_count: int = 4

    frogs = [
        [ 1, 2, 8, 9, 15, 16, 22, 23, 29, 30, 36, 37, 43, 44 ],
        [ 3, 4, 10, 11, 17, 18, 24, 25, 31, 32, 38, 39, 45 ],
        [ 4, 5, 11, 12, 18, 19, 25, 26, 32, 33, 39, 40 ],
        [ 6, 7, 13, 14, 20, 21, 27, 28, 34, 35, 41, 42 ]
    ]

    def __init__(self, min_val: int, max_val: int, index: int, optional: bool=True, debug: bool=False):
        super().__init__(min_val=min_val, max_val=max_val, optional=optional, debug=debug)
        self.index = index

    @property
    def name(self) -> str: return "Frog Range Filter"

    @property
    def description(self) -> str: return f"특정 숫자들과 중복되는 수가 {self.min_val}~{self.max_val}인지 검사"

    def filter(self, numbers: List[int]) -> bool:
        match_count = lotto_util.get_match_count_with_target_list(numbers, self.frogs[self.index])
        if self.min_val <= match_count <= self.max_val:
            return True
        if self.debug:
            print("False :", self.__class__.__name__)
        return False
