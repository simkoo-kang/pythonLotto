from typing import List
from collections import Counter

from myfilter.lotto_filter import ARangeFilter


class SameEndingRangeFilter(ARangeFilter):
    def __init__(self, min_val: int = 1, max_val: int = 2, debug: bool=False):
        """
        로또 번호의 1의 자리 숫자(끝수) 중 '가장 많이 중복된 개수'가 
        지정한 범위(min_val ~ max_val) 안인지 검사합니다.
        
        - 기본값 (2 ~ 3): 2동끝수(2개 중복) 또는 3동끝수(3개 중복)가 포함된 조합만 통과
        """
        # 부모 클래스의 생성자에 '최대 끝수 중복 개수'의 유효 범위 전달
        super().__init__(min_val=min_val, max_val=max_val, debug=debug)

    @property
    def name(self) -> str:
        return "Same Ending Filter"

    @property
    def description(self) -> str:
        return f"로또 번호의 동일 끝수(1의 자리) 최대 중복 개수가 {self.min_val} ~ {self.max_val}개 사이인지 검사합니다."

    def filter(self, numbers: List[int]) -> bool:
        # 2. 이 필터의 핵심 결과값 계산 (1의 자리 숫자들만 추출)
        # 예: -> [4, 4, 3, 2, 4, 1]
        endings = [num % 10 for num in numbers]
        
        # 3. collections.Counter를 사용해 각 끝수별 등장 횟수를 셉니다.
        # 예: {4: 3, 3: 1, 2: 1, 1: 1}
        counts = Counter(endings)
        
        # 4. 가장 많이 겹친 끝수의 빈도수(Max 값)를 추출합니다.
        # 예: 4가 3번 나왔으므로 max_overlap_count = 3
        max_overlap_count = max(counts.values())
        
        # 5. 최대 중복 개수가 설정된 최소/최대 범위 안인지 검사
        if self.min_val <= max_overlap_count <= self.max_val:
            return True
        if self.debug:
            print("False :", self.__class__.__name__)
        return False
