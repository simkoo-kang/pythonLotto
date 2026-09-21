import os
import pandas as pd

from class_main import ClassMain
from file_util import FileUtil
from lotto.vo.number_vo import NumberVO
import lotto_util
from str_util import Str


class LottoFrame(ClassMain):

    lotto_number_path = r"D:\\Workspace\\docs\\lotto\\"
    lotto_working_path = r"D:\\Workspace\\vscode\\lotto\\"
    eclipse_working_path = r"D:\\Workspace\\eclipse\\peace\\"

    lotto_number_filename = "numbers.txt"

    def __init__(
        self, log_fileidr=None, lotto_filename: str = None, debug: bool = False
    ):
        super().__init__(log_fileidr)

        """클래스 초기화 및 데이터 로드"""
        self.filename = lotto_filename or os.path.join(
            self.lotto_number_path, self.lotto_number_filename
        )
        self.df = None
        self.isDebug = debug

        self.numberVos = []  # 로또 번호 조합을 담을 리스트
        self.cache = []  # 1, 2등 번호 캐싱하기 위한 딕셔너리

        self._load_data()

    def _load_data(self):
        """[내부 메서드] 파일을 안전하게 읽어오고 당첨번호를 분리합니다."""
        if not os.path.exists(self.filename):
            self.debug(f"❌ 파일을 찾을 수 없습니다: {self.filename}")
            return

        try:
            # 탭 구분 텍스트 파일 읽기 (기본 인코딩 utf-8)
            self.df = pd.read_csv(self.filename, sep="\t", encoding="utf-8")

            # 당첨번호 분리 (N1-N2-N3-N4-N5-N6 -> 개별 열 생성)
            if "N1-N2-N3-N4-N5-N6" in self.df.columns:
                split_nums = self.df["N1-N2-N3-N4-N5-N6"].str.split("-", expand=True)
                for i in range(6):
                    self.df[f"번호{i+1}"] = split_nums[i].astype(int)
            self.debug(f"✅ 데이터 로드 및 전처리 완료 ({len(self.df)}개 회차)")

            for idx, row in self.df.iterrows():
                numbervo = NumberVO(
                    round=row["회차"],
                    date=row["추첨일"],
                    numbers=[row[f"번호{i+1}"] for i in range(6)],
                    bonus=row["BN"],
                )

                self.numberVos.append(numbervo)
                self.cache.append(numbervo.toString())

                self.cache.extend(
                    lotto_util.generate_second_prize_combinations(
                        main_numbers=[row[f"번호{i+1}"] for i in range(6)],
                        bonus_number=row["BN"],
                    )
                )

        except Exception as e:
            self.debug(f"❌ 데이터 로드 중 오류 발생: {e}")

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

    def get_numbers_from_start(self, startRound: int, rounds: int = 0):
        if rounds == 0:
            nums = []
            vos: list[NumberVO] = self.numberVos[startRound:]
            for vo in vos:
                nums += vo.numbers
            return sorted(list(set(nums)))
        return self.get_numbers(startRound, startRound + rounds)

    def getLastVo(self) -> NumberVO:
        """마지막 NumberVO 객체를 반환합니다."""
        if not self.numberVos:
            raise IndexError("번호 조합이 없습니다.")
        return self.numberVos[-1]

    def save_file(self, output_path: str, tickets: list):
        vo: NumberVO = NumberVO()
        sb: list[str] = []
        for i, ticket in enumerate(tickets, 1):
            vo.numbers = ticket
            line = vo.toString(isSum=True)
            sb.append(line)

        FileUtil.write_lines(output_path, sb, "w")
        print(
            f"✅ 데이터 {Str.number_format(len(tickets))}개가 {output_path}에 저장되었습니다."
        )

    def apppend_number(self, line):
        FileUtil.writeln(self.filename, line, "a")


# ==================== 실행 및 검증 ====================
if __name__ == "__main__":
    classMain = LottoFrame()

    classMain.debug(classMain.getLastVo().toString(isSum=True))
