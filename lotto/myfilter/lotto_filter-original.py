from abc import ABC, abstractmethod
from collections import Counter

from typing import List

import util.lotto_util as lotto_util

# 1. 인터페이스
class LottoFilter(ABC):
    @property
    @abstractmethod
    def name(self) -> str: pass

    @property
    @abstractmethod
    def description(self) -> str: pass

    @abstractmethod
    def filter(self, numbers: List[int]) -> bool: pass


# 2.1. 추상 클래스 (공통 값 설정 및 유틸리티 함수 구현)
class ARangeFilter(LottoFilter):
    def __init__(self, min_val: int, max_val: int):
        self.min_val = min_val
        self.max_val = max_val


# 2.2. 추상 클래스 (공통 값 설정 및 유틸리티 함수 구현)
class ABooleanFilter(LottoFilter):
    def __init__(self, bool_val: bool):
        self.bool_val = bool_val


# 2.3. 추상 클래스 (공통 값 설정 및 유틸리티 함수 구현)
class AMaxFilter(LottoFilter):
    def __init__(self, max_val: int):
        self.max_val = max_val


# 2.4. 추상 클래스 (공통 값 설정 및 유틸리티 함수 구현)
class AMinFilter(LottoFilter):
    def __init__(self, min_val: int):
        self.min_val = min_val


# 3.1. 구체 클래스 (부모의 생성자를 호출하도록 super() 적용)
class ACMinFilter(AMinFilter):
    def __init__(self, min_val: int = 6):
        # super()를 통해 부모 클래스의 생성자에 min, max 범위를 전달합니다.
        super().__init__(min_val=min_val)

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
        return self.min_val <= ac_value


# 3.2. 예시: 총합 범위를 거르는 필터 추가 시
class SumRangeFilter(ARangeFilter):
    def __init__(self, min_val: int = 100, max_val: int = 175):
        # 총합 결과값이 100 ~ 175 사이여야 함을 부모에게 전달
        super().__init__(min_val=min_val, max_val=max_val)

    @property
    def name(self) -> str: return "Sum Range Filter"

    @property
    def description(self) -> str: return f"총합이 {self.min_val}~{self.max_val} 안인지 검사"

    def filter(self, numbers: List[int]) -> bool:
        # 이 필터의 결과값은 '총합'
        total_sum = sum(numbers) 
        
        # 부모의 min_val, max_val과 비교
        return self.min_val <= total_sum <= self.max_val


# 3.3. 추가 필터 예시: 짝수 개수
class EvenRangeFilter(ARangeFilter):
    def __init__(self, min_val: int = 2, max_val: int = 4):
        super().__init__(min_val=min_val, max_val=max_val)

    @property
    def name(self) -> str: return "Even Range Filter"

    @property
    def description(self) -> str: return f"짝수 개수가 {self.min_val}~{self.max_val}인지 검사"

    def filter(self, numbers: List[int]) -> bool:
        # 이 필터의 결과값은 '짝수 개수'
        even_count = sum(1 for n in numbers if n % 2 == 0)
        
        # 부모의 min_val, max_val과 비교
        return self.min_val <= even_count <= self.max_val


# 3.4. 추가 필터 예시: 높은 수 개수
class HighRangeFilter(ARangeFilter):
    def __init__(self, min_val: int = 2, max_val: int = 4):
        super().__init__(min_val=min_val, max_val=max_val)

    @property
    def name(self) -> str: return "High Range Filter"

    @property
    def description(self) -> str: return f"높은 수가 {self.min_val}~{self.max_val}인지 검사"

    def filter(self, numbers: List[int]) -> bool:
        # 이 필터의 결과값은 '높은 수'
        high_count = sum(1 for n in numbers if n > 22)
        
        # 부모의 min_val, max_val과 비교
        return self.min_val <= high_count <= self.max_val


