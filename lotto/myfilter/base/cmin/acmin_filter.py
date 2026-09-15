from typing import List

from lotto.myfilter.lotto_filter import AMinFilter
import util.lotto_util as lotto_util


# 3.1. 구체 클래스 (부모의 생성자를 호출하도록 super() 적용)
class ACMinFilter(AMinFilter):
    def __init__(self, min_val: int = 6, optional: bool=True, debug: bool=False):
        # super()를 통해 부모 클래스의 생성자에 min, max 범위를 전달합니다.
        super().__init__(min_val=min_val, optional=optional, debug=debug)

    @property
    def name(self) -> str:
        return "AC Range Filter"

    @property
    def description(self) -> str:
        return f"{self.min_val} 보다 AC 값이 작지 않은가 검사합니다."

    def filter(self, numbers: List[int]) -> bool:
        # 2. 이 필터의 핵심 결과값(AC값) 계산
        ac_value = lotto_util.calculate_ac(numbers)

        # 3. 결과값이 부모 클래스에 설정된 (min_val) 보다 큰지 비교
        if self.min_val <= ac_value:
            return True
        if self.debug:
            print("False :", self.__class__.__name__)
        return False
