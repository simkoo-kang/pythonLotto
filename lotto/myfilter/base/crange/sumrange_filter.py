from typing import List

from lotto.myfilter.lotto_filter import ARangeFilter


# 3.2. 예시: 총합 범위를 거르는 필터 추가 시
class SumRangeFilter(ARangeFilter):
    def __init__(self, min_val: int = 100, max_val: int = 175, optional: bool=True, debug: bool=False):
        # 총합 결과값이 100 ~ 175 사이여야 함을 부모에게 전달
        super().__init__(min_val=min_val, max_val=max_val, optional=optional, debug=debug)

    @property
    def name(self) -> str: return "Sum Range Filter"

    @property
    def description(self) -> str: return f"총합이 {self.min_val}~{self.max_val} 안인지 검사"

    def filter(self, numbers: List[int]) -> bool:
        # 이 필터의 결과값은 '총합'
        total_sum = sum(numbers) 
        
        # 부모의 min_val, max_val과 비교
        if self.min_val <= total_sum <= self.max_val:
            return True
        if self.debug:
            print("False :", self.__class__.__name__)
        return False
