import numpy as np

import pandas as pd
import os

from myfilter.base.cmax.trianglemax_filter import TriangleMaxFilter
from util.file_util import FileUtil
import myfilter
from myfilter.base.cmax.winningrankgroupmax_filter import WinningRankGroupMaxFilter
from myfilter.base.cmin.last10min_filter import Last10MinFilter
from myfilter.base.crange.neighborrange_filter import NeighborRangeFilter
from myfilter.lotto_filter import LottoFilter
import myfilter.lotto_filter_manager

from myfilter.base.cmax.fondantmax_filter import FondantMaxFilter
from myfilter.base.crange.compositionrange_filter import CompositionRangeFilter
from myfilter.base.crange.frogrange_filter import FrogRangeFilter
from myfilter.base.crange.matchcountrange_filter import MatchCountRangeFilter
from myfilter.base.crange.multiplerange_filter import MultipleRangeFilter
from myfilter.base.crange.neverrange_filter import NeverRangeFilter
from myfilter.base.crange.pairsddangrange_filter import PairsDdangRangeFilter
from myfilter.base.crange.primerange_filter import PrimeRangeFilter
from myfilter.base.crange.repeatrange_filter import RepeatRangeFilter

# from myfilter.lotto_filter_manager import LottoFilterManager

from myfilter.base.cbool.equalintervalBoolean_filter import EqualIntervalBooleanFilter
from myfilter.base.cbool.steppingstoneboolean_filter import SteppingStoneBooleanFilter  

from myfilter.base.cmax.consecutivepairsmax_filter import ConsecutivePairsMaxFilter
from myfilter.base.cmax.firstnumbermax_filter import FirstNumberMaxFilter
from myfilter.base.cmax.numberzonecountmax_filter import NumberZoneCountMaxFilter

from myfilter.base.cmin.acmin_filter import ACMinFilter
from myfilter.base.cmin.lastnumbermin_filter import LastNumberMinFilter

from myfilter.base.crange.cornercountrange_filter import CornerCountRangeFilter
from myfilter.base.crange.evenrange_filter import EvenRangeFilter
from myfilter.base.crange.highrange_filter import HighRangeFilter
from myfilter.base.crange.hlinerange_filter import HLineRangeFilter
from myfilter.base.crange.sameendingrange_filter import SameEndingRangeFilter
from myfilter.base.crange.sectionrange_filter import SectionRangeFilter
from myfilter.base.crange.sumendingrange_filter import SumEndingRangeFilter
from myfilter.base.crange.sumrange_filter import SumRangeFilter
from myfilter.base.crange.vlinerange_filter import VLineRangeFilter

from util.str_util import Str
import util.lotto_util as lotto_util
from vo.number_vo import NumberVO


