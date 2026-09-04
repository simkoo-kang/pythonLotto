from typing import List

from myfilter.lotto_filter import ARangeFilter
import util.lotto_util as lotto_util


# 쌍수, 광땡
class PairsDdangRangeFilter(ARangeFilter):

    pairs = [ 11, 22, 33, 44 ]
    ddang = [ 13, 18, 31, 38 ]

    def __init__(self, min_val: int, max_val: int, index: int, optional: bool=True, debug: bool=False):
        super().__init__(min_val=min_val, max_val=max_val, optional=optional, debug=debug)
        self.arr = [self.pairs, self.ddang][index]

    @property
    def name(self) -> str:
        return "쌍수, 광땡 Range Filter"

    @property
    def description(self) -> str:
        return f"쌍수, 광땡수 갯수가 각 각 {self.min_val}~{self.max_val}개 안인지 검사합니다."

    def filter(self, numbers: List[int]) -> bool:
        match_count = lotto_util.get_match_count_with_target_list(numbers, self.arr)
        if self.min_val <= match_count <= self.max_val:
            return True
        if self.debug:
            print("False :", self.__class__.__name__)
        return False