# 3.5. 추가 필터 예시: 연속된 쌍 개수 ([1,2], [3,4] 등) 범위
class ConsecutivePairsMaxFilter(AMaxFilter):
    def __init__(self, max_val: int = 1):
        super().__init__(max_val=max_val)

    @property
    def name(self) -> str: return "Consecutive Pairs Max Filter"

    @property
    def description(self) -> str: return f"연속된 쌍의 개수가 {self.max_val} 이하인지 검사"

    def filter(self, numbers: List[int]) -> bool:
        # 이 필터의 결과값은 '연속된 쌍의 개수'
        consecutive_count = lotto_util.count_consecutive_pairs(numbers)
        
        # 부모의 max_val과 비교
        return self.max_val >= consecutive_count


# 3.6. 추가 필터 예시: 특정 숫자 배열과의 일치 개수
class MatchCountRangeFilter(ARangeFilter):
    def __init__(self, match_list: List[int], min_val: int = 0, max_val: int = 1):
        super().__init__(min_val=min_val, max_val=max_val)
        self.match_list = match_list

    @property
    def name(self) -> str: return "Match Count Range Filter"

    @property
    def description(self) -> str: return f"특정 숫자들과 중복되는 수가 {self.min_val}~{self.max_val}인지 검사"

    def filter(self, numbers: List[int]) -> bool:
        match_count = lotto_util.get_match_count_with_target_list(numbers, self.match_list)
        return self.min_val <= match_count <= self.max_val


# 3.7. 추가 필터 예시: 가로 라인 분포도
class HLineRangeFilter(ARangeFilter):
    def __init__(self, min_val: int, max_val: int, max_lines: int):
        """
        로또 용지의 가로/세로 라인 분포도를 검사합니다.
        
        :param max_lines: 한 라인(줄)에 허용하는 최대 공의 개수 (기본 3개 제한)
        :param min_val: 공이 들어있는 최소 라인 수 (0이 아닌 라인 수의 하한선)
        :param max_val: 공이 들어있는 최대 라인 수 (0이 아닌 라인 수의 상한선)
        """
        # 부모 클래스의 min_val, max_val에는 '0이 아닌 라인 수' 범위를 기본 지정
        super().__init__(min_val=min_val, max_val=max_val)
        self.max_lines = max_lines

    @property
    def name(self) -> str:
        return "HLine Range Filter"

    @property
    def description(self) -> str:
        return (
            f"한 줄에 최대 {self.max_lines}개까지만 허용하며, "
            f"공이 들어있는 라인 수가 {self.min_val}~{self.max_val}개 안인지 검사합니다."
        )

    def filter(self, numbers: List[int]) -> bool:
        # 1. 공통 함수를 활용해 가로 라인별 공 개수 배열 획득
        horiz_counts = lotto_util.get_horizontal_line_counts(numbers)

        # 2. 각 라인별 공 개수의 Max 값 추출
        max_horiz = max(horiz_counts)
        # [검증 조건 1] 가로나 세로 어느 한 곳이라도 한 줄 몰빵(설정치 초과)이 있으면 탈락
        if max_horiz > self.max_lines:
            return False

        # 3. 0이 아닌 (공이 1개 이상 들어있는) 라인 수 계산
        horiz_lines = sum(1 for count in horiz_counts if count > 0)

        # [검증 조건 2] 0이 아닌 라인 수가 부모 범위(min_val ~ max_val) 안에 들어오는지 체크
        return self.min_val <= horiz_lines <= self.max_val


