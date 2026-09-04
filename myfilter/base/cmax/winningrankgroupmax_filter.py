from typing import List

import numpy as np
import pandas as pd

import util.lotto_util as lotto_util
from myfilter.lotto_filter import AMaxFilter
from vo.number_vo import NumberVO


"""
출현 빈도수 별 그룹을 생성하는 클래스입니다.
1. groupA, groupB, groupC, panelA, panelB, panelC 리스트에 각 각 max개 이상 있으면 차단
2. groupB에 0개 이면 차단, 즉 groupA, groupC에 6개란 뜻
"""
class WinningRankGroupMaxFilter(AMaxFilter):
    def __init__(self, numberVos: list[NumberVO], max_val: int=4, optional: bool=True, debug: bool=False):
        super().__init__(max_val=max_val, optional=optional, debug=debug)

        self.groupA: list[int] = []
        self.groupB: list[int] = []
        self.groupC: list[int] = []
        self.panelA: list[int] = []
        self.panelB: list[int] = []
        self.panelC: list[int] = []

        # [데이터프레임 빌드] 
        demo_data = {
            'num1': [],
            'num2': [],
            'num3': [],
            'num4': [],
            'num5': [],
            'num6': [],
        }
        for numbervo in numberVos:
            nums = numbervo.numbers
            for i in range(0,6):
                cname = f"num{i+1}"
                demo_data[cname].append(nums[i])
        
        df = pd.DataFrame(demo_data)
    
        """
        출현 횟수별 통계 구하기 -------------------------------------------------------
        데이터프레임의 번호 영역만 추출한 뒤 .flatten()을 통해 일렬로 쭉 펼칩니다.
        """
        # [2단계: 6개 당첨 번호 열 전체를 하나로 결합하여 빈도수 계산]
        # 데이터프레임의 번호 영역만 추출한 뒤 .flatten()을 통해 일렬로 쭉 펼칩니다.
        all_drawn_numbers = df[['num1', 'num2', 'num3', 'num4', 'num5', 'num6']].values.flatten()

        # 1부터 45까지 각 숫자의 출현 빈도를 카운트하여 딕셔너리에 담기
        # np.bincount는 인덱스 번호에 해당하는 숫자의 등장 횟수를 초고속으로 세어줍니다.
        counts = np.bincount(all_drawn_numbers, minlength=46)
        
        # 0번 인덱스를 제외하고 1번~45번까지의 빈도 맵 완성
        lotto_frequency_map = {num: int(counts[num]) for num in range(1, 46)}

        # [3단계: 출현 횟수(Value) 기준 내림차순 역순 정렬]
        # x은 딕셔너리의 '출현 횟수'를 의미하며, reverse=True를 통해 큰 숫자부터 정렬합니다.
        # [전제 조건] 앞서 생성된 sorted_ranks 데이터 예시 (총 45개 튜플 리스트)
        # sorted_ranks = [(34, 4), (11, 3), (22, 3), ... (9, 0)]
        sorted_ranks = sorted(lotto_frequency_map.items(), key=lambda x: x, reverse=True)

        # 1. 🔄 정렬된 데이터에서 '로또 번호'만 순서대로 추출하여 1차원 리스트로 평탄화
        # (출현 횟수를 제외하고 순수한 숫자들만 순위대로 정렬된 리스트를 만듭니다)
        pure_ranked_numbers = [item[0] for item in sorted_ranks]

        # 2. ✂️ [핵심] 리스트 슬라이싱을 이용해 15개 단위로 쪼개기
        # 0번부터 14번 인덱스까지 (상위 1~15위)
        self.groupA = pure_ranked_numbers[0:15]  

        # 15번부터 29번 인덱스까지 (중위 16~30위)
        self.groupB = pure_ranked_numbers[15:30] 

        # 30번부터 44번 인덱스까지 (하위 31~45위)
        self.groupC = pure_ranked_numbers[30:45] 

        # 1. ✂️ 각 리스트를 5개씩 3등분 (슬라이싱)
        a1, a2, a3 = self.groupA[0:5], self.groupA[5:10], self.groupA[10:15]
        b1, b2, b3 = self.groupB[0:5], self.groupB[5:10], self.groupB[10:15]
        c1, c2, c3 = self.groupC[0:5], self.groupC[5:10], self.groupC[10:15]

        # 2. 🧱 [핵심] 각 그룹의 n번째 묶음들을 결합하여 최종 3개 리스트로 재조립
        # 리스트끼리 + 연산을 하면 원소들이 순서대로 이어붙습니다.
        self.panelA = a1 + b1 + c1  # 각 그룹의 1번째 5개씩 모음 (총 15개)
        self.panelB = a2 + b2 + c2  # 각 그룹의 2번째 5개씩 모음 (총 15개)
        self.panelC = a3 + b3 + c3  # 각 그룹의 3번째 5개씩 모음 (총 15개)


    @property
    def name(self) -> str:
        return "Winning Rank Group Filter"

    @property
    def description(self) -> str:
        return f"각 그룹에 최대 {self.mam_val} 이하인지 검사합니다."

    def filter(self, numbers: List[int]) -> bool:
        match_count = lotto_util.get_match_count_with_target_list(numbers, self.groupA)
        if self.debug:
            if self.max_val < match_count:
                print("False :", self.__class__.__name__)
                return False
            match_count = lotto_util.get_match_count_with_target_list(numbers, self.groupB)
            if self.max_val < match_count:
                print("False :", self.__class__.__name__)
                return False
            match_count = lotto_util.get_match_count_with_target_list(numbers, self.groupC)
            if self.max_val < match_count:
                print("False :", self.__class__.__name__)
                return False
            match_count = lotto_util.get_match_count_with_target_list(numbers, self.panelA)
            if self.max_val < match_count:
                print("False :", self.__class__.__name__)
                return False
            match_count = lotto_util.get_match_count_with_target_list(numbers, self.panelB)
            if self.max_val < match_count:
                print("False :", self.__class__.__name__)
                return False
            match_count = lotto_util.get_match_count_with_target_list(numbers, self.panelC)
            if self.max_val < match_count:
                print("False :", self.__class__.__name__)
                return False
            if 0 < lotto_util.get_match_count_with_target_list(numbers, self.groupB):
                return True
            print("False :", self.__class__.__name__)
            return False
        
        if self.max_val < match_count:
            return False
        match_count = lotto_util.get_match_count_with_target_list(numbers, self.groupB)
        if self.max_val < match_count:
            return False
        match_count = lotto_util.get_match_count_with_target_list(numbers, self.groupC)
        if self.max_val < match_count:
            return False
        match_count = lotto_util.get_match_count_with_target_list(numbers, self.panelA)
        if self.max_val < match_count:
            return False
        match_count = lotto_util.get_match_count_with_target_list(numbers, self.panelB)
        if self.max_val < match_count:
            return False
        match_count = lotto_util.get_match_count_with_target_list(numbers, self.panelC)
        if self.max_val < match_count:
            return False
        return 0 < lotto_util.get_match_count_with_target_list(numbers, self.groupB)