class LottoMain:

    lotto_number_path = r'D:\\Workspace\\docs\\lotto\\'
    lotto_working_path = r'D:\\Workspace\\vscode\\lotto\\'
    lotto_number_filename = 'numbers.txt'


    def __init__(self, debug: bool=False, file_path=None):
        """클래스 초기화 및 데이터 로드"""
        self.file_path = file_path or os.path.join(self.lotto_number_path, self.lotto_number_filename)
        self.df = None
        self.debug = debug

        self.numberVos = []  # 로또 번호 조합을 담을 리스트
        self.cache = []  # 1, 2등 번호 캐싱하기 위한 딕셔너리

        self._load_data()

        self._lotto_filter_init()


    def _load_data(self):
        """[내부 메서드] 파일을 안전하게 읽어오고 당첨번호를 분리합니다."""
        if not os.path.exists(self.file_path):
            print(f"❌ 파일을 찾을 수 없습니다: {self.file_path}")
            return
            
        try:
            # 탭 구분 텍스트 파일 읽기 (기본 인코딩 utf-8)
            self.df = pd.read_csv(self.file_path, sep='\t', encoding='utf-8')
            
            # 당첨번호 분리 (N1-N2-N3-N4-N5-N6 -> 개별 열 생성)
            if 'N1-N2-N3-N4-N5-N6' in self.df.columns:
                split_nums = self.df['N1-N2-N3-N4-N5-N6'].str.split('-', expand=True)
                for i in range(6):
                    self.df[f'번호{i+1}'] = split_nums[i].astype(int)
            print(f"✅ 데이터 로드 및 전처리 완료 ({len(self.df)}개 회차)")

            for idx, row in self.df.iterrows():
                numbervo = NumberVO(
                    round=row['회차'],
                    numbers=[row[f'번호{i+1}'] for i in range(6)],
                    bonus=row['BN']
                )

                self.numberVos.append(numbervo)
                self.cache.append(numbervo.toString())

                self.cache.extend(lotto_util.generate_second_prize_combinations(
                    main_numbers=[row[f'번호{i+1}'] for i in range(6)],
                    bonus_number=row['BN']))

        except Exception as e:
            print(f"❌ 데이터 로드 중 오류 발생: {e}")


    def _lotto_filter_init(self):

        last_vo: NumberVO = self.getLastVo()
        lastNumbers: list[int] = last_vo.numbers
        print(lastNumbers)

        last10 = sorted(list(set([num for vo in self.numberVos[-10:] for num in vo.numbers])))

        """필터 매니저 초기화 및 필터 등록"""
        self.filter_manager = myfilter.lotto_filter_manager.LottoFilterManager()

        # min filter ----------------------------------------------------------

        # 지난 10회 출현 수
        self.filter_manager.add_filter(Last10MinFilter(last10=last10, min_val=4, debug=self.debug))
        # 예시: AC 값이 7~10 사이인 필터와 합계가 100~175 사이인 필터 등록
        self.filter_manager.add_filter(ACMinFilter(min_val=6, debug=self.debug))
        # 예시: 마지막 번호가 31보다 큰 조합만 허용
        self.filter_manager.add_filter(LastNumberMinFilter(min_val=31, debug=self.debug))

        # max filter ----------------------------------------------------------

        # 예시: 첫 번째 번호가 15보다 작은 조합만 허용
        self.filter_manager.add_filter(FirstNumberMaxFilter(max_val=15, debug=self.debug))
        # 예시: 연속된 숫자 쌍이 0~1개인 조합만 허용, 1,2,3 형식도 차단
        self.filter_manager.add_filter(ConsecutivePairsMaxFilter(max_val=1, debug=self.debug))
        # 번호대별 수량(개수)을 체크하여 특정 번호대에 숫자가 과도하게 몰리거나 전멸하는 조합을 차단
        self.filter_manager.add_filter(NumberZoneCountMaxFilter(max_val=3, max_empty_zones=2, debug=self.debug))

        # boolean filter ----------------------------------------------------------

        # 예시: 지정된 간격으로 연속된 3개의 숫자 그룹이 존재하지 않는 조합만 허용, [1,3,5], [2,4,6] 형식 차단
        self.filter_manager.add_filter(EqualIntervalBooleanFilter(bool_val=False, interval_size=2, debug=self.debug))
        # 예시: 지정된 간격으로 연속된 3개의 숫자 그룹이 존재하지 않는 조합만 허용, [6,12,18], [2,8,14] 대각선 형식 차단
        self.filter_manager.add_filter(EqualIntervalBooleanFilter(bool_val=False, interval_size=6, debug=self.debug))
        # 예시: 지정된 간격으로 연속된 3개의 숫자 그룹이 존재하지 않는 조합만 허용, [1,9,17], [2,10,18] 대각선 형식 차단
        self.filter_manager.add_filter(EqualIntervalBooleanFilter(bool_val=False, interval_size=8, debug=self.debug))
        # 모든 간격에 대해 등간격 패턴이 존재하지 않는 조합만 허용
        # self.filter_manager.add_filter(EqualIntervalBooleanFilter(bool_val=False))
        # 예시: '1,2,4' 또는 '1,3,4' 처럼 3개 숫자가 징검다리 형태로 붙어있는 조합은 차단
        self.filter_manager.add_filter(SteppingStoneBooleanFilter(bool_val=False, debug=self.debug))
        
        # range filter ----------------------------------------------------------

        last5 = sorted(list(set([num for vo in self.numberVos[-5:] for num in vo.numbers])))
        self.filter_manager.add_filter(MatchCountRangeFilter(match_list=last5, min_val=2, max_val=5, title="Last5", debug=self.debug))

        self.filter_manager.add_filter(SumRangeFilter(min_val=100, max_val=175, debug=self.debug))
        self.filter_manager.add_filter(EvenRangeFilter(min_val=2, max_val=4, debug=self.debug))
        self.filter_manager.add_filter(HighRangeFilter(min_val=2, max_val=4, debug=self.debug))
        # 예시: 가로 라인 분포도 필터 등록 (한 줄에 최대 3개까지만 허용, 공이 들어있는 라인 수가 3~5개 안인지 검사)
        self.filter_manager.add_filter(HLineRangeFilter(min_val=3, max_val=5, max_lines=3, debug=self.debug))
        # 예시: 세로 라인 분포도 필터 등록 (한 줄에 최대 3개까지만 허용, 공이 들어있는 라인 수가 3~5개 안인지 검사)
        self.filter_manager.add_filter(VLineRangeFilter(min_val=3, max_val=5, max_lines=3, debug=self.debug))

        # 끝수 중 '가장 많이 중복된 개수'가 지정한 범위(1~2개) 안인지 검사합니다.
        self.filter_manager.add_filter(SameEndingRangeFilter(min_val=1, max_val=2, debug=self.debug))
        # 끝수 합계가 지정한 범위(12~38) 안인지 검사합니다.
        self.filter_manager.add_filter(SumEndingRangeFilter(min_val=12, max_val=38, debug=self.debug))
        # 9구간 라인수 범위 및 최대값 설정
        self.filter_manager.add_filter(SectionRangeFilter(min_val=3, max_val=5, max_counts=3, section=5, debug=self.debug))
        # 5구간 라인수 범위 및 최대값 설정
        self.filter_manager.add_filter(SectionRangeFilter(min_val=3, max_val=5, max_counts=3, section=9, debug=self.debug))

        # 네모서리 숫자들의 포함 갯수
        self.filter_manager.add_filter(CornerCountRangeFilter(min_val=1, max_val=4, debug=self.debug))
        # # 퐁당퐁당 패턴 - 내부적으로 13개 필터 검사
        for index in range(FondantMaxFilter.max_count):
            self.filter_manager.add_filter(FondantMaxFilter(max_val=6, index=index, debug=self.debug))

        # # 개구리 패턴
        for index in range(FrogRangeFilter.max_count):
            self.filter_manager.add_filter(FrogRangeFilter(min_val=2, max_val=4, index=index, debug=self.debug))

        # # 3의 배수, 5의 배수
        self.filter_manager.add_filter(MultipleRangeFilter(min_val=0, max_val=3, index=3, debug=self.debug))
        self.filter_manager.add_filter(MultipleRangeFilter(min_val=0, max_val=3, index=5, debug=self.debug))

        # # 솟수 
        self.filter_manager.add_filter(PrimeRangeFilter(min_val=0, max_val=3, debug=self.debug))

        # # 쌍수, 광땡
        self.filter_manager.add_filter(PairsDdangRangeFilter(min_val=0, max_val=1, index=0, debug=self.debug))
        self.filter_manager.add_filter(PairsDdangRangeFilter(min_val=0, max_val=1, index=1, debug=self.debug))

        # # 합성수
        self.filter_manager.add_filter(CompositionRangeFilter(min_val=0, max_val=3, debug=self.debug))

        for index in range(NeverRangeFilter.max_count):
            # # Never Patterns
            self.filter_manager.add_filter(NeverRangeFilter(min_val=1, max_val=5, index=index, debug=self.debug))

        # 이월수
        # # self.filter_manager.add_filter(RepeatRangeFilter(match_list=lastVo.numbers, min_val=0, max_val=2))
        self.filter_manager.add_filter(MatchCountRangeFilter(match_list=lastNumbers, min_val=0, max_val=2, title="이월수", debug=self.debug))

        # # 이웃수
        self.filter_manager.add_filter(NeighborRangeFilter(match_list=lastNumbers, min_val=0, max_val=3, debug=self.debug))

        for index in range(TriangleMaxFilter.max_count):
            # # 삼각형 패턴
            self.filter_manager.add_filter(TriangleMaxFilter(max_val=6, index=index, debug=self.debug))

        # 출현 빈도수 별 그룹을 생성하는 클래스입니다.
        # 1. groupA, groupB, groupC, panelA, panelB, panelC 리스트에 각 각 max개 이상 있으면 차단
        # 2. groupB에 0개 이면 차단, 즉 groupA, groupC에 6개란 뜻
        self.filter_manager.add_filter(WinningRankGroupMaxFilter(numberVos=self.numberVos, max_val=4))

    def get_sub_filters(self):
        flts: list[LottoFilter] = []
        for filter in self.filter_manager._filters:
            flts.append(filter)
            if isinstance(filter, VLineRangeFilter):
                return flts

        return flts

    """
    demo_data = { 'num1': [], 'num2': [], 'num3': [], 'num4': [], 'num5': [], 'num6': [], }
    """
    # 데이터프레임 빌드
    # txt 파일을 읽어와서 NumberVO 객체를 생성하고, 각 번호를 demo_data 딕셔너리에 추가합니다.
    def get_number_list_data_frame(self):
        # [데이터프레임 빌드] 
        demo_data = {
            'num1': [],
            'num2': [],
            'num3': [],
            'num4': [],
            'num5': [],
            'num6': [],
        }
        for numbervo in self.numberVos:
            nums = numbervo.numbers
            for i in range(0,6):
                cname = f"num{i+1}"
                demo_data[cname].append(nums[i])
        
        return pd.DataFrame(demo_data)


    def get_numbers(self, startRound: int, endRound: int):
        nums = []
        vos: list[NumberVO] = self.numberVos[startRound:endRound]
        # vo: NumberVO = None
        for vo in vos:
            nums += vo.numbers
        return sorted(list(set(nums)))


    def get_numbers_from_last(self, rounds: int):
        nums = []
        vos: list[NumberVO] = self.numberVos[-rounds:]
        for vo in vos:
            nums += vo.numbers
        return sorted(list(set(nums)))


    def get_numbers_from_start(self, startRound: int, rounds: int=0):
        if rounds==0:
            nums = []
            vos: list[NumberVO] = self.numberVos[startRound:]
            for vo in vos:
                nums += vo.numbers
            return sorted(list(set(nums)))
        return self.get_numbers(startRound, startRound+rounds)


    def get_row(self, idx: int) -> pd.Series:
        """데이터프레임에서 특정 인덱스의 행을 반환합니다."""
        if self.df is None:
            raise ValueError("데이터가 로드되지 않았습니다.")
        if idx < 0 or idx >= len(self.df):
            raise IndexError("인덱스가 범위를 벗어났습니다.")
        return self.df.iloc[idx]

    
    def getLastVo(self) -> NumberVO:
        """마지막 NumberVO 객체를 반환합니다."""
        if not self.numberVos:
            raise IndexError("번호 조합이 없습니다.")
        return self.numberVos[-1]


    def add_filter(self, lotto_filter):
        """필터 매니저에 새로운 필터를 추가합니다."""
        self.filter_manager.add_filter(lotto_filter)


    def save_file(self, output_path: str, tickets: list):
        vo: NumberVO = NumberVO()
        sb: list[str] = []
        for i, ticket in enumerate(tickets, 1):
            vo.numbers = ticket
            line = vo.toString(isSum=True)
            sb.append(line)

        FileUtil.write_lines(output_path, sb, "w")
        print(f"✅ 데이터 {Str.number_format(len(tickets))}개가 {output_path}에 저장되었습니다.")


    # def toString(self, numbers: list, isSum: bool=False, bonus: int=None) -> str:
    #     """객체 상태를 문자열로 반환 (디버깅용)"""
    #     str = "-".join(f"{num:02d}" for num in numbers[:6])
    #     if bonus is not None:
    #         str += f" {bonus:02d}]"
    #     if isSum:
    #         str += f" {sum(numbers)}"

    #     return str


