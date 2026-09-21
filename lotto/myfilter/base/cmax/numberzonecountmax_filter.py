from typing import List

from lotto.myfilter.lotto_filter import AMaxFilter


"""
숫자 영역 카운트 범위 필터 ---
로또 번호의 번호대별 수량(개수)을 체크하여 특정 번호대에 숫자가 과도하게 몰리거나
전멸하는 조합을 걸러내는 필터 클래스입니다.
일반적으로 로또는 1번대(1~10), 10번대(11~20), 20번대(21~30), 30번대(31~40), 40번대(41~45)의 5개 번호대로 나뉩니다.
한 번호대에 숫자가 4개 이상 몰리거나, 번호대 3개 이상이 동시에 전멸(멸)하는 조합을 필터링하도록 설계했습니다.
"""
class NumberZoneCountMaxFilter(AMaxFilter):
    def __init__(self, max_val: int=3, max_empty_zones: int=2, optional: bool=True, debug: bool=False):
        """_summary_
        1번대, 10번대, 20번대, 30번대, 40번대의 수량을 체크하고,
        0이면 '0', 아니면 '1'로 변환된 패턴 문자열을 분석하여 필터링합니다.

        Args:
            max_val (int, optional): _description_. Defaults to 3.
            max_empty_zones (int, optional): _description_. Defaults to 2.
            optional (bool, optional): _description_. Defaults to True.
            debug (bool, optional): _description_. Defaults to False.
        """
        super().__init__(max_val=max_val, optional=optional, debug=debug)
        # 전멸(0개) 허용할 최대 번호대 개수 (기본값: 3개 이상 멸하면 탈락)
        self.max_empty_zones = max_empty_zones

    @property
    def name(self) -> str:
        return "Number Zone Count Max Filter"

    @property
    def description(self) -> str:
        return (
            f"한 줄에 최대 {self.max_val}개까지만 허용하며, "
            f"없는 번호대가 최대 {self.max_empty_zones}개까지 허용됩니다."
        )

    def filter(self, numbers: List[int]) -> bool:
        # 5개 번호대 빈도수 배열 초기화 
        # [1번대, 10번대, 20번대, 30번대, 40번대]
        zone_counts = [0] * 5

        for n in numbers:
            if 1 <= n <= 10:
                zone_counts[0] += 1
            elif 11 <= n <= 20:
                zone_counts[1] += 1
            elif 21 <= n <= 30:
                zone_counts[2] += 1
            elif 31 <= n <= 40:
                zone_counts[3] += 1
            elif 41 <= n <= 45:
                zone_counts[4] += 1

        # 1. 특정 번호대 과몰입 체크 (예: 한 번호대에 4개 이상 몰림)
        if max(zone_counts) > self.max_val:
            if self.debug:
                print("False :", self.__class__.__name__)
            return False

        # 2. 전멸(0) 또는 출현(1) 문자열 변환 및 수량 체크
        # 요청하셨던 '0이면 0, 아니면 1' 로직과 'count()' 메서드가 결합되는 구간입니다.
        pattern_str = "".join(['0' if x == 0 else '1' for x in zone_counts])
        
        # 문자열에서 '0'(멸)의 개수를 카운트
        empty_count = pattern_str.count('0')

        # 번호대 멸 개수가 기준을 초과하면 탈락 (예: 3개 번호대가 멸하면 탈락)
        if empty_count > self.max_empty_zones:
            if self.debug:
                print("False :", self.__class__.__name__)
            return False

        return True
