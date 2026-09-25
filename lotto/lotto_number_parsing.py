import re

from lxml import html
import os

from lotto.lotto_frame import LottoFrame
import lotto_util
from str_util import Str
from util.list_util import ListUtil
from util.date_util import CDate


class ParseLottoNumber(LottoFrame):

    def __init__(self, log_filedir=None, lotto_filename=None, debug=False):
        super().__init__(log_filedir, lotto_filename, debug)
        self.tree = None

    # "2026.09.12 추첨"에서 날짜 추출 => 2026-09-12
    def get_date(self, datestr):
        # 2. 정규표현식으로 숫자 패턴 추출 (연-4자리, 월-1~2자리, 일-1~2자리)
        # 구분자가 마침표(.), 하이픈(-), 슬래시(/)인 경우 모두 대응 가능합니다.
        match = re.search(r"(\d{4})[\.\-\/](\d{1,2})[\.\-\/](\d{1,2})", datestr)
        if match:
            # 각 그룹에서 연, 월, 일을 가져옵니다.
            year, month, day = match.groups()
            # 3. f-string을 활용해 YYYY-MM-DD 형식으로 결합 (월, 일이 1자리일 경우 0을 채움)
            formatted_date = f"{year}-{int(month):02d}-{int(day):02d}"

            return formatted_date

        self.debug(f"{datestr} - 날짜 패턴을 찾을 수 없습니다.")

    def parse_html(self, filename):
        if not os.path.exists(filename):
            self.debug(f"{filename} is not found!")
            return

        # 1. HTML 파일 읽기
        with open(filename, "r", encoding="utf-8") as f:
            html_content = f.read()

        # 2. HTML 트리에 로드하기
        tree = html.fromstring(html_content)

        infosb = ListUtil.StrBuilder()

        # 3. XPath로 데이터 추출하기
        """_summary_
        ['제', '1242', '회 추첨 결과', '2026.09.19 추첨']
        node가 이전 회차와 이 번 회차 2개의 정보를 가져온다.
        """
        nodes = tree.xpath("//div[@class='infoWrap-topBox']//text()")
        cleaned_texts = [text.strip() for text in nodes if text.strip()]

        # ['제', '1242', '회 추첨 결과', '2026.09.19 추첨']
        headinfo = cleaned_texts[4:] if 4 < len(cleaned_texts) else cleaned_texts
        round = int(headinfo[1])
        date = self.get_date(headinfo[3])

        infosb.append(round).append(date)
        # self.debug(infosb.to_string_tab())

        """_summary_
        로또 번호 + 보너스 번호
        """
        nodes = tree.xpath("//div[@class='result-ballBox']//text()")
        cleaned_texts = [text.strip() for text in nodes if text.strip()]

        numberinfo = cleaned_texts[9:]
        nn, nac, bn = [], [], 0
        sum, bn = 0, 0
        for i in range(len(numberinfo)):
            if i == 0 or i == 7:
                continue
            n = int(numberinfo[i])
            if i < 7:
                nn.append(f"{n:02d}")
                sum += n
                nac.append(n)
            else:
                bn = f"{n:02d}"

        infosb.append("-".join(nn)).append(bn).append(sum)
        # self.debug(infosb.to_string_tab())

        """_summary_
        AC, 지난 5회, 지난 10회
        """
        last5 = self.get_numbers_from_last(5)
        last10 = self.get_numbers_from_last(10)

        infosb.append(lotto_util.calculate_ac(nac)).append(
            ListUtil.contains(last5, nac)
        ).append(ListUtil.contains(last10, nac))

        # self.debug(infosb.to_string_tab())

        """_summary_
        각 등수의 담첨자 수와 당첨 금액
        """
        nodes = tree.xpath("//div[@class='tbody-tr']//text()")
        cleaned_texts = [text.strip() for text in nodes if text.strip()]

        # 1등
        rank_count, rank_money = 0, 0
        for i in range(len(cleaned_texts)):
            if i == 2:
                rank_count = int(cleaned_texts[i])
            elif i == 3:
                rank_money = Str.number_format(
                    int(Str.strip_not_digit(cleaned_texts[i]))
                )
            elif 3 < i:
                break

        infosb.append(rank_count).append(rank_money)

        # 2등
        cleaned_texts = cleaned_texts[6:]
        rank_count, rank_money = 0, 0
        for i in range(len(cleaned_texts)):
            if i == 2:
                rank_count = int(cleaned_texts[i])
            elif i == 3:
                rank_money = Str.number_format(
                    int(Str.strip_not_digit(cleaned_texts[i]))
                )
            elif 3 < i:
                break

        infosb.append(rank_count).append(rank_money)

        # 3등
        cleaned_texts = cleaned_texts[8:]
        rank_count, rank_money = 0, 0
        for i in range(len(cleaned_texts)):
            if i == 2:
                rank_count = Str.number_format(
                    int(Str.strip_not_digit(cleaned_texts[i]))
                )
            elif i == 3:
                rank_money = Str.number_format(
                    int(Str.strip_not_digit(cleaned_texts[i]))
                )
            elif 3 < i:
                break

        infosb.append(rank_count).append(rank_money)

        # 4등
        cleaned_texts = cleaned_texts[6:]
        rank_count, rank_money = 0, 0
        for i in range(len(cleaned_texts)):
            if i == 2:
                rank_count = Str.number_format(
                    int(Str.strip_not_digit(cleaned_texts[i]))
                )
            elif i == 3:
                rank_money = Str.number_format(
                    int(Str.strip_not_digit(cleaned_texts[i]))
                )
            elif 3 < i:
                break

        infosb.append(rank_count).append(rank_money)

        # 5등
        cleaned_texts = cleaned_texts[6:]
        rank_count, rank_money = 0, 0
        for i in range(len(cleaned_texts)):
            if i == 2:
                rank_count = Str.number_format(
                    int(Str.strip_not_digit(cleaned_texts[i]))
                )
            elif i == 3:
                rank_money = Str.number_format(
                    int(Str.strip_not_digit(cleaned_texts[i]))
                )
            elif 3 < i:
                break

        infosb.append(rank_count).append(rank_money)

        # self.debug(infosb.to_string_tab())

        """_summary_
        # 자동, 수동, 반자동
        """
        nodes = tree.xpath("//div[@id='remarks']//text()")
        cleaned_texts = [text.strip() for text in nodes if text.strip()][1:]
        infosb.append_all([Str.strip_not_digit(text) for text in cleaned_texts])

        self.debug(infosb.to_string_tab())

        self.apppend_number(infosb.to_string_tab())


# ==================== 실행 및 검증 ====================
if __name__ == "__main__":
    classMain = ParseLottoNumber()

    lastVo = classMain.getLastVo()
    round = lastVo.get_round() + 1

    print(lastVo.get_date())
    lotto_date = CDate(lastVo.get_date()).add_days(7)
    next_date = lotto_date.to_string(CDate.DASH_DATE_FORMAT)
    today = CDate()
    if today.is_before(next_date):
        print(f"아직 추첨 전입니다. 추첨일은 {next_date} 입니다.")
    else:
        eclipse_html_path = r"D:\\Workspace\\eclipse\\peace\\conf\\lotto\\html\\"
        filename = os.path.join(eclipse_html_path, f"{round}.html")
        classMain.parse_html(filename=filename)
