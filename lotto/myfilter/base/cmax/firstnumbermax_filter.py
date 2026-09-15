from typing import List

from lotto.myfilter.lotto_filter import AMaxFilter


# 3.11. 추가 필터 예시: 첫번째 숫자 최대 값 범위
class FirstNumberMaxFilter(AMaxFilter):
    def __init__(self, max_val: int = 15, optional=True, debug: bool=False):
        super().__init__(max_val=max_val, optional=optional, debug=debug)

    @property
    def name(self) -> str: return "First Number Filter"

    @property
    def description(self) -> str: return f"첫 번째 번호가 {self.max_val}보다 작은지 검사"

    def filter(self, numbers: List[int]) -> bool:
        if numbers[0] < self.max_val:
            return True
        if self.debug:
            print("False :", self.__class__.__name__)
        return False
