from typing import List

import util.lotto_util as lotto_util
from myfilter.lotto_filter import ARangeFilter


# corners 숫자 배열과의 일치 개수
class CornerCountRangeFilter(ARangeFilter):

    corners = [ 1, 2, 6, 7, 8, 9, 13, 14, 29, 30, 34, 35, 36, 37, 41, 42, 43, 44, 45 ]

    def __init__(self, min_val: int = 0, max_val: int = 1, optional: bool=True, debug: bool=False):
        super().__init__(min_val=min_val, max_val=max_val, optional=optional, debug=debug)

    @property
    def name(self) -> str: return "Corner Count Range Filter"

    @property
    def description(self) -> str: return f"특정 숫자들과 중복되는 수가 {self.min_val}~{self.max_val}인지 검사"

    def filter(self, numbers: List[int]) -> bool:
        match_count = lotto_util.get_match_count_with_target_list(numbers, self.corners)
        if self.min_val <= match_count <= self.max_val:
            return True
        if self.debug:
            print("False :", self.__class__.__name__)
        return False
