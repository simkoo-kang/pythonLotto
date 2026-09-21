from typing import List

from lotto.myfilter.lotto_filter import ABooleanFilter
import util.lotto_util as lotto_util


class SteppingStoneBooleanFilter(ABooleanFilter):
    def __init__(self, bool_val: bool = False, optional: bool=True, debug: bool=False):
        """_summary_
        3.10. 추가 필터 예시: 징검다리 패턴 존재 여부
        Args:
            bool_val (bool, optional): _description_. Defaults to False.
            optional (bool, optional): _description_. Defaults to True.
            debug (bool, optional): _description_. Defaults to False.
        """
        super().__init__(bool_val=bool_val, optional=optional, debug=debug)

    @property
    def name(self) -> str: return "Stepping Stone Pattern Filter"

    @property
    def description(self) -> str: return f"징금다리 패턴이 있는 지 검사"

    def filter(self, numbers: List[int]) -> bool:
        if self.bool_val == lotto_util.has_stepping_stone_pattern(numbers):
            return True
        if self.debug:
            print("False :", self.__class__.__name__)
        return False
