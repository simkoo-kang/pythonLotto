from typing import List

from myfilter.lotto_filter import ARangeFilter
import util.lotto_util as lotto_util


# 합성수
class CompositionRangeFilter(ARangeFilter):

    comps = [ 1, 4, 8, 10, 16, 20, 22, 25, 26, 28, 32, 34, 35, 38, 40, 44 ]

    def __init__(self, min_val: int, max_val: int, debug: bool=False):
        super().__init__(min_val=min_val, max_val=max_val, debug=debug)

    @property
    def name(self) -> str:
        return "합성수 Range Filter"

    @property
    def description(self) -> str:
        return f"합성수 갯수가 {self.min_val}~{self.max_val}개 안인지 검사합니다."

    def filter(self, numbers: List[int]) -> bool:
        match_count = lotto_util.get_match_count_with_target_list(numbers, self.comps)
        if self.min_val <= match_count <= self.max_val:
            return True
        if self.debug:
            print("False :", self.__class__.__name__)
        return False

