from typing import List

from lotto.myfilter.lotto_filter import ARangeFilter


class EvenRangeFilter(ARangeFilter):
    def __init__(self, min_val: int = 2, max_val: int = 4, optional: bool=True, debug: bool=False):
        """_summary_
        3.3. 추가 필터 예시: 짝수 개수
        Args:
            min_val (int, optional): _description_. Defaults to 2.
            max_val (int, optional): _description_. Defaults to 4.
            optional (bool, optional): _description_. Defaults to True.
            debug (bool, optional): _description_. Defaults to False.
        """
        super().__init__(min_val=min_val, max_val=max_val, optional=optional, debug=debug)

    @property
    def name(self) -> str: return "Even Range Filter"

    @property
    def description(self) -> str: return f"짝수 개수가 {self.min_val}~{self.max_val}인지 검사"

    def filter(self, numbers: List[int]) -> bool:
        # 이 필터의 결과값은 '짝수 개수'
        even_count = sum(1 for n in numbers if n % 2 == 0)
        
        # 부모의 min_val, max_val과 비교
        if self.min_val <= even_count <= self.max_val:
            return True
        
        if self.debug:
            print("False :", self.__class__.__name__)
        return False
