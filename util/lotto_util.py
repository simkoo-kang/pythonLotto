import itertools
from typing import List

import numpy as np

from myfilter.lotto_filter import LottoFilter
from vo.number_vo import NumberVO


# nums 의 이웃수 목록
def get_neigbors(nums: list[int]):
    ns = []
    for n in nums:
        ln = n - 1
        rn = n + 1
        if ln<1:
            ln += 45
        if 45<rn:
            rn -= 45
        ns.append(ln)
        ns.append(rn)
    return sorted(set(ns)) # or return sorted(list(set(ns)))


def make_full_lotto_numbers(numbers: List[int], filters: List[LottoFilter]=None, cache: list[str]=None) -> List[NumberVO]:
    """
    1~45 범위의 숫자 중 6개를 뽑아 모든 조합을 생성하고, 필터를 적용하여 결과를 반환합니다.
    :param numbers: 1~45 범위의 숫자 리스트
    :param filters: 적용할 필터 리스트
    :param cache: 캐시된 결과 리스트
    :return: 필터를 통과한 로또 번호 조합 리스트
    """
    combinations = itertools.combinations(numbers, 6)
    result = []
    if filters is None:
        if cache is  None:
            for combo in combinations:
                numbervo = NumberVO(round=None, numbers=list(combo), bonus=None)
                result.append(numbervo)
        else:
            for combo in combinations:
                numbervo = NumberVO(round=None, numbers=list(combo), bonus=None)
                if numbervo.toString() not in cache:
                    result.append(numbervo)
    else:
        if cache is None:
            for combo in combinations:
                numbervo = NumberVO(round=None, numbers=list(combo), bonus=None)
                if all(f.filter(numbervo) for f in filters):
                    result.append(numbervo)
        else:
            for combo in combinations:
                numbervo = NumberVO(round=None, numbers=list(combo), bonus=None)
                if numbervo.toString() not in cache and all(f.filter(numbervo) for f in filters):
                    result.append(numbervo)

    return result


def generate_second_prize_combinations(main_numbers: List[int], bonus_number: int) -> List[str]:
    """
    메인 번호 6개 중 5개와 보너스 번호를 조합하여
    모든 2등 가능 번호 조합을 '01-02-03-04-05-07' 형태의 문자열 리스트로 반환합니다.
    """
    if len(main_numbers) != 6:
        raise ValueError("메인 번호는 정확히 6개여야 합니다.")
        
    result_list = []

    formatted_str = "-".join(f"{num:02d}" for num in main_numbers)
    result_list.append(formatted_str)  # 1등 조합도 포함

    # 1. 메인 번호 6개 중에서 5개를 뽑는 모든 조합 구하기 (6C5 = 6가지 경우)
    for main_five in itertools.combinations(main_numbers, 5):
        # 2. 뽑은 5개에 보너스 번호를 추가하여 6개짜리 2등 조합 완성
        combination_set = list(main_five) + [bonus_number]
        
        # 3. 로또 규격에 맞게 숫자를 오름차순으로 정렬
        sorted_combination = sorted(combination_set)
        
        # 4. 각 숫자를 두 자리 문자열(예: 3 -> '03', 12 -> '12')로 포맷팅 후 하이픈(-) 연결
        # f"{num:02d}" 문법이 숫자를 두 자리 문자로 채워줍니다.
        formatted_str = "-".join(f"{num:02d}" for num in sorted_combination)
        
        result_list.append(formatted_str)
        
    # 시각적 확인을 위해 정렬하여 반환
    return sorted(result_list)


#==================== AC 계산 ====================
def calculate_ac(numbers: List[int]) -> int:
    """숫자 간 차이의 종류 수를 기준으로 AC 값을 계산합니다.

    로또 번호는 6개이므로, 모든 조합의 차이를 구한 뒤 중복을 제거한 결과를
    기준값과 비교해 AC 수준을 판단합니다.
    """
    sorted_nums = sorted(numbers)
    combinations = itertools.combinations(sorted_nums, 2)
    differences = {abs(b - a) for a, b in combinations}
    return len(differences) - 5


