from typing import List

from myfilter.lotto_filter import AMaxFilter
import util.lotto_util as lotto_util


# 3.5. 추가 필터 예시: 연속된 쌍 개수 ([1,2], [3,4] 등) 범위
class ConsecutivePairsMaxFilter(AMaxFilter):
    def __init__(self, max_val: int = 1, debug: bool=False):
        super().__init__(max_val=max_val, debug=debug)

    @property
    def name(self) -> str: return "Consecutive Pairs Max Filter"

    @property
    def description(self) -> str: return f"연속된 쌍의 개수가 {self.max_val} 이하인지 검사"

    def filter(self, numbers: List[int]) -> bool:
        # 이 필터의 결과값은 '연속된 쌍의 개수'
        consecutive_count = lotto_util.count_consecutive_pairs(numbers)
        # 부모의 max_val과 비교
        if self.max_val < consecutive_count:
            if self.debug:
                print("False :", self.__class__.__name__)
            return False
        return True
