from typing import List

import util.lotto_util as lotto_util
from lotto.myfilter.lotto_filter import AMinFilter


class Last10MinFilter(AMinFilter):
    def __init__(self, last10: List[int], min_val: int = 4, optional: bool=True, debug: bool=False):
        """_summary_
        지난 10회 출현 수
        Args:
            last10 (List[int]): _description_
            min_val (int, optional): _description_. Defaults to 4.
            optional (bool, optional): _description_. Defaults to True.
            debug (bool, optional): _description_. Defaults to False.
        """
        super().__init__(min_val=min_val, optional=optional, debug=debug)
        self.last10 = last10

    @property
    def name(self) -> str: return "지난 10회 출현한 번도"

    @property
    def description(self) -> str: return f"지난 10회 번호가 {self.min_val}~{self.max_val}인지 검사"

    def filter(self, numbers: List[int]) -> bool:
        match_count = lotto_util.get_match_count_with_target_list(numbers, self.last10)
        if self.min_val <= match_count:
            return True
        if self.debug:
            print("False :", self.__class__.__name__)
        return False