def get_horizontal_line_counts(numbers: List[int], max_lines: int = 7) -> List[int]:
    """
    [공통 함수] 각 가로 라인(1~7번줄)별로 포함된 번호의 개수를 리스트로 반환합니다.
    반환 리스트 인덱스 0은 1번 가로줄(1~7), 인덱스 6은 7번 가로줄(43~45)을 의미합니다.
    """
    # 7개의 가로줄 카운터 초기화
    counts = [0] * max_lines
    for num in numbers:
        # 1~45 숫자를 max_lines개씩 묶어 행 인덱스 계산
        row_idx = (num - 1) // max_lines
        counts[row_idx] += 1
    return counts


def get_vertical_line_counts(numbers: List[int]) -> List[int]:
    """
    [공통 함수] 각 세로 라인(1~7번열)별로 포함된 번호의 개수를 리스트로 반환합니다.
    인덱스 0은 1번 세로줄(1,8,15...), 인덱스 6은 7번 세로줄(7,14,21...)을 의미합니다.
    """
    # 7개의 세로줄 카운터 초기화
    counts = [0] * 7
    for num in numbers:
        # 7로 나눈 나머지를 이용해 열 인덱스 계산
        col_idx = (num - 1) % 7
        counts[col_idx] += 1
    return counts


def count_consecutive_pairs(numbers: List[int]) -> bool:
    """
    6개 로또 번호 중 연속된 숫자(연번) 쌍의 총 개수를 반환합니다.
    예:  -> 1-2(연번), 2-3(연번)이므로 총 2개 쌍 반환
    예:  -> 5-6(연번)이므로 총 1개 쌍 반환
    """
    if len(numbers) != 6:
        raise ValueError("로또 번호는 정확히 6개여야 합니다.")

    # 1. 번호를 크기순으로 오름차순 정렬
    sorted_nums = sorted(numbers)
    pair_count = 0
    
    # 2. 루프를 돌며 바로 뒤의 숫자와의 차이가 1인지 확인
    for i in range(len(sorted_nums) - 1):
        if sorted_nums[i+1] - sorted_nums[i] == 1:
            pair_count += 1
            
    return pair_count


# count_consecutive_pairs 함수는 연속된 숫자 쌍의 개수에 포함된다.
# def has_consecutive_group_of_size(numbers: List[int], size: int = 3) -> bool:
#     """
#     [기능 1] N개 이상 연속된 숫자가 존재하는지 검사합니다.
#     예: size=3 일 때,  -> True (1,2,3 연속)
#     """
#     sorted_nums = sorted(numbers)
#     consecutive_count = 1
    
#     for i in range(len(sorted_nums) - 1):
#         if sorted_nums[i+1] - sorted_nums[i] == 1:
#             consecutive_count += 1
#             if consecutive_count >= size:
#                 return True
#         else:
#             consecutive_count = 1  # 연속이 끊기면 초기화
            
#     return False


