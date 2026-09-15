# myfilter.py 파일 안에서 구체적인 클래스 이름들을 직접 꺼내옵니다.
from lotto.myfilter.base.crange.matchcountrange_filter import MatchCountRangeFilter

from lotto.lotto_main import LottoMain
import util.lotto_util as lotto_util


class LottoTest(LottoMain):
    def __init__(self):
        super().__init__()


if __name__ == "__main__":
    # LottoTest 인스턴스 생성
    lotto_test = LottoTest()

    lotto_test.add_filter(MatchCountRangeFilter(match_list=[1, 2, 3, 4, 5, 6], min_val=0, max_val=1, title="Match Count Range Filter"))

    # 1. 데이터 로드 및 초기화
    # lotto_test.load_data("lotto_numbers.csv")  # CSV 파일 경로를 지정하세요.
    print(f"총 {len(lotto_test.numberVos)}개의 로또 번호 데이터를 로드했습니다.")

    # 2. 필터 매니저 초기화 및 필터 등록
    # lotto_test._lotto_filter_init()
    print(f"총 {len(lotto_test.filter_manager._filters)}개의 필터를 등록했습니다.")

    # 3. 대량의 가상 로또 번호 조합 리스트 (테스트 데이터)
    bulk_samples = []
    for i in range(1, 10):
        bulk_samples.append(lotto_test.numberVos[-i].numbers)  # 실제 데이터에서 번호 조합을 가져옵니다.

    for sample in bulk_samples:
        for lottoFilter in lotto_test.filter_manager._filters:
            result = lottoFilter.filter(sample)
            if  result:
                print(f"✅ 통과: 번호 조합: {sample} {sum(sample)} AC={lotto_util.calculate_ac(sample)}"
                      f" 필터 이름: {lottoFilter.name}")
            else:
                print(f"차단 번호 조합: {sample} {sum(sample)} AC={lotto_util.calculate_ac(sample)}"
                       f" 필터 이름: {lottoFilter.name}")

    for i in range(0,5):
        print(i)
