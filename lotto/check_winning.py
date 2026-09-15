import os
import re
import traceback

from util.str_util import Str
from util.mydic_util import Dic
from util.log_util import LogUtil
from lotto.lotto_main import LottoMain
from util.file_util import FileUtil
from lotto.vo.number_vo import NumberVO


class CheckWinning(LottoMain):
    def __init__(self):
        super().__init__()

        numbervo: NumberVO = self.getLastVo()
        self.round = numbervo.get_round()
        self.winning_numbers = set(numbervo.get_numbers())
        self.bonus_number = numbervo.get_bonus()
        
        self.logger = LogUtil.get_logger("LottoFileAnalyzer")


    def check_ticket(self, ticket: list[int]):
        matched_count = len(set(ticket) & self.winning_numbers)
        has_bonus = self.bonus_number in ticket
        
        # 등수 정의 (삼항 연산 활용)
        rank = 5 if matched_count == 3 else 4 if matched_count == 4 else 3 if matched_count == 5 and not has_bonus else 2 if matched_count == 5 and has_bonus else 1 if matched_count == 6 else 0
        
        return {
            "ticket": ticket,
            "matched_count": matched_count,
            "has_bonus": has_bonus,
            "rank": rank
        }


    # 로또 번호를 분석하여 당첨 여부를 체크하는 메서드 - make/round.txt 파일을 분석하여 당첨 여부를 체크합니다.
    def analyze_lotto_file(self, file_path: str):
        
        # 1. 조기 반환(Early Return) 패턴 적용: 파일이 아예 없으면 즉시 종료
        if not os.path.exists(file_path):
            self.logger.error(f"파일을 찾을 수 없습니다: {os.path.abspath(file_path)}")
            return  # 함수를 즉시 종료하고 메인으로 돌아감

        self.logger.debug("")
        self.logger.debug(f"*** 분석 시작: {file_path}. =========================")
        # 2. 예외 처리(try-except) 구조로 안전하게 파일 열기
        try:
            collected_numbers = []
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # 1. 상단 로또 조합 패턴 분석 (ex: 06-20-29-33-38-40)
                    if "-" in line and "\t" in line:
                        strs = line.split("\t")
                        ticket = [int(n) for n in strs[0].split("-")]

                        result = self.check_ticket(ticket)
                        if 0 < result['rank']:
                            self.logger.debug(f"[조합] {strs[0]} -> 일치: {result['matched_count']}개 (보너스: {result['has_bonus']}) | 결과: {result['rank']}등")
                    
                    # 2. 하단 번호=개수 패턴 분석 (ex: 01 = 1)
                    elif "=" in line:
                        match = re.match(r"(\d+)\s*=\s*(\d+)", line)
                        if match:
                            num = int(match.group(1))
                            collected_numbers.append(num)
        
            # 3. 하단 수집 번호 최종 결과 도출
            collected_numbers.sort()
            final_matches = set(collected_numbers) & self.winning_numbers
            bonus_match = self.bonus_number in collected_numbers
            
            self.logger.debug("== 하단 집계 번호 분석 결과 ==")
            self.logger.debug(f"- 생성된 번호 리스트: {collected_numbers}")
            self.logger.debug(f"- 당첨 번호 일치 ({len(final_matches)}개): {list(final_matches)}")
            self.logger.debug(f"- 보너스 번호 일치 여부: {'일치(8)' if bonus_match else '불일치'}")

        except FileNotFoundError:
            # 혹시 모를 동시성 삭제 이슈 방어
            self.logger.error(f"파일 열기 실패: {file_path}가 경로에 없습니다.")
            
        except Exception as e:
            # 인코딩 에러 등 기타 알 수 없는 에러 방어
            self.logger.error(f"파일 처리 중 예상치 못한 오류 발생: {e}")
            traceback.print_exc()


    # 로또 번호를 분석하여 당첨 여부를 체크하는 메서드 - make/round_all[filtered].txt 파일을 분석하여 당첨 여부를 체크합니다.
    def analyze_lotto_all_file(self, file_path: str):
        
        # 1. 조기 반환(Early Return) 패턴 적용: 파일이 아예 없으면 즉시 종료
        if not os.path.exists(file_path):
            self.logger.error(f"파일을 찾을 수 없습니다: {os.path.abspath(file_path)}")
            return  # 함수를 즉시 종료하고 메인으로 돌아감

        self.logger.debug("")
        self.logger.debug(f"*** 분석 시작: {file_path}. =========================")
        # 2. 예외 처리(try-except) 구조로 안전하게 파일 열기
        try:
            wins = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # 1. 상단 로또 조합 패턴 분석 (ex: 06-20-29-33-38-40)
                    if "-" in line and "\t" in line:
                        nums_str, count = line.split("\t")
                        ticket = [int(n) for n in nums_str.split("-")]

                        result = self.check_ticket(ticket)
                        if 0 < result['rank']:
                            wins[result['rank']] += 1
                    
            for rank, count in wins.items():
                if 0<count:
                    self.logger.debug(f"- {rank}등 당첨 개수: {count}개")

        except FileNotFoundError:
            # 혹시 모를 동시성 삭제 이슈 방어
            self.logger.error(f"파일 열기 실패: {file_path}가 경로에 없습니다.")
            
        except Exception as e:
            # 인코딩 에러 등 기타 알 수 없는 에러 방어
            self.logger.error(f"파일 처리 중 예상치 못한 오류 발생: {e}")


# ==================== 실행 및 검증 ====================
if __name__ == "__main__":

    checker = CheckWinning()

    round = checker.round

    print(f"== {round}회 로또 당첨 대조 리포트 ==")

    filename = FileUtil.get_lotto_make_file(round)
    checker.analyze_lotto_file(filename)

    filename = FileUtil.get_lotto_make_filtered_file(round)
    checker.analyze_lotto_all_file(filename)

    filename = FileUtil.get_lotto_make_all_file(round)
    checker.analyze_lotto_all_file(filename)

