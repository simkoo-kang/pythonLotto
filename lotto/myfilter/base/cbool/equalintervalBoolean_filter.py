from typing import List

from lotto.myfilter.lotto_filter import ABooleanFilter
import util.lotto_util as lotto_util


class EqualIntervalBooleanFilter(ABooleanFilter):
    def __init__(self, bool_val: bool = False, interval_size: int = 0, optional:bool=True, debug: bool=False):
        """_summary_
        3.9. 추가 필터 예시: 등간격 패턴 존재 여부
        Args:
            bool_val (bool, optional): _description_. Defaults to False.
            interval_size (int, optional): _description_. Defaults to 0.
            optional (bool, optional): _description_. Defaults to True.
            debug (bool, optional): _description_. Defaults to False.
        """
        super().__init__(bool_val=bool_val, optional=optional, debug=debug)
        self.interval_size = interval_size

    @property
    def name(self) -> str: return "Equal Interval Boolean Filter"

    @property
    def description(self) -> str: return f"등간격 패턴의 개수가 있는지 검사"

    def filter(self, numbers: List[int]) -> bool:
        if self.bool_val == lotto_util.has_equal_interval_pattern(numbers, self.interval_size):
            return True
        if self.debug:
            print("False :", self.__class__.__name__)
        return False
