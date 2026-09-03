from typing import List

from myfilter.lotto_filter import ARangeFilter


# 3. Concrete Class (끝수합 필터)
class SumEndingRangeFilter(ARangeFilter):
    """
    일의 자리 숫자의 총합을 기준으로 필터링하는 구체적인 필터 클래스입니다.
    """
    def __init__(self, min_val: int = 20, max_val: int = 35, debug: bool=False):
        super().__init__(min_val, max_val, debug=debug)

    @property
    def name(self) -> str:
        return "Sum Ending Filter"

    @property
    def description(self) -> str:
        return f"로또 번호의 끝수합(1의 자리 숫자들의 합)이 {self.min_val} ~ {self.max_val} 사이인지 검사합니다."

    def filter(self, numbers: List[int]) -> bool:
        # 끝수합 계산 (각 번호를 10으로 나눈 나머지들의 합)
        end_sum = sum(n % 10 for n in numbers)
        
        # 지정된 범위 내에 있는지 판별
        if self.min_val <= end_sum <= self.max_val:
            return True
        if self.debug:
            print("False :", self.__class__.__name__)
        return False
