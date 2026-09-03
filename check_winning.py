import os
import re
import traceback

from util.str_util import Str
from util.mydic_util import MyDic
from util.log_util import LogUtil
from lotto_main import LottoMain
from util.file_util import FileUtil
from vo.number_vo import NumberVO


logger = LogUtil.get_logger("LottoFileAnalyzer")


class CheckWinning(LottoMain):
    def __init__(self):
        super().__init__()

    def check_ticket(self, ticket: list[int]):
        matched_count = len(set(ticket) & self.winning_numbers)
        has_bonus = self.bonus_number in ticket
        
        # 등수 정의 (삼항 연산 활용)
        rank = "5등" if matched_count == 3 else "4등" if matched_count == 4 else "3등" if matched_count == 5 and not has_bonus else "2등" if matched_count == 5 and has_bonus else "1등" if matched_count == 6 else "낙첨"
        
        return {
            "ticket": ticket,
            "matched_count": matched_count,
            "has_bonus": has_bonus,
            "rank": rank
        }


# class CheckWinningReport:
#     def __init__(self, winning_numbers: set[int], bonus_number: int):
#         self.checker = CheckWinning(winning_numbers, bonus_number)
#         self.collected_numbers = []

#     def analyze_file(self, file_path: str):
#         with open(file_path, 'r', encoding='utf-8') as f:
#             for line in f:
#                 line = line.strip()
#                 if not line:
#                     continue
                
#                 # 1. 상단 로또 조합 패턴 분석 (ex: 06-20-29-33-38-40)
#                 if "-" in line and "\t" in line:
#                     nums_str, count = line.split("\t")
#                     ticket = [int(n) for n in nums_str.split("-")]
#                     result = self.checker.check_ticket(ticket)
#                     print(f"[조합] {nums_str} -> 일치: {result['matched']}개 (보너스: {result['has_bonus']}) | 결과: {result['rank']}")
                
#                 # 2. 하단 번호=개수 패턴 분석 (ex: 01 = 1)
#                 elif "=" in line:
#                     match = re.match(r"(\d+)\s*=\s*(\d+)", line)
#                     if match:
#                         num = int(match.group(1))
#                         self.collected_numbers.append(num)

#         # 3. 하단 수집 번호 최종 결과 도출
#         self.collected_numbers.sort()
#         final_matches = set(self.collected_numbers) & self.checker.winning_numbers
#         bonus_match = self.checker.bonus_number in self.collected_numbers
        
#         print("\n== 하단 집계 번호 분석 결과 ==")
#         print(f"- 생성된 번호 리스트: {self.collected_numbers}")
#         print(f"- 당첨 번호 일치 ({len(final_matches)}개): {list(final_matches)}")
#         print(f"- 보너스 번호 일치 여부: {'일치(8)' if bonus_match else '불일치'}")


# 파일 실행 (프로젝트 경로에 맞게 이름 지정)
# analyze_lotto_file("lotto_data.txt")
def analyze_lotto_file(file_path: str, winning_numbers: set[int], bonus_number: int):
    
    # 1. 조기 반환(Early Return) 패턴 적용: 파일이 아예 없으면 즉시 종료
    if not os.path.exists(file_path):
        logger.error(f"파일을 찾을 수 없습니다: {os.path.abspath(file_path)}")
        return  # 함수를 즉시 종료하고 메인으로 돌아감


    logger.debug(f"*** 분석 시작: {file_path}. =========================")
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
                    nums_str, count = line.split("\t")
                    ticket = [int(n) for n in nums_str.split("-")]
                    
                    # 교집합 연산으로 일치 개수 확인
                    matched = len(set(ticket) & winning_numbers)
                    has_bonus = bonus_number in ticket

                    if 0 < matched:
                        # 등수 정의 (삼항 연산 활용)
                        rank = "5등" if matched == 3 else "4등" if matched == 4 else "3등" if matched == 5 and not has_bonus else "2등" if matched == 5 and has_bonus else "1등" if matched == 6 else "낙첨"
                        logger.debug(f"[조합] {nums_str} -> 일치: {matched}개 (보너스: {has_bonus}) | 결과: {rank}")
                
                # 2. 하단 번호=개수 패턴 분석 (ex: 01 = 1)
                elif "=" in line:
                    match = re.match(r"(\d+)\s*=\s*(\d+)", line)
                    if match:
                        num = int(match.group(1))
                        collected_numbers.append(num)
    
        # 3. 하단 수집 번호 최종 결과 도출
        collected_numbers.sort()
        final_matches = set(collected_numbers) & winning_numbers
        bonus_match = bonus_number in collected_numbers
        
        logger.debug("== 하단 집계 번호 분석 결과 ==")
        logger.debug(f"- 생성된 번호 리스트: {collected_numbers}")
        logger.debug(f"- 당첨 번호 일치 ({len(final_matches)}개): {list(final_matches)}")
        logger.debug(f"- 보너스 번호 일치 여부: {'일치(8)' if bonus_match else '불일치'}")

    except FileNotFoundError:
        # 혹시 모를 동시성 삭제 이슈 방어
        logger.error(f"파일 열기 실패: {file_path}가 경로에 없습니다.")
        
    except Exception as e:
        # 인코딩 에러 등 기타 알 수 없는 에러 방어
        logger.error(f"파일 처리 중 예상치 못한 오류 발생: {e}")



