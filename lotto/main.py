
from lotto_filter import ACRangeFilter, SumRangeFilter
from lotto_filter_manager import LottoFilterManager


# ==================== 테스트 검증 실행 ====================
if __name__ == "__main__":
    filter_tool = ACRangeFilter(min_val=7, max_val=10)

    # 테스트 케이스 1: 3개 연속 숫자 검사
    nums_consecutive = [1, 24, 25, 26, 33, 42]
    print(f"[{nums_consecutive}] 3개 연속 숫자 존재 여부:", 
          filter_tool.has_consecutive_group_of_size(nums_consecutive, 3)) # True

    # 테스트 케이스 2: 징검다리 패턴 (1,2,4 또는 1,3,4 타입) 검사
    nums_stone1 =  [14, 15, 17] # 14, 15, 17 (간격 1, 2)
    nums_stone2 = [22, 24, 25]  # 22, 24, 25 (간격 2, 1)
    print(f"[{nums_stone1}] 징검다리 패턴 존재 여부:", filter_tool.has_stepping_stone_pattern(nums_stone1)) # True
    print(f"[{nums_stone2}] 징검다리 패턴 존재 여부:", filter_tool.has_stepping_stone_pattern(nums_stone2)) # True

    # 테스트 케이스 3: 특정 숫자 배열과 매칭되는 개수 구하기 (예: 내가 지정한 고정수나 제외수 목록)
    my_numbers = [5, 7, 8, 23, 41, 44]
    target_list = [5, 12, 23, 34, 41] # 비교할 특정 int[]
    match_count = filter_tool.get_match_count_with_target_list(my_numbers, target_list)
    print(f"[{my_numbers}]와 특정 배열{target_list}의 일치 개수: {match_count}개") # 3개 일치 (5, 23, 41)

    # 1. 필터 매니저 생성
    manager = LottoFilterManager()

    # 2. 분석 필터 규칙들 조립 및 매니저에 등록
    # - AC 복잡도가 7 ~ 10 사이인 번호만 허용
    # - 6개 번호의 총합이 100 ~ 175 사이인 번호만 허용 (통계상 가장 많이 나오는 대역)
    manager.add_filter(ACRangeFilter(min_val=7, max_val=10)) \
           .add_filter(SumRangeFilter(min_val=100, max_val=175))

    print(f"현재 등록된 필터 개수: {len(manager._filters)}개\n")

    # 3. 대량의 가상 로또 번호 조합 리스트 (테스트 데이터)
    bulk_samples = [
        nums_consecutive
        ,  my_numbers
    ]

    print("--- 대량 데이터 개별 검증 시작 ---")
    for idx, nums in enumerate(bulk_samples, 1):
        is_passed = manager.filter_combination(nums)
        print(f"조합 {idx} {nums} -> 최종 필터 통과 여부: {is_passed}")

    print("\n--- 대량 데이터 일괄 필터링 결과 ---")
    # 4. 필터를 통과한 깨끗한 데이터셋만 한 번에 추출
    filtered_results = manager.filter_bulk_combinations(bulk_samples)
    print(f"최종 살아남은 추천 조합 개수: {len(filtered_results)}개")
    print(f"추천 조합 리스트: {filtered_results}")