# 3.8. 추가 필터 예시: 세로 라인 분포도
class VLineRangeFilter(ARangeFilter):
    def __init__(self,  min_val: int, max_val: int, max_lines: int):
        """
        로또 용지의 가로/세로 라인 분포도를 검사합니다.
        
        :param max_lines: 한 라인(열)에 허용하는 최대 공의 개수 (기본 3개 제한)
        :param min_val: 공이 들어있는 최소 라인 수 (0이 아닌 라인 수의 하한선)
        :param max_val: 공이 들어있는 최대 라인 수 (0이 아닌 라인 수의 상한선)
        """
        # 부모 클래스의 min_val, max_val에는 '0이 아닌 라인 수' 범위를 기본 지정
        super().__init__(min_val=min_val, max_val=max_val)
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
            return False

        # 3. 0이 아닌 (공이 1개 이상 들어있는) 라인 수 계산
        active_vert_lines = sum(1 for count in vert_counts if count > 0)

        # [검증 조건 2] 0이 아닌 라인 수가 부모 범위(min_val ~ max_val) 안에 들어오는지 체크
        return self.min_val <= active_vert_lines <= self.max_val


# 3.9. 추가 필터 예시: 등간격 패턴 존재 여부
class EqualIntervalBooleanFilter(ABooleanFilter):
    def __init__(self, bool_val: bool = False, interval_size: int = 2):
        super().__init__(bool_val=bool_val)
        self.interval_size = interval_size

    @property
    def name(self) -> str: return "Equal Interval Boolean Filter"

    @property
    def description(self) -> str: return f"등간격 패턴의 개수가 있는지 검사"

    def filter(self, numbers: List[int]) -> bool:
        return self.bool_val == lotto_util.has_equal_interval_pattern(numbers, self.interval_size)


# 3.10. 추가 필터 예시: 징검다리 패턴 존재 여부
class SteppingStoneBooleanFilter(ABooleanFilter):
    def __init__(self, bool_val: bool = False):
        super().__init__(bool_val=bool_val)

    @property
    def name(self) -> str: return "Stepping Stone Pattern Filter"

    @property
    def description(self) -> str: return f"징금다리 패턴이 있는 지 검사"

    def filter(self, numbers: List[int]) -> bool:
        return self.bool_val == lotto_util.has_stepping_stone_pattern(numbers)


# 3.11. 추가 필터 예시: 첫번째 숫자 최대 값 범위
class FirstNumberMaxFilter(AMaxFilter):
    def __init__(self, max_val: int = 15):
        super().__init__(max_val=max_val)

    @property
    def name(self) -> str: return "First Number Filter"

    @property
    def description(self) -> str: return f"첫 번째 번호가 {self.max_val}보다 작은지 검사"

    def filter(self, numbers: List[int]) -> bool:
        return numbers[0] < self.max_val


# 3.12. 추가 필터 예시: 마지막 숫자 최대 값 범위
class LastNumberMinFilter(AMinFilter):
    def __init__(self, min_val: int = 31):
        """
        로또 번호 중 가장 큰 마지막(6번째) 숫자가 특정 범위(min_val ~ max_val) 안인지 검사합니다.
        - 기본값: 마지막 번호가 최소 31 이상인 경우만 통과 시킵니다.
        """
        # 부모 클래스의 생성자에 '마지막 번호'인 min_val를 전달
        super().__init__(min_val=min_val)

    @property
    def name(self) -> str:
        return "Last Number Filter"

    @property
    def description(self) -> str:
        return f"오름차순 정렬 후 마지막 번호가 최소 {self.min_val} 이상인지 검사합니다."

    def filter(self, numbers: List[int]) -> bool:
        # 3. 결과값(마지막 공 번호)이 설정된 최소값보다 큰지 검사
        return self.min_val < numbers[5]


class SameEndingRangeFilter(ARangeFilter):
    def __init__(self, min_val: int = 1, max_val: int = 2):
        """
        로또 번호의 1의 자리 숫자(끝수) 중 '가장 많이 중복된 개수'가 
        지정한 범위(min_val ~ max_val) 안인지 검사합니다.
        
        - 기본값 (2 ~ 3): 2동끝수(2개 중복) 또는 3동끝수(3개 중복)가 포함된 조합만 통과
        """
        # 부모 클래스의 생성자에 '최대 끝수 중복 개수'의 유효 범위 전달
        super().__init__(min_val=min_val, max_val=max_val)

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
        return self.min_val <= max_overlap_count <= self.max_val