def main():
    lotto_main = LottoMain(debug=True)

    filter: LottoFilter = None
    for filter in lotto_main.filter_manager._filters:
        has_min = filter.has_attr('min_val')
        has_max = filter.has_attr('max_val')
        fld: list[str] = []
        fld.append(f"{filter.__class__.__name__}")
        if has_min:
            fld.append(f"min_val={filter.get_min()}")
        if has_max:
            fld.append(f"max_val={filter.get_max()}")
        if not has_min and not has_max:
            fld.append(f"bool_val={filter.get_bool_val()}")

        sss = "|".join(fld)
        print(sss)

    if 0<len(lotto_main.filter_manager._filters):
        print(f"등록된 필터 개수: {len(lotto_main.filter_manager._filters)}")

        # print(f"Last10:{lotto_main.get_numbers_from_last(10)}")
        
        ns = []
        vos: list[NumberVO] = lotto_main.numberVos[-10:]
        for vo in vos:
            ns += vo.numbers

        last10 = sorted(list(set(ns)))
        print(f"Last10:{last10}")
        last10 = sorted(list(set([num for vo in vos for num in vo.numbers])))
        print(f"Last10:{last10}")
        return

    filtered_df = lotto_main.df.copy()
    for idx, row in filtered_df.iterrows():
        numbers = [row[f'번호{i+1}'] for i in range(6)]
        if idx < 10:
            print(f"{idx} {row['회차']} {numbers} {sum(numbers)}")
        else:
            break

    columns = filtered_df.columns.tolist()
    print("데이터프레임 컬럼 목록:", columns)

    for cache in lotto_main.cache[:5]:
        print("2등 조합 예시:", cache)

    print(f"row: {lotto_main.get_row(0)}")


# ==================== 실행 및 검증 ====================
if __name__ == "__main__":
    main()
