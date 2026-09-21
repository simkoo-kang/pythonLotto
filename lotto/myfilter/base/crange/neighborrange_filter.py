from typing import List

import util.lotto_util as lotto_util
from lotto.myfilter.lotto_filter import ARangeFilter


class NeighborRangeFilter(ARangeFilter):
    """_summary_
    # 이웃수 패턴
    Args:
        ARangeFilter (_type_): _description_
    Returns:
        _type_: _description_
    """
    def __init__(self, match_list: List[int], min_val: int = 0, max_val: int = 1, optional: bool=True, debug: bool=False):
        super().__init__(min_val=min_val, max_val=max_val, optional=optional, debug=debug)
        self.match_list = lotto_util.get_neigbors(match_list)

    @property
    def name(self) -> str: return "이웃수 패턴"

    @property
    def description(self) -> str: return f"특정 숫자들과 중복되는 수가 {self.min_val}~{self.max_val}인지 검사"

    def filter(self, numbers: List[int]) -> bool:
        match_count = lotto_util.get_match_count_with_target_list(numbers, self.match_list)
        if self.min_val <= match_count <= self.max_val:
            return True
        if self.debug:
            print("False :", self.__class__.__name__)
        return False


if __name__ == "__main__":
    nrf = NeighborRangeFilter([1,2,3,4,5,6], 0, 2)
    res = nrf.filter([1,2,6,8,9,12,25])
    print(res)
