from typing import List

from myfilter.lotto_filter import ARangeFilter
import util.lotto_util as lotto_util


# 3.8. 추가 필터 예시: 세로 라인 분포도
class VLineRangeFilter(ARangeFilter):
    def __init__(self,  min_val: int, max_val: int, max_lines: int, optional: bool=True, debug: bool=False):
        """
        로또 용지의 가로/세로 라인 분포도를 검사합니다.
        
        :param max_lines: 한 라인(열)에 허용하는 최대 공의 개수 (기본 3개 제한)
        :param min_val: 공이 들어있는 최소 라인 수 (0이 아닌 라인 수의 하한선)
        :param max_val: 공이 들어있는 최대 라인 수 (0이 아닌 라인 수의 상한선)
        """
        # 부모 클래스의 min_val, max_val에는 '0이 아닌 라인 수' 범위를 기본 지정
        super().__init__(min_val=min_val, max_val=max_val, optional=optional, debug=debug)
        self.max_lines = max_lines

    @property
    def name(self) -> str:
        return "VLine Range Filter"

    @property
    def description(self) -> str:
        return (
            f"한 줄에 최대 {self.max_lines}개까지만 허용하며, "
            f"공이 들어있는 라인 수가 {self.min_val}~{self.max_val}개 안인지 검사합니다."
        )

    def filter(self, numbers: List[int]) -> bool:
        # 1. 공통 함수를 활용해 세로 라인별 공 개수 배열 획득
        vert_counts = lotto_util.get_vertical_line_counts(numbers)

        # 2. 각 라인별 공 개수의 Max 값 추출
        max_vert = max(vert_counts)
        # [검증 조건 1] 가로나 세로 어느 한 곳이라도 한 줄 몰빵(설정치 초과)이 있으면 탈락
        if max_vert > self.max_lines:
            if self.debug:
                print("False :", self.__class__.__name__)
            return False

        # 3. 0이 아닌 (공이 1개 이상 들어있는) 라인 수 계산
        active_vert_lines = sum(1 for count in vert_counts if count > 0)

        # [검증 조건 2] 0이 아닌 라인 수가 부모 범위(min_val ~ max_val) 안에 들어오는지 체크
        if self.min_val <= active_vert_lines <= self.max_val:
            return True
        if self.debug:
            print("False :", self.__class__.__name__)
        return False
