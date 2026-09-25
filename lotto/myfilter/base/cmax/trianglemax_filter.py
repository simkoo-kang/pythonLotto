from typing import List

import util.lotto_util as lotto_util
from lotto.myfilter.lotto_filter import AMaxFilter


class TriangleMaxFilter(AMaxFilter):
    """_summary_
    # 삼각 패턴
    Args:
        AMaxFilter (_type_): _description_
    Returns:
        _type_: _description_
    """

    max_count = 4

    groups = [
        [ 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 16, 17, 18, 19, 22, 23, 24, 25, 29, 30, 31, 36, 37, 43, ],
        [ 1, 8, 9, 15, 16, 17, 22, 23, 24, 25, 29, 30, 31, 32, 33, 36, 37, 38, 39, 40, 41, 43, 44, 45, ],
        [ 1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 13, 14, 17, 18, 19, 20, 21, 25, 26, 27, 28, 33, 34, 35, 41, 42, ],
        [ 7, 13, 14, 19, 20, 21, 25, 26, 27, 28, 31, 32, 33, 34, 35, 37, 38, 39, 40, 41, 42, 43, 44, 45, ],
    ]  # fmt: skip

    def __init__(
        self, max_val: int, index: int, optional: bool = True, debug: bool = False
    ):
        super().__init__(max_val=max_val, optional=optional, debug=debug)
        self.triangle_group = self.groups[index]

    @property
    def name(self) -> str:
        return "삼각 패턴 Filter"

    @property
    def description(self) -> str:
        return f"삼각 패턴의 최대 값이 {self.max_val}보다 작은지 검사"

    def filter(self, numbers: List[int]) -> bool:
        match_count = lotto_util.get_match_count_with_target_list(
            numbers, self.triangle_group
        )
        if match_count < self.max_val:
            return True
        if self.debug:
            print("False :", self.__class__.__name__)
        return False
