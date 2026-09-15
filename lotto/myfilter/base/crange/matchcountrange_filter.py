from typing import List

import util.lotto_util as lotto_util
from lotto.myfilter.lotto_filter import ARangeFilter


# 3.6. 추가 필터 예시: 특정 숫자 배열과의 일치 개수
class MatchCountRangeFilter(ARangeFilter):
    def __init__(self, match_list: List[int], min_val: int = 0, max_val: int = 1, title: str = "Match Count Range Filter", optional: bool=True, debug: bool=False):
        super().__init__(min_val=min_val, max_val=max_val, optional=optional, debug=debug)
        self.match_list = match_list
        self.title = title

    @property
    def name(self) -> str: return self.title

    @property
    def description(self) -> str: return f"특정 숫자들과 중복되는 수가 {self.min_val}~{self.max_val}인지 검사"

    def filter(self, numbers: List[int]) -> bool:
        match_count = lotto_util.get_match_count_with_target_list(numbers, self.match_list)
        if self.min_val <= match_count <= self.max_val:
            return True
        if self.debug:
            print("False :", self.__class__.__name__)
        return False