def analyze_lotto_file_all(file_path: str, winning_numbers: set[int], bonus_number: int, debug: bool=False):
    # 1. 조기 반환(Early Return) 패턴 적용: 파일이 아예 없으면 즉시 종료
    if not os.path.exists(file_path):
        logger.error(f"파일을 찾을 수 없습니다: {os.path.abspath(file_path)}")
        return  # 함수를 즉시 종료하고 메인으로 돌아감

    logger.debug(f"*** 분석 시작: {file_path}. =========================")
    # 2. 예외 처리(try-except) 구조로 안전하게 파일 열기
    try:
        dic = MyDic()
        numDic = MyDic()
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                # 1. 상단 로또 조합 패턴 분석 (ex: 06-20-29-33-38-40)
                if "-" in line and "\t" in line:
                    nums_str, sum = line.split("\t")
                    ticket = [int(n) for n in nums_str.split("-")]
                    numDic.add_list(ticket)
                    if debug:
                        logger.debug(f"분석 중인 라인: {ticket:>15} | 합계: {sum:>3}")
                
                    
                    # 교집합 연산으로 일치 개수 확인
                    matched = len(set(ticket) & winning_numbers)
                    has_bonus = bonus_number in ticket
                    win = 1 if matched == 6 else 2 if matched == 5 and has_bonus else 3 if matched == 5 else 4 if matched == 4 else 5 if matched == 3 else 0
                    if 0 < win:
                        dic.add_dic(win)
                        if win < 4:
                            logger.debug(f"[조합] {nums_str:>2} -> 일치: {matched:>15}개 (보너스: {has_bonus:>5}) | 결과: {win}등")

        dic.sort(key=True, reverse=False) # key 오름차순
        numDic.sort(key=True, reverse=False) # key 오름차순
        logger.debug("== 전체 로또 번호 분석 결과 ==")
        for key, value in dic.items():
            logger.debug(f"- {key}등 당첨 개수: {value}개")
        
        for key, value in numDic.items():
            logger.debug(f"- {key:>2}: {Str.number_format(value):>8}개")

        logger.debug(f"성공: {file_path} 데이터 분석 완료.")

    except FileNotFoundError:
        # 혹시 모를 동시성 삭제 이슈 방어
        logger.error(f"파일 열기 실패: {file_path}가 경로에 없습니다.")
        
    except Exception as e:
        # 인코딩 에러 등 기타 알 수 없는 에러 방어
        logger.error(f"파일 처리 중 예상치 못한 오류 발생: {e}")
        traceback.print_exc()   # 예외 발생 시 스택 트레이스 출력


# ==================== 실행 및 검증 ====================
if __name__ == "__main__":

    checker = CheckWinning()
    lastVO: NumberVO = checker.getLastVo()

    winning_numbers = set(lastVO.get_numbers())
    bonus_number = lastVO.get_bonus()
    round = lastVO.get_round()
    print(f"== {round}회 로또 당첨 대조 리포트 ==")

    filename = os.path.join(FileUtil.CONF_PATH,f"make\{round}.txt")

    print(f"== 로또 {round}회 당첨 번호: {sorted(winning_numbers)} | 보너스 번호: {bonus_number} ==")
    analyze_lotto_file(filename, winning_numbers, bonus_number)
    
    filename = os.path.join(FileUtil.CONF_PATH,f"make\{round}_filtered.txt", )
    analyze_lotto_file_all(filename, winning_numbers, bonus_number)

    filename = os.path.join(FileUtil.CONF_PATH,f"make\{round}_all.txt")
    analyze_lotto_file_all(filename, winning_numbers, bonus_number)

