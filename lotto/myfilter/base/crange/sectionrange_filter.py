from typing import List

from lotto.myfilter.lotto_filter import ARangeFilter
import util.lotto_util as lotto_util


class SectionRangeFilter(ARangeFilter):
    """_summary_
    # 각 구간별 공 개수 계산 및 0이 아닌 구간 수 계산을 위한 공통 함수
    Args:
        ARangeFilter (_type_): _description_
    """
    def __init__(self, min_val: int, max_val: int, max_counts: int, section: int, optional: bool=True, debug: bool=False):
        """
        로또 번호를 구간별로 나누어 각 구간에 포함된 번호의 개수를 검사합니다.
        
        :param min_val: 공이 들어있는 최소 구간 수 (0이 아닌 구간 수의 하한선)
        :param max_val: 공이 들어있는 최대 구간 수 (0이 아닌 구간 수의 상한선)
        :param max_counts: 각 구간에 허용하는 최대 공의 개수
        :param section: 구간 수 (5 또는 9)
        """
        super().__init__(min_val=min_val, max_val=max_val, optional=optional, debug=debug)
        self.max_counts = max_counts
        self.section = section

    @property
    def name(self) -> str:
        return "Section Range Filter"

    @property
    def description(self) -> str:
        return (
            f"각 구간({self.section} 단위)별로 포함된 번호의 개수를 검사하며, "
            f"공이 들어있는 구간 수가 {self.min_val}~{self.max_val}개 안인지 검사합니다."
        )

    def filter(self, numbers: List[int]) -> bool:
        # 1. 각 구간별 공 개수 계산
        section_counts = lotto_util.get_section_numbers(numbers, self.section)

        max_count_in_section = max(section_counts)
        # [검증 조건] 어느 한 구간이라도 허용치(max_counts)를 초과하는 경우 탈락
        if max_count_in_section > self.max_counts:
            if self.debug:
                print("False :", self.__class__.__name__)
            return False
        
        # 2. 0이 아닌 (공이 1개 이상 들어있는) 구간 수 계산
        non_empty_sections = sum(1 for count in section_counts if count > 0)

        # [검증 조건] 0이 아닌 구간 수가 부모 범위(min_val ~ max_val) 안에 들어오는지 체크
        if self.min_val <= non_empty_sections <= self.max_val:
            return True
        if self.debug:
            print("False :", self.__class__.__name__)
        return False

