from typing import List

from lotto.myfilter.lotto_filter import LottoFilter
from lotto.vo.number_vo import NumberVO

class LottoFilterManager:
    def __init__(self):
        """필터들을 등록하고 관리하는 관리자 클래스입니다."""
        self._filters: List[LottoFilter] = []

    def add_filter(self, lotto_filter: LottoFilter) -> "LottoFilterManager":
        """체인 패턴을 지원하도록 필터를 매니저에 추가하고 자기 자신을 반환합니다."""
        self._filters.append(lotto_filter)
        return self

    def add_filters(self, lotto_filters: List[LottoFilter]) -> "LottoFilterManager":
        """여러 개의 필터를 한 번에 추가합니다."""
        self._filters.extend(lotto_filters)
        return self

    def clear_filters(self) -> None:
        """등록된 모든 필터를 초기화합니다."""
        self._filters.clear()

    def filter_combination(self, numbers: List[int]) -> bool:
        """
        [핵심 로직] 하나의 로또 조합이 등록된 '모든 필터'를 통과하는지 검사합니다.
        단 하나라도 통과하지 못하면(False) 즉시 탈락(Short-circuit)시킵니다.
        """
        if not self._filters:
            return True  # 등록된 필터가 없으면 무조건 패스
            
        # 모든 필터의 filter() 결과가 True여야 최종 통과
        return all(lotto_filter.filter(numbers) for lotto_filter in self._filters)

    def filter_bulk_combinations(self, bulk_numbers: List[NumberVO]) -> List[NumberVO]:
        """
        대량의 로또 번호 조합 리스트를 받아서 
        모든 필터 조건을 통과한 청정 조합들만 골라내어 반환합니다.
        """
        return [nums for nums in bulk_numbers if self.filter_combination(nums.numbers)]
    