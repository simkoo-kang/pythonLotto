from typing import List

from myfilter.lotto_filter import ARangeFilter


# 3.4. 추가 필터 예시: 높은 수 개수
class HighRangeFilter(ARangeFilter):
    def __init__(self, min_val: int = 2, max_val: int = 4, debug: bool=False):
        super().__init__(min_val=min_val, max_val=max_val, debug=debug)

    @property
    def name(self) -> str: return "High Range Filter"

    @property
    def description(self) -> str: return f"높은 수가 {self.min_val}~{self.max_val}인지 검사"

    def filter(self, numbers: List[int]) -> bool:
        # 이 필터의 결과값은 '높은 수'
        high_count = sum(1 for n in numbers if n > 22)
        
        # 부모의 min_val, max_val과 비교
        if self.min_val <= high_count <= self.max_val:
            return True
        if self.debug:
            print("False :", self.__class__.__name__)
        return False
