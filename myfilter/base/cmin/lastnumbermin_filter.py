from typing import List

from myfilter.lotto_filter import AMinFilter


# 3.12. 추가 필터 예시: 마지막 숫자 최대 값 범위
class LastNumberMinFilter(AMinFilter):
    def __init__(self, min_val: int = 31, optional=True, debug: bool=False):
        """
        로또 번호 중 가장 큰 마지막(6번째) 숫자가 특정 범위(min_val ~ max_val) 안인지 검사합니다.
        - 기본값: 마지막 번호가 최소 31 이상인 경우만 통과 시킵니다.
        """
        # 부모 클래스의 생성자에 '마지막 번호'인 min_val를 전달
        super().__init__(min_val=min_val, optional=optional, debug=debug)

    @property
    def name(self) -> str:
        return "Last Number Filter"

    @property
    def description(self) -> str:
        return f"오름차순 정렬 후 마지막 번호가 최소 {self.min_val} 이상인지 검사합니다."

    def filter(self, numbers: List[int]) -> bool:
        # 3. 결과값(마지막 공 번호)이 설정된 최소값보다 큰지 검사
        if self.min_val < numbers[5]:
            return True
        if self.debug:
            print("False :", self.__class__.__name__)
        return False
