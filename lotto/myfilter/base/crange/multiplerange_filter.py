from typing import List

from lotto.myfilter.lotto_filter import ARangeFilter
import util.lotto_util as lotto_util


class MultipleRangeFilter(ARangeFilter):
    """_summary_
    # 3의 배수, 5의 배수
    Args:
        ARangeFilter (_type_): _description_
    Returns:
        _type_: _description_
    """

    multi3 = [ 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45 ] # fmt: skip
    multi5 = [ 5, 10, 15, 20, 25, 30, 35, 40, 45 ] # fmt: skip

    def __init__(self, min_val: int, max_val: int, index: int, optional: bool=True, debug: bool=False):
        super().__init__(min_val=min_val, max_val=max_val, optional=optional, debug=debug)
        self.multi = self.multi3 if index == 3 else self.multi5

    @property
    def name(self) -> str:
        return "Multiple Range Filter"

    @property
    def description(self) -> str:
        return f"3의 배수, 5의 배수 각 각 갯수가 {self.min_val}~{self.max_val}개 안인지 검사합니다."

    def filter(self, numbers: List[int]) -> bool:
        match_count = lotto_util.get_match_count_with_target_list(numbers, self.multi)
        if self.min_val <= match_count <= self.max_val:
            return True
        if self.debug:
            print("False :", self.__class__.__name__)
        return False