def has_equal_interval_pattern(numbers: List[int], interval_size: int = 0) -> bool:
    """
    6개 로또 번호 중 정렬했을 때 지정된 간격(기본값 2)으로 
    연속된 3개의 숫자 그룹(예: 1-3-5, 14-16-18)이 존재하는지 검사합니다.
    """
    if len(numbers) != 6:
        raise ValueError("로또 번호는 정확히 6개여야 합니다.")

    # 1. 번호를 크기순으로 오름차순 정렬
    sorted_nums = sorted(numbers)

    if interval_size < 2:
        # 2. 연속된 3개의 숫자 묶음을 순차적으로 검사 (6개 중 3개 묶음은 총 4개 그룹 가능)
        #    모든 interval_size를 검사하여 등간격 패턴이 존재하는지 확인
        for i in range(len(sorted_nums) - 2):
            a = sorted_nums[i]
            b = sorted_nums[i+1]
            c = sorted_nums[i+2]
            
            # 앞뒤 숫자 간의 차이가 모두 입력받은 간격(interval_size)과 일치하는지 확인
            if (b - a == c - b):
                # print(f"🎯 패턴 발견: {a}-{b}-{c} (간격: {b-a})")
                return True

        return False
    
    # 2. 연속된 3개의 숫자 묶음을 순차적으로 검사 (6개 중 3개 묶음은 총 4개 그룹 가능)
    for i in range(len(sorted_nums) - 2):
        a = sorted_nums[i]
        b = sorted_nums[i+1]
        c = sorted_nums[i+2]
        
        # 앞뒤 숫자 간의 차이가 모두 입력받은 간격(interval_size)과 일치하는지 확인
        if (b - a == interval_size) and (c - b == interval_size):
            # print(f"🎯 패턴 발견: {a}-{b}-{c} (간격: {interval_size})")
            return True
            
    return False


def has_stepping_stone_pattern(numbers: List[int]) -> bool:
    """
    [기능 2] '1,2,4' 또는 '1,3,4' 처럼 3개 숫자가 징검다리 형태로 붙어있는지 검사합니다.
    (정렬했을 때 간격이 [1, 2]이거나 [2, 1]인 연속된 3개의 숫자 그룹이 있는지 확인)
    """
    sorted_nums = sorted(numbers)
    
    # 6개 번호 중 연속된 3개 숫자의 조합을 순차적으로 검사 (총 4개 그룹 가능)
    for i in range(len(sorted_nums) - 2):
        a, b, c = sorted_nums[i], sorted_nums[i+1], sorted_nums[i+2]
        diff1 = b - a
        diff2 = c - b
        
        # [1, 2] 패턴 (예: 1, 2, 4) 또는 [2, 1] 패턴 (예: 1, 3, 4)
        if (diff1 == 1 and diff2 == 2) or (diff1 == 2 and diff2 == 1):
            return True
            
    return False


def get_match_count_with_target_list(numbers: List[int], target_list: List[int]) -> int:
    """
    [기능 3] 사용자가 지정한 특정 숫자 배열(int[])과 몇 개나 겹치는지 개수를 반환합니다.
    (특정 예상수 포함 개수 체크나, 제외수/고정수 매칭에 사용 가능)
    """
    # 교집합 연산의 속도를 위해 set으로 변환하여 매칭 개수 계산
    return len(set(numbers) & set(target_list))


def get_section_numbers(numbers: List[int], section: int) -> List[int]:
    """
    [기능 4] 로또 번호를 5구간 또는 9구간으로 나누어
    특정 구간에 속하는 번호들을 리스트로 반환합니다.
    """
    counts = [0] * 9  # 9구간 카운터 초기화
    if section not in [5, 9]:
        raise ValueError("구간은 5 또는 9만 가능합니다.")

    for num in numbers:
        counts[(num - 1) // section] += 1

    return counts


# ==================== 실행 및 검증 ====================
if __name__ == "__main__":
    # 요청하신 예시 데이터 입력
    lotto_main = [1, 2, 3, 4, 5, 6]
    lotto_bonus = 7
    
    # 2등 번호 조합 생성 함수 호출
    second_prize_list = generate_second_prize_combinations(lotto_main, lotto_bonus)
    
    # 결과 출력
    print(f"생성된 2등 조합 개수: {len(second_prize_list)}개")
    print("--- 조합 리스트 ---")
    for combo in second_prize_list:
        print(combo)

    print(np.bincount(np.arange(5)))
    a = [1,3,5,7,2,6,8,1,2,3,6]
    print(np.bincount(a, minlength=1))

    # range(3, 10, 3)은 정확히 [3, 6, 9] 리스트를 의미합니다.
    for i in range(10):
        if i in range(3, 10, 3):
            print(f"{i}는 3, 6, 9 중 하나입니다.")

    print(len(set(lotto_main) & set(a)))  # 교집합 개수 확인
