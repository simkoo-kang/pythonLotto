from typing import List

import util.lotto_util as lotto_util
from myfilter.lotto_filter import ARangeFilter


# 이월수 패턴
class RepeatRangeFilter(ARangeFilter):
    def __init__(self, match_list: List[int], min_val: int = 0, max_val: int = 1, debug: bool=False):
        super().__init__(min_val=min_val, max_val=max_val, debug=debug)
        self.match_list = match_list

    @property
    def name(self) -> str: return "이월수 패턴"

    @property
    def description(self) -> str: return f"특정 숫자들과 중복되는 수가 {self.min_val}~{self.max_val}인지 검사"

    def filter(self, numbers: List[int]) -> bool:
        match_count = lotto_util.get_match_count_with_target_list(numbers, self.match_list)
        if self.min_val <= match_count <= self.max_val:
            return True
        if self.debug:
            print("False :", self.__class__.__name__)
        return False
